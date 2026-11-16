"""The scan cycle of a programmable logic controller (PLC): the best and the worst reaction from an input terminal to an
output terminal, the reactions to events at random moments and the watchdog.

Week: 7
Inputs: the scan time in ms, the delay of the input filter and of the output, the required reaction and the watchdog
time, all in ms; for a simulation, the number of events and a seed.
Outputs: the best and the worst reaction, the reactions to random events, the largest scan time that meets the required
reaction and whether the watchdog stops the PLC.
Example: python plc_scan.py
The example is the PLC of the main switchboard of the campus: an input filter of 3 ms, a relay output of 6 ms, a required
reaction of 50 ms after a trip of the grid breaker and a watchdog of 30 ms. Programs of k thousand instructions take
k + 1 ms per scan. Uses only the standard library of Python.
"""
import math
import random


class ScanCycle:
    """A PLC that writes its outputs and reads its inputs at the boundary of two scans."""

    def __init__(self, scan_ms, t_in=3.0, t_out=6.0, watchdog_ms=30.0):
        self.scan_ms, self.t_in, self.t_out, self.watchdog_ms = scan_ms, t_in, t_out, watchdog_ms

    @property
    def running(self):
        return self.scan_ms <= self.watchdog_ms

    def best(self):
        return self.scan_ms + self.t_in + self.t_out

    def worst(self):
        return 2 * self.scan_ms + self.t_in + self.t_out

    def reaction(self, e):
        """The reaction to an input that changes at the moment e in ms; the scans start at 0, T, 2T and so on."""
        if not self.running:
            return None
        read = math.ceil((e + self.t_in) / self.scan_ms) * self.scan_ms
        return read + self.scan_ms + self.t_out - e

    def simulate(self, n=20, seed=1):
        rng = random.Random(seed)
        return [self.reaction(1000 * i + 1000 * rng.random()) for i in range(n)]


def largest_scan(limit_ms, t_in=3.0, t_out=6.0):
    """The largest scan time whose worst reaction stays within the limit."""
    return (limit_ms - t_in - t_out) / 2


if __name__ == "__main__":
    print(f"largest scan time for 50 ms: {largest_scan(50.0):.1f} ms")
    for k in (12, 19, 20, 30):
        plc = ScanCycle(k + 1.0)
        if not plc.running:
            print(f"{k} thousand instructions: scan {plc.scan_ms:.0f} ms exceeds the watchdog, the PLC stops")
            continue
        r = plc.simulate(20, seed=k)
        print(f"{k} thousand instructions: scan {plc.scan_ms:.0f} ms, best {plc.best():.0f} ms, worst {plc.worst():.0f} ms, "
              f"20 trips from {min(r):.1f} to {max(r):.1f} ms -> "
              + ("within" if plc.worst() <= 50 else "above") + " the limit of 50 ms")
