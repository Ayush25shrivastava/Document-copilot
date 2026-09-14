"""Backfill script for computing missing embeddings.

Queries `document_chunks` where `embedding IS NULL`, generates 3072-dimensional
Gemini vector embeddings in rate-limited batches, and updates the database.
"""

from __future__ import annotations

import logging
import sys
import time

from sqlalchemy import create_engine, select, text
from sqlalchemy.orm import Session

from app.config import settings
from app.database.document_chunk import DocumentChunk
from app.ingestion.embedder import generate_embeddings

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("backfill_embeddings")

BATCH_SIZE = 100  # Number of chunks per API request batch
SLEEP_BETWEEN_BATCHES = 2.0  # Seconds to pause between batches to stay under rate limits


def backfill_embeddings(max_chunks: int | None = None):
    engine = create_engine(settings.sqlalchemy_database_url)

    with Session(engine) as session:
        # Count remaining un-embedded chunks
        unembedded_stmt = select(DocumentChunk).where(DocumentChunk.embedding.is_(None))
        unembedded_chunks = session.scalars(unembedded_stmt).all()
        total_remaining = len(unembedded_chunks)

        logger.info("Found %d total document chunks missing embeddings.", total_remaining)
        if total_remaining == 0:
            logger.info("All document chunks already have embeddings! Nothing to do.")
            return

        chunks_to_process = unembedded_chunks[:max_chunks] if max_chunks else unembedded_chunks
        logger.info("Processing %d chunks in batches of %d...", len(chunks_to_process), BATCH_SIZE)

        processed_count = 0
        for i in range(0, len(chunks_to_process), BATCH_SIZE):
            batch_chunks = chunks_to_process[i : i + BATCH_SIZE]
            batch_texts = [chunk.chunk_text for chunk in batch_chunks]

            logger.info(
                "[%d/%d] Generating embeddings for batch of %d chunks...",
                processed_count + 1,
                len(chunks_to_process),
                len(batch_texts),
            )

            try:
                embeddings = generate_embeddings(batch_texts)
                for chunk, emb in zip(batch_chunks, embeddings):
                    chunk.embedding = emb

                session.commit()
                processed_count += len(batch_chunks)
                logger.info(
                    "  Successfully saved %d embeddings (Total progress: %d/%d).",
                    len(embeddings),
                    processed_count,
                    len(chunks_to_process),
                )
            except Exception as e:
                session.rollback()
                logger.error("Failed to generate/save embeddings for batch: %s", e)
                logger.info("Stopping backfill. You can safely re-run this script anytime.")
                break

            if SLEEP_BETWEEN_BATCHES > 0 and i + BATCH_SIZE < len(chunks_to_process):
                time.sleep(SLEEP_BETWEEN_BATCHES)

        logger.info("Backfill session completed. %d chunks updated.", processed_count)


if __name__ == "__main__":
    limit = int(sys.argv[1]) if len(sys.argv) > 1 else None
    backfill_embeddings(max_chunks=limit)
