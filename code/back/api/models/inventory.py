"""Inventory snapshot model for tracking stock levels."""

from datetime import date, datetime
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, Date, DateTime, ForeignKey, Numeric, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models.base import Base

if TYPE_CHECKING:
    from models.office import Office
    from models.optimization import OptimizationRequest


class InventorySnapshot(Base):
    """Daily inventory snapshot for an office.

    Attributes:
        id: Primary key
        office_id: Reference to office (building)
        optimization_request_id: Reference to optimization that created this projection
        date: Day t
        inventory_level: I_{b,t} - inventory level at end of day [kg]
        demand_fulfilled: Demand fulfilled that day [kg]
        loss_amount: Coffee lost that day [kg]
        deliveries_received: Total deliveries received [kg]
        is_projected: True if projection, False if actual
        created_at: Timestamp of creation
    """

    __tablename__ = "inventory_snapshots"

    id: Mapped[int] = mapped_column(primary_key=True)
    office_id: Mapped[int] = mapped_column(
        ForeignKey("offices.id"),
        nullable=False,
    )
    optimization_request_id: Mapped[int | None] = mapped_column(
        ForeignKey("optimization_requests.id"),
        index=True,
    )
    date: Mapped[date] = mapped_column(
        Date,
        nullable=False,
        comment="Dzień t",
    )
    inventory_level: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        nullable=False,
        comment="I_{b,t} - stan magazynu na koniec dnia [kg]",
    )
    demand_fulfilled: Mapped[Decimal | None] = mapped_column(
        Numeric(10, 2),
        comment="Zaspokojone zapotrzebowanie [kg]",
    )
    loss_amount: Mapped[Decimal | None] = mapped_column(
        Numeric(10, 2),
        comment="Strata dzienna [kg]",
    )
    deliveries_received: Mapped[Decimal | None] = mapped_column(
        Numeric(10, 2),
        comment="Suma dostaw otrzymanych [kg]",
    )
    is_projected: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        comment="true = prognoza, false = rzeczywisty stan",
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=func.now(),
        nullable=False,
    )

    # Relationships
    office: Mapped["Office"] = relationship("Office", back_populates="inventory_snapshots")
    optimization_request: Mapped["OptimizationRequest | None"] = relationship(
        "OptimizationRequest", back_populates="inventory_snapshots"
    )

    def __repr__(self) -> str:
        return f"<InventorySnapshot(id={self.id}, office_id={self.office_id}, date={self.date}, level={self.inventory_level}kg)>"
