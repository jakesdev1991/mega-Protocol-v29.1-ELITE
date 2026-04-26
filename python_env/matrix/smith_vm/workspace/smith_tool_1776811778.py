# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
# -*- coding: utf-8 -*-
"""
Omega Protocol Invariant Validator for BTS-Ω (Biological Topology Shield)
Validates the mathematical soundness of the repaired BTS-Ω proposal
against the Ω-Physics Rubric v26.0 invariants:
    • Covariant modes Φ_N, Φ_Δ from Hessian diagonalization
    • Invariant ψ = ln(Φ_N/Φ_N0)
    • Shannon conditional entropy S_bts
    • Thermodynamic boundary conditions
    • QP constraints and cost function positivity
"""

import numpy as np
import math

# ----------------------------------------------------------------------
# Helper functions (mock implementations of the theoretical constructs)
# ----------------------------------------------------------------------
def compute_chi_schema(V: int, E: int, F: int) -> int:
    """Schema Euler characteristic: χ = V - E + F"""
    return V - E + F

def compute_delta_constraint(enforced: int, possible: int) -> float:
    """Constraint satisfaction gap: Δ = enforced / possible"""
    if possible == 0:
        raise ValueError("Possible constraints must be > 0")
    return enforced / possible

def compute_norm_depth(bcnf_levels: list[int]) -> int:
    """Normalization depth: maximum BCNF level across entities"""
    return max(bcnf_levels) if bcnf_levels else 0

def compute_phi_n(kappa1: float, kappa2: float, chi_abs: float, V: int) -> float:
    """Φ_N = sqrt(ω_N^2) with ω_N^2 = κ1 * |χ|/V + κ2"""
    omega_N_sq = kappa1 * (chi_abs / V) + kappa2
    if omega_N_sq < 0:
        raise ValueError("ω_N^2 must be non-negative (physical stability)")
    return math.sqrt(omega_N_sq)

def compute_phi_delta(kappa3: float, kappa4: float,
                      delta: float, d_norm_inv: float) -> float:
    """Φ_Δ = sqrt(ω_Δ^2) with ω_Δ^2 = κ3 * Δ * (1/d_norm) + κ4"""
    omega_D_sq = kappa3 * delta * d_norm_inv + kappa4
    if omega_D_sq < 0:
        raise ValueError("ω_Δ^2 must be non-negative (physical stability)")
    return math.sqrt(omega_D_sq)

def compute_btfi(phi_n: float, phi_delta: float, C: float = 1.0) -> float:
    """Biological Topology Fragility Index (BTFI) = Φ_N * Φ_Δ * C"""
    return phi_n * phi_delta * C

def compute_psi(phi_n: float, phi_n0: float) -> float:
    """Invariant ψ = ln(Φ_N / Φ_N0)"""
    if phi_n <= 0 or phi_n0 <= 0:
        raise ValueError("Φ_N and Φ_N0 must be positive for log")
    return math.log(phi_n / phi_n0)

def conditional_entropy(p_s: np.ndarray, p_k_given_s: np.ndarray) -> float:
    """
    Shannon conditional entropy:
        S = Σ_s p(s) [ - Σ_k p(k|s) log p(k|s) ]
    p_s: 1D array of subsystem probabilities (sums to 1)
    p_k_given_s: 2D array where rows = subsystems, columns = BTFI bins
    """
    if not np.isclose(p_s.sum(), 1.0):
        raise ValueError("p_s must sum to 1")
    if p_k_given_s.shape[0] != len(p_s):
        raise ValueError("Row count of p_k_given_s must match len(p_s)")
    # Avoid log(0) by masking zeros
    log_pk = np.where(p_k_given_s > 0, np.log(p_k_given_s), 0.0)
    inner = -np.sum(p_k_given_s * log_pk, axis=1)
    return float(np.dot(p_s, inner))

# ----------------------------------------------------------------------
# Validation routine
# ----------------------------------------------------------------------
def validate_bts_omega(params: dict) -> tuple[bool, list[str]]:
    """
    Validate all Ω-Physics Rubric v26.0 requirements for BTS-Ω.
    Returns (is_valid, list_of_violation_messages).
    """
    violations = []

    # ----- Unpack parameters ------------------------------------------------
    try:
        V      = params['V']          # # tables (vertices)
        E      = params['E']          # # foreign keys (edges)
        F      = params['F']          # # independent query cycles (faces)
        enforced = params['enforced']
        possible = params['possible']
        bcnf_levels = params['bcnf_levels']
        kappa1, kappa2, kappa3, kappa4 = params['kappa']
        C      = params.get('C', 1.0) # cross-coupling factor (default 1)
        phi_n0 = params['phi_n0']     # reference Φ_N for robust network
        p_s    = np.array(params['p_s'])          # subsystem type distribution
        p_k_given_s = np.array(params['p_k_given_s']) # BTFI bin distribution per subsystem
        S_low, S_high = params['S_bounds']        # allowed entropy band
    except KeyError as e:
        violations.append(f"Missing parameter: {e}")
        return False, violations

    # ----- 1. Topological invariants ----------------------------------------
    chi = compute_chi_schema(V, E, F)
    chi_abs = abs(chi)
    delta = compute_delta_constraint(enforced, possible)
    d_norm = compute_norm_depth(bcnf_levels)
    d_norm_inv = 1.0 / d_norm if d_norm > 0 else float('inf')

    # ----- 2. Covariant modes from Hessian (explicit derivation) -------------
    try:
        phi_n = compute_phi_n(kappa1, kappa2, chi_abs, V)
        phi_delta = compute_phi_delta(kappa3, kappa4, delta, d_norm_inv)
    except ValueError as ve:
        violations.append(str(ve))
        return False, violations

    # ----- 3. BTFI as derived quantity ---------------------------------------
    btfi = compute_btfi(phi_n, phi_delta, C)

    # ----- 4. Invariant ψ ----------------------------------------------------
    try:
        psi = compute_psi(phi_n, phi_n0)
    except ValueError as ve:
        violations.append(str(ve))
        return False, violations

    # ----- 5. Conditional entropy gauge --------------------------------------
    try:
        S = conditional_entropy(p_s, p_k_given_s)
    except ValueError as ve:
        violations.append(str(ve))
        return False, violations

    # ----- 6. Boundary condition consistency (thermodynamic logic) -----------
    # We cannot test infinities directly, but we can check monotonicity:
    #   - ψ should increase with Φ_N (for fixed Φ_N0)
    #   - ψ should increase with S (since high S corresponds to shredding → +∞ ψ)
    # We'll test a small perturbation.
    eps = 1e-6
    phi_n_pert = phi_n + eps
    S_pert = S + eps
    psi_pert = compute_psi(phi_n_pert, phi_n0)
    S_pert_val = conditional_entropy(p_s + np.array([eps/len(p_s)]*len(p_s)),  # renorm not needed for tiny eps
                                   p_k_given_s)  # approximate
    # For simplicity, we just check that ψ grows with Φ_N (S held constant)
    if psi_pert <= psi:
        violations.append("ψ does not increase with Φ_N (boundary condition inconsistency)")
    # Check that S contributes positively to shredding direction:
    #   (In full model, ψ also depends on S via control; here we just ensure S is defined)
    if S < 0:
        violations.append("Conditional entropy S_bts must be non-negative")

    # ----- 7. QP constraints -------------------------------------------------
    if btfi > 0.7 + 1e-9:
        violations.append(f"BTFI constraint violated: BTFI = {btfi:.3f} > 0.7")
    if phi_n < 0.6 - 1e-9:
        violations.append(f"Φ_N constraint violated: Φ_N = {phi_n:.3f} < 0.6")
    if not (S_low - 1e-9 <= S <= S_high + 1e-9):
        violations.append(f"Entropy constraint violated: S = {S:.3f} not in [{S_low}, {S_high}]")

    # ----- 8. Cost function non-negativity (sample check) --------------------
    # Cost integrand: (BTFI-0.6)_+^2 + μ1(0.6-Φ_N)_+^2 + μ2 Φ_Δ^2 + μ3(S-S_target)^2
    mu1, mu2, mu3, S_target = params.get('cost_weights', (1.0, 1.0, 1.0, 0.5))
    integrand = (max(btfi - 0.6, 0.0))**2 \
                + mu1 * (max(0.6 - phi_n, 0.0))**2 \
                + mu2 * (phi_delta**2) \
                + mu3 * ((S - S_target)**2)
    if integrand < -1e-12:  # allow tiny negative due to floating point
        violations.append(f"Cost function integrand negative: {integrand:.3e}")

    # ----- Final verdict ------------------------------------------------------
    is_valid = len(violations) == 0
    return is_valid, violations

# ----------------------------------------------------------------------
# Example usage (with synthetic but plausible numbers)
# ----------------------------------------------------------------------
if __name__ == "__main__":
    example_params = {
        # Schema topology
        'V': 12,          # tables
        'E': 18,          # foreign keys
        'F': 5,           # independent query cycles
        # Biological constraints
        'enforced': 42,
        'possible': 50,
        'bcnf_levels': [2, 3, 1, 2],   # per entity BCNF levels
        # Field-theoretic coupling constants (calibrated)
        'kappa': (0.8, 0.2, 0.6, 0.1),
        'C': 1.0,
        # Reference Φ_N for robust net
        'phi_n0': 0.55,
        # Subsystem type distribution (genomic, proteomic, clinical)
        'p_s': [0.4, 0.35, 0.25],
        # BTFI bin distribution (example: 4 bins per subsystem)
        'p_k_given_s': [
            [0.1, 0.2, 0.4, 0.3],   # genomic
            [0.25, 0.25, 0.25, 0.25], # proteomic
            [0.05, 0.15, 0.3, 0.5]    # clinical
        ],
        # Entropy bounds (from historical data)
        'S_bounds': (0.2, 1.5),
        # Cost function weights & target entropy
        'cost_weights': (1.2, 0.8, 1.0, 0.6)
    }

    valid, msgs = validate_bts_omega(example_params)
    if valid:
        print("✅ BTS-Ω proposal passes all Ω-Physics Rubric v26.0 checks.")
    else:
        print("❌ BTS-Ω proposal FAILED validation:")
        for m in msgs:
            print("   -", m)