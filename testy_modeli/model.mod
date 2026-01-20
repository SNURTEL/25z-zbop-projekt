# =========================
# SETS
# =========================
set T ordered;
set Thist ordered;
set D;
set B;
set L ordered;

# =========================
# PARAMETERS
# =========================
param Vmax {B} >= 0;
param Q {L} >= 0;
param P {D, T, L} >= 0;
param Cfix {D, B} >= 0;
param Demand {B, T} >= 0;
param I0 {B} >= 0;
param alpha >= 0, <= 1;
param S {D, T} >= 0;
param Smax >= 0;
param LeadTime {D, B} integer >= 0;

param x0 {D, B, Thist, L} >= 0 default 0;

# =========================
# VARIABLES
# =========================
var x {D, B, T, L} >= 0;
var I {B, T} >= 0;
var y_order {D, B, T} binary;
var y_disc {D, B, T, L} binary;

# =========================
# AUXILIARY
# =========================
var xsum {d in D, b in B, t in T} =
    sum {l in L} x[d,b,t,l];

# =========================
# OBJECTIVE
# =========================
minimize TotalCost:
    sum {t in T, b in B, d in D, l in L} P[d,t,l] * x[d,b,t,l]
  + sum {t in T, b in B, d in D} Cfix[d,b] * y_order[d,b,t];

# =========================
# CONSTRAINTS
# =========================

subject to InventoryBalance {b in B, t in T}:
    I[b,t] =
        (if ord(t) = 1 then (1-alpha)*I0[b]
         else (1-alpha)*I[b, prev(t)])
      + sum {d in D, l in L}
            ( sum {tau in T: tau + LeadTime[d,b] = t}
                  x[d,b,tau,l]
            + sum {tau in Thist: tau + LeadTime[d,b] = t}
                  x0[d,b,tau,l] )
      - Demand[b,t];

subject to Capacity {b in B, t in T}:
    I[b,t] <= Vmax[b];

subject to OrderLink {d in D, b in B, t in T}:
    sum {l in L} x[d,b,t,l] <= S[d,t] * y_order[d,b,t];

subject to SupplierLimit {d in D, t in T}:
    sum {b in B, l in L} x[d,b,t,l] <= S[d,t];

subject to DiscountChoice {d in D, b in B, t in T}:
    sum {l in L} y_disc[d,b,t,l] = y_order[d,b,t];

subject to ThresholdLow
{d in D, b in B, t in T, l in L: ord(l) < card(L)}:
    Q[l] * y_disc[d,b,t,l] <= x[d,b,t,l];

subject to ThresholdHigh
{d in D, b in B, t in T, l in L: ord(l) < card(L)}:
    x[d,b,t,l] <= Q[next(l)] * y_disc[d,b,t,l];

subject to ThresholdLastLow {d in D, b in B, t in T}:
    Q[last(L)] * y_disc[d,b,t,last(L)] <= x[d,b,t,last(L)];

subject to ThresholdLastHigh {d in D, b in B, t in T}:
    x[d,b,t,last(L)] <= Smax * y_disc[d,b,t,last(L)];
