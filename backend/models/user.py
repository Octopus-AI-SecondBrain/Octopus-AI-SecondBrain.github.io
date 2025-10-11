from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship, Mapped, mapped_column
from typing import List, TYPE_CHECKING

from .db import Base

if TYPE_CHECKING:
    from .note import Note

class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    username: Mapped[str] = mapped_column(String, unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String, nullable=False)
    notes: Mapped[List["Note"]] = relationship("Note", back_populates="owner")  # One-to-many relationship with Note