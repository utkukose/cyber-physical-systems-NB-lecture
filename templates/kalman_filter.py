"""A Kalman filter for any linear model, written as a class, with an example that tracks the state of charge of a
battery and the offset of its current sensor.

Week: 6
Inputs: the matrices A, B, H, Q and R of the model x[k+1] = A x[k] + B u[k] + w, z[k] = H x[k] + v, an initial state
and its covariance; then, at each step, an input u and a measurement z (or None when a reading is missing).
Outputs: the estimate, its covariance and the innovation of each step.
Example: python kalman_filter.py
The example is the battery of the campus: 500 kWh, an efficiency of 0.95, readings every minute, a current sensor that
reads 5 kW too little and a state of charge from the voltage with a noise of 0.01. Requires NumPy.
"""
import numpy as np


class KalmanFilter:
    """Predict with predict(u), correct with update(z); the attributes x and P hold the estimate and its covariance."""

    def __init__(self, A, B, H, Q, R, x0, P0):
        self.A, self.B, self.H = (np.atleast_2d(np.asarray(m, float)) for m in (A, B, H))
        self.Q, self.R = np.atleast_2d(np.asarray(Q, float)), np.atleast_2d(np.asarray(R, float))
        self.x, self.P = np.asarray(x0, float).ravel(), np.atleast_2d(np.asarray(P0, float))

    def predict(self, u=0.0):
        self.x = self.A @ self.x + (self.B @ np.atleast_1d(np.asarray(u, float))).ravel()
        self.P = self.A @ self.P @ self.A.T + self.Q
        return self.x

    def update(self, z):
        if z is None:                                   # a missing reading: keep the prediction
            return self.x, None
        nu = np.atleast_1d(np.asarray(z, float)) - self.H @ self.x
        S = self.H @ self.P @ self.H.T + self.R
        K = self.P @ self.H.T @ np.linalg.inv(S)
        self.x = self.x + K @ nu
        I_KH = np.eye(len(self.x)) - K @ self.H
        self.P = I_KH @ self.P @ I_KH.T + K @ self.R @ K.T   # the symmetric form keeps P symmetric and positive
        return self.x, nu


if __name__ == "__main__":
    rng = np.random.default_rng(6)
    c = (1 / 60) / (0.95 * 500)                         # state of charge per kW and minute
    power = np.repeat([52.9, 130.5, 135.7, 39.9], 60)   # the evening of 17:00 to 21:00
    soc = 0.9 - np.concatenate([[0.0], np.cumsum(power * c)])
    kf = KalmanFilter(A=[[1, c], [0, 1]], B=[[-c], [0]], H=[[1, 0]], Q=np.diag([1e-8, 1e-6]), R=[[1e-4]],
                      x0=[0.95, 0.0], P0=np.diag([0.05 ** 2, 100.0]))
    errors = []
    for k, p in enumerate(power):
        kf.predict(p - 5.0 + rng.normal(0, 2.0))       # the measured power reads 5 kW too little
        z = soc[k + 1] + rng.normal(0, 0.01) if k % 10 != 9 else None   # every tenth reading is lost
        kf.update(z)
        errors.append(kf.x[0] - soc[k + 1])
        if (k + 1) % 60 == 0:
            print(f"{17 + (k + 1) // 60}:00  state of charge {kf.x[0]:.4f} (true {soc[k + 1]:.4f}), "
                  f"offset {kf.x[1]:6.2f} kW +- {np.sqrt(kf.P[1, 1]):.2f}")
    print(f"RMS error over the evening: {np.sqrt(np.mean(np.square(errors))):.4f}")
