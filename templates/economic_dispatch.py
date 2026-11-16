"""The economic dispatch of generating units with quadratic costs and limits, by bisection on the incremental cost,
with the price of each hour that follows from it.

Week: 9
Inputs: for each unit the cost b P + c P^2 in currency units per hour (P in MW) and the limits of P; the demand of each
hour in MW; for the price, a fixed charge per kWh that is added to the incremental cost.
Outputs: the incremental cost lambda in currency units per MWh, the output of each unit and the total cost of each hour,
and the price of each hour per kWh.
Example: python economic_dispatch.py
The example is the regional grid of the campus with a base, a middle and a peak unit and the demand of a spring weekday;
the price of the campus is 0.10 per kWh plus lambda / 1000. Requires NumPy.
"""
import numpy as np

B = np.array([20.0, 35.0, 60.0])          # linear cost coefficient (per MWh)
C = np.array([0.02, 0.025, 0.25])         # quadratic cost coefficient (per MW^2 h)
P_MIN = np.array([100.0, 0.0, 0.0])       # MW
P_MAX = np.array([600.0, 500.0, 300.0])   # MW


def outputs(lam):
    """The output of each unit at the incremental cost lam, within its limits."""
    return np.clip((lam - B) / (2 * C), P_MIN, P_MAX)


def dispatch(demand, tol=1e-7):
    """Bisection on lam until the outputs add up to the demand; raises an error if the units cannot meet it."""
    if not P_MIN.sum() <= demand <= P_MAX.sum():
        raise ValueError(f"the units cover {P_MIN.sum():.0f} to {P_MAX.sum():.0f} MW, not {demand} MW")
    lo, hi = 0.0, float(np.max(B + 2 * C * P_MAX)) + 1.0
    while hi - lo > tol:
        lam = (lo + hi) / 2
        if outputs(lam).sum() < demand:
            lo = lam
        else:
            hi = lam
    lam = (lo + hi) / 2
    P = outputs(lam)
    return lam, P, float(np.sum(B * P + C * P ** 2))


if __name__ == "__main__":
    demand = [600, 570, 550, 545, 550, 580, 680, 820, 950, 1020, 1050, 1060,
              1040, 1030, 1020, 1010, 1040, 1120, 1220, 1260, 1200, 1050, 850, 700]
    print("hour  demand   lambda   base  middle   peak      cost   price of the campus")
    for hour, D in enumerate(demand):
        lam, P, cost = dispatch(D)
        print(f"{hour:4d} {D:7.0f} {lam:8.2f} {P[0]:6.1f} {P[1]:7.1f} {P[2]:6.1f} {cost:9.0f}   {0.10 + lam / 1000:.4f} per kWh")
