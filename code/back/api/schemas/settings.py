"""System parameter schemas."""

from datetime import datetime

from pydantic import BaseModel


class SystemParameterResponse(BaseModel):
    """Schema for system parameter response."""

    id: int
    parameter_name: str
    parameter_value: str
    description: str | None
    updated_at: datetime

    model_config = {"from_attributes": True}


class SystemParameterUpdate(BaseModel):
    """Schema for updating a system parameter."""

    parameter_value: str
    description: str | None = None
