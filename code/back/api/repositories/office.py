"""Office repository for office-related database operations."""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from models.office import Office
from repositories.base import BaseRepository


class OfficeRepository(BaseRepository[Office]):
    """Repository for Office model operations."""

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, Office)

    async def get_active_offices(self, skip: int = 0, limit: int = 100) -> list[Office]:
        """Get all active offices."""
        result = await self.session.execute(
            select(Office)
            .where(Office.is_active == True)  # noqa: E712
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())

    async def get_by_name(self, name: str) -> Office | None:
        """Get office by name."""
        result = await self.session.execute(
            select(Office).where(Office.name == name)
        )
        return result.scalar_one_or_none()

    async def get_with_pending_orders(self, office_id: int) -> Office | None:
        """Get office with pending orders eagerly loaded."""
        result = await self.session.execute(
            select(Office)
            .where(Office.id == office_id)
            .options(selectinload(Office.orders))
        )
        return result.scalar_one_or_none()

    async def get_with_inventory(self, office_id: int) -> Office | None:
        """Get office with inventory snapshots eagerly loaded."""
        result = await self.session.execute(
            select(Office)
            .where(Office.id == office_id)
            .options(selectinload(Office.inventory_snapshots))
        )
        return result.scalar_one_or_none()
