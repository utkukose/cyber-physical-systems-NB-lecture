"""A synchronised digital twin as a class: one Euler step of a first-order thermal model, the correction of its state by
a gain, a cumulative sum (CUSUM) on the standardised innovations, and the recalibration of the resistance R by a
golden-section search over a sliding window.

Week: 12
Inputs: the calibrated heat capacity C (kWh/K), resistance R (K/kW), solar aperture g and internal gains q (kW) of the
twin, the gain L of the synchronisation, the spread sigma of the innovations in normal operation, the parameters kappa
and h of the CUSUM, the length of the sliding window, and a stream of logged steps of 15 minutes with the indoor
measurement, the outdoor temperature, the heater power, the sun and the opening hours.
Outputs: the state of the twin after each step, its innovations, the alarms of the CUSUM, and the resistance R
recalibrated every hour from the window of recent steps.
Example: python synchronised_twin.py
The example builds two days of a room whose window stays open from 10:00 to 16:00 on the second day, runs the twin with
L = 0.3 and prints the alarms and the R recalibrated over the last 6 hours. Uses the Python standard library and NumPy.
"""
import math
from collections import deque

import numpy as np

DT = 0.25                                     # hours per step


class SynchronisedTwin:
    """A first-order thermal twin that predicts, corrects, watches its innovations and recalibrates R."""

    def __init__(self, C, R, g, q, gain=0.3, sigma=0.13, kappa=0.5, h=5.0, window_steps=48):
        self.C, self.R, self.g, self.q, self.gain = C, R, g, q, gain
        self.sigma, self.kappa, self.h = sigma, kappa, h
        self.temp = None
        self.up = self.down = 0.0
        self.history = deque(maxlen=window_steps + 1)
        self.alarms = []

    def flow(self, temp, t_out, heater_kw, solar_wm2, is_open):
        return (t_out - temp) / self.R + heater_kw + self.g * solar_wm2 + self.q * is_open

    def step(self, k, y, t_out, heater_kw, solar_wm2, is_open):
        """One step of 15 minutes with the inputs of the previous step and the new measurement y. Returns the
        innovation; the first call only sets the state to the measurement."""
        if self.temp is None:
            self.temp, self.last = y, (t_out, heater_kw, solar_wm2, is_open)
            self.history.append((y,) + self.last)
            return 0.0
        pred = self.temp + DT / self.C * self.flow(self.temp, *self.last)
        e = y - pred
        self.temp = pred + self.gain * e
        z = e / self.sigma
        self.up, self.down = max(0.0, self.up + z - self.kappa), min(0.0, self.down + z + self.kappa)
        if self.up > self.h or self.down < -self.h:
            self.alarms.append(k)
            self.up = self.down = 0.0
        self.last = (t_out, heater_kw, solar_wm2, is_open)
        self.history.append((y,) + self.last)
        return e

    def window_error(self, R):
        """Mean squared error of the open-loop twin with the resistance R over the steps in the window."""
        rows = list(self.history)
        temp, err = rows[0][0], 0.0
        for k in range(1, len(rows)):
            y0, t_out, heater_kw, solar_wm2, is_open = rows[k - 1]
            temp += DT / self.C * ((t_out - temp) / R + heater_kw + self.g * solar_wm2 + self.q * is_open)
            err += (temp - rows[k][0]) ** 2
        return err / len(rows)

    def recalibrate_R(self, lo=0.1, hi=1.2, steps=40):
        """Golden-section search for the R with the smallest error over the window."""
        ratio = (math.sqrt(5) - 1) / 2
        c, d = hi - ratio * (hi - lo), lo + ratio * (hi - lo)
        fc, fd = self.window_error(c), self.window_error(d)
        for _ in range(steps):
            if fc < fd:
                hi, d, fd = d, c, fc
                c = hi - ratio * (hi - lo)
                fc = self.window_error(c)
            else:
                lo, c, fc = c, d, fd
                d = lo + ratio * (hi - lo)
                fd = self.window_error(d)
        return (lo + hi) / 2


def example_room(seed=4):
    """Two days of a room with C = 30 kWh/K, a thermostat and a window that opens on the second day (R 0.44 to 0.29)."""
    rng = np.random.default_rng(seed)
    n = 2 * 96
    temp, on, rows = 20.0, False, []
    for k in range(n):
        hour = (k % 96) / 4
        t_out = 3 + 4 * math.sin(2 * math.pi * (hour - 9) / 24)
        sun = 400 * max(0.0, math.sin(math.pi * (hour - 7.5) / 9.5))
        is_open = 1.0 if 8 <= hour < 22 else 0.0
        sp = 21.0 if 6 <= hour < 22 else 17.0
        on = True if temp < sp - 0.5 else (False if temp > sp + 0.5 else on)
        heater = 60.0 if on else 0.0
        R = 0.29 if k >= 96 + 40 and k < 96 + 64 else 0.44
        rows.append((temp + rng.normal(0, 0.1), t_out, heater, sun, is_open))
        temp += DT / 30.0 * ((t_out - temp) / R + heater + 0.018 * sun + 7.3 * is_open)
    return rows


def main():
    twin = SynchronisedTwin(C=30.0, R=0.44, g=0.018, q=7.3, gain=0.3, sigma=0.13, window_steps=24)
    for k, row in enumerate(example_room()):
        twin.step(k, *row)
        if k >= 96 and k % 96 in (32, 48, 64, 80):
            hour = (k % 96) // 4
            print(f"day 2, {hour:02d}:00: twin {twin.temp:.2f} C, R recalibrated over the last 6 h "
                  f"{twin.recalibrate_R():.3f} K/kW")
    alarms = [f"day {1 + k // 96} {(k % 96) // 4:02d}:{(k % 4) * 15:02d}" for k in twin.alarms]
    print("alarms of the CUSUM:", ", ".join(alarms) if alarms else "none")


if __name__ == "__main__":
    main()
