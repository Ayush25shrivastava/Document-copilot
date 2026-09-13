"""Module for chunking markdown documents semantically or by headers/tokens."""

from __future__ import annotations

import re
from typing import Any

import tiktoken


def count_tokens(text: str, model_name: str = "text-embedding-3-small") -> int:
    """Counts tokens in string using tiktoken."""
    try:
        encoding = tiktoken.encoding_for_model(model_name)
    except KeyError:
        encoding = tiktoken.get_encoding("cl100k_base")
    return len(encoding.encode(text))


def chunk_markdown(
    markdown_text: str,
    target_chunk_tokens: int = 500,
    overlap_tokens: int = 50,
    embedding_model: str = "text-embedding-3-small",
) -> list[dict[str, Any]]:
    """Chunks markdown text preserving headings/sections where possible.
    
    Returns a list of dicts containing:
      - chunk_index: int
      - chunk_text: str
      - token_count: int
      - section: str | None
      - metadata_json: dict
    """
    lines = markdown_text.splitlines(keepends=True)
    chunks: list[dict[str, Any]] = []
    
    current_section = "Preamble"
    current_lines: list[str] = []
    current_tokens = 0
    chunk_idx = 0

    header_re = re.compile(r"^(#{1,6})\s+(.+)$")

    for line in lines:
        header_match = header_re.match(line.strip())
        if header_match:
            current_section = header_match.group(2).strip()

        line_tokens = count_tokens(line, model_name=embedding_model)

        if current_tokens + line_tokens > target_chunk_tokens and current_lines:
            section_clean = current_section[:250] if current_section else None
            chunk_text = "".join(current_lines).strip()
            if chunk_text:
                chunks.append({
                    "chunk_index": chunk_idx,
                    "chunk_text": chunk_text,
                    "token_count": count_tokens(chunk_text, model_name=embedding_model),
                    "section": section_clean,
                    "metadata_json": {
                        "header": current_section,
                    },
                })
                chunk_idx += 1

            # Keep overlap lines if possible
            overlap_lines: list[str] = []
            overlap_count = 0
            for prev_line in reversed(current_lines):
                prev_tokens = count_tokens(prev_line, model_name=embedding_model)
                if overlap_count + prev_tokens <= overlap_tokens:
                    overlap_lines.insert(0, prev_line)
                    overlap_count += prev_tokens
                else:
                    break

            current_lines = overlap_lines
            current_tokens = overlap_count

        current_lines.append(line)
        current_tokens += line_tokens

    if current_lines:
        section_clean = current_section[:250] if current_section else None
        chunk_text = "".join(current_lines).strip()
        if chunk_text:
            chunks.append({
                "chunk_index": chunk_idx,
                "chunk_text": chunk_text,
                "token_count": count_tokens(chunk_text, model_name=embedding_model),
                "section": section_clean,
                "metadata_json": {
                    "header": current_section,
                },
            })

    return chunks
