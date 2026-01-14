"""Optimization service integrating with the CPLEX solver."""

import time
from datetime import date, timedelta
from decimal import Decimal

from sqlalchemy.ext.asyncio import AsyncSession

from models.inventory import InventorySnapshot
from models.optimization import OptimizationRequest
from models.order import Order
from repositories.inventory import InventoryRepository
from repositories.office import OfficeRepository
from repositories.optimization import OptimizationRepository
from repositories.order import OrderRepository
from solver import SolverFail, SolverInput, SolverOutput, estimate_demand, solve


class OptimizationService:
    """Service for running optimization and storing results."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.optimization_repo = OptimizationRepository(session)
        self.order_repo = OrderRepository(session)
        self.inventory_repo = InventoryRepository(session)
        self.office_repo = OfficeRepository(session)

    async def get_by_id(self, request_id: int) -> OptimizationRequest | None:
        """Get optimization request by ID."""
        return await self.optimization_repo.get_by_id(request_id)

    async def get_with_results(self, request_id: int) -> OptimizationRequest | None:
        """Get optimization request with all related data."""
        return await self.optimization_repo.get_with_all_relations(request_id)

    async def run_optimization(
        self,
        office_id: int,
        planning_horizon_start: date,
        planning_horizon_days: int,
        initial_inventory: Decimal,
        purchase_costs_daily: list[float],
        transport_cost: float,
        num_workers_daily: list[int],
        num_conferences_daily: list[int],
        is_correction_mode: bool = False,
    ) -> OptimizationRequest:
        """Run the optimization solver and store results.

        Args:
            office_id: ID of the office
            planning_horizon_start: Start date of planning period
            planning_horizon_days: Number of days to plan
            initial_inventory: Initial inventory level [kg]
            purchase_costs_daily: Coffee prices for each day [PLN/kg]
            transport_cost: Transport cost per delivery [PLN]
            num_workers_daily: Number of workers for each day
            num_conferences_daily: Number of conferences for each day
            is_correction_mode: Whether this is a correction run

        Returns:
            OptimizationRequest with results
        """
        # Get office for capacity
        office = await self.office_repo.get_by_id(office_id)
        if not office:
            raise ValueError(f"Office with ID {office_id} not found")

        # Calculate demand for each day
        demands = [
            estimate_demand(workers, conferences)
            for workers, conferences in zip(num_workers_daily, num_conferences_daily)
        ]

        # Prepare solver input
        solver_input = SolverInput(
            V_max=float(office.max_storage_capacity),
            P=purchase_costs_daily,
            C=transport_cost,
            D=demands,
            I0=float(initial_inventory),
            alpha=float(office.daily_loss_rate),
            T=planning_horizon_days,
        )

        # Create optimization request record
        planning_horizon_end = planning_horizon_start + timedelta(days=planning_horizon_days - 1)
        optimization_request = OptimizationRequest(
            office_id=office_id,
            planning_horizon_start=planning_horizon_start,
            planning_horizon_end=planning_horizon_end,
            initial_inventory=initial_inventory,
            is_correction_mode=is_correction_mode,
        )

        # Run solver
        start_time = time.perf_counter()
        try:
            result: SolverOutput = solve(solver_input)
            solve_time_ms = int((time.perf_counter() - start_time) * 1000)

            optimization_request.solver_status = "OPTIMAL"
            optimization_request.total_cost = Decimal(str(result.objective_value))
            optimization_request.solve_time_ms = solve_time_ms

        except SolverFail as e:
            solve_time_ms = int((time.perf_counter() - start_time) * 1000)
            optimization_request.solver_status = str(e)
            optimization_request.solve_time_ms = solve_time_ms

            # Save failed request
            await self.optimization_repo.create(optimization_request)
            return optimization_request

        # Save optimization request
        optimization_request = await self.optimization_repo.create(optimization_request)

        # Create orders from solver results
        await self._create_orders_from_result(
            optimization_request=optimization_request,
            office_id=office_id,
            planning_horizon_start=planning_horizon_start,
            result=result,
            purchase_costs_daily=purchase_costs_daily,
            transport_cost=transport_cost,
        )

        # Create inventory snapshots
        await self._create_inventory_snapshots(
            optimization_request=optimization_request,
            office_id=office_id,
            planning_horizon_start=planning_horizon_start,
            result=result,
            demands=demands,
            alpha=float(office.daily_loss_rate),
        )

        return optimization_request

    async def _create_orders_from_result(
        self,
        optimization_request: OptimizationRequest,
        office_id: int,
        planning_horizon_start: date,
        result: SolverOutput,
        purchase_costs_daily: list[float],
        transport_cost: float,
    ) -> list[Order]:
        """Create orders from solver result."""
        orders = []
        for day_idx, (order_amount, is_order) in enumerate(zip(result.x, result.y)):
            if is_order and order_amount > 0:
                order_date = planning_horizon_start + timedelta(days=day_idx)
                unit_price = Decimal(str(purchase_costs_daily[day_idx]))
                quantity = Decimal(str(order_amount))
                transport = Decimal(str(transport_cost))
                total_cost = (quantity * unit_price) + transport

                order = Order(
                    optimization_request_id=optimization_request.id,
                    office_id=office_id,
                    order_date=order_date,
                    delivery_date=order_date,  # Same day delivery for basic model
                    quantity_kg=quantity,
                    unit_price=unit_price,
                    transport_cost=transport,
                    total_cost=total_cost,
                    status="planned",
                )
                orders.append(order)
                self.session.add(order)

        await self.session.commit()
        return orders

    async def _create_inventory_snapshots(
        self,
        optimization_request: OptimizationRequest,
        office_id: int,
        planning_horizon_start: date,
        result: SolverOutput,
        demands: list[float],
        alpha: float,
    ) -> list[InventorySnapshot]:
        """Create inventory snapshots from solver result."""
        snapshots = []
        for day_idx, inventory_level in enumerate(result.I):
            snapshot_date = planning_horizon_start + timedelta(days=day_idx)

            # Calculate loss (approximation)
            if day_idx == 0:
                prev_inventory = float(optimization_request.initial_inventory)
            else:
                prev_inventory = result.I[day_idx - 1]
            loss = prev_inventory * alpha

            delivery = result.x[day_idx] if result.y[day_idx] else 0.0

            snapshot = InventorySnapshot(
                office_id=office_id,
                optimization_request_id=optimization_request.id,
                date=snapshot_date,
                inventory_level=Decimal(str(inventory_level)),
                demand_fulfilled=Decimal(str(demands[day_idx])),
                loss_amount=Decimal(str(loss)),
                deliveries_received=Decimal(str(delivery)),
                is_projected=True,
            )
            snapshots.append(snapshot)

        return await self.inventory_repo.bulk_create(snapshots)
