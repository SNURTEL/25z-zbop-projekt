import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

sns.set(style="whitegrid")

# =====================
# DANE
# =====================
B = ["B1","B2","B3"]
D = ["D1","D2"]
T = list(range(1,8))
Thist = [-3,-2,-1,0]
L = [1,2,3]

I0 = {"B1":25, "B2":15, "B3":10}

Demand = {
    "B1":[18,14,16,15,17,18,19],
    "B2":[10,12,11,13,12,14,13],
    "B3":[8,9,10,9,11,10,12]
}

S = {
    "D1":[90]*7,
    "D2":[70]*7
}

x0_data = [
    ("D1","B1",-3,1,10), ("D1","B1",-3,2,0), ("D1","B1",-3,3,0),
    ("D1","B1",-2,1,15), ("D1","B1",-2,2,0), ("D1","B1",-2,3,0),
    ("D1","B1",-1,1,0), ("D1","B1",-1,2,20), ("D1","B1",-1,3,0),
    ("D1","B1",0,1,0), ("D1","B1",0,2,0), ("D1","B1",0,3,0),

    ("D1","B2",-3,1,0), ("D1","B2",-3,2,0), ("D1","B2",-3,3,0),
    ("D1","B2",-2,1,30), ("D1","B2",-2,2,0), ("D1","B2",-2,3,0),
    ("D1","B2",-1,1,0), ("D1","B2",-1,2,0), ("D1","B2",-1,3,0),
    ("D1","B2",0,1,0), ("D1","B2",0,2,0), ("D1","B2",0,3,0),

    ("D2","B3",-3,1,5), ("D2","B3",-3,2,0), ("D2","B3",-3,3,0),
    ("D2","B3",-2,1,25), ("D2","B3",-2,2,0), ("D2","B3",-2,3,0),
    ("D2","B3",-1,1,0), ("D2","B3",-1,2,0), ("D2","B3",-1,3,0),
    ("D2","B3",0,1,0), ("D2","B3",0,2,0), ("D2","B3",0,3,0)
]

x0_df = pd.DataFrame(x0_data, columns=["D","B","t","l","qty"])

# =====================
# HEATMAPY 2D
# =====================

# 1. Demand (B x T)
demand_df = pd.DataFrame(Demand, index=T).T  # Biuro x Dni
plt.figure(figsize=(10,4))
sns.heatmap(demand_df, annot=True, fmt="d", cmap="YlGnBu")
plt.title("Zapotrzebowanie dzienne [kg]")
plt.xlabel("Dzień")
plt.ylabel("Biurowiec")
plt.show()

# 2. Initial inventories (B)
plt.figure(figsize=(6,2))
sns.heatmap(pd.DataFrame(I0.values(), index=I0.keys(), columns=["I0"]), annot=True, fmt="d", cmap="YlOrRd")
plt.title("Stan początkowy magazynu [kg]")
plt.show()

# 3. Supplier availability (D x T)
s_df = pd.DataFrame(S, index=T).T
plt.figure(figsize=(10,3))
sns.heatmap(s_df, annot=True, fmt="d", cmap="BuPu")
plt.title("Dostępność u dystrybutorów [kg]")
plt.xlabel("Dzień")
plt.ylabel("Dystrybutor")
plt.show()

# 4. Historical orders x0 (D x B x Thist x L)
# agregacja sumy po poziomie rabatu L, żeby 2D było czytelne
x0_sum = x0_df.groupby(["D","B","t"])["qty"].sum().reset_index()
x0_pivot = x0_sum.pivot(index="B", columns="t", values="qty")
plt.figure(figsize=(8,4))
sns.heatmap(x0_pivot, annot=True, fmt="d", cmap="Greens")
plt.title("Historyczne zamówienia x0 (sumowane po poziomie rabatu) [kg]")
plt.xlabel("Dzień historyczny")
plt.ylabel("Biurowiec")
plt.show()
