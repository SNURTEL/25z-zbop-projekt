"""Authentication router."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from config import settings
from database import get_session
from middleware.auth import get_current_user
from models.user import User
from schemas.auth import TokenResponse, UserLogin, UserRegister, UserResponse
from services.auth import AuthService

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user",
)
async def register(
    data: UserRegister,
    session: AsyncSession = Depends(get_session),
):
    """Register a new user account."""
    auth_service = AuthService(session)

    # Check if email already exists
    if await auth_service.email_exists(data.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )

    user = await auth_service.register(
        email=data.email,
        password=data.password,
        first_name=data.first_name,
        last_name=data.last_name,
    )

    return user


@router.post(
    "/login",
    response_model=TokenResponse,
    summary="Login and get JWT token",
)
async def login(
    data: UserLogin,
    session: AsyncSession = Depends(get_session),
):
    """Authenticate user and return JWT token."""
    auth_service = AuthService(session)

    user = await auth_service.authenticate(data.email, data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = auth_service.create_access_token(user_id=user.id)

    return TokenResponse(
        access_token=token,
        token_type="bearer",
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )


@router.get(
    "/me",
    response_model=UserResponse,
    summary="Get current user info",
)
async def get_me(
    current_user: User = Depends(get_current_user),
):
    """Get information about the currently authenticated user."""
    return current_user
