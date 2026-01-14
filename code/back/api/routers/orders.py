"""Orders router."""

from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_session
from middleware.auth import get_current_user, require_vendor
from models.user import User
from schemas.order import OrderCorrectionCreate, OrderCorrectionResponse, OrderResponse
from services.order import OrderService

router = APIRouter(prefix="/orders", tags=["Orders"])


@router.get(
    "",
    response_model=list[OrderResponse],
    summary="List orders",
)
async def list_orders(
    office_id: int | None = Query(None, description="Filter by office ID"),
    start_date: date | None = Query(None, description="Filter by start date"),
    end_date: date | None = Query(None, description="Filter by end date"),
    status_filter: str | None = Query(None, alias="status", description="Filter by status"),
    session: AsyncSession = Depends(get_session),
    _: User = Depends(get_current_user),
):
    """Get a list of orders with optional filters."""
    order_service = OrderService(session)
    return await order_service.get_all(
        office_id=office_id,
        date_from=start_date,
        date_to=end_date,
        status=status_filter,
    )


@router.get(
    "/{order_id}",
    response_model=OrderResponse,
    summary="Get order details",
)
async def get_order(
    order_id: int,
    session: AsyncSession = Depends(get_session),
    _: User = Depends(get_current_user),
):
    """Get details of a specific order."""
    order_service = OrderService(session)

    order = await order_service.get_by_id(order_id)
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Order {order_id} not found",
        )

    return order


@router.patch(
    "/{order_id}/status",
    response_model=OrderResponse,
    summary="Update order status",
)
async def update_order_status(
    order_id: int,
    new_status: str = Query(..., description="New status: pending/confirmed/delivered/cancelled"),
    session: AsyncSession = Depends(get_session),
    _: User = Depends(require_vendor),
):
    """Update the status of an order (requires vendor role)."""
    order_service = OrderService(session)

    order = await order_service.update_status(order_id, new_status)
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Order {order_id} not found",
        )

    return order


@router.post(
    "/{order_id}/corrections",
    response_model=OrderCorrectionResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Add correction to order",
)
async def add_correction(
    order_id: int,
    data: OrderCorrectionCreate,
    session: AsyncSession = Depends(get_session),
    _: User = Depends(require_vendor),
):
    """Add a correction (increase/decrease quantity) to an existing order."""
    order_service = OrderService(session)

    order = await order_service.get_by_id(order_id)
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Order {order_id} not found",
        )

    # Corrections require an optimization context - use latest for now
    correction = await order_service.create_correction(
        order_id=order_id,
        optimization_request_id=order.optimization_request_id or 0,
        quantity_increase=data.quantity_increase,
        quantity_decrease=data.quantity_decrease,
        reason=data.reason,
    )

    if not correction:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to create correction",
        )

    return correction


@router.get(
    "/{order_id}/corrections",
    response_model=list[OrderCorrectionResponse],
    summary="Get order corrections",
)
async def get_corrections(
    order_id: int,
    session: AsyncSession = Depends(get_session),
    _: User = Depends(get_current_user),
):
    """Get all corrections for an order."""
    order_service = OrderService(session)

    order = await order_service.get_by_id(order_id)
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Order {order_id} not found",
        )

    return await order_service.get_corrections(order_id)
