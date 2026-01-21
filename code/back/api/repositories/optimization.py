"""Optimization request repository."""

from datetime import date

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from models.optimization import OptimizationRequest
from repositories.base import BaseRepository


class OptimizationRepository(BaseRepository[OptimizationRequest]):
    """Repository for OptimizationRequest model operations."""

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, OptimizationRequest)

    async def get_by_office(
        self,
        office_id: int,
        skip: int = 0,
        limit: int = 100,
    ) -> list[OptimizationRequest]:
        """Get optimization requests for a specific office."""
        result = await self.session.execute(
            select(OptimizationRequest)
            .where(OptimizationRequest.office_id == office_id)
            .order_by(OptimizationRequest.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())

    async def get_with_orders(self, request_id: int) -> OptimizationRequest | None:
        """Get optimization request with orders eagerly loaded."""
        result = await self.session.execute(
            select(OptimizationRequest)
            .where(OptimizationRequest.id == request_id)
            .options(selectinload(OptimizationRequest.orders))
        )
        return result.scalar_one_or_none()

    async def get_with_all_relations(self, request_id: int) -> OptimizationRequest | None:
        """Get optimization request with all relations eagerly loaded."""
        result = await self.session.execute(
            select(OptimizationRequest)
            .where(OptimizationRequest.id == request_id)
            .options(
                selectinload(OptimizationRequest.orders),
                selectinload(OptimizationRequest.inventory_snapshots),
                selectinload(OptimizationRequest.corrections),
            )
        )
        return result.scalar_one_or_none()

    async def get_latest_by_office(self, office_id: int) -> OptimizationRequest | None:
        """Get the most recent optimization request for an office."""
        result = await self.session.execute(
            select(OptimizationRequest)
            .where(OptimizationRequest.office_id == office_id)
            .order_by(OptimizationRequest.created_at.desc())
            .limit(1)
        )
        return result.scalar_one_or_none()

    async def get_by_date_range(
        self,
        office_id: int,
        start_date: date,
        end_date: date,
    ) -> list[OptimizationRequest]:
        """Get optimization requests overlapping with a date range."""
        result = await self.session.execute(
            select(OptimizationRequest)
            .where(
                OptimizationRequest.office_id == office_id,
                OptimizationRequest.planning_horizon_start <= end_date,
                OptimizationRequest.planning_horizon_end >= start_date,
            )
            .order_by(OptimizationRequest.created_at.desc())
        )
        return list(result.scalars().all())
