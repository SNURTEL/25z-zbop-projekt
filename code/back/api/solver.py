import json
import random
from typing import NamedTuple, TypedDict

from docplex.mp.model import Model  # type: ignore[import-untyped]
from fastapi import logger

from api_models import DayPrediction, DayPredictionV2, PredictionRequest2


def generate_mock_predictions(
    max_capacity: int, conferences_per_week: int, normal_workers_daily: int
) -> list[DayPrediction]:
    """
    Mock function to generate coffee consumption predictions for 7 days.
    This should be replaced with actual prediction logic later.
    """
    predictions = []
    cumulative_remaining = max_capacity

    # Basic mock logic - adjust consumption based on parameters
    base_consumption_per_worker = 25  # grams per worker per day
    conference_multiplier = 1.5 if conferences_per_week > 3 else 1.2

    for day in range(1, 8):  # 7 days
        # Mock daily consumption calculation
        daily_consumption = int(normal_workers_daily * base_consumption_per_worker)

        # Add some randomness and conference effect
        if day <= conferences_per_week:
            daily_consumption = int(daily_consumption * conference_multiplier)

        # Add some random variation (±20%)
        variation = random.uniform(0.8, 1.2)
        daily_consumption = int(daily_consumption * variation)

        # Mock order amount (refill when running low)
        order_amount = 0
        if cumulative_remaining < max_capacity * 0.3:  # Refill when below 30%
            order_amount = max_capacity
            cumulative_remaining += order_amount

        # Calculate remaining amount
        cumulative_remaining = max(0, cumulative_remaining - daily_consumption)

        predictions.append(
            DayPrediction(
                day=day,
                orderAmount=order_amount,
                consumedAmount=daily_consumption,
                remainingAmount=cumulative_remaining,
                unit="grams",
            )
        )

    logger.logger.info("Generated mock predictions: %s", predictions)

    return predictions


class SolverInput(NamedTuple):
    """Model parameters for the 7-day inventory/ordering problem.

    - V_max — maximum warehouse capacity (kg)
    - P — purchasing cost for each day t (PLN/kg), list length T
    - C — transportation cost if an order is placed (PLN)
    - D — daily demand for each day t (kg), list length T
    - I0 — initial warehouse stock (kg)
    - alpha — daily loss fraction (e.g. 0.1 for 10%)
    - M — big-M constant for linking x_t <= M * y_t
    - T — planning horizon (number of days), default 7
    """

    V_max: float
    P: list[float]
    C: float
    D: list[float]
    I0: float
    alpha: float = 0.1
    M: float = 1e5
    T: int = 7


class SolverOutput(TypedDict):
    """Decision variables (solution) for the planning horizon T.

    - x — amount ordered each day t (kg)
    - I — inventory at the end of each day t (kg)
    - y — binary order indicators for each day t (0/1)
    - objective_value — objective function value for the solution
    """

    x: list[float]
    I: list[float]  # noqa: E741
    y: list[int]
    objective_value: float


class SolverFail(RuntimeError): ...


def solve(inp: SolverInput) -> SolverOutput:
    """Build and solve the inventory/ordering MIP.

    Returns a `SolverOutput` with arrays of length T or raises SolverFail on error.
    """
    T = int(inp.T)
    if len(inp.P) != T or len(inp.D) != T:
        raise ValueError(f"Length of P and D must equal T={T}. Got len(P)={len(inp.P)}, len(D)={len(inp.D)}")

    m = Model(name="coffee_inventory")

    # decision variables indexed 0..T-1
    x = m.continuous_var_list(T, lb=0.0, name="x")
    I = m.continuous_var_list(T, lb=0.0, name="I")  # noqa: E741
    y = m.binary_var_list(T, name="y")

    # minimize sum(P_t * x_t + C * y_t)
    m.minimize(m.sum(inp.P[t] * x[t] for t in range(T)) + inp.C * m.sum(y))

    # I1 = (1-alpha) I0 + x1 - D1
    m.add_constraint(I[0] == (1 - inp.alpha) * inp.I0 + x[0] - inp.D[0])

    # It = (1-alpha) I(t-1) + x_t - D_t for t=2..T
    for t in range(1, T):
        m.add_constraint(I[t] == (1 - inp.alpha) * I[t - 1] + x[t] - inp.D[t])

    # I_t <= V_max
    for t in range(T):
        m.add_constraint(I[t] <= inp.V_max)

    # x_t <= M * y_t
    for t in range(T):
        m.add_constraint(x[t] <= inp.M * y[t])

    sol = m.solve()
    if sol is None:
        status = m.get_solve_status()
        raise SolverFail(f"Solver failed to return a solution. Status: {status}")

    x_vals = [float(x[t].solution_value) for t in range(T)]
    I_vals = [float(I[t].solution_value) for t in range(T)]
    y_vals = [int(round(y[t].solution_value)) for t in range(T)]
    obj = float(m.objective_value)

    return SolverOutput(x=x_vals, I=I_vals, y=y_vals, objective_value=obj)


def estimate_demand(num_workers: int, num_conferences: int) -> float:
    # dummy demand estimation logic
    base_demand_per_worker_kg = 0.25  # kg per worker per day
    conference_multiplier = 1.2**num_conferences
    estimated_demand = num_workers * base_demand_per_worker_kg * conference_multiplier
    return estimated_demand


def generate_predictions(prediction_request: PredictionRequest2) -> list[DayPredictionV2]:
    """Generate coffee consumption predictions using the solver.

    Args:
        prediction_request: PredictionRequest2 containing model parameters.

    Returns:
        List of DayPrediction with consumption, orders, and remaining amounts.
    """
    T = prediction_request.planning_horizon_days
    demand_estimates = [
        estimate_demand(prediction_request.num_workers_daily[t], prediction_request.num_conferences_daily[t])
        for t in range(T)
    ]

    solver_input = SolverInput(
        V_max=prediction_request.storage_capacity_kg,
        P=prediction_request.purchase_costs_pln_per_kg_daily,
        C=prediction_request.transport_cost_pln,
        D=demand_estimates,
        I0=prediction_request.initial_inventory_kg,
        alpha=prediction_request.daily_loss_fraction,
        T=T,
    )

    try:
        solver_output = solve(solver_input)
        logger.logger.warning("Solver output: %s", json.dumps(solver_output, indent=4))
    except SolverFail as e:
        logger.logger.error("Solver failed: %s", e)
        raise

    predictions = []

    for day in range(T):
        order_amount = solver_output["x"][day]
        consumed_amount = demand_estimates[day]

        predictions.append(
            DayPredictionV2(
                day=day + 1,
                orderAmount=round(order_amount, 2),
                consumedAmount=round(consumed_amount, 2),
                remainingAmount=round(solver_output["I"][day], 2),
                unit="kg",
            )
        )

    logger.logger.info("Generated predictions: %s", predictions)

    return predictions
