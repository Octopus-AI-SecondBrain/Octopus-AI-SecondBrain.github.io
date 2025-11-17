"""
Octopus AI Second Brain - Query Log Model
Tracks user queries for analytics and improvement.
"""
from datetime import datetime
from typing import Optional

from sqlalchemy import String, Text, DateTime, Integer, ForeignKey, Float, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from ..session import Base


class QueryLog(Base):
    """Query log model for tracking user searches and questions"""

    __tablename__ = "query_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )

    # Query info
    query_text: Mapped[str] = mapped_column(Text, nullable=False)
    query_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)  # search, answer, etc.
    
    # Results info
    num_results: Mapped[int] = mapped_column(Integer, nullable=False)
    response_time_ms: Mapped[float] = mapped_column(Float, nullable=False)
    
    # Generated answer (if applicable)
    generated_answer: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Feedback (optional)
    user_feedback: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)  # 1-5 rating
    feedback_comment: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Query metadata
    query_metadata: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)

    # Timestamp
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False, index=True
    )

    # Relationships
    user = relationship("User", back_populates="query_logs")

    def __repr__(self) -> str:
        return (
            f"<QueryLog(id={self.id}, user_id={self.user_id}, "
            f"type={self.query_type}, results={self.num_results})>"
        )
