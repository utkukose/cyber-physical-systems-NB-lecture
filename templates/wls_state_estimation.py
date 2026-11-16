"""State estimation by weighted least squares with the chi-square test and the largest normalized residual, removing
bad data one measurement at a time.

Week: 6
Inputs: the measurement matrix H (one row per reading), the standard deviation of each reading, the readings z and
the confidence of the test.
Outputs: the estimate, the test value J with its threshold, the normalized residuals and the list of removed readings.
Example: python wls_state_estimation.py
The example is the campus at 19:00: six feeders, six feeder meters, six building meters and a main meter, with an open
current transformer on the meter of feeder B3. Requires NumPy and SciPy.
"""
import numpy as np
from scipy.stats import chi2


def wls(H, sigma, z):
    """The estimate, J, the threshold of 99 percent and the normalized residuals for the given readings."""
    W = np.diag(1 / sigma ** 2)
    G = H.T @ W @ H
    x = np.linalg.solve(G, H.T @ W @ z)
    r = z - H @ x
    omega = sigma ** 2 - np.einsum("ij,jk,ik->i", H, np.linalg.inv(G), H)
    rn = np.abs(r) / np.sqrt(np.maximum(omega, 1e-12))
    return x, float(r @ W @ r), float(chi2.ppf(0.99, len(z) - H.shape[1])), rn


def estimate_with_bad_data(H, sigma, z, names, max_removals=3):
    """Repeats the estimate and removes the reading with the largest normalized residual while the test fails."""
    keep, removed = np.ones(len(z), bool), []
    while True:
        x, J, thr, rn = wls(H[keep], sigma[keep], z[keep])
        if J <= thr or len(removed) == max_removals or keep.sum() <= H.shape[1] + 1:
            return x, J, thr, removed
        i = int(np.flatnonzero(keep)[np.argmax(rn)])
        keep[i] = False
        removed.append(names[i])


if __name__ == "__main__":
    names = [f"{b} feeder" for b in ["B1", "B2", "B3", "B4", "B5", "Car park"]] + \
            [f"{b} building" for b in ["B1", "B2", "B3", "B4", "B5", "Car park"]] + ["Main meter"]
    H = np.vstack([np.eye(6), np.eye(6), np.ones((1, 6))])
    sigma = np.array([1.5] * 6 + [2.5] * 6 + [3.0])
    z = np.array([130.2, 88.4, 103.3, 64.1, 115.8, 90.0, 130.2, 89.5, 107.9, 65.7, 114.7, 85.3, 585.5])
    for label, zz in [("clean readings", z), ("open CT of B3", np.where(np.arange(13) == 2, 0.0, z))]:
        x, J, thr, removed = estimate_with_bad_data(H, sigma, zz, names)
        print(f"{label}: J = {J:.2f} against {thr:.2f}, removed {removed or 'none'}, estimate {np.round(x, 2)}")
