"""Anomaly detection on the residual of a model: a threshold on the standardised residual and a two-sided cumulative
sum (CUSUM) that restarts after each alarm, scored against a log of known faults.

Week: 10
Inputs: the measured values and the values that a model expects, a training period without faults for the spread of
the residual, the threshold k of the standardised residual, the allowance kappa and the limit h of the CUSUM, and the
hours of the known faults.
Outputs: the standardised residual z of each hour, the alarms of each detector, the counts of true and false alarms,
the precision and the recall, and the first alarm of each fault.
Example: python residual_cusum_detector.py
The example is a solar plant whose power follows a model of the measured irradiance, with a sudden loss of half the power
for four hours and a slow loss of 1.2 percent a day from dust. Requires NumPy.
"""
import numpy as np


def standardise(measured, expected, train):
    """The relative residual e = measured / expected - 1 divided by its standard deviation in the training hours."""
    e = np.asarray(measured, float) / np.asarray(expected, float) - 1
    return e / np.std(e[train], ddof=1)


def threshold(z, k):
    """An alarm in every hour with |z| > k."""
    return np.abs(z) > k


def cusum(z, kappa=0.5, h=4.0):
    """Two-sided CUSUM: S+ = max(0, S+ + z - kappa) and S- = min(0, S- + z + kappa); an alarm when S+ > h or S- < -h,
    after which both sums start again at zero."""
    sp = sm = 0.0
    alarms = np.zeros(len(z), bool)
    for t, v in enumerate(z):
        sp, sm = max(0.0, sp + v - kappa), min(0.0, sm + v + kappa)
        if sp > h or sm < -h:
            alarms[t], sp, sm = True, 0.0, 0.0
    return alarms


def score(alarms, faults, events):
    """Counts true and false alarms against the fault hours and finds the first alarm of each event (start, end)."""
    tp, fp = int(np.sum(alarms & faults)), int(np.sum(alarms & ~faults))
    fn = int(np.sum(~alarms & faults))
    first = {name: next((t for t in range(s, e + 1) if alarms[t]), None) for name, (s, e) in events.items()}
    return {"true": tp, "false": fp, "missed": fn, "precision": tp / max(1, tp + fp), "recall": tp / max(1, tp + fn),
            "first": first}


if __name__ == "__main__":
    rng = np.random.default_rng(6)
    days, per_day = 28, 11                                        # eleven sunny hours a day
    irr = np.tile(950 * np.sin(np.pi * (np.arange(per_day) + 1) / (per_day + 1)), days)
    irr *= np.repeat(rng.uniform(0.5, 1.0, days), per_day)
    expected = 400 * irr / 1000 * 0.95                            # the model of a healthy plant (kW)
    measured = expected * (1 + 0.013 * rng.normal(0, 1, len(irr)))
    faults = np.zeros(len(irr), bool)
    trip = (22 * per_day + 3, 22 * per_day + 6)                   # half the power for four hours
    measured[trip[0]:trip[1] + 1] *= 0.5
    faults[trip[0]:trip[1] + 1] = True
    dust = (24 * per_day, days * per_day - 1)                     # 1.2 percent less each day from day 24
    for d in range(24, days):
        measured[d * per_day:(d + 1) * per_day] *= 1 - 0.012 * (d - 23)
    faults[dust[0]:] = True
    z = standardise(measured, expected, train=slice(0, 21 * per_day))
    events = {"trip": trip, "dust": dust}
    test = slice(21 * per_day, days * per_day)
    for name, alarms in (("threshold k = 3", threshold(z, 3.0)), ("threshold k = 2", threshold(z, 2.0)),
                         ("CUSUM 0.5 / 4", cusum(z[test], 0.5, 4.0))):
        full = np.zeros(len(z), bool)
        full[test] = alarms[test] if len(alarms) == len(z) else alarms
        s = score(full, faults, events)
        first = {k: (None if v is None else f"day {v // per_day}, hour {v % per_day}") for k, v in s["first"].items()}
        print(f"{name:<16} true {s['true']:3}  false {s['false']:2}  precision {s['precision']:.3f}  "
              f"recall {s['recall']:.3f}  first alarms {first}")
