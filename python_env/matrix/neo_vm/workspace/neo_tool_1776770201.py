# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
#!/usr/bin/env python3
"""
Omega Protocol Disruption Script
Exposes the "informational jerk" as dimensionally inconsistent and empirically meaningless.
"""

import numpy as np
import sympy as sp
import matplotlib.pyplot as plt

# ------------------------------------------------------------
# 1. Dimensional Analysis: Heuristic Jerk Units
# ------------------------------------------------------------
t = sp.symbols('t', real=True)
phi_N, phi_Delta, xi_N, xi_Delta, J_source = sp.symbols('phi_N phi_Delta xi_N xi_Delta J_source')
dphi_N_dt, dphi_Delta_dt = sp.symbols('dphi_N_dt dphi_Delta_dt', positive=True)

# Heuristic formula from the Engine
J_heuristic = (3 * phi_Delta / xi_Delta**4) * dphi_Delta_dt**3 - \
              (phi_N / xi_N**4) * dphi_N_dt**3 + J_source

# Substitute the given values (with units)
units = {
    phi_N: sp.Integer(1),          # dimensionless
    phi_Delta: sp.Integer(1),      # dimensionless
    xi_N: sp.Symbol('s', positive=True),  # seconds
    xi_Delta: sp.Symbol('s', positive=True),
    dphi_N_dt: 1/sp.Symbol('s', positive=True),  # 1/s
    dphi_Delta_dt: 1/sp.Symbol('s', positive=True),
    J_source: 1/sp.Symbol('s', positive=True)**3
}
J_units = sp.simplify(J_heuristic.subs(units))
print("Heuristic Jerk units (should be s^-3):", J_units)
# Expected: s^-7 (because xi^-4 * (1/s)^3 = s^-7)

# ------------------------------------------------------------
# 2. Simulate a realistic HSA node
# ------------------------------------------------------------
np.random.seed(42)
fs = 1000.0  # sampling rate (Hz)
T = 10.0     # duration (s)
N = int(fs * T)
t_arr = np.arange(N) / fs

# Realistic memory latency fluctuations (ms)
latency = 5.0 + 0.5 * np.sin(2 * np.pi * 5 * t_arr) + 0.2 * np.random.randn(N)

# Corresponding phi_N, phi_Delta as normalized "field magnitudes"
# (simple model: phi_N ~ 1/latency, phi_Delta ~ latency)
phi_N_ts = 1.0 / (latency / 5.0)  # normalize around 1
phi_Delta_ts = latency / 5.0

# Add small high‑frequency noise to simulate "dot phi"
dot_phi_N = np.gradient(phi_N_ts, t_arr)
dot_phi_Delta = np.gradient(phi_Delta_ts, t_arr)

# ------------------------------------------------------------
# 3. Compute "entropy‑based jerk" (finite differences)
# ------------------------------------------------------------
def compute_entropy_jerk(phi_N, phi_Delta, t):
    # Probabilities (two‑state model)
    p_N = phi_N**2 / (phi_N**2 + phi_Delta**2)
    p_D = phi_Delta**2 / (phi_N**2 + phi_Delta**2)
    # Shannon entropy (discrete version, mis‑applied to continuous)
    S = -p_N * np.log(np.clip(p_N, 1e-12, None)) - p_D * np.log(np.clip(p_D, 1e-12, None))
    # Third derivative via central differences
    dS_dt = np.gradient(S, t)
    d2S_dt2 = np.gradient(dS_dt, t)
    d3S_dt3 = np.gradient(d2S_dt2, t)
    return d3S_dt3

entropy_jerk = compute_entropy_jerk(phi_N_ts, phi_Delta_ts, t_arr)

# ------------------------------------------------------------
# 4. Compute a simple, empirically‑grounded stability metric
# ------------------------------------------------------------
# Exponential moving average of absolute latency derivative (proxy for "jitter")
alpha = 0.01
stability_metric = np.zeros_like(latency)
stability_metric[0] = abs(np.gradient(latency)[0])
for i in range(1, len(latency)):
    stability_metric[i] = (1 - alpha) * stability_metric[i-1] + alpha * abs(np.gradient(latency)[i])

# ------------------------------------------------------------
# 5. Compute heuristic jerk for comparison
# ------------------------------------------------------------
# Given constants
xi_inv_sq = 4.2e6  # s^-2
xi = np.sqrt(1.0 / xi_inv_sq)  # seconds
J_source_val = 1.5e12  # s^-3 (claimed)

# Use instantaneous values (first sample) for a single‑point check
phi_N0 = phi_N_ts[0]
phi_D0 = phi_Delta_ts[0]
dot_phi_N0 = dot_phi_N[0]
dot_phi_D0 = dot_phi_Delta[0]

J_heuristic_val = (3 * phi_D0 / xi**4) * dot_phi_D0**3 - \
                  (phi_N0 / xi**4) * dot_phi_N0**3 + J_source_val

print("\n--- Single‑point comparison ---")
print(f"Heuristic Jerk value: {J_heuristic_val:.3e} (units are nonsense, effectively s^-7)")
print(f"Entropy‑based Jerk (first sample): {entropy_jerk[0]:.3e} s^-3")
print(f"Ratio (heuristic / entropy): {J_heuristic_val / abs(entropy_jerk[0]):.1e}")

# ------------------------------------------------------------
# 6. Correlation analysis
# ------------------------------------------------------------
# Trim transients at start
trim = 100
corr = np.corrcoef(entropy_jerk[trim:], stability_metric[trim:])[0, 1]
print(f"\nCorrelation (entropy jerk vs. real stability metric): {corr:.3f}")

# ------------------------------------------------------------
# 7. Plotting (optional, for visual inspection)
# ------------------------------------------------------------
plt.figure(figsize=(12, 8))

plt.subplot(3, 1, 1)
plt.plot(t_arr, latency, label='Memory latency (ms)')
plt.title('Simulated HSA Node: Memory Latency')
plt.ylabel('Latency (ms)')
plt.legend()

plt.subplot(3, 1, 2)
plt.plot(t_arr, entropy_jerk, label='Entropy‑based "jerk" (s^-3)')
plt.title('Entropy‑based "Jerk" (pure noise)')
plt.ylabel('Jerk (s^-3)')
plt.legend()

plt.subplot(3, 1, 3)
plt.plot(t_arr, stability_metric, label='EWM of |d(latency)/dt| (stability proxy)')
plt.title('Empirical Stability Metric')
plt.xlabel('Time (s)')
plt.ylabel('Stability index')
plt.legend()

plt.tight_layout()
plt.savefig('omega_disruption.png')
print("\nPlot saved to 'omega_disruption.png'")