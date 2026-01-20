from amplpy import AMPL

def main():
    ampl = AMPL()

    # (opcjonalnie) ustaw solver
    # dostępne np.: highs, cbc, gurobi, cplex
    ampl.setOption("solver", "highs")

    # wczytanie modelu i danych
    ampl.read("model.mod")
    ampl.readData("data.dat")

    # rozwiązanie modelu
    ampl.solve()

    # status
    print("Status:", ampl.getValue("solve_result"))
    print("Objective value:", ampl.getObjective("TotalCost").value())

    # ===== WYŚWIETLANIE WYNIKÓW =====
    print("\nZamówienia x[d,b,t,l]:")
    x = ampl.getVariable("x").getValues()
    print(x)

    print("\nStany magazynu I[b,t]:")
    I = ampl.getVariable("I").getValues()
    print(I)

    print("\nCzy złożono zamówienie y_order[d,b,t]:")
    y_order = ampl.getVariable("y_order").getValues()
    print(y_order)

    print("\nWybrany próg rabatowy y_disc[d,b,t,l]:")
    y_disc = ampl.getVariable("y_disc").getValues()
    print(y_disc)


if __name__ == "__main__":
    main()
