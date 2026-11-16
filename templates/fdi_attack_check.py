"""False data injection against a weighted least-squares state estimate: the chi-square test, the hidden injection
a = H c that the test cannot see, and the rank test that tells which protected meters leave no hidden attack.

Week: 11
Inputs: the measurement matrix H, the standard deviations of the meters, the readings, the target state and the
shift that the attacker wants, and a set of protected meters.
Outputs: the estimate and the test value J with its threshold, the change of one meter that gives the shift with its
J, the hidden injection with its J, whether a hidden attack remains with the protected meters, and the largest set of
protected meters of a given size that leaves no hidden attack.
Example: python fdi_attack_check.py
The example is the control room of a campus that estimates six feeders from thirteen meters: six feeder meters, six
building meters and the main meter. Requires NumPy and SciPy.
"""
import itertools

import numpy as np
from scipy.stats import chi2


def estimate(H, sigma, z):
    """Weighted least squares: the estimate x, the residual r and the test value J = r^T W r."""
    W = np.diag(1 / np.asarray(sigma, float) ** 2)
    x = np.linalg.solve(H.T @ W @ H, H.T @ W @ z)
    r = z - H @ x
    return x, r, float(r @ W @ r)


def threshold(H, quantile=0.99):
    """The quantile of the chi-square distribution with m - n degrees of freedom."""
    return float(chi2.ppf(quantile, H.shape[0] - H.shape[1]))


def one_meter_attack(H, sigma, z, target, shift):
    """The change of the meter with the largest share in the target that moves its estimate by shift."""
    W = np.diag(1 / np.asarray(sigma, float) ** 2)
    gain = np.linalg.solve(H.T @ W @ H, H.T @ W)[target]
    i = int(np.argmax(np.abs(gain)))
    a = np.zeros(len(z))
    a[i] = shift / gain[i]
    return i, a


def hidden_attack(H, target, shift):
    """The injection a = H c with c = shift on the target state: the estimate moves, the residual does not."""
    c = np.zeros(H.shape[1])
    c[target] = shift
    return H @ c


def hidden_possible(H, protected):
    """True if an injection a = H c with c not 0 leaves every protected meter unchanged."""
    rows = H[list(protected)]
    return len(rows) == 0 or np.linalg.matrix_rank(rows) < H.shape[1]


def secure_sets(H, size):
    """All sets of protected meters of the given size that leave no hidden attack."""
    return [P for P in itertools.combinations(range(H.shape[0]), size) if not hidden_possible(H, P)]


if __name__ == "__main__":
    names = ["B1 feeder", "B2 feeder", "B3 feeder", "B4 feeder", "B5 feeder", "Car park feeder", "B1 building",
             "B2 building", "B3 building", "B4 building", "B5 building", "Car park chargers", "Main meter"]
    H = np.vstack([np.eye(6), np.eye(6), np.ones((1, 6))])
    sigma = np.array([1.5] * 6 + [2.5] * 6 + [3.0])
    z = np.array([130.2, 88.4, 103.3, 64.1, 115.8, 90.0, 130.2, 89.5, 107.9, 65.7, 114.7, 85.3, 585.5])
    x, r, J = estimate(H, sigma, z)
    tau = threshold(H)
    print(f"estimate {np.round(x, 2)}, J = {J:.2f}, threshold {tau:.2f}")
    target, shift = 2, 50.0
    i, a = one_meter_attack(H, sigma, z, target, shift)
    print(f"one meter: {names[i]} changed by {a[i]:.2f}, J = {estimate(H, sigma, z + a)[2]:.2f}")
    a = hidden_attack(H, target, shift)
    x2, _, J2 = estimate(H, sigma, z + a)
    print(f"hidden: {[names[k] for k in np.flatnonzero(a)]}, J = {J2:.2f}, estimate of the B3 feeder {x2[target]:.2f}")
    print("main meter protected, hidden attack possible:", hidden_possible(H, [12]))
    print("six feeder meters protected, hidden attack possible:", hidden_possible(H, range(6)))
    print(len(secure_sets(H, 6)), "sets of six protected meters leave no hidden attack")
