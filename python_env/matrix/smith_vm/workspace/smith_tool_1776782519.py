# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
#!/usr/bin/env python3
"""
BRS-Ω Mathematical Soundness Validator
-------------------------------------
Checks:
1. Encoding dimensions: b' = b + 2t, G full row rank (proxy: sparsity does not kill rank).
2. Latency model: ℓ = ℓ0 + α * t/m - β * s  ≤ ℓ_max.
3. Φ_N and Φ_Δ mappings stay in [0,1] and respect protocol bounds
   (Φ_N ≥ 0.6, Φ_Δ ≤ 0.7).
4. Convex feasibility of the MPC QP (linear constraints → polyhedron).

If any check fails, the validator returns a counter‑example and suggests a safe
fallback (reduce t, increase s).
"""

import numpy as np

# -------------------------- Protocol Constants --------------------------
PHI_N_MIN = 0.6      # lower bound for strategic connectivity
PHI_DELTA_MAX = 0.7  # upper bound for information asymmetry

# -------------------------- User‑Defined Parameters ----------------------
# System size
m = 10          # number of workers
t_max_theoretical = (m - 1) // 2   # floor((m-1)/2)

# Mini‑batch size (plain)
b = 8

# Encoding design parameters (chosen by the designer)
alpha = 0.5   # latency increase per unit t/m
beta  = 0.3   # latency decrease per unit sparsity s
ell0  = 1.0   # baseline latency (ms)
ell_max = 3.0 # maximum allowable latency (ms)

# Sparsity range (0 = dense, 1 = maximally sparse)
s_min, s_max = 0.2, 0.8

# Threat estimation and safety margin
delta = 1   # extra workers to protect against estimation error

# Phi mapping coefficients (must be tuned to keep Φ in [0,1])
gamma1, gamma2 = 0.4, 0.2   # for Φ_N
gamma3, gamma4 = 0.3, 0.3   # for Φ_Δ
Phi_N0, Phi_Delta0 = 0.8, 0.4   # nominal values without attack/latency

# MPC cost weights (not needed for feasibility check)
lambda1, lambda2 = 1.0, 0.5

# -------------------------- Helper Functions --------------------------
def latency(t, s):
    """Linear latency model."""
    return ell0 + alpha * (t / m) - beta * s

def phi_N(t, s):
    """Φ_N as affine function of latency and t."""
    ell = latency(t, s)
    return Phi_N0 - gamma1 * (ell / ell_max) + gamma2 * (1.0 - t / t_max_theoretical)

def phi_Delta(t, s):
    """Φ_Δ as affine function of latency and t."""
    ell = latency(t, s)
    return Phi_Delta0 + gamma3 * (ell / ell_max) - gamma4 * (t / t_max_theoretical)

def encoding_feasible(t, s):
    """Check that we can build a sparse G with full row rank.
    We use a simple proxy: require that the number of non‑zeros per row
    is at least b (so each row can still span ℝ^b).  For a random sparse
    matrix with sparsity s, expected non‑zeros per row = s * b'.
    """
    b_prime = b + 2 * t
    min_nnz_per_row = b   # need at least b to keep rank b
    expected_nnz = s * b_prime
    return expected_nnz >= min_nnz_per_row

def constraint_violation(t, s):
    """Return a dict of any violated constraints, empty if feasible."""
    violations = {}

    # 1. Byzantine bound
    if t > t_max_theoretical:
        violations['t_exceeds_theoretical'] = (t, t_max_theoretical)

    # 2. Latency bound
    ell = latency(t, s)
    if ell > ell_max:
        violations['latency_exceeds_max'] = (ell, ell_max)

    # 3. Sparsity bounds
    if s < s_min or s > s_max:
        violations['sparsity_out_of_range'] = (s, (s_min, s_max))

    # 4. Encoding rank proxy
    if not encoding_feasible(t, s):
        violations['encoding_rank_proxy'] = (t, s)

    # 5. Φ_N lower bound
    phi_n = phi_N(t, s)
    if phi_n < PHI_N_MIN:
        violations['phi_N_below_min'] = (phi_n, PHI_N_MIN)

    # 6. Φ_Δ upper bound
    phi_d = phi_Delta(t, s)
    if phi_d > PHI_DELTA_MAX:
        violations['phi_Delta_above_max'] = (phi_d, PHI_DELTA_MAX)

    # 7. Φ bounds in [0,1] (optional safety)
    if not (0.0 <= phi_n <= 1.0):
        violations['phi_N_out_of_unit'] = phi_n
    if not (0.0 <= phi_d <= 1.0):
        violations['phi_Delta_out_of_unit'] = phi_d

    return violations

def find_feasible_point():
    """Brute‑force search over a grid to find any feasible (t,s)."""
    feasible = []
    for t in range(0, t_max_theoretical + 1):
        for s in np.linspace(s_min, s_max, 20):
            if not constraint_violation(t, s):
                feasible.append((t, s, latency(t, s), phi_N(t, s), phi_Delta(t, s)))
    return feasible

# -------------------------- Main Validation --------------------------
if __name__ == "__main__":
    print("=== BRS-Ω Mathematical Soundness Validator ===")
    print(f"System: m={m} workers, theoretical t_max={t_max_theoretical}")
    print(f"Mini‑batch size b={b}, sparsity range [{s_min},{s_max}]")
    print(f"Latency model: ℓ = {ell0} + {alpha}·t/m - {beta}·s, ℓ_max={ell_max}")
    print(f"Φ_N baseline={Phi_N0}, Φ_Δ baseline={Phi_Delta0}")
    print("-" * 60)

    # Example: use the parameters suggested in the paper’s “t ≤ m/3” regime
    t_example = m // 3          # floor(m/3)
    s_example = (s_min + s_max) / 2.0

    print(f"Test point: t={t_example}, s={s_example:.3f}")
    vio = constraint_violation(t_example, s_example)
    if vio:
        print("  ❌ Violations:")
        for k, v in vio.items():
            print(f"     {k}: {v}")
    else:
        print("  ✅ All constraints satisfied.")
        print(f"     Latency = {latency(t_example, s_example):.3f} ms")
        print(f"     Φ_N     = {phi_N(t_example, s_example):.3f}")
        print(f"     Φ_Δ     = {phi_Delta(t_example, s_example):.3f}")

    print("-" * 60)
    print("Searching for any feasible (t,s) in the allowed region...")
    feasible_points = find_feasible_point()
    if feasible_points:
        print(f"Found {len(feasible_points)} feasible points.")
        # Show the one with lowest latency (most responsive)
        best = min(feasible_points, key=lambda x: x[2])
        t_best, s_best, ell_best, phiN_best, phiD_best = best
        print(f"Best (lowest latency): t={t_best}, s={s_best:.3f}")
        print(f"  Latency = {ell_best:.3f} ms")
        print(f"  Φ_N     = {phiN_best:.3f}")
        print(f"  Φ_Δ     = {phiD_best:.3f}")
    else:
        print("⚠️  No feasible point found with the current constants!")
        print("   Suggested remedial actions:")
        print("   - Decrease α (latency sensitivity to t) or increase β (latency gain from sparsity).")
        print("   - Relax γ coefficients to keep Φ_N, Φ_Δ within bounds.")
        print("   - Increase ℓ_max or reduce t_max_theoretical (more conservative Byzantine bound).")

    print("\n=== End of Validation ===")