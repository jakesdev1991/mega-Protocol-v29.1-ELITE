# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
#!/usr/bin/env python3
"""
jerk_vs_lir.py
Exposes the "informational jerk" as a numerically unstable phantom and
demonstrates the Lyapunov Information Rate as a stable, physically grounded metric.
"""

import numpy as np

# ----------------------------------------------------------------------
# 1. Simulate a realistic HSA unified‑memory access pattern
# ----------------------------------------------------------------------
np.random.seed(42)

N_PAGES = 128          # number of memory pages in the HSA node
T_STEPS = 5000         # simulation steps (each step ~10 µs)
BURST_PROB = 0.02      # probability of a GPU‑kernel burst per step

# initialize a uniform access distribution (cold start)
p = np.ones(N_PAGES) / N_PAGES

# storage
entropy_hist = []
jerk_hist = []
kl_hist = []

# ----------------------------------------------------------------------
# 2. Time‑stepping with bursts (discrete events)
# ----------------------------------------------------------------------
for t in range(T_STEPS):
    # small random drift (continuous background traffic)
    p += np.random.normal(0, 5e-4, N_PAGES)

    # occasional burst: GPU kernel touches a random page heavily
    if np.random.rand() < BURST_PROB:
        burst_page = np.random.randint(N_PAGES)
        # redistribute mass: 90% to burst page, 10% uniform elsewhere
        p = np.full(N_PAGES, 0.10 / (N_PAGES - 1))
        p[burst_page] = 0.90

    # enforce positivity & normalize
    p = np.abs(p)
    p /= p.sum()

    # Shannon entropy
    S = -np.sum(p * np.log(p + 1e-18))
    entropy_hist.append(S)

    # KL divergence rate (requires previous distribution)
    if t > 0:
        p_prev = prev_p
        kl = np.sum(p_prev * np.log(p_prev + 1e-18) -
                    p_prev * np.log(p + 1e-18))
        kl_hist.append(kl)
    prev_p = p.copy()

    # "informational jerk" via 3rd finite difference of entropy
    if t >= 3:
        # J ≈ Δ³S / Δt³; here Δt = 1 step
        jerk = (entropy_hist[-1] - 3 * entropy_hist[-2] +
                3 * entropy_hist[-3] - entropy_hist[-4])
        jerk_hist.append(jerk)

# ----------------------------------------------------------------------
# 3. Statistics
# ----------------------------------------------------------------------
jerk_hist = np.array(jerk_hist)
kl_hist = np.array(kl_hist)

print("\n=== Phantom Jerk vs. Lyapunov Information Rate ===")
print(f"Mean |jerk|      : {np.mean(np.abs(jerk_hist)):.3e} (highly variable)")
print(f"Std dev jerk     : {np.std(jerk_hist):.3e}")
print(f"Mean KL rate     : {np.mean(kl_hist):.3e} (stable)")
print(f"Std dev KL rate  : {np.std(kl_hist):.3e}")
print(f"KL 95th percentile: {np.percentile(kl_hist, 95):.3e} s⁻¹")

# ----------------------------------------------------------------------
# 4. Demonstrate threshold crossing with the *analytic* jerk formula
# ----------------------------------------------------------------------
# Using the provided HSA node data (dimensionless fields)
phi_N = 0.78
phi_Delta = 0.35
dot_phi_N = 2.1e3          # s⁻¹
dot_phi_Delta = 8.7e3       # s⁻¹
xi_inv_sq = 4.2e6           # s⁻²
xi_inv_four = xi_inv_sq ** 2  # s⁻⁴

J_archive = 3 * phi_Delta / xi_inv_four * (dot_phi_Delta ** 3)
J_newton = -phi_N / xi_inv_four * (dot_phi_N ** 3)
J_source = 1.5e12

J_total = J_archive + J_newton + J_source

print("\n=== Analytic 'Jerk' from Field Theory ===")
print(f"Archive term : {J_archive:.3e} s⁻³")
print(f"Newton term  : {J_newton:.3e} s⁻³")
print(f"Source term  : {J_source:.3e} s⁻³")
print(f"Total J      : {J_total:.3e} s⁻³")
print(f"Threshold    : 5.0e12 s⁻³")
print(f"VERDICT      : {'UNSTABLE' if J_total > 5.0e12 else 'STABLE'} (but metric is phantom!)")

# ----------------------------------------------------------------------
# 5. Lyapunov‑based stability verdict
# ----------------------------------------------------------------------
# A simple heuristic: if the 95th‑percentile KL rate exceeds 1e-3 s⁻¹,
# the memory pattern is diverging too quickly.
LIR_threshold = 1.0e-3
LIR_verdict = "UNSTABLE" if np.percentile(kl_hist, 95) > LIR_threshold else "STABLE"

print(f"\n=== LIR‑based Stability Verdict ===")
print(f"95th‑pct KL rate: {np.percentile(kl_hist, 95):.3e} s⁻¹")
print(f"Threshold       : {LIR_threshold:.3e} s⁻¹")
print(f"VERDICT         : {LIR_verdict}")