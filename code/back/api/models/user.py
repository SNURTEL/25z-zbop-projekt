"""User model for authentication and authorization."""

from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models.base import Base, TimestampMixin


class User(Base, TimestampMixin):
    """User account for the system.

    Attributes:
        id: Primary key
        email: Unique email address (used for login)
        password_hash: Bcrypt hashed password
        first_name: User's first name
        last_name: User's last name
        role: User role (admin, manager, user)
        office_id: Associated office (for managers)
        is_active: Whether the account is active
        last_login: Timestamp of last login
    """

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    first_name: Mapped[str | None] = mapped_column(String(100))
    last_name: Mapped[str | None] = mapped_column(String(100))
    role: Mapped[str] = mapped_column(String(50), default="user", index=True)
    office_id: Mapped[int | None] = mapped_column(ForeignKey("offices.id"))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    last_login: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    # Relationships
    office: Mapped["Office | None"] = relationship("Office", back_populates="users")

    def __repr__(self) -> str:
        return f"<User(id={self.id}, email={self.email}, role={self.role})>"


# Avoid circular import
from models.office import Office  # noqa: E402, F401
