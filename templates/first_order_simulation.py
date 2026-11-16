"""Simulates any model dx/dt = f(t, x, u) with the methods of Euler, Heun and Runge-Kutta, and compares them with an
exact solution.

Week: 2
Inputs: a right-hand side f(t, x), an initial state, a step size and an end time; optionally an exact solution.
Outputs: the trajectories of the three methods and their largest errors.
Example: python first_order_simulation.py
The example is the cabinet of an inverter that warms from 25 toward 45 deg C with a time constant of 20 min; the
Euler method diverges for steps above twice the time constant. Requires NumPy.
"""
import math

import numpy as np


def simulate(f, x0, dt, t_end, method="rk4"):
    n = int(round(t_end / dt))
    t = np.arange(n + 1) * dt
    x = np.empty((n + 1,) + np.shape(x0))
    x[0] = x0
    for k in range(n):
        tk, xk = t[k], x[k]
        if method == "euler":
            x[k + 1] = xk + dt * f(tk, xk)
        elif method == "heun":
            k1 = f(tk, xk)
            k2 = f(tk + dt, xk + dt * k1)
            x[k + 1] = xk + dt * (k1 + k2) / 2
        else:
            k1 = f(tk, xk)
            k2 = f(tk + dt / 2, xk + dt / 2 * k1)
            k3 = f(tk + dt / 2, xk + dt / 2 * k2)
            k4 = f(tk + dt, xk + dt * k3)
            x[k + 1] = xk + dt * (k1 + 2 * k2 + 2 * k3 + k4) / 6
    return t, x


if __name__ == "__main__":
    tau, x_ss, x0 = 20.0, 45.0, 25.0
    f = lambda t, x: (x_ss - x) / tau
    exact = lambda t: x_ss + (x0 - x_ss) * np.exp(-t / tau)
    for dt in (5.0, 20.0, 45.0):
        print(f"step {dt:>4} min:", end="")
        for m in ("euler", "heun", "rk4"):
            t, x = simulate(f, x0, dt, 90, m)
            print(f"  {m} max error {np.max(np.abs(x - exact(t))):9.3f} C", end="")
        print()
    print("exact at 20 min:", round(float(exact(20.0)), 2), "C; e^-1 =", round(math.exp(-1), 4))
