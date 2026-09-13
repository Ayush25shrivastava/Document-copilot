# /// script
# dependencies = [
#     "docling",
# ]
# ///
from __future__ import annotations

import json
import logging
import sys
import time
from pathlib import Path

# pyrefly: ignore [missing-import]
from docling.document_converter import DocumentConverter

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("docling_converter")

DATA_DIR = Path(__file__).resolve().parent
DOWNLOADS_DIR = DATA_DIR / "downloads"
MARKDOWNS_DIR = DATA_DIR / "markdowns"
MANIFEST_PATH = DOWNLOADS_DIR / "manifest.json"
MD_MANIFEST_PATH = MARKDOWNS_DIR / "manifest.json"


def main():
    if not DOWNLOADS_DIR.exists():
        logger.error(f"Downloads directory not found at {DOWNLOADS_DIR}")
        sys.exit(1)

    MARKDOWNS_DIR.mkdir(parents=True, exist_ok=True)

    # Find all html / htm files in downloads
    html_files = sorted(
        list(DOWNLOADS_DIR.rglob("*.htm")) + list(DOWNLOADS_DIR.rglob("*.html"))
    )

    if not html_files:
        logger.warning("No HTML/HTM filing files found in data/downloads!")
        return

    logger.info(f"Found {len(html_files)} files to convert using Docling.")
    logger.info("Initializing DocumentConverter...")
    converter = DocumentConverter()

    converted_records = []
    total_files = len(html_files)

    for idx, file_path in enumerate(html_files, start=1):
        rel_path = file_path.relative_to(DOWNLOADS_DIR)
        out_rel_path = rel_path.with_suffix(".md")
        out_file_path = MARKDOWNS_DIR / out_rel_path

        out_file_path.parent.mkdir(parents=True, exist_ok=True)

        logger.info(f"[{idx}/{total_files}] Converting {rel_path} -> {out_rel_path}...")
        start_time = time.time()

        try:
            conv_result = converter.convert(file_path)
            md_content = conv_result.document.export_to_markdown()

            with open(out_file_path, "w", encoding="utf-8") as f:
                f.write(md_content)

            elapsed = time.time() - start_time
            logger.info(f"Saved {out_rel_path} ({len(md_content):,} chars) in {elapsed:.1f}s")

            converted_records.append({
                "source_path": str(rel_path),
                "markdown_path": str(out_rel_path),
                "size_chars": len(md_content),
                "status": "success",
                "duration_seconds": round(elapsed, 2),
            })
        except Exception as exc:
            logger.exception("Failed to convert %s", rel_path)
            converted_records.append({
                "source_path": str(rel_path),
                "markdown_path": str(out_rel_path),
                "status": "error",
                "error": str(exc),
            })

    # Save conversion manifest
    with open(MD_MANIFEST_PATH, "w", encoding="utf-8") as f:
        json.dump(
            {
                "converted_at": time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime()),
                "total_files": total_files,
                "successful_conversions": sum(1 for r in converted_records if r.get("status") == "success"),
                "records": converted_records,
            },
            f,
            indent=2,
        )

    logger.info(f"Conversion complete! Markdown files and manifest saved to {MARKDOWNS_DIR}")


if __name__ == "__main__":
    main()
