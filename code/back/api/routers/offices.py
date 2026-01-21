"""Office router."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_session
from middleware.auth import get_current_user, require_vendor
from models.user import User
from schemas.office import OfficeCreate, OfficeDetailResponse, OfficeResponse, OfficeUpdate, OrderSummary
from services.office import OfficeService

router = APIRouter(prefix="/offices", tags=["Offices"])


@router.get(
    "",
    response_model=list[OfficeResponse],
    summary="List all offices",
)
async def list_offices(
    session: AsyncSession = Depends(get_session),
    _: User = Depends(get_current_user),
):
    """Get a list of all offices."""
    office_service = OfficeService(session)
    return await office_service.get_all()


@router.post(
    "",
    response_model=OfficeResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new office",
)
async def create_office(
    data: OfficeCreate,
    session: AsyncSession = Depends(get_session),
    _: User = Depends(require_vendor),
):
    """Create a new office (requires vendor role)."""
    office_service = OfficeService(session)
    return await office_service.create(data)


@router.get(
    "/{office_id}",
    response_model=OfficeDetailResponse,
    summary="Get office details",
)
async def get_office(
    office_id: int,
    session: AsyncSession = Depends(get_session),
    _: User = Depends(get_current_user),
):
    """Get detailed information about an office."""
    office_service = OfficeService(session)

    office = await office_service.get_by_id(office_id)
    if not office:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Office {office_id} not found",
        )

    current_inventory = await office_service.get_current_inventory(office_id)
    pending_orders = await office_service.get_pending_orders(office_id)

    return OfficeDetailResponse(
        id=office.id,
        name=office.name,
        address=office.address,
        max_storage_capacity=office.max_storage_capacity,
        daily_loss_rate=office.daily_loss_rate,
        is_active=office.is_active,
        current_inventory=current_inventory,
        pending_orders=[
            OrderSummary(
                id=o.id,
                order_date=str(o.order_date),
                quantity_kg=o.quantity_kg,
                status=o.status,
            )
            for o in pending_orders
        ],
    )


@router.put(
    "/{office_id}",
    response_model=OfficeResponse,
    summary="Update an office",
)
async def update_office(
    office_id: int,
    data: OfficeUpdate,
    session: AsyncSession = Depends(get_session),
    _: User = Depends(require_vendor),
):
    """Update office details (requires vendor role)."""
    office_service = OfficeService(session)

    office = await office_service.update(office_id, data)
    if not office:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Office {office_id} not found",
        )

    return office


@router.delete(
    "/{office_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Deactivate an office",
)
async def delete_office(
    office_id: int,
    session: AsyncSession = Depends(get_session),
    _: User = Depends(require_vendor),
):
    """Soft-delete (deactivate) an office (requires vendor role)."""
    office_service = OfficeService(session)

    success = await office_service.deactivate(office_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Office {office_id} not found",
        )
