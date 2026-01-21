"""Office schemas."""

from decimal import Decimal

from pydantic import BaseModel, Field


class OfficeCreate(BaseModel):
    """Schema for creating an office."""

    name: str = Field(..., max_length=255)
    address: str | None = None
    max_storage_capacity: Decimal = Field(..., gt=0, description="V_max [kg]")
    daily_loss_rate: Decimal = Field(default=Decimal("0.1"), ge=0, le=1)


class OfficeUpdate(BaseModel):
    """Schema for updating an office."""

    name: str | None = Field(None, max_length=255)
    address: str | None = None
    max_storage_capacity: Decimal | None = Field(None, gt=0)
    daily_loss_rate: Decimal | None = Field(None, ge=0, le=1)


class OfficeResponse(BaseModel):
    """Schema for office response."""

    id: int
    name: str
    address: str | None
    max_storage_capacity: Decimal
    daily_loss_rate: Decimal
    is_active: bool

    model_config = {"from_attributes": True}


class OrderSummary(BaseModel):
    """Brief order summary for office details."""

    id: int
    order_date: str
    quantity_kg: Decimal
    status: str

    model_config = {"from_attributes": True}


class OfficeDetailResponse(BaseModel):
    """Schema for office with inventory and orders."""

    id: int
    name: str
    address: str | None
    max_storage_capacity: Decimal
    daily_loss_rate: Decimal
    is_active: bool
    current_inventory: Decimal | None
    pending_orders: list[OrderSummary]
