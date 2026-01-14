"""Order repository for order-related database operations."""

from datetime import date

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from models.order import Order, OrderCorrection
from repositories.base import BaseRepository


class OrderRepository(BaseRepository[Order]):
    """Repository for Order model operations."""

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, Order)

    async def get_by_office(
        self,
        office_id: int,
        skip: int = 0,
        limit: int = 100,
    ) -> list[Order]:
        """Get orders for a specific office."""
        result = await self.session.execute(
            select(Order)
            .where(Order.office_id == office_id)
            .order_by(Order.order_date.desc())
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())

    async def get_by_status(
        self,
        status: str,
        skip: int = 0,
        limit: int = 100,
    ) -> list[Order]:
        """Get orders by status."""
        result = await self.session.execute(
            select(Order)
            .where(Order.status == status)
            .order_by(Order.order_date.desc())
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())

    async def get_by_date_range(
        self,
        date_from: date,
        date_to: date,
        office_id: int | None = None,
        skip: int = 0,
        limit: int = 100,
    ) -> list[Order]:
        """Get orders within a date range."""
        query = select(Order).where(
            Order.order_date >= date_from,
            Order.order_date <= date_to,
        )
        if office_id:
            query = query.where(Order.office_id == office_id)
        query = query.order_by(Order.order_date.desc()).offset(skip).limit(limit)

        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def get_by_optimization_request(
        self,
        optimization_request_id: int,
    ) -> list[Order]:
        """Get all orders created by a specific optimization request."""
        result = await self.session.execute(
            select(Order)
            .where(Order.optimization_request_id == optimization_request_id)
            .order_by(Order.order_date)
        )
        return list(result.scalars().all())

    async def get_with_corrections(self, order_id: int) -> Order | None:
        """Get order with corrections eagerly loaded."""
        result = await self.session.execute(
            select(Order)
            .where(Order.id == order_id)
            .options(selectinload(Order.corrections))
        )
        return result.scalar_one_or_none()

    async def get_pending_orders(
        self,
        office_id: int,
        as_of_date: date | None = None,
    ) -> list[Order]:
        """Get pending (planned/confirmed) orders for an office."""
        query = select(Order).where(
            Order.office_id == office_id,
            Order.status.in_(["planned", "confirmed"]),
        )
        if as_of_date:
            query = query.where(Order.delivery_date >= as_of_date)
        query = query.order_by(Order.delivery_date)

        result = await self.session.execute(query)
        return list(result.scalars().all())


class OrderCorrectionRepository(BaseRepository[OrderCorrection]):
    """Repository for OrderCorrection model operations."""

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, OrderCorrection)

    async def get_by_order(self, order_id: int) -> list[OrderCorrection]:
        """Get all corrections for a specific order."""
        result = await self.session.execute(
            select(OrderCorrection)
            .where(OrderCorrection.original_order_id == order_id)
            .order_by(OrderCorrection.correction_date.desc())
        )
        return list(result.scalars().all())

    async def get_by_optimization_request(
        self,
        optimization_request_id: int,
    ) -> list[OrderCorrection]:
        """Get all corrections from a specific optimization request."""
        result = await self.session.execute(
            select(OrderCorrection)
            .where(OrderCorrection.optimization_request_id == optimization_request_id)
            .order_by(OrderCorrection.correction_date)
        )
        return list(result.scalars().all())
