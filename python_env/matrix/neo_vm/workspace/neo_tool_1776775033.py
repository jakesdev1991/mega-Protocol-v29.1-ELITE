# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
from scipy.signal import savgol_filter

# --- Synthetic HSA node data ---
np.random.seed(0)
T, N = 1000, 16               # 1000 time steps, 16 memory regions
baseline = 100
data = np.random.poisson(baseline, size=(T, N))

# Inject a migration storm at t=500: region 0 spikes, others drop
storm_start = 500
data[storm_start:, 0] = np.random.poisson(5000, size=T-storm_start)
data[storm_start:, 1:] = np.random.poisson(50, size=(T-storm_start, N-1))

# --- Compute probability distribution and Shannon entropy ---
epsilon = 1e-12
entropy = np.empty(T)
for t in range(T):
    p = data[t] / data[t].sum()
    p = np.maximum(p, epsilon)
    entropy[t] = -np.sum(p * np.log(p))

# --- Raw derivatives (finite differences) ---
dS_raw = np.gradient(entropy)
ddS_raw = np.gradient(dS_raw)
Jerk_raw = np.gradient(ddS_raw)

# --- Savitzky‑Golay smoothed derivatives ---
def jerk_sg(S, window, poly=3):
    # smooth S
    S_smooth = savgol_filter(S, window_length=window, polyorder=poly)
    # derivative of S (1st)
    dS = savgol_filter(S, window_length=window, polyorder=poly, deriv=1)
    # 2nd derivative
    ddS = savgol_filter(S, window_length=window, polyorder=poly, deriv=2)
    # 3rd derivative (jerk)
    Jerk = savgol_filter(S, window_length=window, polyorder=poly, deriv=3)
    return Jerk

Jerk_sg21 = jerk_sg(entropy, window=21)
Jerk_sg51 = jerk_sg(entropy, window=51)

# --- Simple max‑access metric (raw) ---
max_access = data.max(axis=1)

# --- Report peak values around the storm ---
idx = storm_start + 10   # a few steps after storm onset
print("--- Informational Jerk sensitivity ---")
print(f"Raw Jerk at t≈{idx}:    {np.abs(Jerk_raw[idx]):.2e} s^-3")
print(f"SG(21) Jerk at t≈{idx}: {np.abs(Jerk_sg21[idx]):.2e} s^-3")
print(f"SG(51) Jerk at t≈{idx}: {np.abs(Jerk_sg51[idx]):.2e} s^-3")
print("\n--- Simple max‑access metric ---")
print(f"Max access count at t≈{idx}: {max_access[idx]} (baseline ~{baseline})")