from typing import Generator, Optional
from fastapi import Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.database import User
from app.core.security import verify_token

# HTTP Bearer for token extraction
security = HTTPBearer()

def get_current_user(
    request: Request,
    db: Session = Depends(get_db)
) -> User:
    """
    Get current authenticated user from Authorization header OR HTTP-only cookie
    """
    # Try Authorization header first (for development)
    auth_header = request.headers.get("Authorization")
    access_token = None
    
    if auth_header and auth_header.startswith("Bearer "):
        access_token = auth_header.split(" ")[1]
        print(f"DEBUG: Token from Authorization header")
    else:
        # Fall back to cookie (for production)
        access_token = request.cookies.get("access_token")
        print(f"DEBUG: Token from cookie: {access_token[:20] if access_token else 'None'}...")
    
    if not access_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated - no access_token found",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Verify token
    payload = verify_token(access_token, token_type="access")
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user_id: str = payload.get("sub")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Get user from database
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user",
        )
    
    return user

def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    """
    Get current active user
    """
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user
