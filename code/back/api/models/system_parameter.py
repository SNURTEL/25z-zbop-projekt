"""System parameters model for global configuration."""

from datetime import datetime

from sqlalchemy import DateTime, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from models.base import Base


class SystemParameter(Base):
    """System-wide configuration parameter.

    Attributes:
        id: Primary key
        parameter_name: Unique parameter name
        parameter_value: Parameter value as string
        description: Optional description
        updated_at: Last update timestamp
    """

    __tablename__ = "system_parameters"

    id: Mapped[int] = mapped_column(primary_key=True)
    parameter_name: Mapped[str] = mapped_column(
        String(100),
        unique=True,
        nullable=False,
    )
    parameter_value: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )
    description: Mapped[str | None] = mapped_column(Text)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    def __repr__(self) -> str:
        return f"<SystemParameter(name={self.parameter_name}, value={self.parameter_value})>"
