"""Office service for office-related business logic."""

from datetime import date
from decimal import Decimal

from sqlalchemy.ext.asyncio import AsyncSession

from models.office import Office
from repositories.inventory import InventoryRepository
from repositories.office import OfficeRepository
from repositories.order import OrderRepository


class OfficeService:
    """Service for office operations."""

    def __init__(self, session: AsyncSession) -> None:
        self.office_repo = OfficeRepository(session)
        self.order_repo = OrderRepository(session)
        self.inventory_repo = InventoryRepository(session)

    async def get_by_id(self, office_id: int) -> Office | None:
        """Get office by ID."""
        return await self.office_repo.get_by_id(office_id)

    async def get_all(self, skip: int = 0, limit: int = 100) -> list[Office]:
        """Get all offices."""
        return await self.office_repo.get_all(skip, limit)

    async def get_active(self, skip: int = 0, limit: int = 100) -> list[Office]:
        """Get all active offices."""
        return await self.office_repo.get_active_offices(skip, limit)

    async def create(
        self,
        name: str,
        max_storage_capacity: Decimal,
        address: str | None = None,
        daily_loss_rate: Decimal = Decimal("0.1"),
    ) -> Office:
        """Create a new office."""
        office = Office(
            name=name,
            address=address,
            max_storage_capacity=max_storage_capacity,
            daily_loss_rate=daily_loss_rate,
        )
        return await self.office_repo.create(office)

    async def update(
        self,
        office_id: int,
        name: str | None = None,
        address: str | None = None,
        max_storage_capacity: Decimal | None = None,
        daily_loss_rate: Decimal | None = None,
    ) -> Office | None:
        """Update an office."""
        office = await self.office_repo.get_by_id(office_id)
        if not office:
            return None

        if name is not None:
            office.name = name
        if address is not None:
            office.address = address
        if max_storage_capacity is not None:
            office.max_storage_capacity = max_storage_capacity
        if daily_loss_rate is not None:
            office.daily_loss_rate = daily_loss_rate

        return await self.office_repo.update(office)

    async def deactivate(self, office_id: int) -> Office | None:
        """Deactivate an office (soft delete)."""
        office = await self.office_repo.get_by_id(office_id)
        if not office:
            return None

        office.is_active = False
        return await self.office_repo.update(office)

    async def get_current_inventory(self, office_id: int) -> Decimal | None:
        """Get the current inventory level for an office."""
        snapshot = await self.inventory_repo.get_latest(office_id)
        if snapshot:
            return snapshot.inventory_level
        return None

    async def get_office_with_details(self, office_id: int) -> dict | None:
        """Get office with current inventory and pending orders."""
        office = await self.office_repo.get_by_id(office_id)
        if not office:
            return None

        current_inventory = await self.get_current_inventory(office_id)
        pending_orders = await self.order_repo.get_pending_orders(
            office_id,
            as_of_date=date.today(),
        )

        return {
            "office": office,
            "current_inventory": current_inventory,
            "pending_orders": pending_orders,
        }
