from typing import Dict, List, NamedTuple
import random

from fastapi import logger

from api_models import DayPrediction
from docplex.mp.model import Model


def generate_mock_predictions(max_capacity: int, conferences_per_week: int, normal_workers_daily: int) -> list[DayPrediction]:
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
        
        predictions.append(DayPrediction(
            day=day,
            orderAmount=order_amount,
            consumedAmount=daily_consumption,
            remainingAmount=cumulative_remaining,
            unit="grams"
        ))
    
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
    P: List[float]
    C: float
    D: List[float]
    I0: float
    alpha: float = 0.1
    M: float = 1e5
    T: int = 7

class SolverOutput(NamedTuple):
    """Decision variables (solution) for the planning horizon T.

    - x — amount ordered each day t (kg)
    - I — inventory at the end of each day t (kg)
    - y — binary order indicators for each day t (0/1)
    - objective_value — objective function value for the solution
    """
    x: List[float]
    I: List[float]
    y: List[int]
    objective_value: float


class SolverFail(RuntimeError): ...


def solve(inp: SolverInput) -> SolverOutput:
    """Build and solve the inventory/ordering MIP using docplex.

    Returns a `SolverOutput` with arrays of length T or raises SolverFail on error.
    """
    # basic validation
    T = int(inp.T)
    if len(inp.P) != T or len(inp.D) != T:
        raise ValueError(f"Length of P and D must equal T={T}. Got len(P)={len(inp.P)}, len(D)={len(inp.D)}")

    m = Model(name="coffee_inventory")

    # decision variables indexed 0..T-1 (maps to days 1..T)
    x = m.continuous_var_list(T, lb=0.0, name="x")
    I = m.continuous_var_list(T, lb=0.0, name="I")
    y = m.binary_var_list(T, name="y")

    # objective: minimize sum(P_t * x_t + C * y_t)
    m.minimize(m.sum(inp.P[t] * x[t] for t in range(T)) + inp.C * m.sum(y))

    # inventory balance constraints
    # I1 = (1-alpha) I0 + x1 - D1  -> index 0
    m.add_constraint(I[0] == (1 - inp.alpha) * inp.I0 + x[0] - inp.D[0])

    for t in range(1, T):
        m.add_constraint(I[t] == (1 - inp.alpha) * I[t - 1] + x[t] - inp.D[t])

    # capacity constraints
    for t in range(T):
        m.add_constraint(I[t] <= inp.V_max)

    # linking orders (big-M)
    for t in range(T):
        m.add_constraint(x[t] <= inp.M * y[t])

    # solve
    sol = m.solve()
    if sol is None:
        # try to provide solver feedback
        status = m.get_solve_status()
        raise SolverFail(f"Solver failed to return a solution. Status: {status}")

    # extract solution values
    x_vals = [float(x[t].solution_value) for t in range(T)]
    I_vals = [float(I[t].solution_value) for t in range(T)]
    y_vals = [int(round(y[t].solution_value)) for t in range(T)]
    obj = float(m.objective_value)

    return SolverOutput(x=x_vals, I=I_vals, y=y_vals, objective_value=obj)
