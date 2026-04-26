# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
"""
Validation script for Refined Predictive Attack Simulation Monitor (PASM-Ω v2)
Checks mathematical consistency of the proposed formulas and enforces
Omega Protocol invariants: Φ_N, Φ_Δ, J* (via derived constraints).
"""

import numpy as np
from typing import Tuple, List

# ----------------------------------------------------------------------
# Mock data generators (replace with real feeds in production)
# ----------------------------------------------------------------------
def mock_sw_wri(t: float) -> float:
    """Mock Sophistication‑Weighted Weaponization Readiness Index."""
    # Simulate a slow rise with noise; clamp to [0,1]
    base = 0.2 + 0.5 * (1 - np.exp(-t/30))   # t in days
    noise = 0.05 * np.random.randn()
    return np.clip(base + noise, 0.0, 1.0)

def mock_intent_convergence(t: float) -> float:
    """Mock intent convergence metric (0→1)."""
    return np.clip(0.1 + 0.6 * (1 - np.exp(-t/20)), 0.0, 1.0)

def mock_strategy_diversity(t: float) -> float:
    """Mock strategy diversity (higher = more spread)."""
    return np.clip(0.3 + 0.4 * np.exp(-t/25), 0.0, 1.0)

def mock_s_weap(t: float) -> float:
    """Mock strategic entropy S_weap (should stay ≥ ln(4) ≈ 1.386)."""
    return np.clip(1.4 + 0.2 * np.sin(t/10), 1.35, 1.6)

def mock_t_complexity(t: float) -> float:
    """Mock topological complexity T_complexity (positive)."""
    return 1.0 + 0.5 * np.tanh(t/15)

# ----------------------------------------------------------------------
# Core PASM-Ω formulas (as per refined proposal)
# ----------------------------------------------------------------------
Phi_N_0 = 1.0          # baseline nominal value
Phi_Delta_0 = 0.5      # baseline nominal value
LAMBDA = 0.3           # coupling constant in ψ_weap
T0 = 1.0               # baseline topological complexity
TAU = 14.0             # delay (days) used in mappings

def compute_phi_n_weap(t: float) -> float:
    """Φ_N^{(weap)}(t) = Φ_N^{(0)} - 0.9·SW-WRI(t-τ) + 0.4·S_weap(t-τ)"""
    sw = mock_sw_wri(t - TAU)
    s  = mock_s_weap(t - TAU)
    return Phi_N_0 - 0.9 * sw + 0.4 * s

def compute_phi_delta_weap(t: float) -> float:
    """Φ_Δ^{(weap)}(t) = Φ_Δ^{(0)} + 0.7·intent_convergence(t-τ) - 0.5·strategy_diversity(t-τ)"""
    ic = mock_intent_convergence(t - TAU)
    sd = mock_strategy_diversity(t - TAU)
    return Phi_Delta_0 + 0.7 * ic - 0.5 * sd

def compute_psi_weap(t: float) -> float:
    """
    ψ_weap(t) = ln(Φ_N^{(weap)}(t)/Φ_N^{(0)})
              = ln(T_complexity(t)/T0) + λ·SW-WRI(t)
    """
    phi_n = compute_phi_n_weap(t)
    lhs = np.log(phi_n / Phi_N_0) if phi_n > 0 else -np.inf
    rhs = np.log(mock_t_complexity(t) / T0) + LAMBDA * mock_sw_wri(t)
    return lhs, rhs   # return both sides for equality check

def compute_j_star(t: float) -> float:
    """
    J* proxy: from proposal J^μ = √2 Φ_Δ^{(weap)} δ^μ_0
    We check the temporal component magnitude.
    """
    return np.sqrt(2) * compute_phi_delta_weap(t)

# ------------------------------------------------------------------
# Invariant & constraint checks
# ------------------------------------------------------------------
def check_constraints(t: float) -> Tuple[bool, List[str]]:
    """Return (all_ok, list_of_violations)."""
    violations = []
    sw = mock_sw_wri(t)
    phi_n = compute_phi_n_weap(t)
    s_weap = mock_s_weap(t)

    if sw > 0.6:
        violations.append(f"SW-WRI = {sw:.3f} > 0.6")
    if phi_n < 0.5:
        violations.append(f"Φ_N^{(weap)} = {phi_n:.3f} < 0.5")
    if s_weap < np.log(4):
        violations.append(f"S_weap = {s_weap:.3f} < ln(4) ≈ {np.log(4):.3f}")

    # Additional refined thresholds (optional, for intent‑proportional response)
    if sw >= 0.55:
        # Not a violation, just a flag for countermeasure activation
        pass

    return len(violations) == 0, violations

def check_psi_equality(t: float, tol: float = 1e-3) -> Tuple[bool, float]:
    """Validate ψ_weap identity; return (holds, diff)."""
    lhs, rhs = compute_psi_weap(t)
    diff = abs(lhs - rhs)
    return diff <= tol, diff

# ------------------------------------------------------------------
# Main validation routine
# ------------------------------------------------------------------
def validate_over_time(days: int = 60) -> None:
    """Run checks over a simulated horizon and report any issues."""
    print("=== PASM-Ω v2 Mathematical & Invariant Validation ===\n")
    all_ok = True
    for day in range(days):
        t = float(day)
        # Constraint check
        ok_cons, viol = check_constraints(t)
        if not ok_cons:
            all_ok = False
            print(f"[DAY {day:3d}] CONSTRAINT VIOLATION: {'; '.join(viol)}")
        # ψ identity check
        ok_psi, diff = check_psi_equality(t)
        if not ok_psi:
            all_ok = False
            print(f"[DAY {day:3d}] ψ IDENTITY FAIL: |LHS−RHS| = {diff:.6f}")
        # Optional: print a summary snapshot every 10 days
        if day % 10 == 0:
            phi_n = compute_phi_n_weap(t)
            phi_d = compute_phi_delta_weap(t)
            psi_lhs, _ = compute_psi_weap(t)
            jstar = compute_j_star(t)
            print(f"[DAY {day:3d}] Φ_N={phi_n:.3f} Φ_Δ={phi_d:.3f} ψ={psi_lhs:.3f} J*={jstar:.3f} SW-WRI={mock_sw_wri(t):.3f}")

    if all_ok:
        print("\n✅ All checks passed over {} days.".format(days))
    else:
        print("\n❌ Some checks failed. Review the violations above.")
        # In a real guardian system, we would trigger a correction protocol here.

if __name__ == "__main__":
    np.random.seed(42)   # deterministic for audit
    validate_over_time(days=60)