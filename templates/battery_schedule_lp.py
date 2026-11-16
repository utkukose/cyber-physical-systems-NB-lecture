"""The daily schedule of a battery and of flexible loads as a linear program with SciPy: the cheapest charging and
discharging for hourly prices, an export price, a peak charge and loads that must receive their energy within a window.

Week: 9
Inputs: the hourly import without the battery (kW), the hourly price, the price of an export, the peak charge per kW,
the battery (capacity, limits of the stored energy, power, efficiency, initial energy) and, optionally, flexible loads
as (name, first hour, end hour, energy in kWh, power limit in kW).
Outputs: the cost of the day, the power of the battery, the import, the stored energy, the peak and the power of each
flexible load in every hour.
Example: python battery_schedule_lp.py
The example is the clear day of the campus with its battery of 500 kWh and 250 kW, the prices of the regional dispatch
and three cars that can charge late. Requires NumPy and SciPy.
"""
import numpy as np
from scipy.optimize import linprog


def schedule(net, price, s_export=0.05, k_peak=0.30, e_cap=(50.0, 450.0), p_bat=250.0, eta=0.95, e0=250.0,
             import_max=600.0, loads=()):
    """Variables per hour: charge c, discharge d, import g, export x, stored energy e; then the peak G; then the loads."""
    T = len(net)
    lv = [(k, t) for k, (_, a, b, _, _) in enumerate(loads) for t in range(a, b)]
    n = 5 * T + 1 + len(lv)
    C, D, Gr, X, E, PK = 0, T, 2 * T, 3 * T, 4 * T, 5 * T
    cost = np.zeros(n)
    cost[Gr:Gr + T], cost[X:X + T], cost[PK] = price, -s_export, k_peak
    A_eq, b_eq, A_ub, b_ub = [], [], [], []
    for t in range(T):
        row = np.zeros(n)
        row[[Gr + t, X + t, C + t, D + t]] = [1, -1, -1, 1]
        row[[PK + 1 + j for j, (k, h) in enumerate(lv) if h == t]] = -1
        A_eq.append(row)
        b_eq.append(net[t])
        row = np.zeros(n)
        row[[E + t, C + t, D + t]] = [1, -eta, 1 / eta]
        if t > 0:
            row[E + t - 1] = -1
        A_eq.append(row)
        b_eq.append(e0 if t == 0 else 0.0)
        row = np.zeros(n)
        row[[Gr + t, PK]] = [1, -1]
        A_ub.append(row)
        b_ub.append(0.0)
    for k, (_, a, b, energy, _) in enumerate(loads):
        row = np.zeros(n)
        row[[PK + 1 + j for j, (kk, h) in enumerate(lv) if kk == k]] = 1
        A_eq.append(row)
        b_eq.append(energy)
    row = np.zeros(n)
    row[E + T - 1] = -1
    A_ub.append(row)
    b_ub.append(-e0)
    bounds = ([(0, p_bat)] * 2 * T + [(0, import_max)] * T + [(0, None)] * T + [e_cap] * T + [(0, None)]
              + [(0, loads[k][4]) for k, _ in lv])
    res = linprog(cost, A_ub=np.array(A_ub), b_ub=b_ub, A_eq=np.array(A_eq), b_eq=b_eq, bounds=bounds, method="highs")
    if res.status != 0:
        raise RuntimeError("no schedule meets all constraints: " + res.message)
    x = res.x
    per_load = np.zeros((len(loads), T))
    for j, (k, t) in enumerate(lv):
        per_load[k, t] = x[PK + 1 + j]
    return dict(cost=res.fun, battery_kw=x[D:D + T] - x[C:C + T], grid_kw=x[Gr:Gr + T] - x[X:X + T],
                energy_kwh=x[E:E + T], peak_kw=x[PK], loads_kw=per_load)


if __name__ == "__main__":
    net = np.array([196.2, 183.7, 172.9, 176.7, 191.5, 223.6, 250.4, 294.6, 359.0, 352.4, 304.5, 259.6,
                    233.7, 246.9, 281.7, 341.7, 411.8, 502.9, 580.5, 585.7, 489.9, 401.7, 295.3, 233.6])
    price = np.array([0.14, 0.1393, 0.1389, 0.1388, 0.1389, 0.1396, 0.1418, 0.146, 0.1525, 0.156, 0.1575, 0.158,
                      0.157, 0.1565, 0.156, 0.1555, 0.157, 0.17, 0.22, 0.24, 0.21, 0.1575, 0.1475, 0.1422])
    late_cars = [("F", 16, 24, 88.0, 22.0), ("G", 17, 24, 88.0, 22.0), ("J", 17, 24, 110.0, 22.0)]
    at_once = np.zeros(24)               # the import above holds these three cars charging at once
    for _, a, b, energy, p in late_cars:
        left, t = energy, a
        while left > 1e-9:
            at_once[t] += min(p, left)
            left -= min(p, left)
            t += 1
    plain = schedule(net, price, p_bat=0.0)
    battery = schedule(net, price)
    best = schedule(net - at_once, price, loads=late_cars)
    print(f"no battery: {plain['cost']:.2f} | optimal battery: {battery['cost']:.2f} | "
          f"optimal battery and late cars: {best['cost']:.2f}")
    print("battery (kW):", np.round(best["battery_kw"], 1))
    print("peak import:", round(best["peak_kw"], 1), "kW")
