"""Module for generating embeddings using Gemini."""

from __future__ import annotations

import logging

from google import genai

from app.config import settings

logger = logging.getLogger(__name__)


def generate_embeddings(texts: list[str]) -> list[list[float]]:
    """Generates embeddings for a batch of text strings using configured Gemini model."""
    if not settings.GEMINI_API_KEY:
        raise ValueError("GEMINI_API_KEY is not configured in settings.")

    client = genai.Client(api_key=settings.GEMINI_API_KEY)
    
    # Process in batches to avoid API limits if texts list is large
    batch_size = 100
    all_embeddings: list[list[float]] = []

    for i in range(0, len(texts), batch_size):
        batch = texts[i : i + batch_size]
        response = client.models.embed_content(
            model=settings.GEMINI_EMBEDDING_MODEL,
            contents=batch,
        )
        batch_embeddings = [data.values for data in response.embeddings]
        all_embeddings.extend(batch_embeddings)

    return all_embeddings
