"""Base repository with generic CRUD operations."""

from typing import Generic, TypeVar

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.base import Base

ModelType = TypeVar("ModelType", bound=Base)


class BaseRepository(Generic[ModelType]):
    """Generic repository providing basic CRUD operations.

    Attributes:
        session: Async SQLAlchemy session
        model: SQLAlchemy model class
    """

    def __init__(self, session: AsyncSession, model: type[ModelType]) -> None:
        self.session = session
        self.model = model

    async def get_by_id(self, id: int) -> ModelType | None:
        """Get a single record by ID."""
        return await self.session.get(self.model, id)

    async def get_all(self, skip: int = 0, limit: int = 100) -> list[ModelType]:
        """Get all records with pagination."""
        result = await self.session.execute(
            select(self.model).offset(skip).limit(limit)
        )
        return list(result.scalars().all())

    async def create(self, obj: ModelType) -> ModelType:
        """Create a new record."""
        self.session.add(obj)
        await self.session.flush()
        return obj

    async def update(self, obj: ModelType) -> ModelType:
        """Update an existing record."""
        await self.session.flush()
        return obj

    async def delete(self, obj: ModelType) -> None:
        """Delete a record."""
        await self.session.delete(obj)
        await self.session.commit()

    async def delete_by_id(self, id: int) -> bool:
        """Delete a record by ID. Returns True if deleted."""
        obj = await self.get_by_id(id)
        if obj:
            await self.delete(obj)
            return True
        return False
