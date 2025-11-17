"""
Octopus AI Second Brain - Video Loader with Audio Transcription
Extracts audio from videos and transcribes using Whisper.
"""
import tempfile
from pathlib import Path
from typing import Any, Optional, TYPE_CHECKING

try:
    from moviepy.editor import VideoFileClip
    MOVIEPY_AVAILABLE = True
except ImportError:
    MOVIEPY_AVAILABLE = False

try:
    import whisper
    WHISPER_AVAILABLE = True
except ImportError:
    WHISPER_AVAILABLE = False
    whisper = None  # type: ignore

from ..interfaces import Loader, Document

if TYPE_CHECKING and whisper:
    from whisper import Whisper


class VideoLoader(Loader):
    """
    Extract audio from videos and transcribe using OpenAI Whisper.

    Supports: MP4, AVI, MOV, MKV, WMV, FLV

    Requirements:
        - openai-whisper: pip install openai-whisper
        - moviepy: pip install moviepy
    """

    SUPPORTED_EXTENSIONS = {".mp4", ".avi", ".mov", ".mkv", ".wmv", ".flv", ".webm"}

    def __init__(
        self,
        model_name: str = "base",
        device: Optional[str] = None,
        extract_audio: bool = True,
        include_timestamps: bool = False,
    ):
        """
        Initialize the video loader.

        Args:
            model_name: Whisper model size (tiny, base, small, medium, large)
            device: Device to run model on (cuda/cpu, auto-detected if None)
            extract_audio: Whether to extract and transcribe audio
            include_timestamps: Whether to include word-level timestamps
        """
        if not WHISPER_AVAILABLE:
            raise ImportError(
                "openai-whisper is required for video transcription. "
                "Install with: pip install openai-whisper"
            )

        if extract_audio and not MOVIEPY_AVAILABLE:
            raise ImportError(
                "moviepy is required for audio extraction. "
                "Install with: pip install moviepy"
            )

        self.model_name = model_name
        self.device = device
        self.extract_audio = extract_audio
        self.include_timestamps = include_timestamps
        self._model: Optional["Whisper"] = None

    @property
    def model(self) -> "Whisper":
        """Lazy load the Whisper model"""
        if self._model is None:
            self._model = whisper.load_model(self.model_name, device=self.device)
        return self._model

    async def load_async(self, source: str | Path) -> list[Document]:
        """
        Load video, extract audio, and transcribe.

        Args:
            source: Path to the video file

        Returns:
            List containing a single Document with transcription

        Raises:
            ValueError: If file format is unsupported
            IOError: If video cannot be processed
        """
        path = Path(source)

        if not path.exists():
            raise IOError(f"Video file not found: {path}")

        if not self.supports(path):
            raise ValueError(
                f"Unsupported video format: {path.suffix}. "
                f"Supported: {', '.join(self.SUPPORTED_EXTENSIONS)}"
            )

        try:
            # Extract video metadata
            video_metadata = self._extract_video_metadata(path)

            if self.extract_audio:
                # Extract audio to temporary file
                with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as audio_file:
                    audio_path = Path(audio_file.name)

                try:
                    # Extract audio from video
                    video = VideoFileClip(str(path))
                    video.audio.write_audiofile(
                        str(audio_path),
                        codec="pcm_s16le",
                        verbose=False,
                        logger=None,
                    )
                    video.close()

                    # Transcribe audio with Whisper
                    result = self.model.transcribe(
                        str(audio_path),
                        word_timestamps=self.include_timestamps,
                        verbose=False,
                    )

                    transcription = result["text"].strip()
                    language = result.get("language", "unknown")

                    # Build document metadata
                    metadata = {
                        **video_metadata,
                        "source": str(path),
                        "modality": "video",
                        "extraction_method": "whisper_transcription",
                        "whisper_model": self.model_name,
                        "detected_language": language,
                        "character_count": len(transcription),
                    }

                    # Add segment timestamps if available
                    if self.include_timestamps and "segments" in result:
                        segments = [
                            {
                                "start": seg["start"],
                                "end": seg["end"],
                                "text": seg["text"],
                            }
                            for seg in result["segments"]
                        ]
                        metadata["segments"] = segments[:100]  # Limit to first 100

                    if not transcription:
                        transcription = "[No speech detected in video]"

                    return [Document(
                        content=transcription,
                        metadata=metadata,
                    )]

                finally:
                    # Clean up temporary audio file
                    if audio_path.exists():
                        audio_path.unlink()

            else:
                # No audio extraction, just return metadata
                return [Document(
                    content=f"Video file: {path.name} (audio extraction disabled)",
                    metadata={
                        **video_metadata,
                        "source": str(path),
                        "modality": "video",
                    }
                )]

        except Exception as e:
            raise IOError(f"Failed to process video {path}: {e}")

    def supports(self, source: str | Path) -> bool:
        """
        Check if this loader supports the given video file.

        Args:
            source: File path to check

        Returns:
            True if file extension is supported
        """
        return Path(source).suffix.lower() in self.SUPPORTED_EXTENSIONS

    def _extract_video_metadata(self, path: Path) -> dict[str, Any]:
        """
        Extract metadata from the video file.

        Args:
            path: Path to the video file

        Returns:
            Dictionary of video metadata
        """
        metadata: dict[str, Any] = {
            "filename": path.name,
            "file_size_bytes": path.stat().st_size if path.exists() else 0,
        }

        if MOVIEPY_AVAILABLE:
            try:
                video = VideoFileClip(str(path))
                metadata.update({
                    "duration_seconds": video.duration,
                    "fps": video.fps,
                    "width": video.w,
                    "height": video.h,
                    "dimensions": f"{video.w}x{video.h}",
                    "has_audio": video.audio is not None,
                })
                video.close()
            except Exception:
                # Metadata extraction is best-effort
                pass

        return metadata
