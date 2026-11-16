"""Runs, tests and checks state machines given as tables: traces, reachable states, states without a way out, safety
properties and the conformance of logs.

Week: 3
Inputs: a transition table {(state, event): next state}, an initial state, sequences of events or a log of transitions.
Outputs: traces, the set of reachable states, dead ends, the result of a safety check and the illegal steps of a log.
Example: python state_machine_toolkit.py
The example is the charger of the car park, whose states A, B, C and F follow the control pilot of IEC 61851-1.
Uses only the Python standard library.
"""
from collections import deque


class StateMachine:
    def __init__(self, table, initial, outputs=None):
        self.table, self.initial, self.outputs = dict(table), initial, outputs or {}
        self.states = {s for s, _ in self.table} | set(self.table.values()) | {initial}
        self.events = sorted({e for _, e in self.table})

    def step(self, state, event, strict=False):
        if (state, event) in self.table:
            return self.table[(state, event)]
        if strict:
            raise ValueError(f"no transition for event {event!r} in state {state!r}")
        return state                                     # events without a transition are ignored

    def run(self, events, state=None, strict=False):
        trace = [self.initial if state is None else state]
        for e in events:
            trace.append(self.step(trace[-1], e, strict))
        return trace

    def reachable(self, start=None):
        start = self.initial if start is None else start
        seen, todo = {start}, deque([start])
        while todo:
            s = todo.popleft()
            for (src, _), dst in self.table.items():
                if src == s and dst not in seen:
                    seen.add(dst)
                    todo.append(dst)
        return seen

    def dead_ends(self):
        return sorted(s for s in self.states if not any(src == s for src, _ in self.table))

    def check(self, prop):
        """Returns the reachable states that violate the property prop(state)."""
        return sorted(s for s in self.reachable() if not prop(s))

    def shortest_path(self, goal):
        """The shortest sequence of events from the initial state to goal, or None."""
        prev, todo = {self.initial: None}, deque([self.initial])
        while todo:
            s = todo.popleft()
            if s == goal:
                path = []
                while prev[s] is not None:
                    s, e = prev[s]
                    path.append(e)
                return path[::-1]
            for (src, e), dst in self.table.items():
                if src == s and dst not in prev:
                    prev[dst] = (s, e)
                    todo.append(dst)
        return None

    def conformance(self, log):
        """log: iterable of (event, state before, state after); returns the steps that the table does not allow."""
        bad = []
        for i, (event, before, after) in enumerate(log):
            if before != after and self.table.get((before, event)) != after:
                bad.append((i, event, before, after))
        return bad


if __name__ == "__main__":
    charger = StateMachine(
        {("A", "plug"): "B", ("A", "fault"): "F", ("B", "ready"): "C", ("B", "unplug"): "A", ("B", "fault"): "F",
         ("C", "full"): "B", ("C", "unplug"): "A", ("C", "fault"): "F", ("F", "reset"): "A"},
        initial="A", outputs={"A": (12, "open"), "B": (9, "open"), "C": (6, "closed"), "F": (-12, "open")})
    print("trace:", " -> ".join(charger.run(["plug", "ready", "full", "ready", "unplug"])))
    print("reachable:", sorted(charger.reachable()), "| dead ends:", charger.dead_ends())
    print("contactor closed outside C:", charger.check(lambda s: (charger.outputs[s][1] == "closed") == (s == "C")) or "never")
    print("shortest way to charging:", charger.shortest_path("C"))
    log = [("plug", "A", "B"), ("ready", "B", "C"), ("reset", "C", "A"), ("plug", "A", "B")]
    print("illegal steps of the log:", charger.conformance(log))
