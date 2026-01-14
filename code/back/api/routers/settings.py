"""Settings router for system parameters."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_session
from middleware.auth import require_vendor
from models.user import User
from schemas.settings import SystemParameterResponse, SystemParameterUpdate
from services.settings import SettingsService

router = APIRouter(prefix="/settings", tags=["Settings"])


@router.get(
    "",
    response_model=list[SystemParameterResponse],
    summary="Get all system parameters",
)
async def list_settings(
    session: AsyncSession = Depends(get_session),
    _: User = Depends(require_vendor),
):
    """Get all system configuration parameters (vendor only)."""
    settings_service = SettingsService(session)
    return await settings_service.get_all()


@router.get(
    "/{param_name}",
    response_model=SystemParameterResponse,
    summary="Get a system parameter",
)
async def get_setting(
    param_name: str,
    session: AsyncSession = Depends(get_session),
    _: User = Depends(require_vendor),
):
    """Get a specific system parameter by name (vendor only)."""
    settings_service = SettingsService(session)

    param = await settings_service.get_by_name(param_name)
    if not param:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Parameter '{param_name}' not found",
        )

    return param


@router.put(
    "/{param_name}",
    response_model=SystemParameterResponse,
    summary="Update a system parameter",
)
async def update_setting(
    param_name: str,
    data: SystemParameterUpdate,
    session: AsyncSession = Depends(get_session),
    _: User = Depends(require_vendor),
):
    """Update a system parameter (vendor only)."""
    settings_service = SettingsService(session)

    param = await settings_service.set_parameter(
        name=param_name,
        value=data.parameter_value,
        description=data.description,
    )

    return param
