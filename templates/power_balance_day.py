"""Computes the hourly balance of a site from its demand, solar and wind models and a battery rule, with the energies,
the peak import and the self-sufficiency.

Week: 1
Inputs: 24 hourly values of the demand (kW), the irradiance (W/m2), the air temperature (deg C) and the wind speed
(m/s); the sizes of the solar plant, the wind turbine and the battery; the threshold of the battery rule.
Outputs: a table of the day with the import and the state of charge, and a summary of energies and peaks.
Example: python power_balance_day.py
The solar model uses a linear temperature coefficient (Skoplaki and Palyvos, 2009) and the wind model a cubic power
curve between cut-in and rated speed (Carrillo et al., 2013). Requires NumPy.
"""
import numpy as np


def pv_power(G, T_amb, p_peak=400.0, gamma=-0.004, k_t=0.03):
    T_cell = np.asarray(T_amb, float) + k_t * np.asarray(G, float)
    return np.maximum(0.0, p_peak * np.asarray(G, float) / 1000 * (1 + gamma * (T_cell - 25)))


def wind_power(v, p_rated=250.0, v_in=3.0, v_rated=12.0, v_out=25.0):
    v = np.asarray(v, float)
    p = p_rated * (v ** 3 - v_in ** 3) / (v_rated ** 3 - v_in ** 3)
    p = np.where(v < v_in, 0.0, np.where(v < v_rated, p, p_rated))
    return np.where(v >= v_out, 0.0, p)


def battery_rule(net_kw, threshold_kw, charge_below_kw, e_kwh=500.0, p_max=250.0, eta=0.95, soc0=0.5,
                 soc_min=0.1, soc_max=0.9):
    """Discharge above the threshold and charge below charge_below_kw, hour by hour (dt = 1 h)."""
    soc, bat, socs = soc0, [], []
    for net in net_kw:
        if net > threshold_kw:
            p = min(net - threshold_kw, p_max, (soc - soc_min) * e_kwh * eta)
        elif net < charge_below_kw:
            p = -min(charge_below_kw - net, p_max, (soc_max - soc) * e_kwh / eta)
        else:
            p = 0.0
        soc += (-p / eta if p > 0 else -p * eta) / e_kwh
        bat.append(p)
        socs.append(soc)
    return np.array(bat), np.array(socs)


def summarise(demand, local, grid):
    imp = np.clip(grid, 0, None).sum()
    return {"demand_kwh": demand.sum(), "local_kwh": local.sum(), "import_kwh": imp,
            "export_kwh": np.clip(-grid, 0, None).sum(), "peak_import_kw": grid.max(),
            "self_sufficiency": 1 - imp / demand.sum()}


if __name__ == "__main__":
    h = np.arange(24)
    demand = np.array([262, 255, 250, 248, 252, 270, 330, 452, 586, 636, 629, 612, 597, 602, 607, 619, 626, 640,
                       630, 588, 494, 412, 320, 280], float)
    G = 950 * np.maximum(0, np.sin(np.pi * (h + 0.5 - 6) / 13))
    T_amb = 12 + 7 * np.sin(np.pi * (h - 9) / 12)
    wind = np.array([7.8, 8.0, 8.2, 8.0, 7.6, 7.0, 6.2, 5.4, 4.8, 4.4, 4.2, 4.6, 5.0, 5.2, 5.0, 4.6, 4.2, 3.8, 3.6,
                     3.5, 3.8, 4.6, 5.8, 7.0])
    local = pv_power(G, T_amb).round(1) + wind_power(wind).round(1)
    net = demand - local
    bat, soc = battery_rule(net, 450, 330)
    for name, grid in [("without the battery", net), ("with the battery rule", net - bat)]:
        s = summarise(demand, local, grid)
        print(f"{name}: import {s['import_kwh']:.0f} kWh, peak {s['peak_import_kw']:.1f} kW, "
              f"self-sufficiency {s['self_sufficiency']:.3f}")
    print("state of charge at midnight:", round(float(soc[-1]), 3))
