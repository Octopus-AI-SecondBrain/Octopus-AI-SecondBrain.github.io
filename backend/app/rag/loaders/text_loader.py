"""
Octopus AI Second Brain - Text Loader
Loads plain text, markdown, and other text-based files.
"""
from pathlib import Path
from typing import Union

from ..interfaces import Loader, Document
from ...core.logging import get_logger
from ...core.utils import chunk_text
from ...core.settings import get_settings

logger = get_logger(__name__)
settings = get_settings()


class TextLoader(Loader):
    """
    Loader for plain text files.
    
    Supports: .txt, .md, .markdown, .json, .xml, .yaml, .yml, .log, .csv
    """
    
    SUPPORTED_EXTENSIONS = {
        ".txt", ".md", ".markdown", ".json", ".xml",
        ".yaml", ".yml", ".log", ".csv", ".rst"
    }
    
    def __init__(
        self,
        chunk_size: int | None = None,
        chunk_overlap: int | None = None,
    ) -> None:
        """
        Initialize text loader.
        
        Args:
            chunk_size: Size of text chunks (default from settings)
            chunk_overlap: Overlap between chunks (default from settings)
        """
        self.chunk_size = chunk_size or settings.rag_ingestion.chunk_size
        self.chunk_overlap = chunk_overlap or settings.rag_ingestion.chunk_overlap
    
    async def load_async(self, source: Union[str, Path]) -> list[Document]:
        """
        Load text from a file and optionally chunk it.
        
        Args:
            source: Path to text file
            
        Returns:
            List of Document objects (one per chunk)
            
        Raises:
            ValueError: If file extension not supported
            IOError: If file cannot be read
        """
        source_path = Path(source)
        
        if not self.supports(source_path):
            raise ValueError(
                f"Unsupported file extension: {source_path.suffix}. "
                f"Supported: {self.SUPPORTED_EXTENSIONS}"
            )
        
        # Read file content
        try:
            with open(source_path, "r", encoding="utf-8") as f:
                content = f.read()
        except UnicodeDecodeError:
            # Try with latin-1 encoding as fallback
            with open(source_path, "r", encoding="latin-1") as f:
                content = f.read()
        
        # Chunk the content
        chunks = chunk_text(content, self.chunk_size, self.chunk_overlap)
        
        # Create Document objects
        documents = []
        for idx, chunk in enumerate(chunks):
            doc = Document(
                content=chunk,
                metadata={
                    "source": str(source_path),
                    "filename": source_path.name,
                    "extension": source_path.suffix,
                    "modality": "text",
                    "chunk_index": idx,
                    "total_chunks": len(chunks),
                },
            )
            documents.append(doc)
        
        logger.info(
            f"Loaded {len(documents)} chunks from {source_path.name} "
            f"(chunk_size={self.chunk_size}, overlap={self.chunk_overlap})"
        )
        
        return documents
    
    def supports(self, source: Union[str, Path]) -> bool:
        """
        Check if this loader supports the given file.
        
        Args:
            source: File path to check
            
        Returns:
            True if extension is supported
        """
        source_path = Path(source)
        return source_path.suffix.lower() in self.SUPPORTED_EXTENSIONS
