"""Computes the trip times of the IEC curves for overcurrent relays and the time multiplier of an upstream relay for a
grading margin.

Week: 3
Inputs: the curve type, the pickup current and the time multiplier of each relay, the fault current and the margin.
Outputs: the trip times, the smallest time multiplier of the upstream relay in steps of 0.01 and the resulting margin.
Example: python overcurrent_coordination.py
The curves follow the dependent-time characteristics of IEC 60255-151: t = TMS * k / ((I / Is)^alpha - 1). The example
is the feeder of the library and the incomer of the transformer of the campus. Uses only the Python standard library.
"""
import math

CURVES = {"standard inverse": (0.14, 0.02), "very inverse": (13.5, 1.0), "extremely inverse": (80.0, 2.0),
          "long-time inverse": (120.0, 1.0)}


def trip_time(I, Is, tms, curve="standard inverse"):
    k, alpha = CURVES[curve]
    M = I / Is
    return math.inf if M <= 1 else tms * k / (M ** alpha - 1)


def upstream_tms(I_fault, t_down, Is_up, margin=0.3, curve="standard inverse", step=0.01):
    """The smallest time multiplier, in steps of step, that trips at least margin after t_down."""
    per_tms = trip_time(I_fault, Is_up, 1.0, curve)
    return math.ceil((t_down + margin) / per_tms / step - 1e-9) * step


if __name__ == "__main__":
    for M in (2, 5, 10, 20):
        row = ", ".join(f"{c} {trip_time(M, 1, 0.1, c):6.3f} s" for c in CURVES)
        print(f"M = {M:>2}, TMS 0.10: {row}")
    I_fault = 5000.0
    t_feeder = trip_time(I_fault, 250, 0.10)
    tms = upstream_tms(I_fault, t_feeder, 1600)
    t_inc = trip_time(I_fault, 1600, tms)
    print(f"fault {I_fault:.0f} A: feeder {t_feeder:.3f} s, incomer TMS {tms:.2f} trips after {t_inc:.3f} s, "
          f"margin {t_inc - t_feeder:.3f} s")
