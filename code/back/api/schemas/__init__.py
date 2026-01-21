"""Pydantic schemas for API request/response validation."""

from schemas.auth import TokenResponse, UserLogin, UserRegister, UserResponse
from schemas.common import ErrorResponse, MessageResponse
from schemas.office import OfficeCreate, OfficeDetailResponse, OfficeResponse, OfficeUpdate
from schemas.optimization import (
    InventorySnapshotResponse,
    OptimizationOrderResponse,
    OptimizationRequestCreate,
    OptimizationRequestResponse,
)
from schemas.order import OrderCorrectionCreate, OrderCorrectionResponse, OrderCreate, OrderResponse
from schemas.settings import SystemParameterResponse, SystemParameterUpdate

__all__ = [
    # Common
    "ErrorResponse",
    "MessageResponse",
    # Auth
    "UserRegister",
    "UserLogin",
    "TokenResponse",
    "UserResponse",
    # Office
    "OfficeCreate",
    "OfficeUpdate",
    "OfficeResponse",
    "OfficeDetailResponse",
    # Order
    "OrderCreate",
    "OrderResponse",
    "OrderCorrectionCreate",
    "OrderCorrectionResponse",
    # Optimization
    "OptimizationRequestCreate",
    "OptimizationRequestResponse",
    "OptimizationOrderResponse",
    "InventorySnapshotResponse",
    # Settings
    "SystemParameterResponse",
    "SystemParameterUpdate",
]
