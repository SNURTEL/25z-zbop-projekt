"""Optimization request model for solver results."""

from datetime import date, datetime
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, Date, DateTime, ForeignKey, Integer, Numeric, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models.base import Base

if TYPE_CHECKING:
    from models.inventory import InventorySnapshot
    from models.office import Office
    from models.order import Order, OrderCorrection


class OptimizationRequest(Base):
    """Optimization request storing solver input and results.

    Attributes:
        id: Primary key
        office_id: Reference to office (building)
        planning_horizon_start: Start date of planning period
        planning_horizon_end: End date of planning period
        initial_inventory: I_0 - initial inventory level [kg]
        total_cost: Total cost calculated by solver [PLN]
        solver_status: Solver status (OPTIMAL, INFEASIBLE, etc.)
        solve_time_ms: Solving time in milliseconds
        is_correction_mode: Whether this is a correction of existing orders
        created_at: Timestamp of request creation
    """

    __tablename__ = "optimization_requests"

    id: Mapped[int] = mapped_column(primary_key=True)
    office_id: Mapped[int] = mapped_column(
        ForeignKey("offices.id"),
        nullable=False,
        index=True,
    )
    planning_horizon_start: Mapped[date] = mapped_column(
        Date,
        nullable=False,
        index=True,
        comment="Początek horyzontu planowania",
    )
    planning_horizon_end: Mapped[date] = mapped_column(
        Date,
        nullable=False,
        comment="Koniec horyzontu planowania",
    )
    initial_inventory: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        nullable=False,
        comment="I_0 - stan magazynu na początku [kg]",
    )
    total_cost: Mapped[Decimal | None] = mapped_column(
        Numeric(12, 2),
        comment="Całkowity koszt obliczony przez solver [PLN]",
    )
    solver_status: Mapped[str | None] = mapped_column(
        String(50),
        comment="Status solvera: OPTIMAL, INFEASIBLE, etc.",
    )
    solve_time_ms: Mapped[int | None] = mapped_column(
        Integer,
        comment="Czas rozwiązywania [ms]",
    )
    is_correction_mode: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        comment="Czy tryb korekty istniejących zamówień",
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=func.now(),
        nullable=False,
        index=True,
    )

    # Relationships
    office: Mapped["Office"] = relationship("Office", back_populates="optimization_requests")
    orders: Mapped[list["Order"]] = relationship("Order", back_populates="optimization_request")
    corrections: Mapped[list["OrderCorrection"]] = relationship(
        "OrderCorrection", back_populates="optimization_request"
    )
    inventory_snapshots: Mapped[list["InventorySnapshot"]] = relationship(
        "InventorySnapshot", back_populates="optimization_request"
    )

    def __repr__(self) -> str:
        return f"<OptimizationRequest(id={self.id}, office_id={self.office_id}, status={self.solver_status})>"
