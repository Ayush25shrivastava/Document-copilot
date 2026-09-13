"""Main ingestion pipeline script.

Reads SEC 10-K filings from data/markdowns and data/downloads/manifest.json,
upserts records into `source_documents`, chunks the content, computes vector embeddings,
and stores chunks in `document_chunks` with TSVector full-text search indexing.
"""

from __future__ import annotations

import json
import logging
import sys
from datetime import UTC, datetime
from pathlib import Path

from sqlalchemy import create_engine, select, text
from sqlalchemy.orm import Session

from app.config import settings
from app.database.document_chunk import DocumentChunk
from app.database.source_document import SourceDocument
from app.ingestion.chunker import chunk_markdown
from app.ingestion.embedder import generate_embeddings

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("ingestion_pipeline")

DATA_DIR = Path(__file__).resolve().parent.parent.parent.parent / "data"
MARKDOWNS_DIR = DATA_DIR / "markdowns"
MANIFEST_PATH = DATA_DIR / "downloads" / "manifest.json"

COMPANY_NAMES = {
    "AAPL": "Apple Inc.",
    "MSFT": "Microsoft Corporation",
    "NVDA": "NVIDIA Corporation",
    "AMZN": "Amazon.com, Inc.",
    "GOOGL": "Alphabet Inc.",
}


def load_manifest() -> dict[str, dict]:
    """Loads downloads manifest and maps filing local path to filing metadata."""
    if not MANIFEST_PATH.exists():
        logger.warning("Manifest file not found at %s", MANIFEST_PATH)
        return {}

    with open(MANIFEST_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)

    manifest_map = {}
    for filing in data.get("filings", []):
        # normalize path representation
        norm_path = filing.get("local_path", "").replace("/", "\\")
        manifest_map[norm_path] = filing
    return manifest_map


def ingest_all(generate_embeds: bool = True):
    engine = create_engine(settings.sqlalchemy_database_url)
    manifest_map = load_manifest()

    md_files = sorted(MARKDOWNS_DIR.rglob("*.md"))
    logger.info("Found %d markdown filing files to ingest.", len(md_files))

    with Session(engine) as session:
        for idx, md_file in enumerate(md_files, start=1):
            rel_path = str(md_file.relative_to(MARKDOWNS_DIR))
            # match with source htm relative path in manifest
            source_htm_rel_path = rel_path.replace(".md", ".htm")
            filing_meta = manifest_map.get(source_htm_rel_path, {})

            ticker = filing_meta.get("ticker")
            if not ticker:
                # Fallback parse from filename e.g. 2021\aapl_10-k_...
                ticker = md_file.name.split("_")[0].upper()

            company_name = COMPANY_NAMES.get(ticker, f"{ticker} Corp.")
            filing_type = filing_meta.get("form", "10-K")
            
            filing_date_str = filing_meta.get("filing_date")
            filing_date = (
                datetime.strptime(filing_date_str, "%Y-%m-%d").replace(tzinfo=UTC).date()
                if filing_date_str
                else datetime.now(UTC).date()
            )

            # Year from parent directory e.g. 2021
            try:
                fiscal_year = int(md_file.parent.name)
            except ValueError:
                fiscal_year = filing_date.year

            accession_number = filing_meta.get("accession_number")
            source_url = filing_meta.get("source_url")

            with open(md_file, "r", encoding="utf-8") as f:
                content = f.read()

            logger.info(
                "[%d/%d] Ingesting %s (%s %d)...",
                idx,
                len(md_files),
                ticker,
                filing_type,
                fiscal_year,
            )

            # Check if source document already exists (upsert logic)
            stmt = select(SourceDocument).where(
                SourceDocument.ticker == ticker,
                SourceDocument.fiscal_year == fiscal_year,
                SourceDocument.filing_type == filing_type,
            )
            existing_doc = session.scalars(stmt).first()

            if existing_doc:
                existing_doc.content = content
                existing_doc.company_name = company_name
                existing_doc.filing_date = filing_date
                existing_doc.accession_number = accession_number
                existing_doc.source_url = source_url
                existing_doc.metadata_json = filing_meta
                doc = existing_doc
                logger.info("  Updated existing SourceDocument ID: %s", doc.id)
            else:
                doc = SourceDocument(
                    ticker=ticker,
                    company_name=company_name,
                    filing_type=filing_type,
                    filing_date=filing_date,
                    fiscal_year=fiscal_year,
                    accession_number=accession_number,
                    source_url=source_url,
                    content=content,
                    metadata_json=filing_meta,
                )
                session.add(doc)
                session.flush()  # populate doc.id
                logger.info("  Created new SourceDocument ID: %s", doc.id)

            # Delete any existing chunks for this document before re-chunking
            session.query(DocumentChunk).filter(
                DocumentChunk.document_id == doc.id
            ).delete()

            # Chunk markdown document
            chunks_data = chunk_markdown(content)
            logger.info("  Generated %d chunks for document.", len(chunks_data))

            # Generate embeddings
            embeddings = []
            if generate_embeds and chunks_data:
                logger.info("  Computing embeddings for %d chunks...", len(chunks_data))
                chunk_texts = [c["chunk_text"] for c in chunks_data]
                embeddings = generate_embeddings(chunk_texts)

            # Create DocumentChunk instances
            for i, chunk_info in enumerate(chunks_data):
                emb = embeddings[i] if generate_embeds and i < len(embeddings) else None
                chunk_obj = DocumentChunk(
                    document_id=doc.id,
                    chunk_index=chunk_info["chunk_index"],
                    chunk_text=chunk_info["chunk_text"],
                    token_count=chunk_info["token_count"],
                    section=chunk_info["section"],
                    metadata_json=chunk_info["metadata_json"],
                    embedding=emb,
                )
                session.add(chunk_obj)

            session.commit()

        # Update tsvector column for full-text search across all chunks
        logger.info("Updating full-text TSVector search_vector on document_chunks...")
        session.execute(
            text(
                "UPDATE document_chunks "
                "SET search_vector = to_tsvector('english', chunk_text) "
                "WHERE search_vector IS NULL;"
            )
        )
        session.commit()
        logger.info("Ingestion completed successfully!")


if __name__ == "__main__":
    generate = "--no-embeds" not in sys.argv
    ingest_all(generate_embeds=generate)
