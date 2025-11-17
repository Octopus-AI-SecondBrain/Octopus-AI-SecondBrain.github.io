"""
Octopus AI Second Brain - Embedding Model
Stores vector embeddings using pgvector for semantic search.
"""
from datetime import datetime
from typing import Optional

from sqlalchemy import String, DateTime, Integer, ForeignKey, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from pgvector.sqlalchemy import Vector

from ..session import Base


class Embedding(Base):
    """Embedding model with pgvector support"""

    __tablename__ = "embeddings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    chunk_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("chunks.id", ondelete="CASCADE"), nullable=False, index=True
    )

    # Vector embedding (dimension set via configuration, default 384 for all-MiniLM-L6-v2)
    # Note: The dimension must match the embedding model output
    embedding_vector: Mapped[Optional[Vector]] = mapped_column(Vector(384), nullable=True)

    # Embedding metadata
    model_name: Mapped[str] = mapped_column(String(100), nullable=False)
    embedding_dimension: Mapped[int] = mapped_column(Integer, nullable=False)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    # Relationships
    chunk = relationship("Chunk", back_populates="embeddings")

    # Indexes for vector similarity search
    __table_args__ = (
        # Index for cosine similarity (most common for semantic search)
        Index(
            "ix_embeddings_vector_cosine",
            embedding_vector,
            postgresql_using="ivfflat",
            postgresql_with={"lists": 100},
            postgresql_ops={"embedding_vector": "vector_cosine_ops"},
        ),
        # Index for L2 distance
        Index(
            "ix_embeddings_vector_l2",
            embedding_vector,
            postgresql_using="ivfflat",
            postgresql_with={"lists": 100},
            postgresql_ops={"embedding_vector": "vector_l2_ops"},
        ),
    )

    def __repr__(self) -> str:
        return (
            f"<Embedding(id={self.id}, chunk_id={self.chunk_id}, "
            f"model={self.model_name}, dim={self.embedding_dimension})>"
        )
