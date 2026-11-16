"""A first-order thermal twin in a closed loop with an on and off thermostat, heating schedules with a fixed or an
optimal start, and a Monte Carlo comparison of the schedules over random weeks of weather and visitors.

Week: 13
Inputs: the parameters of a calibrated twin, C dT/dt = (T_out - T)/R + P + g G + q o, with the heat capacity C (kWh/K),
the resistance R (K/kW), the solar aperture g (kW per W/m2) and the internal gains q (kW) while the building is open;
the power of the heating and the comfort limit; the schedules to compare; optionally one week of weather in a file of
comma-separated values with the columns t_out (C), solar_wm2 (W/m2) and open (0 or 1), 672 rows of DT hours from a
Monday 00:00.
Outputs: for each schedule, the heating energy (kWh) and the comfort deficit (K h) of the given week, and over the
random weeks the mean energy, its 90 percent quantile, the mean comfort deficit and the probability of a comfort
deficit above 1 K h with its standard error.
Example: python whatif_scenarios.py [week.csv]
Without a file, the example uses the twin of the library from Week 12 and a week of weather drawn with the seed 1. The
Monte Carlo comparison runs every schedule over the same 300 random weeks. Requires NumPy.
"""
import csv
import math
import sys

import numpy as np

DT = 0.25                                        # hours between two rows
TWIN = dict(C=30.41, R=0.440, g=0.0178, q=7.33)  # the twin of the library, calibrated in Week 12
P_MAX = 60.0                                     # power of the heating (kW)
DAY_SETPOINT = 21.0                              # setpoint while the heating schedule is on (C)
LIMIT = 20.0                                     # comfort limit while the building is open (C)
TARGET = 20.5                                    # temperature that the optimal start reaches by the opening (C)
BAND = 0.5                                       # half the band of the thermostat (K)
SCHEDULES = [("17 C at night, start 6:00", 17.0, 6.0, False),
             ("19 C at night, start 6:00", 19.0, 6.0, False),
             ("17 C at night, optimal start", 17.0, 0.0, True),
             ("13 C at night, optimal start", 13.0, 0.0, True)]


def opening_hours(day):
    """The opening and the closing hour of a day of the week, with 0 for Monday."""
    return (8, 22) if day % 7 < 5 else (10, 18)


def warm_up_hours(temp, t_out, twin=TWIN):
    """The time that the full power needs to bring the twin from temp to TARGET, from the solution of the first-order
    model with a constant outdoor temperature."""
    steady = t_out + twin["R"] * P_MAX
    if temp >= TARGET:
        return 0.0
    if steady <= TARGET:
        return math.inf
    return twin["R"] * twin["C"] * math.log((steady - temp) / (steady - TARGET))


def run_week(weather, night=17.0, start=6.0, optimal=False, temp0=18.0, visitors=None, twin=TWIN):
    """The twin in a closed loop with the thermostat over the rows of weather, from a Monday 00:00. The heating
    schedule starts at start on weekdays and 2 hours later at weekends and ends at closing. With optimal=True it starts
    as soon as the warm-up time reaches the time left before opening. Returns the temperature, the heating power, the
    energy (kWh) and the comfort deficit (K h)."""
    C, R, g, q = twin["C"], twin["R"], twin["g"], twin["q"]
    t_out, sun, is_open = (np.asarray(weather[c], float) for c in ("t_out", "solar_wm2", "open"))
    n = len(t_out)
    temp, heat = np.zeros(n), np.zeros(n)
    temp[0] = temp0
    on, started = False, -1
    for k in range(n - 1):
        day, hour = k // 96, (k % 96) * DT
        opens, closes = opening_hours(day)
        if optimal:
            if hour < opens and started != day and warm_up_hours(temp[k], t_out[k], twin) >= (opens - hour) - DT:
                started = day
            setpoint = DAY_SETPOINT if (started == day or opens <= hour) and hour < closes else night
        else:
            begin = start if day % 7 < 5 else start + 2
            setpoint = DAY_SETPOINT if begin <= hour < closes else night
        if temp[k] < setpoint - BAND:
            on = True
        elif temp[k] > setpoint + BAND:
            on = False
        heat[k] = P_MAX if on else 0.0
        gains = q * is_open[k] * (1.0 if visitors is None else visitors[day])
        temp[k + 1] = temp[k] + DT / C * ((t_out[k] - temp[k]) / R + heat[k] + g * sun[k] + gains)
    heat[-1] = heat[-2]
    deficit = float((np.maximum(0.0, LIMIT - temp) * is_open).sum() * DT)
    return dict(temp=temp, heat=heat, energy=float(heat.sum() * DT), deficit=deficit)


def random_week(rng):
    """One random week: A daily level of the outdoor temperature that follows the level of the day before, and a cloud
    factor and a factor of the visitors for each day. Returns the weather and the factors of the visitors."""
    level = np.zeros(7)
    for d in range(7):
        level[d] = 2.5 * rng.normal() if d == 0 else 0.6 * level[d - 1] + 2.0 * rng.normal()
    cloud, visitors = 0.25 + 0.75 * rng.random(7), 0.6 + 0.8 * rng.random(7)
    hours = (np.arange(672) + 0.5) * DT              # the middle of each row, in hours since Monday 00:00
    hour, day = hours % 24, (hours // 24).astype(int)
    t_out = 3 + 4 * np.sin(2 * np.pi * (hour - 9) / 24) + np.interp(hours, 12 + 24 * np.arange(7), level)
    sun = 450 * np.maximum(0, np.sin(np.pi * (hour - 7.5) / 9.5)) * cloud[day]
    is_open = np.array([opening_hours(d)[0] <= h < opening_hours(d)[1] for d, h in zip(day, hour)], float)
    return dict(t_out=t_out, solar_wm2=sun, open=is_open), visitors


def monte_carlo(schedules, weeks=300, seed=13):
    """Every schedule over the same random weeks: The mean energy, its 90 percent quantile, the mean comfort deficit and
    the probability of a comfort deficit above 1 K h with its standard error."""
    rng = np.random.default_rng(seed)
    drawn = [random_week(rng) for _ in range(weeks)]
    out = {}
    for name, night, start, optimal in schedules:
        energy = np.array([run_week(w, night, start, optimal, visitors=v)["energy"] for w, v in drawn])
        deficit = np.array([run_week(w, night, start, optimal, visitors=v)["deficit"] for w, v in drawn])
        p = float(np.mean(deficit > 1.0))
        out[name] = dict(mean_kwh=float(energy.mean()), p90_kwh=float(np.percentile(energy, 90)),
                         mean_deficit=float(deficit.mean()), p_deficit=p, se=math.sqrt(p * (1 - p) / weeks))
    return out


def load_week(path):
    """Reads one week of weather from a file of comma-separated values."""
    with open(path, newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    return {c: np.array([float(r[c]) for r in rows]) for c in ("t_out", "solar_wm2", "open")}


def main():
    if len(sys.argv) > 1:
        week, visitors = load_week(sys.argv[1]), None
        print(f"weather of {sys.argv[1]}: {len(week['t_out'])} rows")
    else:
        week, visitors = random_week(np.random.default_rng(1))
        print("weather: one random week, seed 1")
    print(f"{'schedule':32s} {'energy (kWh)':>13s} {'deficit (K h)':>14s}")
    for name, night, start, optimal in SCHEDULES:
        run = run_week(week, night, start, optimal, visitors=visitors)
        print(f"{name:32s} {run['energy']:13.1f} {run['deficit']:14.3f}")
    print("\n300 random weeks, the same for every schedule:")
    print(f"{'schedule':32s} {'mean (kWh)':>11s} {'90 % (kWh)':>11s} {'deficit (K h)':>14s} {'P(D > 1 K h)':>14s}")
    for name, m in monte_carlo(SCHEDULES).items():
        print(f"{name:32s} {m['mean_kwh']:11.1f} {m['p90_kwh']:11.1f} {m['mean_deficit']:14.3f} "
              f"{m['p_deficit']:8.3f} ± {m['se']:.3f}")


if __name__ == "__main__":
    main()
