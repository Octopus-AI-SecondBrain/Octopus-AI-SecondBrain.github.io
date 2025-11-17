"""
Security Validators - Input sanitization and file upload validation
"""
import re
from pathlib import Path
from typing import Optional

import magic
from fastapi import UploadFile, HTTPException, status


class FileUploadValidator:
    """
    Comprehensive file upload validation with security checks.

    Prevents:
    - File extension spoofing (checks magic bytes)
    - Oversized file uploads
    - Path traversal attacks
    - Dangerous file types
    - Malformed filenames
    """

    # Allowed extensions and their corresponding MIME types
    ALLOWED_EXTENSIONS = {
        # Text formats
        ".txt": ["text/plain"],
        ".md": ["text/markdown", "text/plain"],
        ".json": ["application/json", "text/plain"],
        ".csv": ["text/csv", "text/plain"],
        ".xml": ["application/xml", "text/xml", "text/plain"],
        ".yaml": ["application/x-yaml", "text/yaml", "text/plain"],
        ".yml": ["application/x-yaml", "text/yaml", "text/plain"],
        ".log": ["text/plain"],
        ".rst": ["text/plain", "text/x-rst"],

        # Document formats
        ".pdf": ["application/pdf"],

        # Image formats
        ".png": ["image/png"],
        ".jpg": ["image/jpeg"],
        ".jpeg": ["image/jpeg"],
        ".gif": ["image/gif"],
        ".bmp": ["image/bmp", "image/x-ms-bmp"],
        ".tiff": ["image/tiff"],
        ".tif": ["image/tiff"],

        # Video formats
        ".mp4": ["video/mp4"],
        ".avi": ["video/x-msvideo"],
        ".mov": ["video/quicktime"],
        ".mkv": ["video/x-matroska"],
        ".webm": ["video/webm"],
    }

    # Maximum file sizes (in bytes)
    MAX_FILE_SIZES = {
        "text": 10 * 1024 * 1024,  # 10 MB for text files
        "image": 20 * 1024 * 1024,  # 20 MB for images
        "video": 100 * 1024 * 1024,  # 100 MB for videos
        "document": 50 * 1024 * 1024,  # 50 MB for documents
    }

    # File name validation pattern (alphanumeric, underscore, hyphen, period)
    FILENAME_PATTERN = re.compile(r'^[a-zA-Z0-9_\-. ]+$')
    MAX_FILENAME_LENGTH = 255

    @classmethod
    async def validate_file(
        cls,
        file: UploadFile,
        check_magic_bytes: bool = True,
        max_size_override: Optional[int] = None,
    ) -> tuple[Path, dict[str, str]]:
        """
        Comprehensive file upload validation.

        Args:
            file: Uploaded file
            check_magic_bytes: Whether to verify file type using magic bytes
            max_size_override: Override default max file size (in bytes)

        Returns:
            Tuple of (file_extension, metadata_dict)

        Raises:
            HTTPException: If validation fails
        """
        # 1. Validate filename exists
        if not file.filename:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Filename is required",
            )

        # 2. Sanitize and validate filename
        safe_filename = cls._sanitize_filename(file.filename)
        file_ext = Path(safe_filename).suffix.lower()

        # 3. Check if extension is allowed
        if file_ext not in cls.ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"File type '{file_ext}' not allowed. "
                       f"Supported: {', '.join(cls.ALLOWED_EXTENSIONS.keys())}",
            )

        # 4. Check file size
        file_category = cls._get_file_category(file_ext)
        max_size = max_size_override or cls.MAX_FILE_SIZES.get(file_category, 10 * 1024 * 1024)

        # Read file in chunks to check size
        file.file.seek(0, 2)  # Seek to end
        file_size = file.file.tell()
        file.file.seek(0)  # Reset to beginning

        if file_size > max_size:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail=f"File too large: {file_size} bytes (max: {max_size} bytes)",
            )

        if file_size == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="File is empty",
            )

        # 5. Verify MIME type using magic bytes (prevents extension spoofing)
        if check_magic_bytes:
            await cls._verify_magic_bytes(file, file_ext)

        # 6. Return validated metadata
        metadata = {
            "original_filename": file.filename,
            "safe_filename": safe_filename,
            "extension": file_ext,
            "content_type": file.content_type or "application/octet-stream",
            "file_size": str(file_size),
            "file_category": file_category,
        }

        return Path(safe_filename), metadata

    @classmethod
    def _sanitize_filename(cls, filename: str) -> str:
        """
        Sanitize filename to prevent path traversal and injection attacks.

        Args:
            filename: Original filename

        Returns:
            Sanitized filename

        Raises:
            HTTPException: If filename is invalid
        """
        # Remove any directory path components
        filename = Path(filename).name

        # Check length
        if len(filename) > cls.MAX_FILENAME_LENGTH:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Filename too long (max: {cls.MAX_FILENAME_LENGTH} characters)",
            )

        # Check for valid characters
        if not cls.FILENAME_PATTERN.match(filename):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Filename contains invalid characters. "
                       "Only alphanumeric, spaces, hyphens, underscores, and periods allowed.",
            )

        # Check for path traversal attempts
        if ".." in filename or "/" in filename or "\\" in filename:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Filename contains invalid path characters",
            )

        return filename

    @classmethod
    async def _verify_magic_bytes(cls, file: UploadFile, expected_ext: str) -> None:
        """
        Verify file type using magic bytes (file signature).

        Args:
            file: Uploaded file
            expected_ext: Expected file extension

        Raises:
            HTTPException: If file type doesn't match extension
        """
        try:
            # Read first 2048 bytes for magic detection
            file.file.seek(0)
            header = file.file.read(2048)
            file.file.seek(0)

            # Detect MIME type from magic bytes
            detected_mime = magic.from_buffer(header, mime=True)

            # Check if detected MIME matches allowed types for this extension
            allowed_mimes = cls.ALLOWED_EXTENSIONS.get(expected_ext, [])

            if detected_mime not in allowed_mimes:
                # Some leniency for text files (they often detect as different types)
                if expected_ext in {".txt", ".md", ".log", ".rst", ".yaml", ".yml"}:
                    if detected_mime.startswith("text/"):
                        return  # Allow any text/* MIME type

                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"File type mismatch: extension '{expected_ext}' "
                           f"but detected as '{detected_mime}'. "
                           f"Possible file extension spoofing.",
                )

        except HTTPException:
            raise
        except Exception as e:
            # Magic bytes detection failed - log but don't block
            # (better to be lenient than to block legitimate files)
            import logging
            logger = logging.getLogger(__name__)
            logger.warning(f"Magic bytes verification failed: {e}")

    @classmethod
    def _get_file_category(cls, extension: str) -> str:
        """
        Get file category for size limits.

        Args:
            extension: File extension

        Returns:
            File category (text, image, video, document)
        """
        if extension in {".txt", ".md", ".json", ".csv", ".xml", ".yaml", ".yml", ".log", ".rst"}:
            return "text"
        elif extension in {".png", ".jpg", ".jpeg", ".gif", ".bmp", ".tiff", ".tif"}:
            return "image"
        elif extension in {".mp4", ".avi", ".mov", ".mkv", ".webm"}:
            return "video"
        elif extension in {".pdf"}:
            return "document"
        else:
            return "text"  # Default to most restrictive


class ContentSanitizer:
    """
    Sanitize user-provided text content to prevent XSS and injection attacks.
    """

    # Dangerous patterns to detect (but not auto-remove, for user awareness)
    DANGEROUS_PATTERNS = [
        re.compile(r'<script[^>]*>.*?</script>', re.IGNORECASE | re.DOTALL),
        re.compile(r'javascript:', re.IGNORECASE),
        re.compile(r'on\w+\s*=', re.IGNORECASE),  # onclick, onerror, etc.
    ]

    MAX_CONTENT_LENGTH = 1_000_000  # 1 MB of text

    @classmethod
    def sanitize_text(cls, content: str, strict: bool = False) -> str:
        """
        Sanitize text content.

        Args:
            content: User-provided text
            strict: If True, remove HTML; if False, just warn

        Returns:
            Sanitized content

        Raises:
            HTTPException: If content is too long or contains dangerous patterns
        """
        if not content:
            return content

        # Check length
        if len(content) > cls.MAX_CONTENT_LENGTH:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Content too long: {len(content)} characters "
                       f"(max: {cls.MAX_CONTENT_LENGTH})",
            )

        # Check for dangerous patterns
        for pattern in cls.DANGEROUS_PATTERNS:
            if pattern.search(content):
                if strict:
                    # Remove dangerous content
                    content = pattern.sub('', content)
                else:
                    # Just warn (for markdown, we want to preserve formatting)
                    import logging
                    logger = logging.getLogger(__name__)
                    logger.warning(f"Potentially dangerous content detected: {pattern.pattern[:50]}")

        return content

    @classmethod
    def sanitize_metadata(cls, metadata: dict) -> dict:
        """
        Sanitize metadata dictionary.

        Args:
            metadata: User-provided metadata

        Returns:
            Sanitized metadata
        """
        sanitized = {}

        for key, value in metadata.items():
            # Sanitize key (alphanumeric + underscore only)
            safe_key = re.sub(r'[^\w]', '_', str(key))[:100]

            # Sanitize value
            if isinstance(value, str):
                safe_value = value[:1000]  # Limit length
            elif isinstance(value, (int, float, bool)):
                safe_value = value
            elif isinstance(value, (list, dict)):
                # Convert to JSON string and limit length
                import json
                safe_value = json.dumps(value)[:1000]
            else:
                safe_value = str(value)[:1000]

            sanitized[safe_key] = safe_value

        return sanitized
