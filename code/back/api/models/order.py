"""Order and OrderCorrection models."""

from datetime import date, datetime
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import Date, DateTime, ForeignKey, Numeric, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models.base import Base, TimestampMixin

if TYPE_CHECKING:
    from models.distributor import Distributor
    from models.office import Office
    from models.optimization import OptimizationRequest


class Order(Base, TimestampMixin):
    """Coffee order from a distributor to an office.

    Attributes:
        id: Primary key
        optimization_request_id: Reference to optimization that created this order
        distributor_id: Reference to distributor
        office_id: Reference to office (building)
        order_date: Date when order is placed (day t)
        delivery_date: Expected delivery date
        quantity_kg: x_{d,b,t} - ordered quantity [kg]
        unit_price: Unit price [PLN/kg]
        transport_cost: Transport cost [PLN]
        total_cost: Total order cost [PLN]
        status: Order status (planned/confirmed/delivered/cancelled)
    """

    __tablename__ = "orders"

    id: Mapped[int] = mapped_column(primary_key=True)
    optimization_request_id: Mapped[int | None] = mapped_column(
        ForeignKey("optimization_requests.id"),
        index=True,
    )
    distributor_id: Mapped[int | None] = mapped_column(
        ForeignKey("distributors.id"),
    )
    office_id: Mapped[int] = mapped_column(
        ForeignKey("offices.id"),
        nullable=False,
    )
    order_date: Mapped[date] = mapped_column(
        Date,
        nullable=False,
        index=True,
        comment="Dzień złożenia zamówienia t",
    )
    delivery_date: Mapped[date] = mapped_column(
        Date,
        nullable=False,
        comment="Dzień dostawy",
    )
    quantity_kg: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        nullable=False,
        comment="x_{d,b,t} - zamówiona ilość [kg]",
    )
    unit_price: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        nullable=False,
        comment="Cena jednostkowa [PLN/kg]",
    )
    transport_cost: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        nullable=False,
        comment="Koszt transportu [PLN]",
    )
    total_cost: Mapped[Decimal] = mapped_column(
        Numeric(12, 2),
        nullable=False,
        comment="Łączny koszt zamówienia [PLN]",
    )
    status: Mapped[str] = mapped_column(
        String(50),
        default="planned",
        index=True,
        comment="planned/confirmed/delivered/cancelled",
    )

    # Relationships
    optimization_request: Mapped["OptimizationRequest | None"] = relationship(
        "OptimizationRequest", back_populates="orders"
    )
    distributor: Mapped["Distributor | None"] = relationship("Distributor", back_populates="orders")
    office: Mapped["Office"] = relationship("Office", back_populates="orders")
    corrections: Mapped[list["OrderCorrection"]] = relationship("OrderCorrection", back_populates="original_order")

    def __repr__(self) -> str:
        return f"<Order(id={self.id}, quantity={self.quantity_kg}kg, status={self.status})>"


class OrderCorrection(Base):
    """Correction to an existing order.

    Attributes:
        id: Primary key
        original_order_id: Reference to the order being corrected
        optimization_request_id: Reference to optimization that suggested this correction
        correction_date: When the correction was made
        quantity_increase: r^+_{d,b,t} - increase in quantity [kg]
        quantity_decrease: r^-_{d,b,t} - decrease in quantity [kg]
        correction_cost: Cost of correction [PLN]
        reason: Explanation for the correction
    """

    __tablename__ = "order_corrections"

    id: Mapped[int] = mapped_column(primary_key=True)
    original_order_id: Mapped[int] = mapped_column(
        ForeignKey("orders.id"),
        nullable=False,
        index=True,
    )
    optimization_request_id: Mapped[int] = mapped_column(
        ForeignKey("optimization_requests.id"),
        nullable=False,
        index=True,
    )
    correction_date: Mapped[datetime] = mapped_column(
        DateTime,
        default=func.now(),
        nullable=False,
    )
    quantity_increase: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        default=Decimal("0"),
        comment="r^+_{d,b,t} - zwiększenie zamówienia [kg]",
    )
    quantity_decrease: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        default=Decimal("0"),
        comment="r^-_{d,b,t} - zmniejszenie zamówienia [kg]",
    )
    correction_cost: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        nullable=False,
        comment="Koszt korekty [PLN]",
    )
    reason: Mapped[str | None] = mapped_column(Text)

    # Relationships
    original_order: Mapped["Order"] = relationship("Order", back_populates="corrections")
    optimization_request: Mapped["OptimizationRequest"] = relationship(
        "OptimizationRequest", back_populates="corrections"
    )

    def __repr__(self) -> str:
        return f"<OrderCorrection(id={self.id}, order_id={self.original_order_id})>"
