"""Order service for order-related business logic."""

from datetime import date
from decimal import Decimal

from sqlalchemy.ext.asyncio import AsyncSession

from models.order import Order, OrderCorrection
from repositories.order import OrderCorrectionRepository, OrderRepository


class OrderService:
    """Service for order operations."""

    def __init__(self, session: AsyncSession) -> None:
        self.order_repo = OrderRepository(session)
        self.correction_repo = OrderCorrectionRepository(session)

    async def get_by_id(self, order_id: int) -> Order | None:
        """Get order by ID."""
        return await self.order_repo.get_by_id(order_id)

    async def get_with_corrections(self, order_id: int) -> Order | None:
        """Get order with corrections."""
        return await self.order_repo.get_with_corrections(order_id)

    async def get_all(
        self,
        office_id: int | None = None,
        status: str | None = None,
        date_from: date | None = None,
        date_to: date | None = None,
        skip: int = 0,
        limit: int = 100,
    ) -> list[Order]:
        """Get orders with optional filtering."""
        if date_from and date_to:
            return await self.order_repo.get_by_date_range(
                date_from, date_to, office_id, skip, limit
            )
        elif office_id:
            return await self.order_repo.get_by_office(office_id, skip, limit)
        elif status:
            return await self.order_repo.get_by_status(status, skip, limit)
        else:
            return await self.order_repo.get_all(skip, limit)

    async def create(
        self,
        office_id: int,
        order_date: date,
        delivery_date: date,
        quantity_kg: Decimal,
        unit_price: Decimal,
        transport_cost: Decimal,
        distributor_id: int | None = None,
        optimization_request_id: int | None = None,
    ) -> Order:
        """Create a new order."""
        total_cost = (quantity_kg * unit_price) + transport_cost

        order = Order(
            office_id=office_id,
            distributor_id=distributor_id,
            optimization_request_id=optimization_request_id,
            order_date=order_date,
            delivery_date=delivery_date,
            quantity_kg=quantity_kg,
            unit_price=unit_price,
            transport_cost=transport_cost,
            total_cost=total_cost,
            status="planned",
        )
        return await self.order_repo.create(order)

    async def update_status(self, order_id: int, status: str) -> Order | None:
        """Update order status."""
        order = await self.order_repo.get_by_id(order_id)
        if not order:
            return None

        order.status = status
        return await self.order_repo.update(order)

    async def cancel(self, order_id: int) -> Order | None:
        """Cancel an order."""
        return await self.update_status(order_id, "cancelled")

    async def create_correction(
        self,
        order_id: int,
        optimization_request_id: int,
        quantity_increase: Decimal = Decimal("0"),
        quantity_decrease: Decimal = Decimal("0"),
        correction_cost: Decimal = Decimal("0"),
        reason: str | None = None,
    ) -> OrderCorrection | None:
        """Create a correction for an order."""
        order = await self.order_repo.get_by_id(order_id)
        if not order:
            return None

        correction = OrderCorrection(
            original_order_id=order_id,
            optimization_request_id=optimization_request_id,
            quantity_increase=quantity_increase,
            quantity_decrease=quantity_decrease,
            correction_cost=correction_cost,
            reason=reason,
        )

        # Update the order quantity
        new_quantity = order.quantity_kg + quantity_increase - quantity_decrease
        order.quantity_kg = new_quantity
        order.total_cost = (new_quantity * order.unit_price) + order.transport_cost

        await self.order_repo.update(order)
        return await self.correction_repo.create(correction)

    async def get_corrections(self, order_id: int) -> list[OrderCorrection]:
        """Get all corrections for an order."""
        return await self.correction_repo.get_by_order(order_id)

    async def get_pending_orders(
        self,
        office_id: int,
        as_of_date: date | None = None,
    ) -> list[Order]:
        """Get pending orders for an office."""
        return await self.order_repo.get_pending_orders(office_id, as_of_date)
