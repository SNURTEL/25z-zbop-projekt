"""Order schemas."""

from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, Field


class OrderCreate(BaseModel):
    """Schema for creating an order."""

    office_id: int
    distributor_id: int | None = None
    order_date: date
    delivery_date: date
    quantity_kg: Decimal = Field(..., gt=0)
    unit_price: Decimal = Field(..., ge=0)
    transport_cost: Decimal = Field(..., ge=0)


class OrderResponse(BaseModel):
    """Schema for order response."""

    id: int
    optimization_request_id: int | None
    office_id: int
    distributor_id: int | None
    order_date: date
    delivery_date: date
    quantity_kg: Decimal
    unit_price: Decimal
    transport_cost: Decimal
    total_cost: Decimal
    status: str
    created_at: datetime

    model_config = {"from_attributes": True}


class OrderCorrectionCreate(BaseModel):
    """Schema for creating an order correction."""

    quantity_increase: Decimal = Field(default=Decimal("0"), ge=0)
    quantity_decrease: Decimal = Field(default=Decimal("0"), ge=0)
    reason: str | None = None


class OrderCorrectionResponse(BaseModel):
    """Schema for order correction response."""

    id: int
    original_order_id: int
    optimization_request_id: int
    correction_date: datetime
    quantity_increase: Decimal
    quantity_decrease: Decimal
    correction_cost: Decimal
    reason: str | None

    model_config = {"from_attributes": True}
