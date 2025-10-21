"""
Professional configuration management for SecondBrain application.
Uses Pydantic for validation and environment variable management.
"""
import os
from pathlib import Path
from typing import List, Optional, Literal
from pydantic import BaseModel, Field, field_validator, model_validator
from functools import lru_cache


class DatabaseSettings(BaseModel):
    """Database configuration settings."""
    url: str = Field(
        default="sqlite:///./data/database/secondbrain.db",
        description="Database connection URL"
    )
    echo: bool = Field(
        default=False,
        description="Enable SQLAlchemy query logging"
    )
    pool_size: int = Field(
        default=10,
        ge=1,
        le=100,
        description="Database connection pool size"
    )
    max_overflow: int = Field(
        default=20,
        ge=0,
        le=100,
        description="Maximum number of connections to overflow the pool"
    )
    
    @field_validator('url', mode='before')
    @classmethod
    def check_env_overrides(cls, v):
        """Check for SECONDBRAIN_DB_URL or DATABASE_URL environment overrides."""
        # Check for legacy SECONDBRAIN_DB_URL first, then DATABASE_URL
        return os.getenv("SECONDBRAIN_DB_URL") or os.getenv("DATABASE_URL") or v


class SecuritySettings(BaseModel):
    """Security configuration settings."""
    secret_key: str = Field(
        default="dev-secret-change-me",
        min_length=32,
        description="Secret key for JWT token signing"
    )
    algorithm: str = Field(
        default="HS256",
        description="JWT signing algorithm"
    )
    access_token_expire_minutes: int = Field(
        default=30,
        ge=1,
        le=10080,  # Max 1 week
        description="JWT token expiration time in minutes"
    )
    password_min_length: int = Field(
        default=8,
        ge=8,
        le=128,
        description="Minimum password length"
    )
    max_login_attempts: int = Field(
        default=5,
        ge=1,
        le=100,
        description="Maximum failed login attempts before account lockout"
    )
    lockout_duration_minutes: int = Field(
        default=15,
        ge=1,
        le=1440,  # Max 24 hours
        description="Account lockout duration in minutes"
    )

    @field_validator('secret_key', mode='before')
    @classmethod
    def validate_secret_key(cls, v):
        """Validate secret key strength."""
        secret_key = os.getenv("SECRET_KEY", v)
        environment = os.getenv("ENVIRONMENT", "development")
        
        # Enforce SECRET_KEY requirement in non-development environments
        if environment != "development":
            if not secret_key or secret_key in ("dev-secret-change-me", "your-secret-key-here"):
                raise ValueError(
                    f"CRITICAL: SECRET_KEY is required when ENVIRONMENT={environment}. "
                    "Set a strong SECRET_KEY environment variable (32+ characters). "
                    "Generate one with: openssl rand -base64 48"
                )
            if len(secret_key) < 32:
                raise ValueError(
                    f"CRITICAL: SECRET_KEY must be at least 32 characters in {environment} environment. "
                    f"Current length: {len(secret_key)}. Generate a secure key with: openssl rand -base64 48"
                )
        
        return secret_key


class VectorStoreSettings(BaseModel):
    """Vector store configuration settings."""
    chroma_path: Path = Field(
        default=Path("./data/vector_db"),
        description="ChromaDB storage path"
    )
    embedding_model: str = Field(
        default="text-embedding-3-small",
        description="OpenAI embedding model name"
    )
    max_query_results: int = Field(
        default=10,
        ge=1,
        le=100,
        description="Maximum number of search results to return"
    )
    similarity_threshold: float = Field(
        default=0.7,
        ge=0.0,
        le=1.0,
        description="Minimum similarity score for search results"
    )
    
    @field_validator('chroma_path', mode='before')
    @classmethod
    def check_chroma_path_overrides(cls, v):
        """Check for SECONDBRAIN_CHROMA_PATH or CHROMA_PATH environment overrides."""
        path_str = os.getenv("SECONDBRAIN_CHROMA_PATH") or os.getenv("CHROMA_PATH")
        if path_str:
            return Path(path_str)
        return Path(v) if isinstance(v, str) else v


class ServerSettings(BaseModel):
    """Server configuration settings."""
    host: str = Field(
        default="127.0.0.1",
        description="Server host address"
    )
    port: int = Field(
        default=8000,
        ge=1024,
        le=65535,
        description="Server port number"
    )
    workers: int = Field(
        default=1,
        ge=1,
        le=16,
        description="Number of worker processes"
    )
    reload: bool = Field(
        default=False,
        description="Enable auto-reload in development"
    )
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = Field(
        default="INFO",
        description="Logging level"
    )


class CORSSettings(BaseModel):
    """CORS configuration settings."""
    allowed_origins: List[str] = Field(
        default=[
            "http://localhost:3000",
            "http://127.0.0.1:3000",
            "http://localhost:3001",
            "http://127.0.0.1:3001", 
            "http://localhost:8080",
            "http://127.0.0.1:8080",
            "http://localhost:5173",
            "http://127.0.0.1:5173",
            "http://localhost:4173",
            "http://127.0.0.1:4173"
        ],
        description="Allowed CORS origins - use host URLs only, no path segments"
    )
    allow_credentials: bool = Field(
        default=True,
        description="Allow credentials in CORS requests"
    )
    allowed_methods: List[str] = Field(
        default=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        description="Allowed HTTP methods"
    )
    allowed_headers: List[str] = Field(
        default=["*"],
        description="Allowed HTTP headers"
    )
    max_age: int = Field(
        default=600,
        ge=0,
        description="CORS preflight cache time in seconds"
    )
    
    @field_validator('allowed_origins', mode='before')
    @classmethod
    def parse_cors_origins(cls, v):
        """Parse CORS_ORIGINS environment variable and add production origins."""
        env_origins = os.getenv("CORS_ORIGINS")
        if env_origins:
            # Split by comma and clean up
            origins = [origin.strip() for origin in env_origins.split(",") if origin.strip()]
            return origins
        
        # Start with default origins
        origins = v if isinstance(v, list) else [v]
        
        # Add production origins from environment variables
        environment = os.getenv("ENVIRONMENT", "development")
        if environment in ("staging", "production"):
            # Add Render backend URL (for self-references)
            render_url = os.getenv("RENDER_EXTERNAL_URL")
            if render_url and render_url not in origins:
                origins.append(render_url)
            
            # Add GitHub Pages frontend URL
            github_pages_url = os.getenv("GITHUB_PAGES_URL")
            if github_pages_url and github_pages_url not in origins:
                origins.append(github_pages_url)
            elif "octopus-ai-secondbrain.github.io" not in str(origins):
                # Default GitHub Pages URL if not provided
                origins.append("https://octopus-ai-secondbrain.github.io")
        
        return origins


class RateLimitSettings(BaseModel):
    """Rate limiting configuration settings."""
    enabled: bool = Field(
        default=True,
        description="Enable rate limiting"
    )
    default_limit: str = Field(
        default="100/minute",
        description="Default rate limit"
    )
    auth_limit: str = Field(
        default="10/minute",
        description="Rate limit for authentication endpoints"
    )
    signup_limit: str = Field(
        default="5/minute",
        description="Rate limit for signup endpoint"
    )


class OpenAISettings(BaseModel):
    """OpenAI API configuration settings."""
    api_key: Optional[str] = Field(
        default=None,
        description="OpenAI API key"
    )
    organization: Optional[str] = Field(
        default=None,
        description="OpenAI organization ID"
    )
    timeout: int = Field(
        default=30,
        ge=1,
        le=300,
        description="API request timeout in seconds"
    )
    max_retries: int = Field(
        default=3,
        ge=0,
        le=10,
        description="Maximum number of API request retries"
    )


class Settings(BaseModel):
    """Main application settings."""
    
    # Environment
    environment: Literal["development", "staging", "production"] = Field(
        default="development",
        description="Application environment"
    )
    debug: bool = Field(
        default=True,
        description="Enable debug mode"
    )
    enable_https: bool = Field(
        default=False,
        description="Enable HTTPS-specific features (e.g., HSTS headers)"
    )
    
    # Application info
    app_name: str = Field(
        default="SecondBrain API",
        description="Application name"
    )
    app_version: str = Field(
        default="0.1.0",
        description="Application version"
    )
    
    # Nested settings - will be loaded from environment
    database: DatabaseSettings = DatabaseSettings()
    security: SecuritySettings = SecuritySettings()
    vector_store: VectorStoreSettings = VectorStoreSettings()
    server: ServerSettings = ServerSettings()
    cors: CORSSettings = CORSSettings()
    rate_limit: RateLimitSettings = RateLimitSettings()
    openai: OpenAISettings = OpenAISettings()
    
    # Logging
    log_file: Optional[Path] = Field(
        default=None,
        description="Log file path"
    )
    enable_json_logging: bool = Field(
        default=False,
        description="Enable JSON structured logging"
    )
    
    class Config:
        """Pydantic configuration."""
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
        extra = "ignore"
    
    @field_validator('database', mode='before')
    @classmethod
    def validate_database_settings(cls, v):
        """Validate database settings."""
        if isinstance(v, dict):
            return DatabaseSettings(**v)
        return v
    
    @field_validator('security', mode='before')
    @classmethod
    def validate_security_settings(cls, v):
        """Validate security settings."""
        if isinstance(v, dict):
            return SecuritySettings(**v)
        return v
    
    def get_database_url(self) -> str:
        """Get the complete database URL."""
        if self.database.url.startswith("sqlite:///"):
            # Ensure the directory exists for SQLite
            db_path = Path(self.database.url.replace("sqlite:///", ""))
            db_path.parent.mkdir(parents=True, exist_ok=True)
        return self.database.url
    
    def is_production(self) -> bool:
        """Check if running in production environment."""
        return self.environment == "production"
    
    def is_development(self) -> bool:
        """Check if running in development environment."""
        return self.environment == "development"


# Load settings from environment
def _load_settings() -> Settings:
    """Load settings from environment variables."""
    from dotenv import load_dotenv
    load_dotenv()
    
    # Helper to cast environment
    env_val = os.getenv("ENVIRONMENT", "development")
    environment: Literal["development", "staging", "production"] = "development"
    if env_val in ("development", "staging", "production"):
        environment = env_val  # type: ignore
    
    log_level_val = os.getenv("LOG_LEVEL", "INFO")
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = "INFO"
    if log_level_val in ("DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"):
        log_level = log_level_val  # type: ignore
    
    log_file_str = os.getenv("LOG_FILE")
    log_file_path = Path(log_file_str) if log_file_str else None
    
    # Load environment-specific values
    # Note: Field validators will handle SECONDBRAIN_* overrides
    return Settings(
        environment=environment,
        debug=os.getenv("DEBUG", "true").lower() == "true",
        enable_https=os.getenv("ENABLE_HTTPS", "false").lower() == "true",
        database=DatabaseSettings(
            url=os.getenv("DATABASE_URL", "sqlite:///./data/database/secondbrain.db"),
            echo=os.getenv("DATABASE_ECHO", "false").lower() == "true",
        ),
        security=SecuritySettings(
            secret_key=os.getenv("SECRET_KEY", "dev-secret-change-me"),
            algorithm=os.getenv("ALGORITHM", "HS256"),
            access_token_expire_minutes=int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30")),
        ),
        vector_store=VectorStoreSettings(
            chroma_path=Path(os.getenv("CHROMA_PATH", "./data/vector_db")),
        ),
        server=ServerSettings(
            host=os.getenv("HOST", "127.0.0.1"),
            port=int(os.getenv("PORT", "8000")),
            log_level=log_level,
        ),
        cors=CORSSettings(
            allowed_origins=os.getenv("CORS_ORIGINS", "").split(",") if os.getenv("CORS_ORIGINS") else [
                "http://localhost:3000",
                "http://127.0.0.1:3000",
                "http://localhost:3001",
                "http://127.0.0.1:3001",
                "http://localhost:8080", 
                "http://127.0.0.1:8080",
                "http://localhost:5173",
                "http://127.0.0.1:5173",
                "http://localhost:4173",
                "http://127.0.0.1:4173"
            ],
        ),
        openai=OpenAISettings(
            api_key=os.getenv("OPENAI_API_KEY"),
        ),
        log_file=log_file_path,
        enable_json_logging=os.getenv("ENABLE_JSON_LOGGING", "false").lower() == "true",
    )


# Global settings instance
settings = _load_settings()


@lru_cache()
def get_settings() -> Settings:
    """Get the global settings instance (cached)."""
    return settings