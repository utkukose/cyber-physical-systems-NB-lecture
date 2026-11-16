"""Simulates a first-order control loop with network delay, sampling and packet loss, and computes its delay margin.

Week: 8
Inputs: the constants a and b of dx/dt = -a x - b x(t - tau) - d, the delay tau, the sampling period, the loss rate.
Outputs: the trajectory of the loop, its outcome (settled, growing or tripped) and the delay margin.
Example: python networked_loop_sim.py
The delay margin tau* = arccos(-a/b) / sqrt(b^2 - a^2) holds for b > |a| (Hayes, 1950). The default constants are
those of the frequency loop of the campus microgrid: M = 80 kW s/Hz, D = 12 kW/Hz and K = 125 kW/Hz.
Requires NumPy.
"""
import math

import numpy as np


def delay_margin(a: float, b: float) -> float:
    if b <= abs(a):
        return math.inf
    return math.acos(-a / b) / math.sqrt(b * b - a * a)


def simulate(a, b, tau, d=0.0, step_at=1.0, T=30.0, dt=0.005, Ts=0.0, loss=0.0, seed=1, trip=None):
    """Euler steps of x' = -a x - b u + d(t). The controller samples x every Ts seconds (hold in between), the sample
    reaches the actuator after tau seconds, and each sample is lost with probability loss (the last one is kept)."""
    rng = np.random.default_rng(seed)
    n, lag = int(T / dt), int(round(tau / dt))
    x, u_seen = np.zeros(n), np.zeros(n)
    held, next_sample = 0.0, 0.0
    for k in range(1, n):
        t = k * dt
        if t >= next_sample:
            if rng.random() >= loss:
                held = x[k - 1]
            next_sample += Ts if Ts > 0 else dt
        u_seen[k] = held
        u = u_seen[k - lag] if k - lag >= 0 else 0.0
        dist = d if t >= step_at else 0.0
        x[k] = x[k - 1] + dt * (-a * x[k - 1] - b * u - dist)
        if trip is not None and abs(x[k]) > trip:
            return np.arange(k + 1) * dt, x[:k + 1], "tripped"
    tt = np.arange(n) * dt
    final = -d / (a + b)
    early = np.abs(x[(tt >= T / 3) & (tt < 2 * T / 3)] - final).max()
    late = np.abs(x[tt >= 2 * T / 3] - final).max()
    return tt, x, "settled" if late < early else "growing"


if __name__ == "__main__":
    M, D, K = 80.0, 12.0, 125.0
    a, b = D / M, K / M
    print(f"delay margin: {delay_margin(a, b):.3f} s")
    for tau, Ts, loss in [(0.4, 0.0, 0.0), (1.0, 0.0, 0.0), (1.1, 0.0, 0.0), (0.3, 0.2, 0.0), (0.3, 0.2, 0.3)]:
        _, x, out = simulate(a, b, tau, d=66 / M, Ts=Ts, loss=loss, trip=2.5)
        print(f"tau {tau:.2f} s, Ts {Ts:.1f} s, loss {loss:.1f}: lowest {x.min():.3f} Hz -> {out}")
