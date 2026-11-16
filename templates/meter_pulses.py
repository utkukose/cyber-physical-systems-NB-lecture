"""Turns the times of the pulses of a meter into power, integrates a power profile into intervals of 15 minutes and
reports the demands.

Week: 4
Inputs: the pulse times in seconds, the meter constant in pulses per kWh, the ratio of the current transformers and a
power profile in kW with its time step.
Outputs: the mean period and power from the pulses, the energy and demand of each interval and the highest demand.
Example: python meter_pulses.py
The example is the meter of the library with 1000 pulses per kWh and current transformers of 200/5 A. Requires NumPy.
"""
import numpy as np


def power_from_pulses(times_s, imp_kwh=1000, ct_ratio=40.0):
    """Primary power in kW from a list of pulse times; N pulses span N - 1 periods."""
    t = np.sort(np.asarray(times_s, float))
    if len(t) < 2:
        raise ValueError("at least two pulses are needed")
    period = (t[-1] - t[0]) / (len(t) - 1)
    return period, 3600 / (imp_kwh * period) * ct_ratio


def demands(power_kw, step_s, interval_s=900):
    """Mean power of each full interval of interval_s seconds."""
    p = np.asarray(power_kw, float)
    n = int(interval_s // step_s)
    full = len(p) // n * n
    return p[:full].reshape(-1, n).mean(axis=1)


if __name__ == "__main__":
    rng = np.random.default_rng(7)
    clicks = 1.8 * np.arange(6) + rng.normal(0.15, 0.05, 6)        # six presses of a student at a period of 1.8 s
    period, p = power_from_pulses(clicks)
    print(f"mean period {period:.3f} s -> {p:.1f} kW (true 80 kW)")
    t = np.arange(0, 4 * 3600, 1.0)                                # four hours, one value a second
    heater_on = (t / 60) % 27 < 18                                  # a thermostat cycle of 18 minutes on and 9 off
    power = 20 + 60 * heater_on
    d = demands(power, 1.0)
    print("demands of 15 minutes (kW):", np.round(d, 1))
    print(f"energy {power.mean() * 4:.1f} kWh, highest demand {d.max():.1f} kW, momentary peak {power.max():.1f} kW")
