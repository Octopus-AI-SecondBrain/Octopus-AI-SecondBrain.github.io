"""
Security utilities for SecondBrain application.
Provides password hashing, JWT token management, and authentication helpers.
"""
from datetime import datetime, timedelta, timezone
from typing import Optional

from jose import jwt, JWTError
from passlib.context import CryptContext

from backend.config.config import get_settings
from backend.core.logging import get_logger

# Get settings
settings = get_settings()

# Logger
logger = get_logger("secondbrain.security")

# Validate security configuration
if settings.is_production():
    if settings.security.secret_key in ("dev-secret-change-me", "your-secret-key-here"):
        error_msg = (
            "CRITICAL: Default SECRET_KEY detected in production environment. "
            "Set a strong SECRET_KEY environment variable immediately."
        )
        logger.error(error_msg)
        raise RuntimeError(error_msg)
    if len(settings.security.secret_key) < 32:
        error_msg = (
            "CRITICAL: SECRET_KEY is too short for production (minimum 32 characters). "
            "Set a stronger SECRET_KEY environment variable."
        )
        logger.error(error_msg)
        raise RuntimeError(error_msg)
else:
    # Warn in development
    if settings.security.secret_key in ("dev-secret-change-me", "your-secret-key-here"):
        logger.warning(
            "Using default SECRET_KEY in development mode. "
            "This is acceptable for local dev but DO NOT use in production."
        )

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """
    Hash a password using bcrypt.
    
    Args:
        password: The plain text password to hash
        
    Returns:
        The hashed password
    """
    try:
        hashed = pwd_context.hash(password)
        logger.debug("Password hashed successfully")
        return hashed
    except Exception as exc:
        logger.error(f"Error hashing password: {exc}", exc_info=True)
        raise


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a password against its hash.
    
    Args:
        plain_password: The plain text password to verify
        hashed_password: The hashed password to compare against
        
    Returns:
        True if the password matches, False otherwise
    """
    try:
        result = pwd_context.verify(plain_password, hashed_password)
        logger.debug(f"Password verification: {'successful' if result else 'failed'}")
        return result
    except Exception as exc:
        logger.error(f"Error verifying password: {exc}", exc_info=True)
        return False


def create_access_token(data: dict, expires_minutes: Optional[int] = None) -> str:
    """
    Create a JWT access token.
    
    Args:
        data: The data to encode in the token (must include 'sub' for subject)
        expires_minutes: Optional expiration time in minutes. Defaults to settings value
        
    Returns:
        The encoded JWT token
        
    Raises:
        ValueError: If data doesn't contain required fields
        Exception: If token creation fails
    """
    if "sub" not in data:
        logger.error("Token data missing required 'sub' field")
        raise ValueError("Token data must contain 'sub' field")
    
    try:
        to_encode = data.copy()
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=expires_minutes or settings.security.access_token_expire_minutes
        )
        to_encode.update({"exp": expire})
        
        encoded_jwt = jwt.encode(
            to_encode, 
            settings.security.secret_key, 
            algorithm=settings.security.algorithm
        )
        logger.debug(
            f"Access token created for user: {data.get('sub')}",
            extra={"user": data.get("sub")}
        )
        return encoded_jwt
    except Exception as exc:
        logger.error(f"Error creating access token: {exc}", exc_info=True)
        raise


def decode_access_token(token: str) -> dict:
    """
    Decode and validate a JWT access token.
    
    Args:
        token: The JWT token to decode
        
    Returns:
        The decoded token payload
        
    Raises:
        JWTError: If the token is invalid or expired
    """
    try:
        payload = jwt.decode(
            token, 
            settings.security.secret_key, 
            algorithms=[settings.security.algorithm]
        )
        logger.debug("Access token decoded successfully")
        return payload
    except JWTError as exc:
        logger.warning(f"Invalid token: {exc}")
        raise


__all__ = [
    "hash_password",
    "verify_password",
    "create_access_token",
    "decode_access_token",
]