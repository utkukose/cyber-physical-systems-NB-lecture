"""Simulates a building with its RC model and a heating schedule, and finds the latest start of the heater for a target
temperature by bisection.

Week: 2
Inputs: the heat capacity C (kWh/K), the thermal resistance R (K/kW), the outdoor temperature, the heater power, the
temperature at the start of the night, the length of the night and the target at its end.
Outputs: the latest start of the heater, the energy of the night and the energy of keeping the comfort temperature.
Example: python building_preheat.py
The RC model C dT/dt = (T_out - T)/R + P follows the simple grey-box models of buildings (Bacher and Madsen, 2011).
Uses only the Python standard library.
"""


def night_end_temperature(start_h, C=30.0, R=0.4, T_out=5.0, P=60.0, T0=21.0, hours=12.0, dt=1 / 60):
    T, t = T0, 0.0
    while t < hours - 1e-9:
        p = P if t >= start_h - 1e-9 else 0.0
        T += dt * ((T_out - T) / R + p) / C
        t += dt
    return T


def latest_start(target=20.0, **kw):
    lo, hi = 0.0, kw.get("hours", 12.0)
    if night_end_temperature(lo, **kw) < target:
        return None                                   # even a heater that runs all night is too weak
    for _ in range(40):
        mid = (lo + hi) / 2
        lo, hi = (mid, hi) if night_end_temperature(mid, **kw) >= target else (lo, mid)
    return lo


if __name__ == "__main__":
    for T_out in (-5.0, 0.0, 5.0, 10.0):
        s = latest_start(T_out=T_out)
        if s is None:
            print(f"outside {T_out:5.1f} C: 60 kW are not enough")
            continue
        keep = (21 - T_out) / 0.4 * 12
        print(f"outside {T_out:5.1f} C: start {s:5.2f} h after 20:00, energy {60 * (12 - s):6.1f} kWh "
              f"against {keep:6.1f} kWh at 21 C all night")
