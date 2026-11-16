"""A breadth-first model checker for a finite-state controller: it visits every reachable state, checks a safety
invariant in each one and returns the shortest counterexample if the invariant fails.

Week: 14
Inputs: an initial state, a function that lists the successor states of a state (all choices of the environment and
the reaction of the controller) and a function that tells whether a state is unsafe.
Outputs: the number of reachable states, the unsafe states and the shortest path from the initial state to an unsafe
state, step by step.
Example: python model_check.py
The example checks the transfer logic of the island controller of the campus microgrid in two versions. When the grid
fails, the controller must open the breaker at the point of common coupling before the inverter of the battery forms
the island grid. Version 1 trusts a timer and version 2 waits for the breaker to report open. Requires only Python.
"""
from collections import deque


def model_check(initial, successors, unsafe):
    """Breadth-first search over all reachable states. Returns the dictionary of parents, the unsafe states and the
    shortest path to an unsafe state (an empty list if the invariant holds)."""
    parent, depth, queue, bad = {initial: None}, {initial: 0}, deque([initial]), []
    while queue:
        s = queue.popleft()
        if unsafe(s):
            bad.append(s)
        for n in successors(s):
            if n not in parent:
                parent[n], depth[n] = s, depth[s] + 1
                queue.append(n)
    path = []
    if bad:
        x = min(bad, key=lambda b: depth[b])
        while x is not None:
            path.append(x)
            x = parent[x]
        path.reverse()
    return parent, bad, path


# The example: a state is (mode, timer, breaker closed, inverter, grid ok, breaker stuck closed).
INIT = ("GRID", 0, 1, "follow", 1, 0)


def step(state, grid, stuck, version):
    """One step of 100 ms of the transfer logic after the environment has chosen the grid and a stuck breaker."""
    mode, t, brk, inv = state[:4]
    cmd = None
    if mode == "GRID":
        inv = "follow"
        if not grid:
            mode, t, inv, cmd = "OPENING", 0, "off", "open"
    elif mode == "OPENING":
        cmd = "open"
        if version == 1:
            if t >= 1:
                mode, t, inv = "ISLAND", 0, "form"
            else:
                t += 1
        elif brk == 0:
            mode, t, inv = "ISLAND", 0, "form"
        elif t >= 2:
            mode, t, inv = "FAULT", 0, "off"
        else:
            t += 1
    elif mode == "ISLAND":
        if grid:
            mode, t = "SYNC", 0
    elif mode == "SYNC":
        if not grid:
            mode, t = "ISLAND", 0
        elif t >= 1:
            mode, t, inv, cmd = "GRID", 0, "follow", "close"
        else:
            t += 1
    elif mode == "FAULT":
        if grid and brk == 1:
            mode, inv = "GRID", "follow"
    if cmd == "open" and not stuck:
        brk = 0
    elif cmd == "close":
        brk = 1
    return (mode, t, brk, inv, grid, stuck)


def successors_of(version):
    """All successor states: the grid may fail or return, and a breaker may stick closed and then stays stuck."""
    def successors(s):
        return [step(s, grid, stuck, version) for grid in (0, 1) for stuck in ((1,) if s[5] else (0, 1))]
    return successors


def back_feed(s):
    """The safety invariant is broken if the inverter forms the grid while the breaker is closed."""
    return s[3] == "form" and s[2] == 1


def main():
    for version in (1, 2):
        parent, bad, path = model_check(INIT, successors_of(version), back_feed)
        print(f"version {version}: {len(parent)} reachable states, {len(bad)} unsafe")
        for k, s in enumerate(path):
            print(f"  {k * 100:>4} ms  mode {s[0]:<8} breaker {'closed' if s[2] else 'open':<6}  inverter {s[3]:<6}  "
                  f"grid {'ok' if s[4] else 'lost'}  stuck {s[5]}")


if __name__ == "__main__":
    main()
