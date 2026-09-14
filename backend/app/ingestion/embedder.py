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
        batch_texts = texts[i : i + batch_size]
        batch = [[t] for t in batch_texts]
        
        max_retries = 7
        response = None
        for attempt in range(max_retries):
            try:
                response = client.models.embed_content(
                    model=settings.GEMINI_EMBEDDING_MODEL,
                    contents=batch,
                )
                break
            except Exception as e:
                import time
                if hasattr(e, 'code') and e.code == 429 and attempt < max_retries - 1:
                    sleep_time = 15 * (2 ** attempt)
                    logger.warning("Rate limit hit. Retrying in %s seconds...", sleep_time)
                    time.sleep(sleep_time)
                else:
                    raise

        if response is None:
            raise RuntimeError("Failed to generate embeddings after multiple retries.")
            
        batch_embeddings = [data.values for data in response.embeddings]
        all_embeddings.extend(batch_embeddings)

    return all_embeddings
