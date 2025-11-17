"""
Octopus AI Second Brain - Core Utilities
Common utility functions for the application.
"""
from datetime import datetime, timezone


def utcnow() -> datetime:
    """
    Get current UTC datetime with timezone info.

    Returns:
        Current UTC datetime
    """
    return datetime.now(timezone.utc)


def chunk_text(text: str, chunk_size: int, overlap: int = 0) -> list[str]:
    """
    Split text into overlapping chunks.

    Args:
        text: Input text
        chunk_size: Size of each chunk in characters
        overlap: Number of characters to overlap between chunks

    Returns:
        List of text chunks
    """
    if not text:
        return []

    chunks = []
    start = 0

    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end]
        chunks.append(chunk)

        if end >= len(text):
            break

        # Move start position, accounting for overlap
        start = end - overlap

    return chunks
