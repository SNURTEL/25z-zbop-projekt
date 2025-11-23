from docplex.mp.model import Model
from typing import List, Dict, Optional


def solve(
    purchase_costs: List[float],
    daily_demands: List[float],
    V_max: float = 1000.0,
    C: float = 50.0,
    I_0: float = 200.0,
    alpha: float = 0.1
) -> Optional[Dict]:
    """
    Solve the coffee inventory optimization problem.
    
    Parameters:
    -----------
    purchase_costs : List[float]
        Purchase cost per day (zł/kg) for each day
    daily_demands : List[float]
        Daily demand (kg) for each day
    V_max : float, optional
        Maximum warehouse capacity (kg), default 1000.0
    C : float, optional
        Transport cost (zł) if order is placed, default 50.0
    I_0 : float, optional
        Initial warehouse state (kg), default 200.0
    alpha : float, optional
        Coffee loss rate per day (0.1 = 10%), default 0.1
    
    Returns:
    --------
    Dict or None
        Dictionary with solution details if found, None otherwise
        Contains: total_cost, orders, inventory, transport_days, purchase_cost, transport_cost
    """
    
    # Validate input
    if len(purchase_costs) != len(daily_demands):
        raise ValueError("purchase_costs and daily_demands must have the same length")
    
    n = len(purchase_costs)
    days = range(1, n + 1)
    
    # Big M for linking order quantity with binary variable
    M = V_max
    
    # Create a CPLEX model
    model = Model(name='coffee_inventory_optimization')
    
    # Decision variables
    x = model.continuous_var_list(days, lb=0, name='x')  # Order quantity on day t (kg)
    I = model.continuous_var_list(days, lb=0, name='I')  # Inventory at end of day t (kg)
    y = model.binary_var_list(days, name='y')  # Binary: 1 if order placed, 0 otherwise
    
    # Objective function: minimize total cost (purchase + transport)
    total_cost = model.sum(purchase_costs[t-1] * x[t-1] + C * y[t-1] for t in days)
    model.minimize(total_cost)
    
    # Constraints
    for t in days:
        if t == 1:
            # Day 1: I_1 = (1 - alpha) * I_0 + x_1 - D_1
            model.add_constraint(
                I[0] == (1 - alpha) * I_0 + x[0] - daily_demands[0],
                ctname='inventory_day_1'
            )
        else:
            # Days 2-n: I_t = (1 - alpha) * I_{t-1} + x_t - D_t
            model.add_constraint(
                I[t-1] == (1 - alpha) * I[t-2] + x[t-1] - daily_demands[t-1],
                ctname=f'inventory_day_{t}'
            )
        
        # Warehouse capacity constraint: I_t ≤ V_max
        model.add_constraint(
            I[t-1] <= V_max,
            ctname=f'capacity_day_{t}'
        )
        
        # Link order quantity with transport cost: x_t ≤ M * y_t
        model.add_constraint(
            x[t-1] <= M * y[t-1],
            ctname=f'link_order_transport_{t}'
        )
    
    # Solve the model
    solution = model.solve()
    
    if solution:
        # Extract solution
        order_values = []
        inventory_values = []
        transport_days = []
        transport_cost = 0
        purchase_cost = 0
        
        for t in days:
            x_val = solution.get_value(x[t-1])
            y_val = solution.get_value(y[t-1])
            I_val = solution.get_value(I[t-1])
            
            order_values.append(x_val)
            inventory_values.append(I_val)
            
            if y_val > 0.5:  # Binary variable is 1
                transport_days.append(t)
                transport_cost += C
            purchase_cost += purchase_costs[t-1] * x_val
        
        return {
            'total_cost': solution.get_objective_value(),
            'orders': order_values,
            'inventory': inventory_values,
            'transport_days': transport_days,
            'purchase_cost': purchase_cost,
            'transport_cost': transport_cost
        }
    else:
        return None


if __name__ == '__main__':
    # Example usage
    P = [757, 757, 757, 757, 757, 757, 757]  # Purchase cost per day (zł/kg)
    D = [10, 12, 11, 9, 13, 10, 11]  # Daily demand (kg)
    
    result = solve(P, D)
    
    if result:
        print(f"Total cost: {result['total_cost']:.2f} zł")
        print(f"\nOrder schedule:")
        for t, (order, inventory) in enumerate(zip(result['orders'], result['inventory']), 1):
            transport = "Yes" if t in result['transport_days'] else "No"
            print(f"Day {t}: Order {order:.2f} kg, Inventory at end: {inventory:.2f} kg, Transport: {transport}")
        
        print(f"\nTotal purchase cost: {result['purchase_cost']:.2f} zł")
        print(f"Total transport cost: {result['transport_cost']:.2f} zł")
        print(f"\nOrder array: {[round(v, 2) for v in result['orders']]}")
    else:
        print("No solution found")