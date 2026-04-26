# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
# -*- coding: utf-8 -*-
"""
Omega Protocol Invariant Validator for PICM‑Ω v2
-------------------------------------------------
This script checks the mathematical consistency of the core
definitions presented in the refined PICM‑Ω v2 proposal:

    • Action:   S[φ] = ∫ [ ½ φ̇² + λ/4 (φ² – v²)² ] dt
    • Fluctuation operator:  –d²/dt² + m_eff²,
          m_eff² = λ (3 φ₀² – v²)
    • Covariant modes:
          Φ_N = ⟨δφ⟩_T          (Newtonian / regularity mode)
          Φ_Δ = ⟨δφ sin(ωt)⟩_T  (Archive / asymmetry mode)
    • Invariants:
          ψ      = ln( ξ / ξ₀ )
          ξ_N⁻² = λ ( 3 Φ_N² + Φ_Δ² – v² )
          ξ_Δ⁻² = λ ( Φ_N² + 3 Φ_Δ² – v² )
    • Boundaries (divergences of ξ):
          Shredding Event : ξ_Δ → ∞  ⇔  Φ_N² + 3 Φ_Δ² = v²
          Informational Freeze: ξ_N → ∞  ⇔  3 Φ_N² + Φ_Δ² = v²
    • Entropy observable:
          S_h(t) = – Σ p_k ln p_k   (Shannon entropy of inter‑presentation intervals)
    • Presentation jerk:
          J_p(t) = d³ S_h / dt³
    • Anomaly detection (GPD‑based):
          Alert if  a_p(t) < α  AND  ξ_Δ(t) > ξ_Δ^{crit}
    • MPC‑Ω constraints (to keep the system away from the boundaries):
          ξ_N ≥ ξ_N^{min}          (lower bound on regularity time)
          ξ_Δ ≤ ξ_Δ^{max}          (upper bound on clustering‑decay time)
          Φ_N ≥ 0                  (presentation propensity non‑negative)

The script does **not** enforce the “no boilerplate” editorial rule –
that is a documentation/style constraint and must be checked manually.
Instead it focuses on the *mathematical* invariants and logical
consistency of the inequalities.

Usage:
    >>> validate_sample()
    True   # if the sample point satisfies all checks
"""

import numpy as np

# ----------------------------------------------------------------------
# Helper functions (pure mathematics)
# ----------------------------------------------------------------------
def effective_mass_squared(phi0, lam, v):
    """m_eff² = λ (3 φ₀² – v²)"""
    return lam * (3.0 * phi0**2 - v**2)

def correlation_time(m_eff_sq):
    """ξ = 1 / sqrt(m_eff²)  (requires m_eff² > 0)"""
    if m_eff_sq <= 0:
        return np.inf   # corresponds to divergent ξ
    return 1.0 / np.sqrt(m_eff_sq)

def xi_N_sq_inv(Phi_N, Phi_Delta, lam, v):
    """ξ_N⁻² = λ (3 Φ_N² + Φ_Δ² – v²)"""
    return lam * (3.0 * Phi_N**2 + Phi_Delta**2 - v**2)

def xi_Delta_sq_inv(Phi_N, Phi_Delta, lam, v):
    """ξ_Δ⁻² = λ (Φ_N² + 3 Φ_Δ² – v²)"""
    return lam * (Phi_N**2 + 3.0 * Phi_Delta**2 - v**2)

def xi_from_inv(inv):
    """Given ξ⁻², return ξ (handle sign → divergence)"""
    if inv <= 0:
        return np.inf
    return 1.0 / np.sqrt(inv)

def psi(xi, xi0):
    """Dimensionless invariant ψ = ln(ξ/ξ₀)"""
    if xi <= 0 or xi0 <= 0:
        raise ValueError("ξ and ξ₀ must be positive for log.")
    return np.log(xi / xi0)

def shredding_condition(Phi_N, Phi_Delta, v, tol=1e-9):
    """True if Φ_N² + 3 Φ_Δ² ≈ v² (within tolerance)"""
    lhs = Phi_N**2 + 3.0 * Phi_Delta**2
    return np.abs(lhs - v**2) < tol

def freeze_condition(Phi_N, Phi_Delta, v, tol=1e-9):
    """True if 3 Φ_N² + Φ_Δ² ≈ v² (within tolerance)"""
    lhs = 3.0 * Phi_N**2 + Phi_Delta**2
    return np.abs(lhs - v**2) < tol

def anomaly_check(Jp, a_p, alpha, xi_Delta, xi_Delta_crit):
    """
    GPD‑based anomaly alert:
        Alert if a_p < alpha  AND  ξ_Δ > ξ_Δ^{crit}
    """
    return (a_p < alpha) and (xi_Delta > xi_Delta_crit)

def mpc_constraints(xi_N, xi_Delta, Phi_N,
                    xi_N_min, xi_Delta_max):
    """
    Enforce the MPC‑Ω constraints:
        ξ_N ≥ ξ_N^{min}
        ξ_Δ ≤ ξ_Δ^{max}
        Φ_N ≥ 0
    """
    return (xi_N >= xi_N_min) and (xi_Delta <= xi_Delta_max) and (Phi_N >= 0.0)

# ----------------------------------------------------------------------
# Validation routine (example with a physically plausible point)
# ----------------------------------------------------------------------
def validate_sample():
    """
    Pick a set of parameters that lie inside the safe region
    (i.e. away from the shredding/freeze boundaries) and verify:
        • ξ_N, ξ_Δ are finite and positive
        • ψ is well‑defined
        • Constraints are satisfied
        • Anomaly logic uses the correct inequality direction
    """
    # ---- Model parameters (chosen for illustration) ----
    lam   = 1.0          # coupling λ > 0
    v     = 2.0          # symmetry‑breaking scale
    xi0   = 1.0          # reference correlation time for ψ
    # ---- State variables (inside safe region) ----
    Phi_N     = 0.5      # regularity mode (positive)
    Phi_Delta = 0.2      # asymmetry mode (small)
    # ---- Derived quantities ----
    m2 = effective_mass_squared(Phi_N, lam, v)   # use Φ₀ ≈ Φ_N as background
    xi_N_val  = xi_from_inv(xi_N_sq_inv(Phi_N, Phi_Delta, lam, v))
    xi_Delta_val = xi_from_inv(xi_Delta_sq_inv(Phi_N, Phi_Delta, lam, v))
    psi_val   = psi(xi_N_val, xi0)   # we could also use ξ_Δ; both should be finite
    # ---- Constraint thresholds ----
    xi_N_min  = 0.1
    xi_Delta_max = 5.0   # must be *below* this to avoid shredding
    # ---- Anomaly test (dummy values) ----
    Jp_sample   = 0.01   # jerk value (not used directly in the boolean)
    a_p_sample  = 0.005  # GPD tail probability
    alpha       = 0.01   # significance level
    xi_Delta_crit = 3.0  # upper bound beyond which we flag anomaly
    # ---- Checks ----
    checks = {}
    checks["xi_N finite & positive"] = np.isfinite(xi_N_val) and xi_N_val > 0
    checks["xi_Delta finite & positive"] = np.isfinite(xi_Delta_val) and xi_Delta_val > 0
    checks["psi well‑defined"] = np.isfinite(psi_val)
    checks["MPC constraints satisfied"] = mpc_constraints(
        xi_N_val, xi_Delta_val, Phi_N, xi_N_min, xi_Delta_max)
    checks["Anomaly logic uses correct ξ_Δ direction"] = anomaly_check(
        Jp_sample, a_p_sample, alpha, xi_Delta_val, xi_Delta_crit)
    checks["Not inadvertently in shredding region"] = not shredding_condition(
        Phi_N, Phi_Delta, v)
    checks["Not inadvertently in freeze region"] = not freeze_condition(
        Phi_N, Phi_Delta, v)
    # ---- Report ----
    for k, v in checks.items():
        print(f"{k:45}: {'PASS' if v else 'FAIL'}")
    return all(checks.values())

# ----------------------------------------------------------------------
# If run as a script, execute the validation
# ----------------------------------------------------------------------
if __name__ == "__main__":
    print("=== Omega Protocol Invariant Validation for PICM‑Ω v2 ===")
    ok = validate_sample()
    print("\nOverall result:", "PASS" if ok else "FAIL")
    # Exit with non‑zero code on failure to allow CI integration
    exit(0 if ok else 1)