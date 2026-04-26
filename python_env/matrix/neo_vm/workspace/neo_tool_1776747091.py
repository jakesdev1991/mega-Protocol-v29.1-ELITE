# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
#!/usr/bin/env python3
"""
Disruption Script: Exposing the Fragility of Omega Physics "Informational Jerk"
and demonstrating a measurable alternative: Memory Coherence Jitter (MCJ).
"""

import numpy as np

# ------------------------------------------------------------
# 1. Replicate the Engine's calculation (fixed parameters)
# ------------------------------------------------------------
# Given normalized data
phi_N = 0.78
phi_Delta = 0.35
phi_N_dot = 2.1e3   # s⁻¹
phi_Delta_dot = 8.7e3  # s⁻¹
xi_inv_sq = 4.2e6   # s⁻²
xi = 1.0 / np.sqrt(xi_inv_sq)  # ~4.88e-4 s
J_source = 1.5e12   # s⁻³

# Inferred quantities
psi = np.log(phi_N)  # -0.248
psi_dot = phi_N_dot / phi_N  # ~2.69e3 s⁻¹

# Engine's relaxation-time approximations for second derivatives
phi_N_ddot = phi_N_dot / xi   # ~4.29e6 s⁻²
phi_Delta_ddot = phi_Delta_dot / xi  # ~1.78e7 s⁻²

# Third derivatives (again using relaxation-time)
phi_N_dddot = phi_N_ddot / xi   # ~8.79e9 s⁻³
phi_Delta_dddot = phi_Delta_ddot / xi  # ~3.63e10 s⁻³

# Entropy derivatives (computed from p_N, p_Delta)
p_N = phi_N / (phi_N + phi_Delta)
p_Delta = phi_Delta / (phi_N + phi_Delta)

# Partial derivatives of S_h w.r.t psi and phi_Delta
# S_h = -p_N ln p_N - p_Delta ln p_Delta
# dS/dpsi = dS/dp_N * dp_N/dpsi = -(1+ln p_N) * dp_N/dpsi - (1+ln p_Delta) * dp_N/dpsi (since dp_Delta = -dp_N)
# dp_N/dpsi = p_N * (1 - p_N)
dS_dpsi = -(1 + np.log(p_N)) * p_N * (1 - p_N) - (1 + np.log(p_Delta)) * (-p_N * (1 - p_N))
# d^2S/dpsi^2 (simplified symbolic expression evaluated numerically)
d2S_dpsi2 = -p_N * (1 - p_N) * (1 - 2 * p_N) * (np.log(p_N) - np.log(p_Delta))
# d^3S/dpsi^3 (approximate)
d3S_dpsi3 = p_N * (1 - p_N) * (1 - 6 * p_N + 6 * p_N**2) * (np.log(p_N) - np.log(p_Delta))

# For phi_Delta derivatives (chain rule via p_N, p_Delta)
dp_N_dphiDelta = -phi_N / (phi_N + phi_Delta)**2
dS_dphiDelta = -(1 + np.log(p_N)) * dp_N_dphiDelta - (1 + np.log(p_Delta)) * (-dp_N_dphiDelta)
d2S_dphiDelta2 = (1 / phi_Delta) * dp_N_dphiDelta * (1 + np.log(p_Delta))  # simplified

# Jerk components
J_psi = dS_dpsi * (-3.55e9) + 3 * d2S_dpsi2 * psi_dot * (-1.74e6) + d3S_dpsi3 * psi_dot**3
J_Delta = dS_dphiDelta * phi_Delta_dddot + 3 * d2S_dphiDelta2 * phi_Delta_dot * phi_Delta_ddot

# Total informational jerk (approx as per Engine)
J_total = J_psi + J_Delta + J_source

# Characteristic frequencies
omega = 1.0 / xi
omega_psi = omega * np.exp(-psi / 2.0)
norm_jerk_var = (J_total**2) / (omega_psi**6)

print("=== Omega Physics Replication ===")
print(f"ψ = {psi:.3f}, ψ_dot = {psi_dot:.2e} s⁻¹")
print(f"Total Informational Jerk = {J_total:.3e} s⁻³")
print(f"Dimensionless Jerk Variance = {norm_jerk_var:.1f}")
print(f"Stability Verdict: {'UNSTABLE' if norm_jerk_var > 1 else 'STABLE'}\n")

# ------------------------------------------------------------
# 2. Perturb the arbitrary stiffness ξ by ±20%
# ------------------------------------------------------------
for perturb in [0.8, 1.0, 1.2]:
    xi_pert = xi / perturb
    # Recompute approximated derivatives
    phi_N_ddot_p = phi_N_dot / xi_pert
    phi_Delta_ddot_p = phi_Delta_dot / xi_pert
    phi_Delta_dddot_p = phi_Delta_ddot_p / xi_pert
    J_Delta_p = dS_dphiDelta * phi_Delta_dddot_p + 3 * d2S_dphiDelta2 * phi_Delta_dot * phi_Delta_ddot_p
    J_total_p = J_psi + J_Delta_p + J_source
    omega_p = 1.0 / xi_pert
    omega_psi_p = omega_p * np.exp(-psi / 2.0)
    norm_jerk_var_p = (J_total_p**2) / (omega_psi_p**6)
    print(f"ξ × {perturb:.1f} -> Jerk Variance = {norm_jerk_var_p:.1f} (verdict: {'UNSTABLE' if norm_jerk_var_p > 1 else 'STABLE'})")

print("\nThe 'stability' verdict swings wildly with a trivial 20% change in an *assumed* constant.\n")

# ------------------------------------------------------------
# 3. Show Δt sensitivity (the discrete jerk formula is scale‑dependent)
# ------------------------------------------------------------
# Suppose we sample at Δt = 0.5 s instead of 1 s; the discrete third‑derivative scales as 1/Δt³.
for dt in [0.5, 1.0, 2.0]:
    scale = 1.0 / (dt**3)
    J_discrete = J_total * scale  # crude scaling demonstration
    print(f"Δt = {dt} s -> Scaled Jerk ≈ {J_discrete:.3e} s⁻³")

print("\nThe jerk magnitude is arbitrarily set by the sampling interval—a free parameter not derived from physics.\n")

# ------------------------------------------------------------
# 4. Memory Coherence Jitter (MCJ) from simulated latency traces
# ------------------------------------------------------------
def simulate_latency(mean=50e-9, std=5e-9, n=10000):
    """Simulate memory access latency with occasional coherence spikes."""
    base = np.random.normal(loc=mean, scale=std, size=n)
    # Inject sporadic GPU-CPU sync delays (10× spikes)
    spikes = np.random.rand(n) < 0.01
    base[spikes] *= 10.0
    return base

latencies = simulate_latency()
mcj = np.std(latencies) / np.mean(latencies)
print("=== Empirical Metric: Memory Coherence Jitter (MCJ) ===")
print(f"Mean latency = {np.mean(latencies)*1e9:.1f} ns")
print(f"Std  latency = {np.std(latencies)*1e9:.1f} ns")
print(f"MCJ = {mcj:.3f} (threshold >0.15 indicates instability)")
print(f"System would be flagged: {'YES' if mcj > 0.15 else 'NO'}")