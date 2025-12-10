from fastapi import APIRouter, Depends, HTTPException, status, Response, Request
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr
from datetime import timedelta, datetime
from app.database import get_db
from app.models.database import User, OTP
from app.core.security import (
    get_password_hash,
    verify_password,
    create_access_token,
    create_refresh_token,
    verify_token
)
from app.api.dependencies import get_current_user
from app.services.email_service import send_otp_email, generate_otp

router = APIRouter(prefix="/api/auth", tags=["authentication"])

# Request/Response Models
class SignupRequest(BaseModel):
    email: EmailStr
    username: str
    password: str

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    id: str
    email: str
    username: str
    is_active: bool
    
    class Config:
        from_attributes = True

class MessageResponse(BaseModel):
    message: str

@router.post("/signup", response_model=MessageResponse, status_code=status.HTTP_201_CREATED)
async def signup(
    user_data: SignupRequest,
    db: Session = Depends(get_db)
):
    """Register a new user and send OTP for email verification"""
    # Check if email already exists
    existing_user = db.query(User).filter(User.email == user_data.email).first()
    if existing_user:
        if existing_user.is_verified:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        # User exists but not verified - resend OTP
        db.delete(existing_user)
        db.commit()
    
    # Check if username already exists
    existing_username = db.query(User).filter(User.username == user_data.username).first()
    if existing_username:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already taken"
        )
    
    # Create new user (inactive until verified)
    hashed_password = get_password_hash(user_data.password)
    new_user = User(
        email=user_data.email,
        username=user_data.username,
        hashed_password=hashed_password,
        is_active=False,
        is_verified=False
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    # Generate and save OTP
    otp_code = generate_otp()
    otp_expires = datetime.utcnow() + timedelta(minutes=10)
    
    new_otp = OTP(
        user_id=new_user.id,
        code=otp_code,
        expires_at=otp_expires
    )
    
    db.add(new_otp)
    db.commit()
    
    # Send OTP email
    await send_otp_email(new_user.email, otp_code, new_user.username)
    
    return {"message": "OTP sent to your email. Please verify to complete registration."}

class LoginResponse(BaseModel):
    message: str
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

class VerifyOTPRequest(BaseModel):
    email: EmailStr
    otp: str

@router.post("/verify-otp", response_model=LoginResponse)
async def verify_otp(
    response: Response,
    otp_data: VerifyOTPRequest,
    db: Session = Depends(get_db)
):
    """Verify OTP and activate user account"""
    # Find user
    user = db.query(User).filter(User.email == otp_data.email).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    if user.is_verified:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already verified"
        )
    
    # Find valid OTP
    otp = db.query(OTP).filter(
        OTP.user_id == user.id,
        OTP.code == otp_data.otp,
        OTP.is_used == False,
        OTP.expires_at > datetime.utcnow()
    ).first()
    
    if not otp:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired OTP"
        )
    
    # Mark OTP as used
    otp.is_used = True
    
    # Activate user
    user.is_active = True
    user.is_verified = True
    
    db.commit()
    
    # Auto-login after verification
    access_token = create_access_token(data={"sub": str(user.id)})
    refresh_token = create_refresh_token(data={"sub": str(user.id)})
    
    # Set cookies
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        secure=False,
        samesite="lax",
        path="/",
        max_age=60 * 15
    )
    
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=False,
        samesite="lax",
        path="/",
        max_age=60 * 60 * 24 * 7
    )
    
    return {
        "message": "Email verified successfully",
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }


@router.post("/login", response_model=LoginResponse)
async def login(
    response: Response,
    credentials: LoginRequest,
    db: Session = Depends(get_db)
):
    """Login user and return tokens (also sets HTTP-only cookies for production)"""
    # Find user by email
    user = db.query(User).filter(User.email == credentials.email).first()
    
    if not user or not verify_password(credentials.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    
    # Create tokens
    access_token = create_access_token(data={"sub": str(user.id)})
    refresh_token = create_refresh_token(data={"sub": str(user.id)})
    
    print(f"DEBUG LOGIN: Setting cookies for user {user.email}")
    
    # Set HTTP-only cookies (for production with proxy/same domain)
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        secure=False,
        samesite="lax",
        path="/",
        max_age=60 * 15
    )
    
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=False,
        samesite="lax",
        path="/",
        max_age=60 * 60 * 24 * 7
    )
    
    # ALSO return tokens in response body for development (different ports)
    return {
        "message": "Login successful",
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }

@router.post("/refresh", response_model=MessageResponse)
async def refresh_token_endpoint(
    request: Request,
    response: Response,
    db: Session = Depends(get_db)
):
    """Refresh access token using refresh token"""
    refresh_token = request.cookies.get("refresh_token")
    
    if not refresh_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token not found"
        )
    
    # Verify refresh token
    payload = verify_token(refresh_token, token_type="refresh")
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )
    
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload"
        )
    
    # Verify user exists
    user = db.query(User).filter(User.id == user_id).first()
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive"
        )
    
    # Create new access token
    new_access_token = create_access_token(data={"sub": str(user.id)})
    
    # Set new access token cookie
    response.set_cookie(
        key="access_token",
        value=new_access_token,
        httponly=True,
        secure=False,  # Set to True in production with HTTPS
        samesite="lax",
        path="/",
        max_age=60 * 15  # 15 minutes
    )
    
    return {"message": "Token refreshed successfully"}

@router.post("/logout", response_model=MessageResponse)
async def logout(response: Response):
    """Logout user by clearing cookies"""
    response.delete_cookie(key="access_token", path="/")
    response.delete_cookie(key="refresh_token", path="/")
    return {"message": "Logout successful"}

@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_user)
):
    """Get current authenticated user information"""
    return UserResponse(
        id=str(current_user.id),
        email=current_user.email,
        username=current_user.username,
        is_active=current_user.is_active
    )
