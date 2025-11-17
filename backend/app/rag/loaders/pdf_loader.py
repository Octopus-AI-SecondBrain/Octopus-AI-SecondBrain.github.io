"""
Octopus AI Second Brain - PDF Loader
Loads and extracts text from PDF files.
"""
from pathlib import Path
from typing import Union

from ..interfaces import Loader, Document
from ...core.logging import get_logger
from ...core.utils import chunk_text
from ...core.settings import get_settings

logger = get_logger(__name__)
settings = get_settings()


class PDFLoader(Loader):
    """
    Loader for PDF files.
    
    Extracts text from PDF documents and creates chunks.
    """
    
    def __init__(
        self,
        chunk_size: int | None = None,
        chunk_overlap: int | None = None,
    ) -> None:
        """
        Initialize PDF loader.
        
        Args:
            chunk_size: Size of text chunks (default from settings)
            chunk_overlap: Overlap between chunks (default from settings)
        """
        self.chunk_size = chunk_size or settings.rag_ingestion.chunk_size
        self.chunk_overlap = chunk_overlap or settings.rag_ingestion.chunk_overlap
    
    async def load_async(self, source: Union[str, Path]) -> list[Document]:
        """
        Load text from a PDF file and chunk it.
        
        Args:
            source: Path to PDF file
            
        Returns:
            List of Document objects (one per chunk)
            
        Raises:
            ValueError: If file is not a PDF
            IOError: If file cannot be read
        """
        from PyPDF2 import PdfReader  # type: ignore[import-untyped]
        
        source_path = Path(source)
        
        if not self.supports(source_path):
            raise ValueError(f"Not a PDF file: {source_path}")
        
        # Read PDF
        try:
            reader = PdfReader(str(source_path))
            num_pages = len(reader.pages)
            
            # Extract text from all pages
            full_text = []
            for page_num, page in enumerate(reader.pages):
                text = page.extract_text()
                if text.strip():
                    full_text.append(text)
            
            content = "\n\n".join(full_text)
            
        except Exception as e:
            logger.error(f"Failed to read PDF {source_path}: {e}")
            raise IOError(f"Failed to read PDF: {e}")
        
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
                    "extension": ".pdf",
                    "modality": "pdf",
                    "num_pages": num_pages,
                    "chunk_index": idx,
                    "total_chunks": len(chunks),
                },
            )
            documents.append(doc)
        
        logger.info(
            f"Loaded {len(documents)} chunks from {source_path.name} "
            f"({num_pages} pages, chunk_size={self.chunk_size})"
        )
        
        return documents
    
    def supports(self, source: Union[str, Path]) -> bool:
        """
        Check if this loader supports the given file.
        
        Args:
            source: File path to check
            
        Returns:
            True if file is a PDF
        """
        source_path = Path(source)
        return source_path.suffix.lower() == ".pdf"
