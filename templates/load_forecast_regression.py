"""A day-ahead forecast of an hourly load by linear regression on the hour, the type of day and the heating degrees,
with the error measures MAE, RMSE and MAPE and two naive forecasts for comparison.

Week: 10
Inputs: hourly loads of the training days with their type (working or free) and their measured temperature; the type of
the days to forecast and their temperature forecast; the base temperature of the heating degrees (15 degrees Celsius).
Outputs: the 49 coefficients (24 hours for each type of day and one heating coefficient), the forecast of each hour and
the MAE, the RMSE (both in the unit of the load) and the MAPE in percent, also for the forecasts yesterday and last week.
Example: python load_forecast_regression.py
The example builds six weeks of a campus-like load with weekends, a holiday and random weather, learns from five weeks and
forecasts the sixth with a temperature forecast that carries an error. Requires NumPy.
"""
import numpy as np

T_BASE = 15.0                      # degrees Celsius below which the buildings heat


def features(hours, free, temp):
    """One row per hour: a 1 in the column of its hour (0 to 23 on working days, 24 to 47 on free days) and the
    heating degrees max(0, T_BASE - temp) in the last column."""
    X = np.zeros((len(hours), 49))
    X[np.arange(len(hours)), np.where(free, 24, 0) + hours] = 1
    X[:, 48] = np.maximum(0.0, T_BASE - np.asarray(temp, float))
    return X


def fit(hours, free, temp, load):
    """Least squares: the coefficients beta that minimise the sum of the squared errors."""
    return np.linalg.lstsq(features(hours, free, temp), np.asarray(load, float), rcond=None)[0]


def errors(actual, forecast):
    """The MAE, the RMSE and the MAPE (percent, over the hours with an actual value above zero)."""
    a, f = np.asarray(actual, float), np.asarray(forecast, float)
    e, pos = a - f, a > 0
    return {"mae": float(np.abs(e).mean()), "rmse": float(np.sqrt((e ** 2).mean())),
            "mape": float(100 * np.abs(e[pos] / a[pos]).mean())}


def example_history(days=42, seed=4):
    """A campus-like load: a day profile, a lower level on free days, heating below T_BASE and random noise."""
    rng = np.random.default_rng(seed)
    h = np.tile(np.arange(24), days)
    d = np.repeat(np.arange(days), 24)
    free = (d % 7 >= 5) | (d == 31)                                      # weekends and one holiday in the last week
    temp = (6 + 6 * d / days + np.repeat(rng.normal(0, 2.5, days), 24) + 6 * np.sin(np.pi * (h - 9) / 12))
    temp_fc = temp + np.repeat(rng.normal(0, 1.2, days), 24)              # the forecast of the weather service
    day = 220 + 360 * np.exp(-((h - 12.5) / 4.5) ** 2)
    level = np.where(free, 0.55 * day + 0.45 * 220, day)
    load = (level + 5.5 * np.maximum(0, T_BASE - temp)) * (1 + 0.025 * rng.normal(0, 1, len(h)))
    return h, free, temp, temp_fc, load


if __name__ == "__main__":
    h, free, temp, temp_fc, load = example_history()
    train, test = slice(0, 35 * 24), slice(35 * 24, 42 * 24)
    beta = fit(h[train], free[train], temp[train], load[train])
    forecast = features(h[test], free[test], temp_fc[test]) @ beta
    print(f"heating coefficient: {beta[48]:.2f} kW per kelvin below {T_BASE:.0f} C")
    print("working day at 08:00 and 12:00:", np.round(beta[[8, 12]], 1), "| free day:", np.round(beta[[32, 36]], 1))
    for name, f in (("regression", forecast), ("yesterday", load[test.start - 24:test.stop - 24]),
                    ("last week", load[test.start - 168:test.stop - 168])):
        e = errors(load[test], f)
        print(f"{name:<11} MAE {e['mae']:6.2f}  RMSE {e['rmse']:6.2f}  MAPE {e['mape']:5.2f} percent")
