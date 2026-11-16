"""Calibrates a sensor at two points, checks a sampling rate for aliasing, quantises a signal and filters its noise with
a moving average or an exponential filter.

Week: 4
Inputs: two calibration points, a signal frequency and a sampling rate, the bits and range of a converter, noisy
readings and the window or coefficient of a filter.
Outputs: gain and offset, the apparent frequency, the step and RMS error of the converter, the filtered readings with
their noise and delay.
Example: python signal_conditioning.py
The example follows the temperature sensor of the library, the grid voltage of 50 Hz and the frequency reading of the
campus. Requires NumPy.
"""
import math

import numpy as np


def two_point(c1, x1, c2, x2):
    """Gain and offset of the line x = gain * c + offset through two calibration points."""
    gain = (x2 - x1) / (c2 - c1)
    return gain, x1 - gain * c1


def alias(f, fs):
    """Apparent frequency of a sine of f Hz sampled at fs Hz."""
    return abs(f - fs * round(f / fs))


def quantise(x, bits, full_range):
    q = full_range / 2 ** bits
    return q * np.round(np.asarray(x, float) / q), q


def moving_average(x, n):
    return np.convolve(np.asarray(x, float), np.ones(n) / n, mode="valid")


def exponential(x, a):
    """First-order filter y[k] = y[k-1] + a (x[k] - y[k-1])."""
    y = np.empty(len(x))
    y[0] = x[0]
    for k in range(1, len(x)):
        y[k] = y[k - 1] + a * (x[k] - y[k - 1])
    return y


if __name__ == "__main__":
    gain, offset = two_point(635, 0.0, 1243, 50.0)
    print(f"calibration: gain {gain:.5f} K per count, offset {offset:.2f} C, 1000 counts = {gain * 1000 + offset:.2f} C")
    for fs in (1000, 110, 90, 60):
        print(f"50 Hz sampled at {fs:>4}/s appears at {alias(50, fs):5.1f} Hz")
    for bits in (8, 12, 16):
        _, q = quantise([0.0], bits, 10.0)
        print(f"{bits:>2} bits over 10 V: step {1000 * q:.3f} mV, RMS error {1000 * q / math.sqrt(12):.3f} mV")
    rng = np.random.default_rng(42)
    f = 50 + rng.normal(0, 0.025, 3000)
    for n in (1, 7, 25):
        print(f"moving average of {n:>2}: noise {1000 * moving_average(f, n).std():5.2f} mHz, delay {(n - 1) / 2 * 10:5.1f} ms")
    for a in (0.5, 0.25, 0.1):
        y = exponential(f, a)
        print(f"exponential filter a = {a}: noise {1000 * y[100:].std():5.2f} mHz, time constant {10 * (1 - a) / a:5.1f} ms")
