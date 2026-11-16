"""A fault tree over minimal cut sets with independent basic events: the probability of the top event, the importance of
each basic event, hidden faults with proof tests and a common cause, and a Monte Carlo check.

Week: 14
Inputs: the probabilities of the basic events on demand, the minimal cut sets of the top event, the number of demands
per year; for hidden faults the failure rate, the proof test interval and the share of common causes.
Outputs: the probability of the top event per demand (exact for independent cut sets that share no event, otherwise the
rare event approximation and the upper bound), the top events per year, the Fussell-Vesely importance of each basic
event and an estimate from simulated demands.
Example: python fault_tree.py
The example is the critical supply of the campus microgrid: In an outage of the grid, the critical loads lose their
supply if the battery is below its reserve, the battery management system blocks, the inverter is under repair, both
island controllers have failed or the breaker fails to open. Requires NumPy.
"""
import math

import numpy as np


def hidden_fault(lam, tau):
    """Mean unavailability of one part with hidden faults at the rate lam and a proof test every tau years."""
    return lam * tau / 2


def hidden_pair(lam, tau, beta):
    """Mean unavailability of two such parts, one out of two, with a share beta of common causes."""
    return beta * lam * tau / 2 + ((1 - beta) * lam * tau) ** 2 / 3


def top_event(q, cuts):
    """Probability of the top event from minimal cut sets: exact if no event appears in two cut sets, otherwise the
    rare event approximation and the upper bound of the minimal cut sets."""
    p_cut = [math.prod(q[e] for e in c) for c in cuts]
    shared = len({e for c in cuts for e in c}) < sum(len(c) for c in cuts)
    bound = 1 - math.prod(1 - p for p in p_cut)
    return dict(p_cut=p_cut, rare=sum(p_cut), bound=bound, exact=None if shared else bound)


def importance(q, cuts):
    """Fussell-Vesely importance: the share of the probability of the top event in the cut sets with the event."""
    p_cut = [math.prod(q[e] for e in c) for c in cuts]
    total = sum(p_cut)
    return {e: sum(p for c, p in zip(cuts, p_cut) if e in c) / total for e in q}


def simulate(q, cuts, demands, seed=16):
    """Share of simulated demands in which every event of at least one cut set occurs."""
    rng = np.random.default_rng(seed)
    names = list(q)
    occurs = rng.random((demands, len(names))) < np.array([q[n] for n in names])
    col = {n: i for i, n in enumerate(names)}
    top = np.zeros(demands, bool)
    for c in cuts:
        top |= np.all(occurs[:, [col[e] for e in c]], axis=1)
    return float(top.mean())


def main():
    outages = 2.0                                       # outages of the grid per year that need the island
    lam, tau, beta = 0.1, 1.0, 0.1                      # hidden faults of a controller, yearly proof tests
    q_ind = hidden_fault((1 - beta) * lam, tau)         # independent part of one controller (for the simulation)
    q = {"battery below the reserve": 4 / 24, "battery management blocks": 0.004, "inverter under repair": 0.0082,
         "common cause of the controllers": hidden_fault(beta * lam, tau), "controller A": q_ind, "controller B": q_ind,
         "breaker fails to open": 0.003}
    cuts = [("battery below the reserve",), ("battery management blocks",), ("inverter under repair",),
            ("common cause of the controllers",), ("controller A", "controller B"), ("breaker fails to open",)]
    print(f"controller pair with the test interval: {hidden_pair(lam, tau, beta):.5f} "
          f"(independent demands give {hidden_fault(beta * lam, tau) + q_ind ** 2:.5f})")
    res = top_event(q, cuts)
    p = res["exact"] if res["exact"] is not None else res["bound"]
    print(f"P(top) per outage: {p:.5f} (rare event approximation {res['rare']:.5f})")
    print(f"losses per year: {outages * p:.4f}, one in {1 / (outages * p):.1f} years")
    for e, v in sorted(importance(q, cuts).items(), key=lambda x: -x[1]):
        print(f"  importance of {e:<34} {v:.3f}")
    print(f"simulation of 1,000,000 outages: P(top) = {simulate(q, cuts, 1_000_000):.5f}")
    q["battery below the reserve"] = 0.0
    p = top_event(q, cuts)["bound"]
    print(f"with the reserve rule: P(top) = {p:.5f}, {outages * p:.4f} losses per year")


if __name__ == "__main__":
    main()
