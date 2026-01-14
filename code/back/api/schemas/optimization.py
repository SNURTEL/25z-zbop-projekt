"""Optimization schemas."""

from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, Field, model_validator
from typing_extensions import Self


class OptimizationRequestCreate(BaseModel):
    """Schema for creating an optimization request."""

    office_id: int
    planning_horizon_start: date
    planning_horizon_days: int = Field(..., ge=1, le=30)
    initial_inventory: Decimal = Field(..., ge=0)
    purchase_costs_daily: list[float]
    transport_cost: float = Field(..., ge=0)
    num_workers_daily: list[int]
    num_conferences_daily: list[int]
    is_correction_mode: bool = False

    @model_validator(mode="after")
    def check_array_lengths(self) -> Self:
        """Validate that all daily arrays match planning horizon."""
        n = self.planning_horizon_days
        if len(self.purchase_costs_daily) != n:
            raise ValueError(f"purchase_costs_daily must have {n} elements")
        if len(self.num_workers_daily) != n:
            raise ValueError(f"num_workers_daily must have {n} elements")
        if len(self.num_conferences_daily) != n:
            raise ValueError(f"num_conferences_daily must have {n} elements")
        return self


class InventorySnapshotResponse(BaseModel):
    """Schema for inventory snapshot."""

    date: date
    inventory_level: Decimal
    demand_fulfilled: Decimal | None
    loss_amount: Decimal | None
    deliveries_received: Decimal | None

    model_config = {"from_attributes": True}


class OptimizationOrderResponse(BaseModel):
    """Simplified order response for optimization results."""

    id: int
    order_date: date
    delivery_date: date
    quantity_kg: Decimal
    unit_price: Decimal
    transport_cost: Decimal
    total_cost: Decimal
    status: str

    model_config = {"from_attributes": True}


class OptimizationRequestResponse(BaseModel):
    """Schema for optimization request response."""

    id: int
    office_id: int
    planning_horizon_start: date
    planning_horizon_end: date
    initial_inventory: Decimal
    total_cost: Decimal | None
    solver_status: str | None
    solve_time_ms: int | None
    is_correction_mode: bool
    created_at: datetime
    orders: list[OptimizationOrderResponse] = []
    inventory_projections: list[InventorySnapshotResponse] = []

    model_config = {"from_attributes": True}
