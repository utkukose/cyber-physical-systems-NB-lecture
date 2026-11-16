"""Output-error calibration of a first-order thermal twin, C dT/dt = (T_out - T)/R + P + g G + q o, fitted to a log by
least squares on the simulated output and validated on a second period.

Week: 12
Inputs: a log in a file of comma-separated values with the columns t_in (C), t_out (C), heater_kw (kW), solar_wm2
(W/m2) and open (0 or 1), one row per step of DT hours; the number of rows of the calibration period; start values of
C, R, g and q.
Outputs: the calibrated heat capacity C (kWh/K), resistance R (K/kW), solar aperture g (kW per W/m2) and internal gains
q (kW), the time constant RC in hours, and the root mean square error (RMSE) of the open-loop twin in the calibration
and in the validation period.
Example: python twin_calibration.py [log.csv]
Without a file, the example builds two weeks of a library with a heating of 60 kW, the sun and visitors from a room with
two heat capacities, calibrates the twin on the first week and validates it on the second. Requires NumPy and SciPy.
"""
import csv
import sys

import numpy as np
from scipy.optimize import least_squares

DT = 0.25                                     # hours between two rows of the log
COLUMNS = ("t_in", "t_out", "heater_kw", "solar_wm2", "open")


def load_log(path):
    """Reads the log into a dictionary of NumPy arrays, one per column."""
    with open(path, newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    return {c: np.array([float(r[c]) for r in rows]) for c in COLUMNS}


def part(log, a, b):
    """The rows a to b - 1 of the log."""
    return {c: v[a:b] for c, v in log.items()}


def simulate(log, C, R, g=0.0, q=0.0, gain=0.0):
    """The twin over the log: open loop with gain 0, corrected with each measurement otherwise. The twin starts from
    the first measurement. Returns the twin after each update and the one-step prediction before it."""
    y = log["t_in"]
    twin, pred = np.zeros(len(y)), np.zeros(len(y))
    twin[0] = pred[0] = y[0]
    for k in range(len(y) - 1):
        flow = (log["t_out"][k] - twin[k]) / R + log["heater_kw"][k] + g * log["solar_wm2"][k] + q * log["open"][k]
        p = twin[k] + DT / C * flow
        pred[k + 1] = p
        twin[k + 1] = p + gain * (y[k + 1] - p)
    return twin, pred


def rmse(a, b):
    return float(np.sqrt(np.mean((np.asarray(a, float) - np.asarray(b, float)) ** 2)))


def calibrate(log, x0=(25.0, 0.5, 0.0, 0.0)):
    """Output-error least squares: the C, R, g and q that bring the open-loop twin closest to the measurements."""
    res = least_squares(lambda p: simulate(log, *p)[0] - log["t_in"], x0=x0,
                        bounds=([1e-3, 1e-3, -1.0, -100.0], [1e4, 100.0, 1.0, 100.0]))
    return dict(zip(("C", "R", "g", "q"), (float(v) for v in res.x)))


def example_log(days=14, seed=12):
    """A library with a heating of 60 kW and a thermostat, simulated minute by minute with a heat capacity for the air
    and one for the walls, and logged every 15 minutes with a sensor noise of 0.1 K."""
    rng = np.random.default_rng(seed)
    n = days * 24 * 60
    t = np.arange(n) / 60.0
    hour, day = t % 24, (t // 24).astype(int)
    weekday = day % 7
    t_out = 3 + 4 * np.sin(2 * np.pi * (hour - 9) / 24) + np.repeat(rng.normal(0, 2.0, days), 24 * 60)
    sun = 450 * np.maximum(0, np.sin(np.pi * (hour - 7.5) / 9.5)) * rng.uniform(0.25, 1.0, days)[day]
    is_open = np.where(weekday < 5, (hour >= 8) & (hour < 22), (hour >= 10) & (hour < 18)).astype(float)
    heated = np.where(weekday < 5, (hour >= 6) & (hour < 22), (hour >= 8) & (hour < 18))
    gains = 6.0 * is_open * rng.uniform(0.6, 1.4, days)[day]
    air, mass, heat = np.full(n, 18.0), np.full(n, 18.0), np.zeros(n)
    on = False
    for k in range(n - 1):
        sp = 21.0 if heated[k] else 17.0
        on = True if air[k] < sp - 0.5 else (False if air[k] > sp + 0.5 else on)
        heat[k] = 60.0 if on else 0.0
        q_air = (mass[k] - air[k]) / 0.02 + (t_out[k] - air[k]) / 6.0 + heat[k] + 0.01 * sun[k] + gains[k]
        q_mass = (air[k] - mass[k]) / 0.02 + (t_out[k] - mass[k]) / 0.46 + 0.01 * sun[k]
        air[k + 1] = air[k] + q_air / 20.0 / 60
        mass[k + 1] = mass[k] + q_mass / 10.0 / 60
    heat[-1] = heat[-2]
    mean15 = lambda a: a.reshape(-1, 15).mean(axis=1)
    return {"t_in": air[::15] + rng.normal(0, 0.1, n // 15), "t_out": mean15(t_out), "heater_kw": mean15(heat),
            "solar_wm2": mean15(sun), "open": mean15(is_open)}


def main():
    log = load_log(sys.argv[1]) if len(sys.argv) > 1 else example_log()
    split = len(log["t_in"]) // 2
    cal, val = part(log, 0, split), part(log, split, len(log["t_in"]))
    fit = calibrate(cal)
    print(f"calibration on {split} rows, validation on {len(val['t_in'])} rows")
    print(f"C = {fit['C']:.2f} kWh/K, R = {fit['R']:.3f} K/kW, g = {fit['g']:.4f} kW per W/m2, q = {fit['q']:.2f} kW")
    print(f"time constant RC = {fit['R'] * fit['C']:.2f} h")
    print(f"RMSE of the open-loop twin: calibration {rmse(simulate(cal, **fit)[0], cal['t_in']):.3f} K, "
          f"validation {rmse(simulate(val, **fit)[0], val['t_in']):.3f} K")


if __name__ == "__main__":
    main()
