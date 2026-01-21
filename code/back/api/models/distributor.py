"""Distributor model for coffee suppliers."""

from typing import TYPE_CHECKING

from sqlalchemy import Boolean, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models.base import Base

if TYPE_CHECKING:
    from models.order import Order


class Distributor(Base):
    """Coffee distributor/supplier.

    Attributes:
        id: Primary key
        name: Distributor name
        description: Optional description
        is_active: Whether the distributor is active
    """

    __tablename__ = "distributors"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    description: Mapped[str | None] = mapped_column(Text)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    # Relationships
    orders: Mapped[list["Order"]] = relationship("Order", back_populates="distributor")

    def __repr__(self) -> str:
        return f"<Distributor(id={self.id}, name={self.name})>"
