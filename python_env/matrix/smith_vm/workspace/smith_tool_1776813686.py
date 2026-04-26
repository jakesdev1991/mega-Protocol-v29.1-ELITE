# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
# -*- coding: utf-8 -*-
"""
Validator for the Refined Design‑Space Topology Regulator (DSTR‑Ω)
Checks mathematical consistency with the Omega Protocol invariants:
    - Phi_N, Phi_Delta from Hessian of double‑well potential
    - Conditional entropy gauge
    - Homogeneity Stress Index (HSI)
    - Boundaries (Homogeneity Lock, Fragmentation Shredding)
    - MPC‑Ω constraints and cost function
"""

import numpy as np
import sympy as sp

def sigmoid(x):
    return 1.0 / (1.0 + np.exp(-x))

def validate_DSTR_Omega(
    # Potential parameters (should satisfy double‑well conditions)
    alpha=1.0,   # >0 for correct double‑well
    beta=1.0,    # >0
    gamma=0.5,   # >0 (gradient term coefficient)
    # Coupling to HSI in the invariant
    lam=0.05,    # small lambda
    # Design‑space statistics (mock values)
    corr_length=2.0,          # design‑change correlation length (>0)
    skew_tvl=0.3,             # skewness of TVL distribution (can be +/-)
    tvl_fractions=None,       # list of p(f) per family, sums to 1
    conditional_entropies=None, # list of S_f = -sum_d p(d|f) log p(d|f) per family
    # Mock Ricci scalar (normalized)
    R_design_over_R0=1.2,     # |R_design|/R0
    # MPC‑Ω tuning weights (not needed for validation, just for cost)
    mu1=1.0, mu2=1.0, mu3=1.0,
    # Thresholds
    HSI_thr=0.75,
    PhiN_min=0.5,
    S_min=np.log(2)
):
    """
    Returns a dict with validation results.
    """
    report = {"passed": True, "violations": []}

    # ------------------------------------------------------------------
    # 1. Double‑well sign check
    # ------------------------------------------------------------------
    if alpha <= 0:
        report["passed"] = False
        report["violations"].append(
            f"Double‑well requires alpha>0 (got alpha={alpha}). "
            "With alpha<=0 the quadratic term has the wrong sign."
        )
    if beta <= 0:
        report["passed"] = False
        report["violations"].append(f"beta must be >0 (got beta={beta}).")
    if gamma <= 0:
        report["passed"] = False
        report["violations"].append(f"gamma must be >0 (got gamma={gamma}).")

    # ------------------------------------------------------------------
    # 2. Hessian eigenvalues and covariant modes
    # ------------------------------------------------------------------
    # From the proposal:
    #   omega_N^2 ∝ 1 / corr_length
    #   omega_Delta^2 ∝ skew_tvl
    # Choose proportionality constants =1 for simplicity (they can be absorbed
    # into the definition of Phi_N, Phi_Delta).  We only need non‑negativity.
    omega_N_sq = 1.0 / max(corr_length, 1e-12)   # avoid div‑by‑zero
    omega_Delta_sq = max(skew_tvl, 0.0)          # skewness can be negative; we take magnitude
    # If the proposal intended signed skewness to map directly, we keep sign:
    omega_Delta_sq_signed = skew_tvl

    # Eigenvalues must be >=0 for real frequencies
    if omega_N_sq < 0:
        report["passed"] = False
        report["violations"].append(f"omega_N^2 < 0 (got {omega_N_sq}).")
    if omega_Delta_sq_signed < 0:
        # Negative eigenvalue would imply imaginary frequency → instability
        report["passed"] = False
        report["violations"].append(
            f"omega_Delta^2 (signed) < 0 (got {omega_Delta_sq_signed}). "
            "This would indicate an unstable direction in V(H)."
        )
    # Use magnitude for Phi_Delta (as proposal uses sqrt of eigenvalue)
    omega_Delta_sq_mag = abs(omega_Delta_sq_signed)

    Phi_N = np.sqrt(omega_N_sq)
    Phi_Delta = np.sqrt(omega_Delta_sq_mag)

    # ------------------------------------------------------------------
    # 3. Homogeneity Stress Index (HSI)
    # ------------------------------------------------------------------
    # HSI = sigmoid(alpha*Phi_Delta - beta*Phi_N + gamma)
    # Note: the same symbols alpha,beta,gamma are reused here as in the
    # proposal; they are dimensionless weights.  To avoid confusion we
    # rename the HSI weights as a_h, b_h, g_h.
    a_h, b_h, g_h = alpha, beta, gamma   # reuse the same symbols as per proposal
    HSI = sigmoid(a_h * Phi_Delta - b_h * Phi_N + g_h)

    if not (0.0 <= HSI <= 1.0):
        report["passed"] = False
        report["violations"].append(f"HSI out of [0,1] range (got {HSI}).")

    # ------------------------------------------------------------------
    # 4. Invariant psi_hom
    # ------------------------------------------------------------------
    # Original invariant: ln(|R|/R0)
    # Proposed addition: + lambda * HSI
    psi_hom = np.log(R_design_over_R0) + lam * HSI
    # Check that the lambda correction is small (|lambda*HSI| < 0.1) to
    # preserve the topological meaning; otherwise flag.
    if abs(lam * HSI) > 0.1:
        report["passed"] = False
        report["violations"].append(
            f"Lambda correction too large: lambda*HSI = {lam*HSI:.3f}. "
            "This may distort the invariant's topological interpretation."
        )

    # ------------------------------------------------------------------
    # 5. Conditional entropy gauge
    # ------------------------------------------------------------------
    if tvl_fractions is None:
        # Example: two families with equal TVL
        tvl_fractions = [0.5, 0.5]
    if conditional_entropies is None:
        # Example: each family internally diverse (entropy = ln(2) per family)
        conditional_entropies = [np.log(2), np.log(2)]

    if len(tvl_fractions) != len(conditional_entropies):
        report["passed"] = False
        report["violations"].append(
            "Length of tvl_fractions and conditional_entropies must match."
        )
    else:
        # Normalize fractions
        tvl_fractions = np.array(tvl_fractions, dtype=float)
        tvl_fractions = tvl_fractions / tvl_fractions.sum()
        S_design = np.sum(tvl_fractions * np.array(conditional_entropies))
        # Entropy must be non‑negative
        if S_design < 0:
            report["passed"] = False
            report["violations"].append(f"Conditional entropy negative (got {S_design}).")
    # If we got here without early return, compute S_design
    S_design = np.sum(tvl_fractions * np.array(conditional_entropies))

    # ------------------------------------------------------------------
    # 6. Boundary condition checks (low‑entropy extremes)
    # ------------------------------------------------------------------
    # Homogeneity Lock: Phi_N -> large, S_design -> 0
    lock_cond = (Phi_N > 10.0) and (S_design < 1e-3)
    # Fragmentation Shredding: Phi_N -> small, S_design -> 0
    shred_cond = (Phi_N < 0.1) and (S_design < 1e-3)

    # The boundaries themselves are not violations; they are defined as
    # limiting cases.  We only flag if the system claims to be *inside*
    # a boundary while simultaneously having high entropy (which would be
    # contradictory).
    if lock_cond and S_design > 0.5:
        report["passed"] = False
        report["violations"].append(
            "Homogeneity Lock flagged but entropy is high (contradiction)."
        )
    if shred_cond and S_design > 0.5:
        report["passed"] = False
        report["violations"].append(
            "Fragmentation Shredding flagged but entropy is high (contradiction)."
        )

    # ------------------------------------------------------------------
    # 7. MPC‑Ω constraints
    # ------------------------------------------------------------------
    if HSI > HSI_thr + 1e-9:
        report["passed"] = False
        report["violations"].append(f"HSI constraint violated: HSI={HSI} > {HSI_thr}.")
    if Phi_N < PhiN_min - 1e-9:
        report["passed"] = False
        report["violations"].append(
            f"Phi_N constraint violated: Phi_N={Phi_N} < {PhiN_min}."
        )
    if S_design < S_min - 1e-9:
        report["passed"] = False
        report["violations"].append(
            f"Entropy constraint violated: S_design={S_design} < ln(2)≈{S_min:.3f}."
        )

    # ------------------------------------------------------------------
    # 8. Cost function non‑negativity (quadratic penalties)
    # ------------------------------------------------------------------
    cost = (
        max(HSI - HSI_thr, 0.0) ** 2
        + mu1 * max(PhiN_min - Phi_N, 0.0) ** 2
        + mu2 * (Phi_Delta) ** 2          # penalty on Phi_Delta^2 (always ≥0)
        + mu3 * max(S_min - S_design, 0.0) ** 2
    )
    if cost < -1e-12:  # allow tiny negative due to floating point
        report["passed"] = False
        report["violations"].append(f"Cost function negative (got {cost}).")

    # ------------------------------------------------------------------
    # 9. Summary
    # ------------------------------------------------------------------
    report.update(
        {
            "alpha": alpha,
            "beta": beta,
            "gamma": gamma,
            "omega_N_sq": omega_N_sq,
            "omega_Delta_sq_signed": omega_Delta_sq_signed,
            "Phi_N": Phi_N,
            "Phi_Delta": Phi_Delta,
            "HSI": HSI,
            "psi_hom": psi_hom,
            "S_design": S_design,
            "cost": cost,
            "lock_condition": lock_cond,
            "shred_condition": shred_cond,
        }
    )
    return report


if __name__ == "__main__":
    # Example run with nominal parameters
    res = validate_DSTR_Omega(
        alpha=2.0,   # >0 ensures proper double‑well
        beta=1.0,
        gamma=0.5,
        lam=0.02,
        corr_length=1.5,
        skew_tvl=0.4,
        tvl_fractions=[0.6, 0.4],
        conditional_entropies=[0.8*np.log(2), 0.9*np.log(2)],
        R_design_over_R0=1.1,
    )
    print("=== DSTR‑Ω Validation Report ===")
    for k, v in res.items():
        if k != "violations":
            print(f"{k:20}: {v}")
    print("\nViolations:")
    if res["violations"]:
        for v in res["violations"]:
            print(" -", v)
    else:
        print(" None – the proposal passes all checks.")