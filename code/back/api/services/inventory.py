"""Inventory service for inventory-related operations."""

from datetime import date
from decimal import Decimal

from sqlalchemy.ext.asyncio import AsyncSession

from models.inventory import InventorySnapshot
from repositories.inventory import InventoryRepository


class InventoryService:
    """Service for inventory operations."""

    def __init__(self, session: AsyncSession) -> None:
        self.inventory_repo = InventoryRepository(session)

    async def get_current(self, office_id: int) -> InventorySnapshot | None:
        """Get current inventory snapshot for an office."""
        return await self.inventory_repo.get_latest(office_id)

    async def get_by_date(
        self,
        office_id: int,
        snapshot_date: date,
    ) -> InventorySnapshot | None:
        """Get inventory snapshot for a specific date."""
        return await self.inventory_repo.get_by_date(office_id, snapshot_date)

    async def get_history(
        self,
        office_id: int,
        start_date: date,
        end_date: date,
        projected_only: bool = False,
    ) -> list[InventorySnapshot]:
        """Get inventory history for a date range."""
        return await self.inventory_repo.get_date_range(
            office_id, start_date, end_date, projected_only
        )

    async def get_projections(
        self,
        optimization_request_id: int,
    ) -> list[InventorySnapshot]:
        """Get inventory projections from an optimization request."""
        return await self.inventory_repo.get_by_optimization_request(
            optimization_request_id
        )

    async def record_actual(
        self,
        office_id: int,
        snapshot_date: date,
        inventory_level: Decimal,
        demand_fulfilled: Decimal | None = None,
        loss_amount: Decimal | None = None,
        deliveries_received: Decimal | None = None,
    ) -> InventorySnapshot:
        """Record actual inventory level."""
        snapshot = InventorySnapshot(
            office_id=office_id,
            date=snapshot_date,
            inventory_level=inventory_level,
            demand_fulfilled=demand_fulfilled,
            loss_amount=loss_amount,
            deliveries_received=deliveries_received,
            is_projected=False,
        )
        return await self.inventory_repo.create(snapshot)
