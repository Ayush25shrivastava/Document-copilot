"""Module for generating embeddings using OpenAI or Gemini."""

from __future__ import annotations

import logging

from openai import OpenAI

from app.config import settings

logger = logging.getLogger(__name__)


def generate_embeddings(texts: list[str]) -> list[list[float]]:
    """Generates embeddings for a batch of text strings using configured OpenAI model."""
    if not settings.OPENAI_API_KEY:
        raise ValueError("OPENAI_API_KEY is not configured in settings.")

    client = OpenAI(api_key=settings.OPENAI_API_KEY)
    
    # Process in batches to avoid API limits if texts list is large
    batch_size = 100
    all_embeddings: list[list[float]] = []

    for i in range(0, len(texts), batch_size):
        batch = texts[i : i + batch_size]
        response = client.embeddings.create(
            input=batch,
            model=settings.OPENAI_EMBEDDING_MODEL,
        )
        batch_embeddings = [data.embedding for data in response.data]
        all_embeddings.extend(batch_embeddings)

    return all_embeddings
