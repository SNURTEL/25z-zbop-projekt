import matplotlib.pyplot as plt

# =====================
# Dane cenowe
# =====================

# Dystrybutory
D = ["D1","D2"]
# Dni (przyszłość)
T = [1,2,3,4,5]
# Progi rabatowe
L = [1,2,3]

# Ceny (P[d,t,l])
P = {
    "D1": {
        1: {1:12.5, 2:11.5, 3:10.8},
        2: {1:12.4, 2:11.4, 3:10.7},
        3: {1:12.6, 2:11.6, 3:10.9},
        4: {1:12.7, 2:11.7, 3:11.0},
        5: {1:12.8, 2:11.8, 3:11.1},
    },
    "D2": {
        1: {1:12.0, 2:11.0, 3:10.4},
        2: {1:11.9, 2:10.9, 3:10.3},
        3: {1:12.1, 2:11.1, 3:10.5},
        4: {1:12.2, 2:11.2, 3:10.6},
        5: {1:12.3, 2:11.3, 3:10.7},
    }
}

# =====================
# Wykresy
# =====================

for d in D:
    plt.figure(figsize=(8,5))
    for t in T:
        # ceny dla danego dnia w zależności od progu
        y = [P[d][t][l] for l in L]
        plt.plot(L, y, marker='o', label=f"Day {t}")
    plt.title(f"Cena jednostkowa vs próg rabatowy dla dystrybutora {d}")
    plt.xlabel("Poziom rabatu (L)")
    plt.ylabel("Cena jednostkowa [zł/kg]")
    plt.xticks(L)
    plt.grid(True)
    plt.legend()
    plt.show()
