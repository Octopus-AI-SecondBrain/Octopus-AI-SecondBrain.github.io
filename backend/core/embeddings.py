from __future__ import annotations

import hashlib
import math
import os
import re
from pathlib import Path
from typing import List, Tuple

from dotenv import load_dotenv

try:
    from openai import OpenAI  # type: ignore
except ImportError:  # pragma: no cover - optional dependency
    OpenAI = None  # type: ignore

EMBEDDING_DIM = 1536
OPENAI_MODEL_NAME = "text-embedding-3-small"
OPENAI_MODEL_ID = f"openai/{OPENAI_MODEL_NAME}"
FALLBACK_MODEL_ID = f"local/hashed-{EMBEDDING_DIM}-v1"
_TOKEN_PATTERN = re.compile(r"[\w']+")


class _EmbeddingProvider:
    """Encapsulates OpenAI setup while providing a deterministic fallback."""

    def __init__(self) -> None:
        self._env_loaded = False
        self._openai_client: OpenAI | None = None  # type: ignore[name-defined]
        self._openai_ready = False
        self._openai_known = False

    def _ensure_env_loaded(self) -> None:
        if self._env_loaded:
            return

        try:
            load_dotenv()
            self._env_loaded = True
            return
        except AssertionError:
            # Happens when running under certain sandboxes where frame inspection fails.
            pass

        project_root = Path(__file__).resolve().parents[2]
        dotenv_path = project_root / ".env"
        if dotenv_path.exists():
            try:
                load_dotenv(dotenv_path=dotenv_path, override=False)
            except Exception:
                pass
        self._env_loaded = True

    def _get_openai_client(self) -> OpenAI | None:  # type: ignore[name-defined]
        if OpenAI is None:
            return None
        if self._openai_known and not self._openai_ready:
            return None
        if self._openai_client is not None:
            return self._openai_client

        self._ensure_env_loaded()
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            self._openai_known = True
            self._openai_ready = False
            return None

        try:
            client = OpenAI(api_key=api_key)  # type: ignore[operator]
        except Exception:
            self._openai_known = True
            self._openai_ready = False
            return None

        self._openai_client = client
        self._openai_ready = True
        self._openai_known = True
        return client

    def _disable_openai(self) -> None:
        self._openai_client = None
        self._openai_ready = False
        self._openai_known = True


def _hashed_embedding(text: str) -> List[float]:
    tokens = _TOKEN_PATTERN.findall(text.lower())
    if not tokens:
        return [0.0] * EMBEDDING_DIM

    vector = [0.0] * EMBEDDING_DIM
    for token in tokens:
        digest = hashlib.sha1(token.encode("utf-8")).digest()
        index = int.from_bytes(digest[:4], "big") % EMBEDDING_DIM
        sign = 1.0 if digest[4] % 2 == 0 else -1.0
        vector[index] += sign

    norm = math.sqrt(sum(value * value for value in vector))
    if norm:
        vector = [value / norm for value in vector]

    return vector


def generate_embedding(text: str) -> Tuple[List[float], str]:
    """Return an embedding vector and the model identifier used to build it."""
    normalized_text = (text or "").strip()
    if not normalized_text:
        return [0.0] * EMBEDDING_DIM, FALLBACK_MODEL_ID

    client = _PROVIDER._get_openai_client()
    if client is not None:
        try:
            response = client.embeddings.create(
                model=OPENAI_MODEL_NAME,
                input=normalized_text,
            )
            embedding = list(response.data[0].embedding)
            if embedding:
                return embedding, OPENAI_MODEL_ID
        except Exception:
            _PROVIDER._disable_openai()

    return _hashed_embedding(normalized_text), FALLBACK_MODEL_ID


_PROVIDER = _EmbeddingProvider()


__all__ = [
    "generate_embedding",
    "OPENAI_MODEL_ID",
    "FALLBACK_MODEL_ID",
    "EMBEDDING_DIM",
]
