"""Authentication service for JWT and password handling."""

from datetime import datetime, timedelta, timezone

from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.ext.asyncio import AsyncSession

from config import settings
from models.user import User
from repositories.user import UserRepository

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class AuthService:
    """Service for authentication operations."""

    def __init__(self, session: AsyncSession) -> None:
        self.user_repo = UserRepository(session)

    @staticmethod
    def hash_password(password: str) -> str:
        """Hash a password using bcrypt."""
        return pwd_context.hash(password)

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """Verify a password against its hash."""
        return pwd_context.verify(plain_password, hashed_password)

    @staticmethod
    def create_access_token(user_id: int, expires_delta: timedelta | None = None) -> str:
        """Create a JWT access token."""
        if expires_delta:
            expire = datetime.now(timezone.utc) + expires_delta
        else:
            expire = datetime.now(timezone.utc) + timedelta(
                minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
            )

        payload = {
            "sub": str(user_id),
            "exp": expire,
            "iat": datetime.now(timezone.utc),
        }
        return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

    @staticmethod
    def decode_token(token: str) -> dict | None:
        """Decode and validate a JWT token."""
        try:
            payload = jwt.decode(
                token,
                settings.SECRET_KEY,
                algorithms=[settings.ALGORITHM],
            )
            return payload
        except JWTError:
            return None

    async def email_exists(self, email: str) -> bool:
        """Check if an email is already registered."""
        return await self.user_repo.email_exists(email)

    async def authenticate(self, email: str, password: str) -> User | None:
        """Authenticate a user by email and password."""
        user = await self.user_repo.get_by_email(email)
        if not user:
            return None
        if not user.is_active:
            return None
        if not self.verify_password(password, user.password_hash):
            return None

        # Update last login
        user.last_login = datetime.now(timezone.utc)
        await self.user_repo.update(user)

        return user

    async def register(
        self,
        email: str,
        password: str,
        first_name: str | None = None,
        last_name: str | None = None,
        role: str = "user",
    ) -> User | None:
        """Register a new user."""
        # Check if email already exists
        if await self.user_repo.email_exists(email):
            return None

        user = User(
            email=email,
            password_hash=self.hash_password(password),
            first_name=first_name,
            last_name=last_name,
            role=role,
        )
        return await self.user_repo.create(user)

    async def get_user_by_token(self, token: str) -> User | None:
        """Get user from a valid JWT token."""
        payload = self.decode_token(token)
        if not payload:
            return None

        user_id = payload.get("sub")
        if not user_id:
            return None

        try:
            user = await self.user_repo.get_by_id(int(user_id))
            if user and user.is_active:
                return user
        except ValueError:
            pass

        return None
