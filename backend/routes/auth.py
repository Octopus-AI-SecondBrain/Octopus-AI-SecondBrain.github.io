"""
Authentication routes for SecondBrain API.
Handles user registration, login, and token management.
JWTs are stored in secure, httpOnly cookies for enhanced security.
"""
from fastapi import APIRouter, Depends, HTTPException, status, Request, Response
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel, field_validator
from sqlalchemy.orm import Session
from sqlalchemy.exc import OperationalError
from jose import JWTError, jwt
from typing import Annotated, Optional

from backend.models import db, user
from backend.core.security import (
    hash_password,
    verify_password,
    create_access_token,
    decode_access_token,
)
from backend.core.logging import get_logger
from backend.config.config import get_settings

router = APIRouter()
logger = get_logger("secondbrain.auth")
settings = get_settings()


# --- DB dependency ---
def get_db():
    """Database session dependency."""
    db_session = db.SessionLocal()
    try:
        yield db_session
    finally:
        db_session.close()


# --- OAuth2 config ---
# Custom OAuth2 scheme that reads from cookies instead of Authorization header
class OAuth2PasswordBearerCookie(OAuth2PasswordBearer):
    """OAuth2 scheme that supports both cookies and Authorization header."""
    
    async def __call__(self, request: Request) -> Optional[str]:
        # First try to get token from cookie
        token = request.cookies.get("access_token")
        if token:
            return token
        
        # Fall back to Authorization header for backward compatibility during transition
        return await super().__call__(request)


oauth2_scheme = OAuth2PasswordBearerCookie(tokenUrl="/auth/token")


# --- Pydantic schemas ---
class UserCreate(BaseModel):
    """Schema for user creation/registration."""
    username: str
    email: str | None = None
    password: str
    
    @field_validator('username')
    @classmethod
    def validate_username(cls, v: str) -> str:
        """Validate username format and constraints."""
        if not v or len(v.strip()) < 3:
            raise ValueError('Username must be at least 3 characters long')
        if len(v) > 50:
            raise ValueError('Username must be less than 50 characters')
        if not v.replace('_', '').replace('-', '').replace('.', '').isalnum():
            raise ValueError('Username can only contain letters, numbers, hyphens, underscores, and periods')
        return v.strip()
    
    @field_validator('email')
    @classmethod
    def validate_email(cls, v: str | None) -> str | None:
        """Validate email format."""
        if v is None:
            return None
        v = v.strip()
        if not v:
            return None
        if len(v) < 3:
            raise ValueError('Email must be at least 3 characters long')
        if len(v) > 255:
            raise ValueError('Email must be less than 255 characters')
        # Basic email regex validation
        import re
        if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', v):
            raise ValueError('Invalid email format')
        return v.lower()
    
    @field_validator('password')
    @classmethod
    def validate_password(cls, v: str) -> str:
        """Validate password strength."""
        if not v or len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        if len(v) > 128:
            raise ValueError('Password must be less than 128 characters')
        # Check for basic complexity
        if not any(c.isupper() for c in v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not any(c.islower() for c in v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not any(c.isdigit() for c in v):
            raise ValueError('Password must contain at least one digit')
        return v


class TokenResponse(BaseModel):
    """Schema for token response."""
    access_token: str
    token_type: str = "bearer"


class UserResponse(BaseModel):
    """Schema for user information response."""
    id: int
    username: str
    email: str | None = None
    
    class Config:
        from_attributes = True


# --- Signup (JSON body) ---
@router.post("/signup", status_code=status.HTTP_201_CREATED, response_model=UserResponse)
def signup(
    request: Request, 
    payload: UserCreate, 
    db: Annotated[Session, Depends(get_db)]
) -> user.User:
    """
    Register a new user account.
    Rate limited to 5 requests per minute via SlowAPI middleware.
    
    Args:
        request: FastAPI request object
        payload: User registration data
        db: Database session
        
    Returns:
        The newly created user
        
    Raises:
        HTTPException: If username is already taken or validation fails
    """
    logger.info(f"Signup attempt for username: {payload.username}")
    
    try:
        # Check if username already exists
        existing = db.query(user.User).filter(
            user.User.username == payload.username
        ).first()
        
        if existing:
            logger.warning(f"Signup failed: Username '{payload.username}' already exists")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already taken"
            )
        
        # Check if email already exists (if email provided)
        if payload.email:
            existing_email = db.query(user.User).filter(
                user.User.email == payload.email
            ).first()
            
            if existing_email:
                logger.warning(f"Signup failed: Email '{payload.email}' already exists")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email already registered"
                )

        # Create new user
        new_user = user.User(
            username=payload.username,
            email=payload.email,
            hashed_password=hash_password(payload.password),
        )
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        
        logger.info(
            f"User created successfully: {new_user.username}",
            extra={"user_id": new_user.id}
        )
        return new_user
        
    except HTTPException:
        raise
    except OperationalError as exc:
        db.rollback()  # Ensure rollback on database errors
        # Specifically handle database operational errors (missing tables, etc.)
        error_message = str(exc).lower()
        if "no such table" in error_message or "table" in error_message:
            logger.error(f"Database schema missing - likely need to run migrations: {exc}")
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Service temporarily unavailable. Database initialization required."
            )
        else:
            logger.error(f"Database operational error during signup: {exc}", exc_info=True)
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Service temporarily unavailable. Please try again later."
            )
    except Exception as exc:
        logger.error(f"Error creating user: {exc}", exc_info=True)
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Service temporarily unavailable. Please try again later."
        )


# --- Token (login) using OAuth2 Password flow ---
@router.post("/token", response_model=TokenResponse)
def login_for_access_token(
    request: Request,
    response: Response,
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: Annotated[Session, Depends(get_db)],
) -> dict:
    """
    Authenticate user and return access token.
    Token is stored in a secure, httpOnly cookie for enhanced security.
    Rate limited to 10 requests per minute via SlowAPI middleware.
    
    Args:
        request: FastAPI request object
        response: FastAPI response object
        form_data: OAuth2 form data containing username and password
        db: Database session
        
    Returns:
        Dictionary containing access_token and token_type
        
    Raises:
        HTTPException: If authentication fails
    """
    logger.info(f"Login attempt for username: {form_data.username}")
    
    try:
        # Find user
        db_user = db.query(user.User).filter(
            user.User.username == form_data.username
        ).first()
        
        # Verify credentials
        if not db_user or not verify_password(
            form_data.password, 
            str(db_user.hashed_password)
        ):
            logger.warning(f"Login failed: Invalid credentials for '{form_data.username}'")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Create access token
        access_token = create_access_token({"sub": db_user.username})
        
        # Set secure, httpOnly cookie
        # Use SameSite=None for cross-origin when HTTPS enabled (GitHub Pages → Render)
        # Use SameSite=Lax for same-origin development
        is_cross_site = settings.enable_https and settings.is_production()
        response.set_cookie(
            key="access_token",
            value=access_token,
            httponly=True,  # Prevents JavaScript access
            secure=is_cross_site,  # Secure required for SameSite=None
            samesite="none" if is_cross_site else "lax",  # None for cross-site, Lax for dev
            max_age=settings.security.access_token_expire_minutes * 60,  # Convert to seconds
        )
        
        logger.info(
            f"Login successful for user: {db_user.username}",
            extra={"user_id": db_user.id}
        )
        
        # Still return token in response for backward compatibility
        return {"access_token": access_token, "token_type": "bearer"}
        
    except HTTPException:
        raise
    except OperationalError as exc:
        # Specifically handle database operational errors (missing tables, etc.)
        error_message = str(exc).lower()
        if "no such table" in error_message or "table" in error_message:
            logger.error(f"Database schema missing during login - likely need to run migrations: {exc}")
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Service temporarily unavailable. Database initialization required."
            )
        else:
            logger.error(f"Database operational error during login: {exc}", exc_info=True)
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Service temporarily unavailable. Please try again later."
            )
    except Exception as exc:
        logger.error(f"Error during login: {exc}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Service temporarily unavailable. Please try again later."
        )


# --- Current user helper (protected) ---
def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    db: Annotated[Session, Depends(get_db)],
) -> user.User:
    """
    Get the current authenticated user from JWT token.
    
    Args:
        token: JWT access token
        db: Database session
        
    Returns:
        The authenticated user
        
    Raises:
        HTTPException: If token is invalid or user not found
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        # Decode token
        payload = decode_access_token(token)
        username: str | None = payload.get("sub")
        
        if username is None:
            logger.warning("Token missing 'sub' claim")
            raise credentials_exception
            
    except JWTError as exc:
        logger.warning(f"JWT validation failed: {exc}")
        raise credentials_exception

    # Find user
    db_user = db.query(user.User).filter(
        user.User.username == username
    ).first()
    
    if db_user is None:
        logger.warning(f"User not found: {username}")
        raise credentials_exception
        
    return db_user


# --- Protected route example ---
@router.get("/me", response_model=UserResponse)
def read_me(
    current_user: Annotated[user.User, Depends(get_current_user)]
) -> user.User:
    """
    Get current user information.
    
    Args:
        current_user: The authenticated user
        
    Returns:
        User information
    """
    logger.debug(f"User info requested: {current_user.username}")
    return current_user


@router.post("/logout")
def logout(response: Response) -> dict:
    """
    Logout user by clearing the authentication cookie.
    
    Args:
        response: FastAPI response object
        
    Returns:
        Success message
    """
    # Match cookie settings used during login
    is_cross_site = settings.enable_https and settings.is_production()
    response.delete_cookie(
        key="access_token",
        httponly=True,
        secure=is_cross_site,
        samesite="none" if is_cross_site else "lax"
    )
    logger.info("User logged out successfully")
    return {"message": "Successfully logged out"}


class ProfileUpdate(BaseModel):
    """Schema for profile update."""
    email: str | None = None
    current_password: str | None = None
    new_password: str | None = None
    
    @field_validator('email')
    @classmethod
    def validate_email(cls, v: str | None) -> str | None:
        """Validate email format."""
        if v is None or not v.strip():
            return None
        v = v.strip()
        if len(v) < 3:
            raise ValueError('Email must be at least 3 characters long')
        if len(v) > 255:
            raise ValueError('Email must be less than 255 characters')
        # Basic email regex validation
        import re
        if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', v):
            raise ValueError('Invalid email format')
        return v.lower()
    
    @field_validator('new_password')
    @classmethod
    def validate_new_password(cls, v: str | None) -> str | None:
        """Validate password strength."""
        if v is None or not v:
            return None
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        if len(v) > 128:
            raise ValueError('Password must be less than 128 characters')
        # Check for basic complexity
        if not any(c.isupper() for c in v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not any(c.islower() for c in v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not any(c.isdigit() for c in v):
            raise ValueError('Password must contain at least one digit')
        return v


@router.put("/profile", response_model=UserResponse)
def update_profile(
    request: Request,
    payload: ProfileUpdate,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[user.User, Depends(get_current_user)]
) -> user.User:
    """
    Update user profile (email and/or password).
    Rate limited to 10 requests per minute.
    
    Args:
        request: FastAPI request object
        payload: Profile update data
        db: Database session
        current_user: The authenticated user
        
    Returns:
        Updated user information
        
    Raises:
        HTTPException: If validation fails or email already taken
    """
    logger.info(f"Profile update attempt for user: {current_user.username}")
    
    try:
        updated = False
        
        # Update email if provided
        if payload.email is not None and payload.email != current_user.email:
            # Check if email already exists
            existing_email = db.query(user.User).filter(
                user.User.email == payload.email,
                user.User.id != current_user.id
            ).first()
            
            if existing_email:
                logger.warning(f"Email update failed: '{payload.email}' already registered")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email already registered to another account"
                )
            
            current_user.email = payload.email
            updated = True
            logger.info(f"Email updated for user {current_user.username}")
        
        # Update password if both current and new passwords provided
        if payload.current_password and payload.new_password:
            # Verify current password
            if not verify_password(payload.current_password, str(current_user.hashed_password)):
                logger.warning(f"Password update failed: incorrect current password for user {current_user.username}")
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Current password is incorrect"
                )
            
            # Set new password
            current_user.hashed_password = hash_password(payload.new_password)
            updated = True
            logger.info(f"Password updated for user {current_user.username}")
        elif payload.current_password or payload.new_password:
            # One password field provided but not both
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Both current_password and new_password are required to change password"
            )
        
        if not updated:
            logger.info(f"No changes requested for user {current_user.username}")
            return current_user
        
        # Commit changes
        db.commit()
        db.refresh(current_user)
        
        logger.info(f"Profile updated successfully for user: {current_user.username}")
        return current_user
        
    except HTTPException:
        raise
    except OperationalError as exc:
        db.rollback()
        error_message = str(exc).lower()
        if "no such table" in error_message or "table" in error_message:
            logger.error(f"Database schema missing during profile update: {exc}")
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Service temporarily unavailable. Database initialization required."
            )
        else:
            logger.error(f"Database operational error during profile update: {exc}", exc_info=True)
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Service temporarily unavailable. Please try again later."
            )
    except Exception as exc:
        logger.error(f"Error updating profile: {exc}", exc_info=True)
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Service temporarily unavailable. Please try again later."
        )
