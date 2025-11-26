Sets:
$$
T = \{1,2,\dots,7\}
$$

Parameters:
$$
V_{\max} \text{ -- maximum warehouse capacity (kg)}
$$
$$
P_t \text{ -- cost of purchasing coffee on day } t \text{ (PLN/kg)}
$$
$$
C \text{ -- transportation cost (PLN) if an order is placed}
$$
$$
D_t \text{ -- daily coffee demand (kg)}
$$
$$
I_0 \text{ -- initial warehouse stock (kg)}
$$
$$
\alpha = 0.1 \text{ -- percentage of coffee lost each day}
$$

Decision variables:
$$
x_t \text{ -- amount of coffee ordered on day } t \text{ (kg)}
$$
$$
I_t \text{ -- warehouse stock at the end of day } t \text{ (kg)}
$$
$$
y_t \in \{0,1\} \text{ -- binary variable (1 = order placed, 0 = no order)}
$$

Objective function:
$$
\min \sum_{t \in T} \left( P_t \, x_t + C \, y_t \right)
$$

Constraints – inventory balance:
$$
I_1 = (1 - \alpha) I_0 + x_1 - D_1
$$
$$
I_t = (1 - \alpha) I_{t-1} + x_t - D_t \quad \forall\, t \in T,\ t > 1
$$

Warehouse capacity:
$$
I_t \leq V_{\max} \quad \forall\, t \in T
$$

Linking orders with transportation cost (big-M):
$$
x_t \leq M \, y_t \quad \forall\, t \in T
$$

Nonnegativity and binarity:
$$
x_t \geq 0 \quad \forall\, t \in T
$$
$$
I_t \geq 0 \quad \forall\, t \in T
$$
$$
y_t \in \{0,1\} \quad \forall\, t \in T
$$
