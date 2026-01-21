"""Office (building) model for coffee inventory management."""

from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models.base import Base

if TYPE_CHECKING:
    from models.inventory import InventorySnapshot
    from models.optimization import OptimizationRequest
    from models.order import Order
    from models.user import User


class Office(Base):
    """Office building with coffee storage.

    Attributes:
        id: Primary key
        name: Office name
        address: Physical address
        max_storage_capacity: V_max - maximum storage capacity [kg]
        daily_loss_rate: alpha - daily coffee loss fraction (default 10%)
        is_active: Whether the office is active
    """

    __tablename__ = "offices"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    address: Mapped[str | None] = mapped_column(Text)
    max_storage_capacity: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        nullable=False,
        comment="V_max - maksymalna pojemność magazynu [kg]",
    )
    daily_loss_rate: Mapped[Decimal] = mapped_column(
        Numeric(5, 4),
        default=Decimal("0.1"),
        comment="alpha - współczynnik dziennej straty kawy",
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    # Relationships
    users: Mapped[list["User"]] = relationship("User", back_populates="office")
    optimization_requests: Mapped[list["OptimizationRequest"]] = relationship(
        "OptimizationRequest", back_populates="office"
    )
    orders: Mapped[list["Order"]] = relationship("Order", back_populates="office")
    inventory_snapshots: Mapped[list["InventorySnapshot"]] = relationship(
        "InventorySnapshot", back_populates="office"
    )

    def __repr__(self) -> str:
        return f"<Office(id={self.id}, name={self.name})>"
