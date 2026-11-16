"""Metrics of a step response, the stability limit of the integral gain by the Routh-Hurwitz criterion and the
settings of Ziegler and Nichols.

Week: 5
Inputs: a sampled response with its time step and its tolerance band; the inertia, the damping, the lag of the actuator
and the gains of a loop of the form M tau s^3 + (M + D tau + Kd) s^2 + (D + Kp) s + Ki; an ultimate gain and period.
Outputs: the nadir, the overshoot, the settling time and the final value; the limit of Ki with the frequency of the
oscillation at the limit; the gains of P, PI and PID controllers by Ziegler and Nichols.
Example: python loop_tuning.py
The example is the island of the campus with M = 80 kW s/Hz, D = 12 kW/Hz and an inverter lag of 0.2 s. Requires
NumPy.
"""
import math

import numpy as np


def step_metrics(y, dt, band, target=0.0):
    """Nadir (first dip), overshoot above the target, settling time within the band and the final value."""
    y = np.asarray(y, float)
    dips = np.where((y[1:-1] < y[:-2]) & (y[1:-1] <= y[2:]))[0] + 1
    outside = np.where(np.abs(y - target) > band)[0]
    settle = float((outside[-1] + 1) * dt) if len(outside) else 0.0
    if abs(y[-1] - target) > band:
        settle = None
    return {"nadir": float(y[dips[0]]) if len(dips) else float(y.min()), "overshoot": max(0.0, float(y.max() - target)),
            "settle": settle, "final": float(y[-1])}


def ki_limit(M, D, tau, kp, kd=0.0):
    """The largest stable Ki for a3 s^3 + a2 s^2 + a1 s + Ki with a3 = M tau, a2 = M + D tau + Kd, a1 = D + Kp."""
    a3, a2, a1 = M * tau, M + D * tau + kd, D + kp
    return a2 * a1 / a3, math.sqrt(a1 / a3)


def ziegler_nichols(ku, tu):
    """Gains (Kp, Ki, Kd) of P, PI and PID controllers from the ultimate gain ku and the ultimate period tu."""
    out = {"P": (0.5 * ku, 0.0, 0.0)}
    kp = 0.45 * ku
    out["PI"] = (kp, kp / (tu / 1.2), 0.0)
    kp = 0.6 * ku
    out["PID"] = (kp, kp / (tu / 2), kp * tu / 8)
    return out


if __name__ == "__main__":
    for kd in [0.0, 20.0, 40.0]:
        lim, w = ki_limit(80.0, 12.0, 0.2, 125.0, kd)
        print(f"Kd = {kd:4.0f}: limit Ki* = {lim:8.2f} kW/(Hz s), oscillation {w:.3f} rad/s, period {2 * math.pi / w:.3f} s")
    t = np.arange(0, 20, 0.01)
    y = -0.4 * np.exp(-t / 1.5) * np.sin(1.2 * t + 0.6) / math.sin(0.6)
    print("metrics of a test response:", {k: (None if v is None else round(v, 3)) for k, v in step_metrics(y, 0.01, 0.02).items()})
    # the ultimate gain and period of a P controller on the island with a pure delay of 0.2 s instead of the lag
    for name, (kp, ki, kd) in ziegler_nichols(ku=636.0, tu=0.79).items():
        print(f"Ziegler-Nichols {name:>3}: Kp = {kp:6.1f}, Ki = {ki:7.1f}, Kd = {kd:5.1f}")
