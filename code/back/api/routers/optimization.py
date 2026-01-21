"""Optimization router."""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_session
from middleware.auth import get_current_user, require_vendor
from models.user import User
from schemas.optimization import (
    InventorySnapshotResponse,
    OptimizationOrderResponse,
    OptimizationRequestCreate,
    OptimizationRequestResponse,
)
from services.optimization import OptimizationService

router = APIRouter(prefix="/optimization", tags=["Optimization"])


@router.post(
    "/requests",
    response_model=OptimizationRequestResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create and run optimization",
)
async def create_optimization(
    data: OptimizationRequestCreate,
    session: AsyncSession = Depends(get_session),
    _: User = Depends(require_vendor),
):
    """
    Create a new optimization request and run the CPLEX solver.
    
    This is the main endpoint for generating optimal order schedules.
    The solver minimizes total costs while satisfying:
    - Demand (based on workers and conferences)
    - Storage constraints (V_max)
    - Delivery lead times
    """
    optimization_service = OptimizationService(session)

    try:
        result = await optimization_service.run_optimization(
            office_id=data.office_id,
            horizon_start=data.planning_horizon_start,
            horizon_days=data.planning_horizon_days,
            initial_inventory=float(data.initial_inventory),
            purchase_costs=data.purchase_costs_daily,
            transport_cost=data.transport_cost,
            num_workers=data.num_workers_daily,
            num_conferences=data.num_conferences_daily,
            is_correction=data.is_correction_mode,
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )

    return _build_optimization_response(result)


@router.get(
    "/requests",
    response_model=list[OptimizationRequestResponse],
    summary="List optimization requests",
)
async def list_optimization_requests(
    office_id: int | None = Query(None, description="Filter by office ID"),
    limit: int = Query(10, ge=1, le=100),
    session: AsyncSession = Depends(get_session),
    _: User = Depends(get_current_user),
):
    """Get a list of optimization requests."""
    optimization_service = OptimizationService(session)

    requests = await optimization_service.get_recent(office_id=office_id, limit=limit)
    return [_build_optimization_response(r) for r in requests]


@router.get(
    "/requests/{request_id}",
    response_model=OptimizationRequestResponse,
    summary="Get optimization result",
)
async def get_optimization_request(
    request_id: int,
    session: AsyncSession = Depends(get_session),
    _: User = Depends(get_current_user),
):
    """Get details of an optimization request with results."""
    optimization_service = OptimizationService(session)

    request = await optimization_service.get_with_results(request_id)
    if not request:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Optimization request {request_id} not found",
        )

    return _build_optimization_response(request)


def _build_optimization_response(opt_request) -> OptimizationRequestResponse:
    """Build a complete optimization response with nested data."""
    orders = []
    if hasattr(opt_request, "orders") and opt_request.orders:
        orders = [
            OptimizationOrderResponse(
                id=o.id,
                order_date=o.order_date,
                delivery_date=o.delivery_date,
                quantity_kg=o.quantity_kg,
                unit_price=o.unit_price,
                transport_cost=o.transport_cost,
                total_cost=o.total_cost,
                status=o.status,
            )
            for o in opt_request.orders
        ]

    inventory = []
    if hasattr(opt_request, "inventory_snapshots") and opt_request.inventory_snapshots:
        inventory = [
            InventorySnapshotResponse(
                date=s.snapshot_date,
                inventory_level=s.inventory_level,
                demand_fulfilled=s.demand_fulfilled,
                loss_amount=s.loss_amount,
                deliveries_received=s.deliveries_received,
            )
            for s in opt_request.inventory_snapshots
        ]

    return OptimizationRequestResponse(
        id=opt_request.id,
        office_id=opt_request.office_id,
        planning_horizon_start=opt_request.planning_horizon_start,
        planning_horizon_end=opt_request.planning_horizon_end,
        initial_inventory=opt_request.initial_inventory,
        total_cost=opt_request.total_cost,
        solver_status=opt_request.solver_status,
        solve_time_ms=opt_request.solve_time_ms,
        is_correction_mode=opt_request.is_correction_mode,
        created_at=opt_request.created_at,
        orders=orders,
        inventory_projections=inventory,
    )
