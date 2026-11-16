"""The remaining useful life (RUL) of a battery from its capacity tests: A least-squares fit of calendar and cycle
ageing, 1 - Q/Q0 = a sqrt(t) + b N, the end of life from a quadratic equation in sqrt(t), a Monte Carlo distribution of
the end of life from the uncertainty of the fit and the latest safe order of spare parts.

Week: 13
Inputs: a file of comma-separated values with the columns years (age at the test), efc (equivalent full cycles up to the
test) and capacity_kwh, one row per test; the rated capacity Q0 (kWh); the cycles per day from now on; the share of the
capacity lost at the end of life (0.2 for 80 percent); the lead time of the spare parts (months) and the required
probability that they arrive in time.
Outputs: a and b with their standard errors and their correlation, the root mean square error (RMSE) of the fit in kWh,
the end of life and the RUL in years, the 5, 50 and 95 percent quantiles of the end of life over 2000 futures, and the
latest month after the last test to order the spare parts.
Example: python remaining_useful_life.py [tests.csv] [cycles_per_day]
Without a file, the example builds 36 monthly tests of a battery of 500 kWh that makes about one cycle per day. Requires
NumPy.
"""
import csv
import math
import sys

import numpy as np

Q0 = 500.0          # rated capacity (kWh)
LIMIT = 0.2         # share of the capacity lost at the end of life
LEAD_MONTHS = 6     # lead time of the spare parts
LEVEL = 0.95        # required probability that the spare parts arrive in time


def example_tests(seed=13, months=36, a_true=0.025, b_true=0.00004):
    """Monthly capacity tests of a battery with more cycles in summer and a noise of 1.5 kWh."""
    rng = np.random.default_rng(seed)
    rows, cycles = [], 0.0
    for m in range(months):
        per_day = (1.0 + 0.2 * math.sin(2 * math.pi * (m - 3) / 12)) * (0.92 + 0.16 * rng.random())
        cycles += per_day * 365.25 / 12
        years = (m + 1) / 12
        capacity = Q0 * (1 - a_true * math.sqrt(years) - b_true * cycles) + 1.5 * rng.normal()
        rows.append((years, round(cycles, 1), round(capacity, 1)))
    return {c: np.array(v) for c, v in zip(("years", "efc", "capacity_kwh"), zip(*rows))}


def load_tests(path):
    """Reads the capacity tests from a file of comma-separated values."""
    with open(path, newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    return {c: np.array([float(r[c]) for r in rows]) for c in ("years", "efc", "capacity_kwh")}


def fit_ageing(tests):
    """Least squares of 1 - Q/Q0 = a sqrt(t) + b N. Returns a, b, their covariance and the RMSE in kWh."""
    X = np.column_stack([np.sqrt(tests["years"]), tests["efc"]])
    y = 1 - tests["capacity_kwh"] / Q0
    (a, b), *_ = np.linalg.lstsq(X, y, rcond=None)
    resid = y - X @ np.array([a, b])
    s2 = resid @ resid / (len(y) - 2)                # variance of the residuals
    cov = s2 * np.linalg.inv(X.T @ X)
    return float(a), float(b), cov, float(np.sqrt(np.mean(resid ** 2)) * Q0)


def end_of_life(a, b, per_day, t_now, n_now, limit=LIMIT):
    """Years from the commissioning until a sqrt(t) + b N(t) reaches the limit, with N(t) = n_now + 365.25 per_day
    (t - t_now). The equation is quadratic in x = sqrt(t): k x^2 + a x + c0 = 0."""
    k = b * 365.25 * per_day
    c0 = b * (n_now - 365.25 * per_day * t_now) - limit
    if abs(k) < 1e-15:
        return (-c0 / a) ** 2 if a > 0 else math.inf
    disc = a * a - 4 * k * c0
    if disc < 0:
        return math.inf
    x = (-a + math.sqrt(disc)) / (2 * k)
    return x * x if x > 0 else math.inf


def futures(a, b, cov, per_day, t_now, n_now, n=2000, seed=77):
    """The end of life for n parameter pairs drawn from the uncertainty of the fit with the Cholesky factor of the
    covariance."""
    L = np.linalg.cholesky(cov)
    z = np.random.default_rng(seed).standard_normal((n, 2))
    pairs = np.array([a, b]) + z @ L.T
    return np.array([end_of_life(ai, bi, per_day, t_now, n_now) for ai, bi in pairs])


def latest_order(ends, t_now, lead_months=LEAD_MONTHS, level=LEVEL):
    """The latest month after now to order spare parts that arrive before the end of life with the given probability,
    and that probability. Returns None when even an order today is too late."""
    best = None
    for months in range(0, 241):
        p = float(np.mean(ends > t_now + (months + lead_months) / 12))
        if p >= level:
            best = (months, p)
    return best


def main():
    tests = load_tests(sys.argv[1]) if len(sys.argv) > 1 else example_tests()
    per_day = float(sys.argv[2]) if len(sys.argv) > 2 else 1.0
    t_now, n_now = float(tests["years"][-1]), float(tests["efc"][-1])
    a, b, cov, rmse = fit_ageing(tests)
    se_a, se_b = np.sqrt(np.diag(cov))
    print(f"{len(tests['years'])} tests, the last after {t_now:.2f} years and {n_now:.1f} cycles: "
          f"{tests['capacity_kwh'][-1]:.1f} kWh")
    print(f"a = {a:.5f} ± {se_a:.5f} per square root of a year, b = {b:.3e} ± {se_b:.1e} per cycle, "
          f"correlation {cov[0, 1] / (se_a * se_b):.3f}, RMSE {rmse:.2f} kWh")
    eol = end_of_life(a, b, per_day, t_now, n_now)
    print(f"{per_day} cycles per day from now on: end of life after {eol:.2f} years, RUL {eol - t_now:.2f} years")
    ends = futures(a, b, cov, per_day, t_now, n_now)
    p5, p50, p95 = np.percentile(ends, [5, 50, 95])
    print(f"2000 futures: 5 percent {p5:.2f}, median {p50:.2f}, 95 percent {p95:.2f} years")
    order = latest_order(ends, t_now)
    if order is None:
        print(f"even an order today arrives in time with a probability below {LEVEL}")
    else:
        print(f"latest order: within {order[0]} months, P(in time) = {order[1]:.3f} "
              f"with a lead time of {LEAD_MONTHS} months")


if __name__ == "__main__":
    main()
