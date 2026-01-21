"""Inventory snapshot repository."""

from datetime import date

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.inventory import InventorySnapshot
from repositories.base import BaseRepository


class InventoryRepository(BaseRepository[InventorySnapshot]):
    """Repository for InventorySnapshot model operations."""

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, InventorySnapshot)

    async def get_by_office(
        self,
        office_id: int,
        skip: int = 0,
        limit: int = 100,
    ) -> list[InventorySnapshot]:
        """Get inventory snapshots for a specific office."""
        result = await self.session.execute(
            select(InventorySnapshot)
            .where(InventorySnapshot.office_id == office_id)
            .order_by(InventorySnapshot.date.desc())
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())

    async def get_by_date(
        self,
        office_id: int,
        snapshot_date: date,
    ) -> InventorySnapshot | None:
        """Get inventory snapshot for a specific date."""
        result = await self.session.execute(
            select(InventorySnapshot)
            .where(
                InventorySnapshot.office_id == office_id,
                InventorySnapshot.date == snapshot_date,
                InventorySnapshot.is_projected == False,  # noqa: E712
            )
            .order_by(InventorySnapshot.created_at.desc())
            .limit(1)
        )
        return result.scalar_one_or_none()

    async def get_latest(self, office_id: int) -> InventorySnapshot | None:
        """Get the most recent actual inventory snapshot for an office."""
        result = await self.session.execute(
            select(InventorySnapshot)
            .where(
                InventorySnapshot.office_id == office_id,
                InventorySnapshot.is_projected == False,  # noqa: E712
            )
            .order_by(InventorySnapshot.date.desc())
            .limit(1)
        )
        return result.scalar_one_or_none()

    async def get_by_optimization_request(
        self,
        optimization_request_id: int,
    ) -> list[InventorySnapshot]:
        """Get all inventory projections for an optimization request."""
        result = await self.session.execute(
            select(InventorySnapshot)
            .where(InventorySnapshot.optimization_request_id == optimization_request_id)
            .order_by(InventorySnapshot.date)
        )
        return list(result.scalars().all())

    async def get_date_range(
        self,
        office_id: int,
        start_date: date,
        end_date: date,
        projected_only: bool = False,
    ) -> list[InventorySnapshot]:
        """Get inventory snapshots within a date range."""
        query = select(InventorySnapshot).where(
            InventorySnapshot.office_id == office_id,
            InventorySnapshot.date >= start_date,
            InventorySnapshot.date <= end_date,
        )
        if projected_only:
            query = query.where(InventorySnapshot.is_projected == True)  # noqa: E712
        query = query.order_by(InventorySnapshot.date)

        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def bulk_create(self, snapshots: list[InventorySnapshot]) -> list[InventorySnapshot]:
        """Create multiple inventory snapshots at once."""
        self.session.add_all(snapshots)
        await self.session.commit()
        for snapshot in snapshots:
            await self.session.refresh(snapshot)
        return snapshots
