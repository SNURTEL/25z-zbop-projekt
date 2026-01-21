"""Distributor repository for distributor-related database operations."""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.distributor import Distributor
from repositories.base import BaseRepository


class DistributorRepository(BaseRepository[Distributor]):
    """Repository for Distributor model operations."""

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, Distributor)

    async def get_active_distributors(self, skip: int = 0, limit: int = 100) -> list[Distributor]:
        """Get all active distributors."""
        result = await self.session.execute(
            select(Distributor)
            .where(Distributor.is_active == True)  # noqa: E712
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())

    async def get_by_name(self, name: str) -> Distributor | None:
        """Get distributor by name."""
        result = await self.session.execute(
            select(Distributor).where(Distributor.name == name)
        )
        return result.scalar_one_or_none()
