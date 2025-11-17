"""
Octopus AI Second Brain - Image Loader with OCR
Extracts text from images using Tesseract OCR.
"""
from pathlib import Path
from typing import Any

from PIL import Image
import pytesseract

from ..interfaces import Loader, Document


class ImageLoader(Loader):
    """
    Extract text from images using OCR (Optical Character Recognition).

    Supports: PNG, JPG, JPEG, GIF, BMP, TIFF
    """

    SUPPORTED_EXTENSIONS = {".png", ".jpg", ".jpeg", ".gif", ".bmp", ".tiff", ".tif"}

    def __init__(self, lang: str = "eng", config: str = ""):
        """
        Initialize the image loader.

        Args:
            lang: Tesseract language code (default: "eng")
            config: Additional Tesseract configuration string
        """
        self.lang = lang
        self.config = config

    async def load_async(self, source: str | Path) -> list[Document]:
        """
        Load and extract text from an image file using OCR.

        Args:
            source: Path to the image file

        Returns:
            List containing a single Document with extracted text

        Raises:
            ValueError: If file format is unsupported
            IOError: If file cannot be read or OCR fails
        """
        path = Path(source)

        if not path.exists():
            raise IOError(f"Image file not found: {path}")

        if not self.supports(path):
            raise ValueError(
                f"Unsupported image format: {path.suffix}. "
                f"Supported: {', '.join(self.SUPPORTED_EXTENSIONS)}"
            )

        try:
            # Open and load image
            image = Image.open(path)

            # Extract image metadata
            image_metadata = self._extract_image_metadata(image, path)

            # Perform OCR
            text = pytesseract.image_to_string(
                image,
                lang=self.lang,
                config=self.config
            )

            # Clean up extracted text
            text = text.strip()

            if not text:
                text = "[No text detected in image]"

            return [Document(
                content=text,
                metadata={
                    **image_metadata,
                    "source": str(path),
                    "modality": "image",
                    "extraction_method": "tesseract_ocr",
                    "character_count": len(text),
                }
            )]

        except pytesseract.TesseractError as e:
            raise IOError(f"OCR failed for {path}: {e}")
        except Exception as e:
            raise IOError(f"Failed to load image {path}: {e}")

    def supports(self, source: str | Path) -> bool:
        """
        Check if this loader supports the given image file.

        Args:
            source: File path to check

        Returns:
            True if file extension is supported
        """
        return Path(source).suffix.lower() in self.SUPPORTED_EXTENSIONS

    def _extract_image_metadata(self, image: Image.Image, path: Path) -> dict[str, Any]:
        """
        Extract metadata from the image.

        Args:
            image: PIL Image object
            path: Path to the image file

        Returns:
            Dictionary of image metadata
        """
        metadata: dict[str, Any] = {
            "filename": path.name,
            "format": image.format or "unknown",
            "mode": image.mode,
            "width": image.width,
            "height": image.height,
            "dimensions": f"{image.width}x{image.height}",
            "file_size_bytes": path.stat().st_size if path.exists() else 0,
        }

        # Extract EXIF data if available
        try:
            exif = image.getexif()
            if exif:
                # Add selected EXIF tags
                exif_data = {}
                for tag_id, value in exif.items():
                    tag_name = Image.ExifTags.TAGS.get(tag_id, tag_id)
                    if isinstance(tag_name, str):
                        exif_data[tag_name] = str(value)[:200]  # Limit length

                if exif_data:
                    metadata["exif"] = exif_data
        except Exception:
            # EXIF extraction is best-effort
            pass

        return metadata
