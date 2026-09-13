from datetime import datetime
from typing import TYPE_CHECKING, Any
import uuid
from pgvector.sqlalchemy import Vector
from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB, TSVECTOR, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.config import settings
from app.database.base import Base

if TYPE_CHECKING:
    from app.database.message_citation import MessageCitation
    from app.database.source_document import SourceDocument


class DocumentChunk(Base):
    """Chunk of a source SEC filing optimized for vector and full-text search."""

    __tablename__ = "document_chunks"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    document_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("source_documents.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    chunk_index: Mapped[int] = mapped_column(Integer, nullable=False)
    chunk_text: Mapped[str] = mapped_column(Text, nullable=False)
    token_count: Mapped[int] = mapped_column(Integer, nullable=False)
    page_number: Mapped[int | None] = mapped_column(Integer, nullable=True)
    section: Mapped[str | None] = mapped_column(String(255), nullable=True)
    metadata_json: Mapped[dict[str, Any] | None] = mapped_column(
        JSONB, nullable=True
    )
    embedding: Mapped[list[float] | None] = mapped_column(
        Vector(settings.GEMINI_EMBEDDING_DIMENSIONS),
        nullable=True,
    )
    search_vector: Mapped[Any | None] = mapped_column(TSVECTOR, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    document: Mapped["SourceDocument"] = relationship(
        "SourceDocument", back_populates="chunks"
    )
    citations: Mapped[list["MessageCitation"]] = relationship(
        "MessageCitation", back_populates="chunk"
    )
