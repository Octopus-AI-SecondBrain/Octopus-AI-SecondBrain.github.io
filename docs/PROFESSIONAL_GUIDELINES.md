# Professional Development Guidelines for SecondBrain

## Overview
This document outlines professional development practices, code standards, and best practices for contributing to the SecondBrain project.

## Code Standards

### Python Code Style
- Follow PEP 8 style guide
- Use type hints for all function parameters and return values
- Write comprehensive docstrings (Google style)
- Maximum line length: 100 characters
- Use f-strings for string formatting

### Import Organization
```python
# Standard library imports
import os
from pathlib import Path
from typing import Optional, List

# Third-party imports
from fastapi import APIRouter, Depends
from pydantic import BaseModel

# Local application imports
from backend.models import user
from backend.core.logging import get_logger
```

### Docstring Format
```python
def function_name(param1: str, param2: int) -> dict:
    """
    Brief description of function purpose.
    
    Detailed description if needed, explaining the function's
    behavior, algorithm, or important notes.
    
    Args:
        param1: Description of param1
        param2: Description of param2
        
    Returns:
        Description of return value
        
    Raises:
        ValueError: Description of when this is raised
        HTTPException: Description of when this is raised
        
    Example:
        >>> result = function_name("test", 42)
        >>> print(result)
        {'key': 'value'}
    """
    pass
```

## Error Handling Best Practices

### 1. Use Specific Exceptions
```python
# ❌ Bad
try:
    result = risky_operation()
except:
    pass

# ✅ Good
try:
    result = risky_operation()
except ValueError as exc:
    logger.error(f"Invalid value: {exc}", exc_info=True)
    raise HTTPException(status_code=400, detail=str(exc))
except DatabaseError as exc:
    logger.error(f"Database error: {exc}", exc_info=True)
    raise HTTPException(status_code=500, detail="Database error occurred")
```

### 2. Always Log Errors
```python
# ❌ Bad
try:
    result = process_data(data)
except Exception:
    return {"error": "Failed"}

# ✅ Good
try:
    result = process_data(data)
except Exception as exc:
    logger.error(
        f"Error processing data: {exc}",
        exc_info=True,
        extra={"data_id": data.get('id')}
    )
    raise HTTPException(
        status_code=500,
        detail="Error processing data"
    )
```

### 3. Provide Context
```python
# ❌ Bad
raise HTTPException(status_code=404, detail="Not found")

# ✅ Good
raise HTTPException(
    status_code=404,
    detail=f"Note with ID {note_id} not found for user {user.id}"
)
```

## Logging Best Practices

### Log Levels
- **DEBUG**: Detailed information for diagnosing problems
- **INFO**: General information about application flow
- **WARNING**: Warning messages for potentially harmful situations
- **ERROR**: Error messages for serious problems
- **CRITICAL**: Critical messages for very serious errors

### Logging Examples
```python
# Debug - detailed diagnostic information
logger.debug(f"Processing request with params: {params}")

# Info - general information
logger.info(
    "User logged in successfully",
    extra={"user_id": user.id, "username": user.username}
)

# Warning - potentially harmful situation
logger.warning(
    f"Rate limit approaching for user {user.id}",
    extra={"user_id": user.id, "current_count": count}
)

# Error - serious problem
logger.error(
    f"Database connection failed: {exc}",
    exc_info=True,
    extra={"database": "postgres", "host": db_host}
)

# Critical - very serious error
logger.critical(
    "Application startup failed - exiting",
    exc_info=True
)
```

## Database Best Practices

### 1. Always Use Context Managers or Dependencies
```python
# ❌ Bad
db = SessionLocal()
user = db.query(User).first()
db.close()

# ✅ Good
def get_user(db: Session = Depends(get_db)):
    return db.query(User).first()
```

### 2. Handle Transactions Properly
```python
# ❌ Bad
new_user = User(username="test")
db.add(new_user)
db.commit()

# ✅ Good
try:
    new_user = User(username="test")
    db.add(new_user)
    db.commit()
    logger.info(f"User created: {new_user.id}")
except IntegrityError as exc:
    db.rollback()
    logger.error(f"Failed to create user: {exc}")
    raise HTTPException(status_code=400, detail="Username already exists")
except Exception as exc:
    db.rollback()
    logger.error(f"Database error: {exc}", exc_info=True)
    raise HTTPException(status_code=500, detail="Database error")
```

### 3. Use Type Hints with SQLAlchemy
```python
from sqlalchemy.orm import Mapped, mapped_column

class User(Base):
    __tablename__ = "users"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    username: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    email: Mapped[Optional[str]] = mapped_column(String, nullable=True)
```

## API Endpoint Best Practices

### 1. Use Proper HTTP Status Codes
```python
# 200 - OK (successful GET, PUT)
# 201 - Created (successful POST creating a resource)
# 204 - No Content (successful DELETE)
# 400 - Bad Request (client error, invalid input)
# 401 - Unauthorized (authentication required)
# 403 - Forbidden (authenticated but not authorized)
# 404 - Not Found (resource doesn't exist)
# 409 - Conflict (resource conflict, e.g., duplicate)
# 422 - Unprocessable Entity (validation error)
# 500 - Internal Server Error (server error)

@router.post("/users", status_code=status.HTTP_201_CREATED)
def create_user(user: UserCreate):
    # Create and return user
    pass

@router.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(user_id: int):
    # Delete user
    pass
```

### 2. Use Request/Response Models
```python
# ❌ Bad
@router.post("/users")
def create_user(data: dict):
    return {"id": 1, "username": data["username"]}

# ✅ Good
class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr

class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    created_at: datetime
    
    class Config:
        from_attributes = True

@router.post("/users", response_model=UserResponse, status_code=201)
def create_user(user: UserCreate):
    # Implementation
    pass
```

### 3. Add Comprehensive Documentation
```python
@router.post(
    "/users",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new user",
    description="Register a new user account with username and email",
    responses={
        201: {"description": "User created successfully"},
        400: {"description": "Invalid input data"},
        409: {"description": "Username or email already exists"}
    }
)
def create_user(
    user: UserCreate,
    db: Session = Depends(get_db)
) -> User:
    """
    Create a new user account.
    
    This endpoint handles user registration, including:
    - Username uniqueness validation
    - Email format validation
    - Password hashing
    - Database insertion
    
    Args:
        user: User creation data
        db: Database session
        
    Returns:
        The newly created user
        
    Raises:
        HTTPException: If validation fails or username/email exists
    """
    pass
```

## Security Best Practices

### 1. Input Validation
```python
from pydantic import BaseModel, Field, field_validator

class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=8, max_length=128)
    
    @field_validator('username')
    @classmethod
    def validate_username(cls, v: str) -> str:
        if not v.replace('_', '').replace('-', '').isalnum():
            raise ValueError('Username can only contain letters, numbers, hyphens, and underscores')
        return v.strip().lower()
    
    @field_validator('password')
    @classmethod
    def validate_password(cls, v: str) -> str:
        if not any(c.isupper() for c in v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not any(c.islower() for c in v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not any(c.isdigit() for c in v):
            raise ValueError('Password must contain at least one digit')
        return v
```

### 2. Rate Limiting
```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

@router.post("/login")
@limiter.limit("5/minute")
def login(request: Request, credentials: LoginCredentials):
    # Implementation
    pass
```

### 3. Authentication
```python
from fastapi import Depends
from typing import Annotated

@router.get("/protected")
def protected_route(
    current_user: Annotated[User, Depends(get_current_user)]
):
    # Only accessible to authenticated users
    pass
```

## Testing Best Practices

### 1. Unit Tests
```python
import pytest
from backend.core.security import hash_password, verify_password

def test_password_hashing():
    """Test password hashing functionality."""
    password = "SecurePass123!"
    hashed = hash_password(password)
    
    # Verify hash is different from original
    assert hashed != password
    
    # Verify password can be validated
    assert verify_password(password, hashed) is True
    
    # Verify wrong password fails
    assert verify_password("WrongPass", hashed) is False
```

### 2. Integration Tests
```python
from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)

def test_user_registration():
    """Test user registration endpoint."""
    response = client.post(
        "/auth/signup",
        json={"username": "testuser", "password": "SecurePass123!"}
    )
    assert response.status_code == 201
    data = response.json()
    assert data["username"] == "testuser"
    assert "id" in data
```

### 3. Fixtures
```python
@pytest.fixture
def db_session():
    """Create a test database session."""
    connection = engine.connect()
    transaction = connection.begin()
    session = SessionLocal(bind=connection)
    
    yield session
    
    session.close()
    transaction.rollback()
    connection.close()
```

## Git Commit Best Practices

### Commit Message Format
```
<type>(<scope>): <subject>

<body>

<footer>
```

### Types
- **feat**: New feature
- **fix**: Bug fix
- **docs**: Documentation changes
- **style**: Code style changes (formatting, etc.)
- **refactor**: Code refactoring
- **test**: Adding or updating tests
- **chore**: Maintenance tasks

### Examples
```bash
feat(auth): add password complexity validation

- Add uppercase letter requirement
- Add lowercase letter requirement
- Add digit requirement
- Update tests

Closes #123
```

```bash
fix(database): resolve connection pool exhaustion

Previously, database connections were not being properly released,
causing pool exhaustion after extended use. This commit ensures
all connections are properly closed using context managers.

Fixes #456
```

## Code Review Checklist

Before submitting a PR, ensure:

- [ ] Code follows PEP 8 style guide
- [ ] All functions have type hints
- [ ] All functions have docstrings
- [ ] Proper error handling is implemented
- [ ] Logging is used appropriately
- [ ] Input validation is implemented
- [ ] Tests are added/updated
- [ ] Documentation is updated
- [ ] No hardcoded values (use configuration)
- [ ] No security vulnerabilities
- [ ] Database transactions are handled properly
- [ ] No unnecessary dependencies added
- [ ] Code is DRY (Don't Repeat Yourself)
- [ ] Performance considerations addressed

## Resources

- [PEP 8 Style Guide](https://www.python.org/dev/peps/pep-0008/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- [Pydantic Documentation](https://docs.pydantic.dev/)
- [Python Logging](https://docs.python.org/3/library/logging.html)

---

**Remember**: Professional code is not just about making it work—it's about making it maintainable, secure, and scalable.
