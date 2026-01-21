"""
Advanced coffee inventory optimization model with order correction capability.

Extends solver_v2 by allowing modifications to previously planned orders
using correction variables r+ (increase) and r- (decrease).

Based on Section 2 of model_final.tex: "Model matematyczny w wersji zaawansowanej z korektą"
"""

from typing import NamedTuple

from docplex.mp.model import Model  # type: ignore[import-untyped]


class SolverInputV2Correction(NamedTuple):
    """
    Parameters for the advanced coffee ordering optimization model with correction.

    Sets:
        T: Planning horizon (number of days)
        D: Number of distributors
        B: Number of buildings
        L: Number of discount threshold levels

    Base Parameters (same as SolverInputV2):
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
        x_hist: Historical orders in transit, dict: (d,b,tau) -> amount [kg]

    Correction Parameters:
        x_kor_0: Previously planned orders below threshold, dict: (d,b,t) -> amount [kg]
        x_kor: Previously planned orders at threshold level l, dict: (d,b,t,l) -> amount [kg]
        K: Correction cost per unit change [PLN/kg], shape (D, B, T)
        R_max: Maximum allowed correction per order [kg], shape (D, B, T)
    """

    T: int  # Planning horizon length
    D: int  # Number of distributors
    B: int  # Number of buildings
    L: int  # Number of discount levels

    # Base parameters
    V_max: list[float]  # shape (B,)
    Q: list[float]  # shape (L+1,)
    P_0: list[list[float]]  # shape (D, T)
    P: list[list[list[float]]]  # shape (D, T, L)
    C_fix: list[list[float]]  # shape (D, B)
    Demand: list[list[float]]  # shape (B, T)
    I_0: list[float]  # shape (B,)
    alpha: float
    S: list[list[float]]  # shape (D, T)
    X: list[list[int]]  # shape (D, B)
    x_hist: dict[tuple[int, int, int], float]  # (d, b, tau) -> amount

    # Correction parameters
    x_kor_0: dict[tuple[int, int, int], float]  # (d, b, t) -> amount below threshold
    x_kor: dict[tuple[int, int, int, int], float]  # (d, b, t, l) -> amount at threshold l
    K: list[list[list[float]]]  # shape (D, B, T) - correction cost per unit
    R_max: list[list[list[float]]]  # shape (D, B, T) - max correction allowed


class SolverOutputV2Correction(NamedTuple):
    """
    Solution for the advanced coffee ordering model with correction.

    Variables:
        x_0: Final amount below threshold [kg], dict: (d, b, t) -> amount
        x: Final amount at threshold level l [kg], dict: (d, b, t, l) -> amount
        r_plus_0: Increase to order below threshold [kg], dict: (d, b, t) -> amount
        r_minus_0: Decrease to order below threshold [kg], dict: (d, b, t) -> amount
        r_plus: Increase to order at threshold l [kg], dict: (d, b, t, l) -> amount
        r_minus: Decrease to order at threshold l [kg], dict: (d, b, t, l) -> amount
        I: Inventory at building b at end of day t [kg], dict: (b, t) -> amount
        y_order: Binary indicator if order placed, dict: (d, b, t) -> {0, 1}
        y_threshold: Binary indicator if threshold l reached, dict: (d, b, t, l) -> {0, 1}
        objective_value: Total cost [PLN]
        correction_cost: Total correction cost [PLN]
    """

    x_0: dict[tuple[int, int, int], float]
    x: dict[tuple[int, int, int, int], float]
    r_plus_0: dict[tuple[int, int, int], float]
    r_minus_0: dict[tuple[int, int, int], float]
    r_plus: dict[tuple[int, int, int, int], float]
    r_minus: dict[tuple[int, int, int, int], float]
    I: dict[tuple[int, int], float]
    y_order: dict[tuple[int, int, int], int]
    y_threshold: dict[tuple[int, int, int, int], int]
    objective_value: float
    correction_cost: float


class SolverFail(RuntimeError):
    """Raised when the solver fails to find a solution."""

    pass


def solve(inp: SolverInputV2Correction) -> SolverOutputV2Correction:
    """
    Build and solve the advanced coffee ordering MIP model with correction capability.

    The model allows modifying previously planned orders (x_kor) by:
    - r_plus: increasing the order amount
    - r_minus: decreasing the order amount

    Subject to correction costs (K per unit changed) and limits (R_max).

    Returns SolverOutputV2Correction with the optimal solution or raises SolverFail on error.
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
    assert len(inp.K) == D and all(len(inp.K[d]) == B for d in range(D))
    assert all(len(inp.K[d][b]) == T for d in range(D) for b in range(B))
    assert len(inp.R_max) == D and all(len(inp.R_max[d]) == B for d in range(D))
    assert all(len(inp.R_max[d][b]) == T for d in range(D) for b in range(B))

    m = Model(name="coffee_inventory_v2_correction")

    # Decision variables

    # x_{d,b,t,0} - final amount ordered below first threshold
    x_0 = {}
    for d in range(D):
        for b in range(B):
            for t in range(T):
                x_0[d, b, t] = m.continuous_var(lb=0, name=f"x_below_d{d}_b{b}_t{t}")

    # x_{d,b,t,l} - final amount ordered at threshold level l
    x = {}
    for d in range(D):
        for b in range(B):
            for t in range(T):
                for l in range(1, L + 1):
                    x[d, b, t, l] = m.continuous_var(lb=0, name=f"x_above_d{d}_b{b}_t{t}_l{l}")

    # r+_{d,b,t,0} - increase to order below threshold
    r_plus_0 = {}
    for d in range(D):
        for b in range(B):
            for t in range(T):
                r_plus_0[d, b, t] = m.continuous_var(lb=0, name=f"r_plus_0_d{d}_b{b}_t{t}")

    # r-_{d,b,t,0} - decrease to order below threshold
    r_minus_0 = {}
    for d in range(D):
        for b in range(B):
            for t in range(T):
                r_minus_0[d, b, t] = m.continuous_var(lb=0, name=f"r_minus_0_d{d}_b{b}_t{t}")

    # r+_{d,b,t,l} - increase to order at threshold level l
    r_plus = {}
    for d in range(D):
        for b in range(B):
            for t in range(T):
                for l in range(1, L + 1):
                    r_plus[d, b, t, l] = m.continuous_var(lb=0, name=f"r_plus_d{d}_b{b}_t{t}_l{l}")

    # r-_{d,b,t,l} - decrease to order at threshold level l
    r_minus = {}
    for d in range(D):
        for b in range(B):
            for t in range(T):
                for l in range(1, L + 1):
                    r_minus[d, b, t, l] = m.continuous_var(lb=0, name=f"r_minus_d{d}_b{b}_t{t}_l{l}")

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

    # Objective function: minimize total cost including correction costs
    # Cost = purchase cost + fixed delivery cost + correction costs

    purchase_cost = m.sum(inp.P_0[d][t] * x_0[d, b, t] for d in range(D) for b in range(B) for t in range(T))

    threshold_cost = m.sum(
        inp.P[d][t][l - 1] * x[d, b, t, l]
        for d in range(D)
        for b in range(B)
        for t in range(T)
        for l in range(1, L + 1)
    )

    fixed_cost = m.sum(inp.C_fix[d][b] * y_order[d, b, t] for d in range(D) for b in range(B) for t in range(T))

    # Correction cost for below-threshold orders
    correction_cost_0 = m.sum(
        inp.K[d][b][t] * (r_plus_0[d, b, t] + r_minus_0[d, b, t]) for d in range(D) for b in range(B) for t in range(T)
    )

    # Correction cost for threshold-level orders
    correction_cost_l = m.sum(
        inp.K[d][b][t] * (r_plus[d, b, t, l] + r_minus[d, b, t, l])
        for d in range(D)
        for b in range(B)
        for t in range(T)
        for l in range(1, L + 1)
    )

    m.minimize(purchase_cost + threshold_cost + fixed_cost + correction_cost_0 + correction_cost_l)

    # Constraints

    # NEW: Link x to x_kor via correction variables
    # x_{d,b,t,0} = x^{kor}_{d,b,t,0} + r+_{d,b,t,0} - r-_{d,b,t,0}
    for d in range(D):
        for b in range(B):
            for t in range(T):
                x_kor_0_val = inp.x_kor_0.get((d, b, t), 0.0)
                m.add_constraint(x_0[d, b, t] == x_kor_0_val + r_plus_0[d, b, t] - r_minus_0[d, b, t])

    # x_{d,b,t,l} = x^{kor}_{d,b,t,l} + r+_{d,b,t,l} - r-_{d,b,t,l}
    for d in range(D):
        for b in range(B):
            for t in range(T):
                for l in range(1, L + 1):
                    x_kor_val = inp.x_kor.get((d, b, t, l), 0.0)
                    m.add_constraint(x[d, b, t, l] == x_kor_val + r_plus[d, b, t, l] - r_minus[d, b, t, l])

    # NEW: Maximum correction constraint
    # sum_l(r+_{d,b,t,l} + r-_{d,b,t,l}) + r+_{d,b,t,0} + r-_{d,b,t,0} <= R^max_{d,b,t}
    for d in range(D):
        for b in range(B):
            for t in range(T):
                total_correction = r_plus_0[d, b, t] + r_minus_0[d, b, t]
                total_correction += m.sum(r_plus[d, b, t, l] + r_minus[d, b, t, l] for l in range(1, L + 1))
                m.add_constraint(total_correction <= inp.R_max[d][b][t])

    # Inventory balance with delivery times and historical orders
    for b in range(B):
        for t in range(T):
            # Deliveries arriving on day t (ordered at tau where tau + X[d][b] = t)
            deliveries_today = m.sum(x_0[d, b, tau] for d in range(D) for tau in range(T) if tau + inp.X[d][b] == t)

            deliveries_today += m.sum(
                x[d, b, tau, l] for d in range(D) for tau in range(T) for l in range(1, L + 1) if tau + inp.X[d][b] == t
            )

            # Historical orders arriving today
            hist_deliveries_today = sum(
                inp.x_hist.get((d, b, tau), 0.0) for d in range(D) for tau in range(-100, 0) if tau + inp.X[d][b] == t
            )

            if t == 0:
                m.add_constraint(
                    I[b, t]
                    == (1 - inp.alpha) * inp.I_0[b] + deliveries_today + hist_deliveries_today - inp.Demand[b][t]
                )
            else:
                m.add_constraint(
                    I[b, t]
                    == (1 - inp.alpha) * I[b, t - 1] + deliveries_today + hist_deliveries_today - inp.Demand[b][t]
                )

    # Warehouse capacity constraints
    for b in range(B):
        for t in range(T):
            m.add_constraint(I[b, t] <= inp.V_max[b])

    # Link order amount to binary order indicator
    for d in range(D):
        for b in range(B):
            for t in range(T):
                m.add_constraint(x_0[d, b, t] <= inp.S[d][t] * y_order[d, b, t])

    # Distributor supply limit
    for d in range(D):
        for t in range(T):
            total_ordered = m.sum(x_0[d, b, t] for b in range(B))
            total_ordered += m.sum(x[d, b, t, l] for b in range(B) for l in range(1, L + 1))
            m.add_constraint(total_ordered <= inp.S[d][t])

    # Threshold constraints
    for d in range(D):
        for b in range(B):
            for t in range(T):
                # Link threshold variables to order variable
                for l in range(1, L + 1):
                    m.add_constraint(y_threshold[d, b, t, l] <= y_order[d, b, t])

                # x_0 is limited by first threshold Q[1]
                m.add_constraint(x_0[d, b, t] <= inp.Q[1])

                # For intermediate thresholds l=1..L-1
                for l in range(1, L):
                    m.add_constraint(x[d, b, t, l] <= (inp.Q[l + 1] - inp.Q[l]) * y_threshold[d, b, t, l])

                # For the last threshold L
                S_max = max(inp.S[d][t] for d in range(D) for t in range(T))
                m.add_constraint(x[d, b, t, L] <= S_max * y_threshold[d, b, t, L])

                # Threshold activation constraints
                m.add_constraint(x_0[d, b, t] >= inp.Q[1] * y_threshold[d, b, t, 1])

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

    r_plus_0_vals = {
        (d, b, t): float(r_plus_0[d, b, t].solution_value) for d in range(D) for b in range(B) for t in range(T)
    }

    r_minus_0_vals = {
        (d, b, t): float(r_minus_0[d, b, t].solution_value) for d in range(D) for b in range(B) for t in range(T)
    }

    r_plus_vals = {
        (d, b, t, l): float(r_plus[d, b, t, l].solution_value)
        for d in range(D)
        for b in range(B)
        for t in range(T)
        for l in range(1, L + 1)
    }

    r_minus_vals = {
        (d, b, t, l): float(r_minus[d, b, t, l].solution_value)
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

    # Calculate total correction cost
    total_correction_cost = sum(
        inp.K[d][b][t] * (r_plus_0_vals[d, b, t] + r_minus_0_vals[d, b, t])
        for d in range(D)
        for b in range(B)
        for t in range(T)
    )
    total_correction_cost += sum(
        inp.K[d][b][t] * (r_plus_vals[d, b, t, l] + r_minus_vals[d, b, t, l])
        for d in range(D)
        for b in range(B)
        for t in range(T)
        for l in range(1, L + 1)
    )

    return SolverOutputV2Correction(
        x_0=x_0_vals,
        x=x_vals,
        r_plus_0=r_plus_0_vals,
        r_minus_0=r_minus_0_vals,
        r_plus=r_plus_vals,
        r_minus=r_minus_vals,
        I=I_vals,
        y_order=y_order_vals,
        y_threshold=y_threshold_vals,
        objective_value=obj,
        correction_cost=total_correction_cost,
    )
