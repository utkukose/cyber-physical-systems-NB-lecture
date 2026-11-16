"""Periodic real-time tasks as a class, the utilization tests of rate-monotonic (RM) and earliest-deadline-first (EDF)
scheduling, the response-time analysis and a simulator of both schedulers.

Week: 7
Inputs: a list of tasks, each with a name, a worst-case execution time C and a period T in whole milliseconds (the
deadline equals the period); the scheduler, "RM" or "EDF", and the length of the simulation in ms.
Outputs: the utilization and its tests, the worst-case response time of each task under RM and, from the simulation,
the missed deadlines and the worst response time of each task, with a text chart of the schedule.
Example: python rt_scheduler.py
The example is the controller of the battery container of the campus: protection 1 ms every 5 ms, frequency control
3 ms every 10 ms, battery management 5 or 6 ms every 20 ms and Modbus polling 9 ms every 50 ms. Uses only the standard
library of Python 3.9 or later.
"""
import math
from dataclasses import dataclass


@dataclass
class Task:
    """A periodic task whose deadline equals its period."""
    name: str
    C: int          # worst-case execution time in ms
    T: int          # period and deadline in ms

    @property
    def utilization(self):
        return self.C / self.T


def utilization(tasks):
    """The share of the processor that the tasks need."""
    return sum(t.utilization for t in tasks)


def rm_bound(n):
    """The bound of Liu and Layland: RM meets every deadline if the utilization stays below it."""
    return n * (2 ** (1 / n) - 1)


def response_times(tasks, limit=10):
    """The worst-case response time of each task under RM priorities, by the iteration of Joseph and Pandya.
    Returns {name: R in ms}, with None if R grows beyond limit times the period."""
    order = sorted(tasks, key=lambda t: t.T)
    out = {}
    for i, task in enumerate(order):
        higher = order[:i]
        R = task.C + sum(h.C for h in higher)
        while R <= limit * task.T:
            nxt = task.C + sum(math.ceil(R / h.T) * h.C for h in higher)
            if nxt == R:
                break
            R = nxt
        out[task.name] = R if R <= limit * task.T else None
    return out


def simulate(tasks, policy="RM", horizon=None, extra=None):
    """Preemptive scheduling in steps of 1 ms. Returns the trace (the index of the running task, or None, for each ms)
    and every job as a dictionary with its task, release, deadline, remaining work and finish."""
    horizon = horizon or math.lcm(*[t.T for t in tasks])
    extra = horizon // 2 if extra is None else extra
    jobs = [dict(task=i, release=r, deadline=r + t.T, left=t.C, finish=None)
            for i, t in enumerate(tasks) for r in range(0, horizon + extra, t.T)]
    trace = []
    for now in range(horizon + extra):
        ready = [j for j in jobs if j["release"] <= now and j["left"] > 0]
        if not ready:
            trace.append(None)
            continue
        if policy == "RM":
            job = min(ready, key=lambda j: (tasks[j["task"]].T, j["task"], j["release"]))
        else:
            job = min(ready, key=lambda j: (j["deadline"], j["task"], j["release"]))
        job["left"] -= 1
        trace.append(job["task"])
        if job["left"] == 0:
            job["finish"] = now + 1
    return trace, jobs


def report(tasks, jobs, horizon):
    """For each task: the jobs due within the horizon, the missed deadlines and the worst response time."""
    rows = []
    for i, t in enumerate(tasks):
        mine = [j for j in jobs if j["task"] == i and j["deadline"] <= horizon]
        missed = sum(j["finish"] is None or j["finish"] > j["deadline"] for j in mine)
        done = [j["finish"] - j["release"] for j in mine if j["finish"] is not None]
        rows.append((t.name, len(mine), missed, max(done) if len(done) == len(mine) else None))
    return rows


def chart(tasks, trace, width):
    """A text chart of the schedule: one line per task, # where the task runs."""
    lines = []
    for i, t in enumerate(tasks):
        lines.append(f"{t.name[:18]:<18} " + "".join("#" if trace[k] == i else "." for k in range(width)))
    return "\n".join(lines)


if __name__ == "__main__":
    for c_bm in (5, 6):
        tasks = [Task("protection", 1, 5), Task("frequency control", 3, 10), Task("battery management", c_bm, 20),
                 Task("Modbus", 9, 50)]
        U = utilization(tasks)
        print(f"battery management {c_bm} ms: U = {U:.2f}, RM bound {rm_bound(len(tasks)):.4f}, EDF test (U <= 1): "
              f"{'passed' if U <= 1 else 'failed'}")
        for name, R in response_times(tasks).items():
            T = next(t.T for t in tasks if t.name == name)
            print(f"  RM response time of {name:<20} {R} ms against {T} ms")
        for policy in ("RM", "EDF"):
            trace, jobs = simulate(tasks, policy, 100)
            print(f"  {policy}: " + ", ".join(f"{n} missed {m} of {j}" for n, j, m, _ in report(tasks, jobs, 100)))
        print(chart(tasks, simulate(tasks, "RM", 60)[0], 60))
        print()
