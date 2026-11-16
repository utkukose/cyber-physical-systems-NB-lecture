"""A skeleton of a periodic control loop with a sensor, a controller and an actuator as small classes, run against a
simulated plant.

Week: 1
Inputs: the period of the loop, the target, the gain and a simulated plant (here the import of a site with a battery).
Outputs: a log of every step: time, measurement, error, set point and the state of the plant.
Example: python sense_compute_actuate.py
Replace SimulatedSite with an interface to real hardware (for example a Modbus meter and inverter, see Week 8) and keep
the loop and the limits. Uses only the Python standard library.
"""
import time


class SimulatedSite:
    """The plant: a net load that a battery reduces; the import is what the meter measures."""

    def __init__(self, net_kw=530.0):
        self.net_kw, self.battery_kw = net_kw, 0.0

    def import_kw(self):
        return self.net_kw - self.battery_kw


class Sensor:
    def __init__(self, site):
        self.site = site

    def read(self):
        return self.site.import_kw()


class Controller:
    """Integrating peak shaving: the set point grows by K times the excess over the target, within the limits."""

    def __init__(self, target_kw=400.0, gain=0.5, p_max=250.0):
        self.target, self.gain, self.p_max, self.set_point = target_kw, gain, p_max, 0.0

    def step(self, measured_kw):
        error = measured_kw - self.target
        self.set_point = min(self.p_max, max(-self.p_max, self.set_point + self.gain * error))
        return error, self.set_point


class Actuator:
    def __init__(self, site):
        self.site = site

    def apply(self, set_point_kw):
        self.site.battery_kw = set_point_kw


def run(period_s=0.0, steps=8, gain=0.5):
    site = SimulatedSite()
    sensor, ctl, act = Sensor(site), Controller(gain=gain), Actuator(site)
    for k in range(steps):
        y = sensor.read()                      # sense
        e, u = ctl.step(y)                     # compute
        act.apply(u)                           # actuate
        print(f"step {k}: measured {y:7.2f} kW, error {e:7.2f} kW, set point {u:7.2f} kW")
        if period_s:
            time.sleep(period_s)               # a real loop waits for the next period


if __name__ == "__main__":
    run()
