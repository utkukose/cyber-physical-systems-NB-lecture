"""A discrete PID controller with output limits, an anti-windup and a filtered derivative, written as a closure, and a
test on the island of the campus microgrid.

Week: 5
Inputs: the gains kp, ki and kd, the sampling period ts in seconds, the limit of the output, the window of the moving
average and the distance of the difference for the derivative, in samples.
Outputs: a function pid(error) that returns the limited command at each call; the example prints the nadir and the
settling time of the island after a load step.
Example: python pid_controller.py
The example is the battery of the campus with Kp = 125 kW/Hz, Ki = 60 kW/(Hz s), Kd = 40 kW s/Hz and a limit of
250 kW, called 100 times a second. Requires NumPy.
"""
from collections import deque

import numpy as np


def make_pid(kp, ki, kd, ts, u_max, window=7, span=10):
    """A PID controller called every ts seconds; the derivative uses a moving average of `window` errors and their
    difference over `span` samples, and the integral stops while the output is beyond its limit (anti-windup)."""
    integral = 0.0
    recent, history = deque(maxlen=window), deque(maxlen=span + 1)

    def pid(error):
        nonlocal integral
        recent.append(error)
        history.append(sum(recent) / len(recent))
        derivative = (history[-1] - history[0]) / (ts * (len(history) - 1)) if len(history) > 1 else 0.0
        u = kp * error + integral + kd * derivative
        if not (abs(u) > u_max and error * u > 0):
            integral += ki * ts * error
        return min(u_max, max(-u_max, u))
    return pid


def island(pid, step_kw, T=30.0, dt=0.002, ts=0.01, M=80.0, D=12.0, tau_a=0.2, noise=0.0, seed=1):
    """The island of the campus with an inverter of time constant tau_a; the controller sees the frequency every ts
    seconds, with an optional noise in Hz."""
    rng = np.random.default_rng(seed)
    f, pb, u, trace = 0.0, 0.0, 0.0, []
    every = int(round(ts / dt))
    for k in range(int(T / dt)):
        if k % every == 0:
            u = pid(-(f + noise * rng.normal()))
        pb += dt * (u - pb) / tau_a
        f += dt * (pb - step_kw - D * f) / M
        trace.append(f)
    return np.array(trace)


if __name__ == "__main__":
    for kd, noise in [(0.0, 0.0), (40.0, 0.0), (40.0, 0.025)]:
        pid = make_pid(125.0, 60.0, kd, 0.01, 250.0)
        F = island(pid, 66.0, noise=noise)
        outside = np.where(np.abs(F) > 0.02)[0]
        print(f"Kd = {kd:4.0f}, noise {1000 * noise:4.0f} mHz: nadir {F.min():.3f} Hz, "
              f"within 20 mHz after {(outside[-1] + 1) * 0.002:.2f} s")
    pid = make_pid(125.0, 60.0, 0.0, 0.01, 250.0)
    F = island(pid, 240.0)
    print(f"trip of 240 kW with anti-windup: nadir {F.min():.3f} Hz, overshoot {max(0.0, F.max()):.3f} Hz")
