"""
Advanced coffee inventory optimization model with multiple distributors,
buildings, delivery times, and volume-based pricing tiers.

Based on the mathematical model described in main.tex.
"""

from typing import NamedTuple

from docplex.mp.model import Model  # type: ignore[import-untyped]


class SolverInputV2(NamedTuple):
    """
    Parameters for the advanced coffee ordering optimization model.

    Sets:
        T: Planning horizon (list of days, e.g., [1,2,...,7])
        D: Number of distributors
        B: Number of buildings
        L: Number of discount threshold levels

    Parameters:
        V_max: Maximum warehouse capacity for each building b [kg], shape (B,)
        Q: Discount thresholds [kg], shape (L+1,) where Q[0]=0, Q[1]=first threshold, etc.
        P_0: Unit price from distributor d on day t below threshold [PLN/kg], shape (D, T)
        P: Unit price from distributor d on day t at threshold level l [PLN/kg], shape (D, T, L)
        C_fix: Fixed delivery cost from distributor d to building b [PLN], shape (D, B)
        Demand: Demand at building b on day t [kg], shape (B, T)
        I_0: Initial inventory at building b [kg], shape (B,)
        alpha: Daily loss rate (fraction, e.g., 0.1 for 10%)
        S: Supply limit for distributor d on day t [kg], shape (D, T)
        X: Delivery time from distributor d to building b [days], shape (D, B)
        x_hist: Historical orders in transit, dict: (d,b,tau,l) -> amount [kg]
                tau is negative for historical days (e.g., -1, -2, ...)
    """

    T: int  # Planning horizon length
    D: int  # Number of distributors
    B: int  # Number of buildings
    L: int  # Number of discount levels

    V_max: list[float]  # shape (B,)
    Q: list[float]  # shape (L+1,) - Q[0]=0, Q[1]=first threshold, ..., Q[L]=last threshold
    P_0: list[list[float]]  # shape (D, T) - price below first threshold
    P: list[list[list[float]]]  # shape (D, T, L) - price at each threshold level
    C_fix: list[list[float]]  # shape (D, B)
    Demand: list[list[float]]  # shape (B, T)
    I_0: list[float]  # shape (B,)
    alpha: float
    S: list[list[float]]  # shape (D, T)
    X: list[list[int]]  # shape (D, B) - delivery time in days
    x_hist: dict[tuple[int, int, int, int], float]  # (d, b, tau, l) -> amount


class SolverOutputV2(NamedTuple):
    """
    Solution for the advanced coffee ordering model.

    Variables:
        x_0: Amount ordered from distributor d to building b on day t below threshold [kg],
             dict: (d, b, t) -> amount
        x: Amount ordered from distributor d to building b on day t at threshold level l [kg],
           dict: (d, b, t, l) -> amount
        I: Inventory at building b at end of day t [kg], dict: (b, t) -> amount
        y_order: Binary indicator if order placed from distributor d to building b on day t,
                 dict: (d, b, t) -> {0, 1}
        y_threshold: Binary indicator if threshold l reached for order d->b on day t,
                     dict: (d, b, t, l) -> {0, 1}
        objective_value: Total cost [PLN]
    """

    x_0: dict[tuple[int, int, int], float]
    x: dict[tuple[int, int, int, int], float]
    I: dict[tuple[int, int], float]
    y_order: dict[tuple[int, int, int], int]
    y_threshold: dict[tuple[int, int, int, int], int]
    objective_value: float


class SolverFail(RuntimeError):
    """Raised when the solver fails to find a solution."""

    pass


def solve(inp: SolverInputV2) -> SolverOutputV2:
    """
    Build and solve the advanced coffee ordering MIP model.

    Returns SolverOutputV2 with the optimal solution or raises SolverFail on error.
    """
    T, D, B, L = inp.T, inp.D, inp.B, inp.L

    # Validation
    assert len(inp.V_max) == B
    assert len(inp.Q) == L + 1
    assert len(inp.P_0) == D and all(len(inp.P_0[d]) == T for d in range(D))
    assert len(inp.P) == D and all(len(inp.P[d]) == T for d in range(D))
    assert all(len(inp.P[d][t]) == L for d in range(D) for t in range(T))
    assert len(inp.C_fix) == D and all(len(inp.C_fix[d]) == B for d in range(D))
    assert len(inp.Demand) == B and all(len(inp.Demand[b]) == T for b in range(B))
    assert len(inp.I_0) == B
    assert len(inp.S) == D and all(len(inp.S[d]) == T for d in range(D))
    assert len(inp.X) == D and all(len(inp.X[d]) == B for d in range(D))

    m = Model(name="coffee_inventory_v2")

    # Decision variables
    # x_{d,b,t,0} - amount ordered below first threshold
    x_0 = {}
    for d in range(D):
        for b in range(B):
            for t in range(T):
                x_0[d, b, t] = m.continuous_var(lb=0, name=f"x_below_d{d}_b{b}_t{t}")

    # x_{d,b,t,l} - amount ordered at threshold level l
    x = {}
    for d in range(D):
        for b in range(B):
            for t in range(T):
                for l in range(1, L + 1):
                    x[d, b, t, l] = m.continuous_var(lb=0, name=f"x_d{d}_b{b}_t{t}_l{l}")

    # I_{b,t} - inventory at building b at end of day t
    I = {}
    for b in range(B):
        for t in range(T):
            I[b, t] = m.continuous_var(lb=0, name=f"inv_b{b}_t{t}")

    # y^{order}_{d,b,t} - binary indicator if order placed
    y_order = {}
    for d in range(D):
        for b in range(B):
            for t in range(T):
                y_order[d, b, t] = m.binary_var(name=f"y_order_d{d}_b{b}_t{t}")

    # y^{threshold}_{d,b,t,l} - binary indicator if threshold l reached
    y_threshold = {}
    for d in range(D):
        for b in range(B):
            for t in range(T):
                for l in range(1, L + 1):
                    y_threshold[d, b, t, l] = m.binary_var(name=f"y_thresh_d{d}_b{b}_t{t}_l{l}")

    # Objective function: minimize total cost
    # Cost = purchase cost + fixed delivery cost
    purchase_cost = m.sum(inp.P_0[d][t] * x_0[d, b, t] for d in range(D) for b in range(B) for t in range(T))

    threshold_cost = m.sum(
        inp.P[d][t][l - 1] * x[d, b, t, l]
        for d in range(D)
        for b in range(B)
        for t in range(T)
        for l in range(1, L + 1)
    )

    fixed_cost = m.sum(inp.C_fix[d][b] * y_order[d, b, t] for d in range(D) for b in range(B) for t in range(T))

    m.minimize(purchase_cost + threshold_cost + fixed_cost)

    # Constraints

    # 1. Inventory balance with delivery times and historical orders
    for b in range(B):
        for t in range(T):
            # Deliveries arriving on day t (ordered at tau where tau + X[d][b] = t)
            deliveries_today = m.sum(x_0[d, b, tau] for d in range(D) for tau in range(T) if tau + inp.X[d][b] == t)

            deliveries_today += m.sum(
                x[d, b, tau, l] for d in range(D) for tau in range(T) for l in range(1, L + 1) if tau + inp.X[d][b] == t
            )

            # Historical orders arriving today
            hist_deliveries_today = sum(
                inp.x_hist.get((d, b, tau, l), 0.0)
                for d in range(D)
                for l in range(1, L + 1)
                for tau in range(-100, 0)  # Check historical days
                if tau + inp.X[d][b] == t
            )

            if t == 0:
                # First day: I[b,0] = (1-alpha)*I_0[b] + deliveries - demand
                m.add_constraint(
                    I[b, t]
                    == (1 - inp.alpha) * inp.I_0[b] + deliveries_today + hist_deliveries_today - inp.Demand[b][t]
                )
            else:
                # Other days: I[b,t] = (1-alpha)*I[b,t-1] + deliveries - demand
                m.add_constraint(
                    I[b, t]
                    == (1 - inp.alpha) * I[b, t - 1] + deliveries_today + hist_deliveries_today - inp.Demand[b][t]
                )

    # 2. Warehouse capacity constraints
    for b in range(B):
        for t in range(T):
            m.add_constraint(I[b, t] <= inp.V_max[b])

    # 3. Link order amount to binary order indicator
    for d in range(D):
        for b in range(B):
            for t in range(T):
                m.add_constraint(x_0[d, b, t] <= inp.S[d][t] * y_order[d, b, t])

    # 4. Distributor supply limit
    for d in range(D):
        for t in range(T):
            total_ordered = m.sum(x_0[d, b, t] for b in range(B))
            total_ordered += m.sum(x[d, b, t, l] for b in range(B) for l in range(1, L + 1))
            m.add_constraint(total_ordered <= inp.S[d][t])

    # 5. Threshold constraints
    # For each (d, b, t), the total order is partitioned across thresholds

    for d in range(D):
        for b in range(B):
            for t in range(T):
                # Link threshold variables to order variable
                # Threshold variables can only be active if an order is placed
                for l in range(1, L + 1):
                    m.add_constraint(y_threshold[d, b, t, l] <= y_order[d, b, t])

                # x_0 is limited by first threshold Q[1]
                m.add_constraint(x_0[d, b, t] <= inp.Q[1])

                # For intermediate thresholds l=1..L-1
                for l in range(1, L):
                    # x[l] can be at most (Q[l+1] - Q[l])
                    m.add_constraint(x[d, b, t, l] <= (inp.Q[l + 1] - inp.Q[l]) * y_threshold[d, b, t, l])

                # For the last threshold L
                # x[L] can be at most S_max (large enough value)
                S_max = max(inp.S[d][t] for d in range(D) for t in range(T))
                m.add_constraint(x[d, b, t, L] <= S_max * y_threshold[d, b, t, L])

                # Threshold activation constraints
                # If threshold l+1 is active, threshold l must be full
                # x_0 >= Q[1] * y_threshold[1]
                m.add_constraint(x_0[d, b, t] >= inp.Q[1] * y_threshold[d, b, t, 1])

                # For l=1..L-1: x[l] >= (Q[l+1] - Q[l]) * y_threshold[l+1]
                for l in range(1, L):
                    m.add_constraint(x[d, b, t, l] >= (inp.Q[l + 1] - inp.Q[l]) * y_threshold[d, b, t, l + 1])

    # Solve
    sol = m.solve()

    if sol is None:
        status = m.get_solve_status()
        raise SolverFail(f"Solver failed to return a solution. Status: {status}")

    # Extract solution
    x_0_vals = {(d, b, t): float(x_0[d, b, t].solution_value) for d in range(D) for b in range(B) for t in range(T)}

    x_vals = {
        (d, b, t, l): float(x[d, b, t, l].solution_value)
        for d in range(D)
        for b in range(B)
        for t in range(T)
        for l in range(1, L + 1)
    }

    I_vals = {(b, t): float(I[b, t].solution_value) for b in range(B) for t in range(T)}

    y_order_vals = {
        (d, b, t): int(round(y_order[d, b, t].solution_value)) for d in range(D) for b in range(B) for t in range(T)
    }

    y_threshold_vals = {
        (d, b, t, l): int(round(y_threshold[d, b, t, l].solution_value))
        for d in range(D)
        for b in range(B)
        for t in range(T)
        for l in range(1, L + 1)
    }

    obj = float(m.objective_value)

    return SolverOutputV2(
        x_0=x_0_vals, x=x_vals, I=I_vals, y_order=y_order_vals, y_threshold=y_threshold_vals, objective_value=obj
    )
