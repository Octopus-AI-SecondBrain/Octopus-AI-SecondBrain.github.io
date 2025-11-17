"""
Octopus AI Second Brain - Centralized Configuration
Uses Pydantic Settings for environment variable management with full type validation.
"""
import os
from pathlib import Path
from typing import Literal, Optional
from functools import lru_cache

from pydantic import Field, field_validator, SecretStr, ConfigDict, BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict


class DatabaseSettings(BaseSettings):
    """PostgreSQL + pgvector database configuration"""

    model_config = SettingsConfigDict(env_prefix="DATABASE_", case_sensitive=False)

    url: str = Field(
        default="postgresql://secondbrain:secondbrain@localhost:5432/secondbrain",
        description="PostgreSQL connection URL",
    )
    echo: bool = Field(default=False, description="Enable SQLAlchemy query logging")
    pool_size: int = Field(default=10, ge=1, le=100, description="Connection pool size")
    max_overflow: int = Field(
        default=20, ge=0, le=100, description="Max connections beyond pool_size"
    )

    @field_validator("url")
    @classmethod
    def validate_postgresql(cls, v: str) -> str:
        """Ensure PostgreSQL is being used"""
        if not v.startswith(("postgresql://", "postgresql+psycopg://")):
            raise ValueError(
                "Only PostgreSQL is supported. DATABASE_URL must start with 'postgresql://'"
            )
        return v


class SecuritySettings(BaseSettings):
    """Security and authentication configuration"""

    model_config = SettingsConfigDict(case_sensitive=False)

    secret_key: SecretStr = Field(
        default=SecretStr("dev-secret-change-me-min-32-chars"),
        description="JWT signing secret key (min 32 chars in production)",
    )
    algorithm: str = Field(default="HS256", description="JWT algorithm")
    access_token_expire_minutes: int = Field(
        default=30, ge=1, le=10080, description="Token expiration (max 1 week)"
    )
    password_min_length: int = Field(default=8, ge=8, le=128, description="Min password length")
    max_login_attempts: int = Field(default=5, ge=1, le=100, description="Max login attempts")
    lockout_duration_minutes: int = Field(
        default=15, ge=1, le=1440, description="Lockout duration (max 24h)"
    )

    @field_validator("secret_key", mode="before")
    @classmethod
    def validate_secret_key(cls, v: str | SecretStr) -> SecretStr:
        """Validate secret key strength in production"""
        environment = os.getenv("ENVIRONMENT", "development")
        secret_str = v.get_secret_value() if isinstance(v, SecretStr) else v

        if environment != "development":
            if secret_str in ("dev-secret-change-me-min-32-chars", "your-secret-key-here"):
                raise ValueError(
                    f"CRITICAL: SECRET_KEY must be set for {environment} environment. "
                    "Generate with: openssl rand -base64 48"
                )
            if len(secret_str) < 32:
                raise ValueError(
                    f"CRITICAL: SECRET_KEY must be >= 32 chars in {environment}. "
                    f"Current: {len(secret_str)}"
                )

        return SecretStr(secret_str) if not isinstance(v, SecretStr) else v


class RAGEmbedderSettings(BaseSettings):
    """RAG embedder configuration"""

    model_config = SettingsConfigDict(env_prefix="RAG_EMBEDDER_", case_sensitive=False)

    text_model: str = Field(
        default="sentence-transformers/all-MiniLM-L6-v2", description="Text embedding model"
    )
    clip_model: str = Field(
        default="openai/clip-vit-base-patch32", description="CLIP model for images"
    )
    device: Literal["cpu", "cuda"] = Field(default="cpu", description="Device for inference")
    batch_size: int = Field(default=32, ge=1, le=256, description="Embedding batch size")


class RAGVectorStoreSettings(BaseSettings):
    """RAG vector store configuration"""

    model_config = SettingsConfigDict(env_prefix="RAG_VECTORSTORE_", case_sensitive=False)

    backend: Literal["pgvector", "faiss"] = Field(
        default="pgvector", description="Vector store backend (default: pgvector)"
    )
    table_name: str = Field(default="embeddings", description="pgvector table name")
    dimension: int = Field(default=384, ge=128, le=2048, description="Embedding dimension")

    # FAISS options (optional, only used when backend=faiss)
    index_type: str = Field(default="Flat", description="FAISS index type")
    persist_dir: Path = Field(default=Path("./data/vector_index"), description="FAISS persist dir")
    metric: Literal["cosine", "l2", "ip"] = Field(
        default="cosine", description="Distance metric"
    )


class RAGRetrieverSettings(BaseSettings):
    """RAG retriever configuration"""

    model_config = SettingsConfigDict(env_prefix="RAG_RETRIEVER_", case_sensitive=False)

    top_k: int = Field(default=10, ge=1, le=100, description="Number of results to retrieve")
    min_similarity: float = Field(
        default=0.15, ge=0.0, le=1.0, description="Minimum similarity threshold"
    )
    max_distance: float = Field(
        default=1.0, ge=0.0, le=2.0, description="Maximum distance threshold"
    )

    # Hybrid search settings
    use_hybrid_search: bool = Field(
        default=True, description="Enable hybrid search (vector + keyword)"
    )
    hybrid_alpha: float = Field(
        default=0.5,
        ge=0.0,
        le=1.0,
        description="Hybrid search weight (0=keyword only, 0.5=balanced, 1=semantic only)",
    )
    hybrid_rrf_k: int = Field(
        default=60, ge=1, le=100, description="RRF constant for rank fusion"
    )

    # Caching settings
    use_caching: bool = Field(default=True, description="Enable embedding and search result caching")


class RAGGeneratorSettings(BaseModel):
    """RAG Generator settings"""

    model_config = ConfigDict(protected_namespaces=())  # Allow model_ prefix

    model_name: str = Field(
        default="gpt-3.5-turbo",
        description="OpenAI model name for answer generation",
    )
    temperature: float = Field(
        default=0.7,
        ge=0.0,
        le=2.0,
        description="Temperature for answer generation",
    )
    max_tokens: int = Field(
        default=2048,
        ge=1,
        le=4096,
        description="Maximum tokens for answer generation",
    )


class RAGIngestionSettings(BaseSettings):
    """RAG ingestion configuration"""

    model_config = SettingsConfigDict(env_prefix="RAG_INGEST_", case_sensitive=False)

    batch_size: int = Field(default=10, ge=1, le=100, description="Documents per batch")
    max_workers: int = Field(default=4, ge=1, le=16, description="Parallel workers")
    chunk_size: int = Field(default=512, ge=128, le=2048, description="Text chunk size")
    chunk_overlap: int = Field(default=50, ge=0, le=512, description="Chunk overlap")


class CORSSettings(BaseSettings):
    """CORS configuration"""

    model_config = SettingsConfigDict(env_prefix="CORS_", case_sensitive=False)

    origins: list[str] = Field(
        default=["http://localhost:3000", "http://localhost:5173"],
        description="Allowed CORS origins",
    )
    credentials: bool = Field(default=True, description="Allow credentials")
    methods: list[str] = Field(default=["*"], description="Allowed HTTP methods")
    headers: list[str] = Field(default=["*"], description="Allowed HTTP headers")

    @field_validator("origins", mode="before")
    @classmethod
    def parse_origins(cls, v: str | list[str]) -> list[str]:
        """Parse CORS origins from comma-separated string or list"""
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",") if origin.strip()]
        return v


class RateLimitSettings(BaseSettings):
    """Rate limiting configuration"""

    model_config = SettingsConfigDict(env_prefix="RATE_LIMIT_", case_sensitive=False)

    enabled: bool = Field(default=True, description="Enable rate limiting")
    default: str = Field(default="100/minute", description="Default rate limit")
    auth: str = Field(default="10/minute", description="Auth endpoints rate limit")
    signup: str = Field(default="5/minute", description="Signup endpoint rate limit")


class RedisSettings(BaseSettings):
    """Redis configuration for caching and job queue"""

    model_config = SettingsConfigDict(env_prefix="REDIS_", case_sensitive=False)

    enabled: bool = Field(default=True, description="Enable Redis (fallback to in-memory if False)")
    url: str = Field(
        default="redis://localhost:6379/0",
        description="Redis connection URL",
    )
    max_connections: int = Field(default=50, ge=1, le=500, description="Max connection pool size")
    socket_timeout: int = Field(default=5, ge=1, le=30, description="Socket timeout (seconds)")
    socket_connect_timeout: int = Field(
        default=5, ge=1, le=30, description="Socket connect timeout (seconds)"
    )

    # Cache settings
    cache_ttl_default: int = Field(default=3600, ge=60, description="Default cache TTL (seconds)")
    cache_ttl_embeddings: int = Field(default=86400, description="Embedding cache TTL (24h)")
    cache_ttl_search: int = Field(default=3600, description="Search results cache TTL (1h)")

    # Job queue settings
    job_ttl: int = Field(default=86400, ge=3600, description="Job record TTL (24h)")
    job_result_ttl: int = Field(default=3600, ge=300, description="Job result TTL (1h)")
    max_retries: int = Field(default=3, ge=0, le=10, description="Max job retry attempts")
    retry_delay: int = Field(default=60, ge=1, le=3600, description="Retry delay (seconds)")

    @field_validator("url")
    @classmethod
    def validate_redis_url(cls, v: str) -> str:
        """Ensure Redis URL format is valid"""
        if not v.startswith(("redis://", "rediss://")):
            raise ValueError(
                "REDIS_URL must start with 'redis://' or 'rediss://' for SSL"
            )
        return v


class Settings(BaseSettings):
    """Main application settings"""

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", case_sensitive=False, extra="ignore"
    )

    # Environment
    environment: Literal["development", "staging", "production"] = Field(default="development")
    debug: bool = Field(default=True, description="Debug mode")
    enable_https: bool = Field(default=False, description="Enable HTTPS-specific features")

    # App info
    app_name: str = Field(default="Octopus AI Second Brain", description="Application name")
    app_version: str = Field(default="2.0.0", description="Application version")

    # Nested configurations
    database: DatabaseSettings = Field(default_factory=DatabaseSettings)
    security: SecuritySettings = Field(default_factory=SecuritySettings)
    cors: CORSSettings = Field(default_factory=CORSSettings)
    rate_limit: RateLimitSettings = Field(default_factory=RateLimitSettings)
    redis: RedisSettings = Field(default_factory=RedisSettings)

    # RAG configurations
    rag_embedder: RAGEmbedderSettings = Field(default_factory=RAGEmbedderSettings)
    rag_vectorstore: RAGVectorStoreSettings = Field(default_factory=RAGVectorStoreSettings)
    rag_retriever: RAGRetrieverSettings = Field(default_factory=RAGRetrieverSettings)
    rag_generator: RAGGeneratorSettings = Field(default_factory=RAGGeneratorSettings)
    rag_ingestion: RAGIngestionSettings = Field(default_factory=RAGIngestionSettings)

    # API keys
    openai_api_key: Optional[SecretStr] = Field(default=None, description="OpenAI API key")
    huggingface_token: Optional[SecretStr] = Field(default=None, description="HuggingFace token")

    # Server
    host: str = Field(default="0.0.0.0", description="Server host")
    port: int = Field(default=8000, ge=1024, le=65535, description="Server port")
    workers: int = Field(default=4, ge=1, le=16, description="Number of workers")
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = Field(default="INFO")

    # Logging
    log_file: Optional[Path] = Field(default=None, description="Log file path")
    enable_json_logging: bool = Field(default=False, description="Enable JSON logging")

    # Upload configuration
    upload_dir: Path = Field(default=Path("./data/uploads"), description="Upload directory")
    max_upload_size: int = Field(default=52428800, description="Max upload size (bytes)")

    def is_production(self) -> bool:
        """Check if running in production"""
        return self.environment == "production"

    def is_development(self) -> bool:
        """Check if running in development"""
        return self.environment == "development"

    def get_database_url(self) -> str:
        """Get database URL"""
        return self.database.url

    def get_secret_key(self) -> str:
        """Get secret key as plain string"""
        return self.security.secret_key.get_secret_value()


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()
