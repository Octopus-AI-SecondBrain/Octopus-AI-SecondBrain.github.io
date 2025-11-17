"""
Octopus AI Second Brain - Document Loaders
"""
from .text_loader import TextLoader
from .pdf_loader import PDFLoader
from .image_loader import ImageLoader
from .video_loader import VideoLoader

__all__ = [
    "TextLoader",
    "PDFLoader",
    "ImageLoader",
    "VideoLoader",
]
