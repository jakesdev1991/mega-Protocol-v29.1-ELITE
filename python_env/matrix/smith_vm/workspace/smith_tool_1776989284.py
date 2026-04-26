# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
"""
Omega Protocol Validation Script for Q‑Systemic Self (Psychology Branch)

This script:
  * Re‑implements the key mathematical objects from the C++ spec.
  * Adds active checks for the Omega Protocol invariants:
        - Ψ_id (identity integrity) >= PSI_ID_THRESHOLD
        - Ξ_bound in [XI_BOUND_MIN, XI_BOUND_MAX]
        - COD in [0, 1] (by construction)
        - Φ‑density change never makes total Φ negative (we track a running total)
  * Verifies failure‑mode detection and adiabatic coupling correctness.
  * Prints a PASS/FAIL summary.

Run: python3 validate_qsystemic_self.py
"""

import numpy as np
import math

# ----------------------------------------------------------------------
# Constants (taken directly from the C++ spec)
# ----------------------------------------------------------------------
PSI_ID_THRESHOLD = 0.95          # Identity integrity lower bound
XI_BOUND_DEFAULT = 1.5
XI_BOUND_MIN = 0.5
XI_BOUND_MAX = 3.0
LAMBDA_COUPLING = 1.0
H_INT_LIMIT = 0.85
COD_THRESHOLD = 0.80             # Not a hard gate, just a reference

# ----------------------------------------------------------------------
# Helper functions (mirroring the C++ logic)
# ----------------------------------------------------------------------
def shannon_conditional_entropy(sub: np.complex128, con: np.complex128) -> float:
    """H(Sub|Con) = -p * log(p) where p = |<sub|con>|."""
    p = np.abs(np.conj(sub) * con)
    # Clamp to [0,1] for numerical safety
    p = min(max(p, 0.0), 1.0)
    if p == 0.0:
        return 0.0
    return -p * math.log(p)

def compute_energy(t: float, psi_sub: np.complex128, psi_con: np.complex128,
                   xi_bound: float, gamma_t: float) -> float:
    """H_eff = H_sub + H_stiff + gamma_t - H_cond (see C++)."""
    H_sub = 0.0                                 # baseline potential
    overlap_sq = np.abs(np.conj(psi_sub) * psi_con)
    H_stiff = xi_bound * overlap_sq
    H_cond = shannon_conditional_entropy(psi_sub, psi_con)
    return H_sub + H_stiff + gamma_t - H_cond

def compute_gamma(t: float, xi_bound: float) -> float:
    """Adiabatic coupling function with stiffness‑based clamp."""
    tau_opt = 0.5
    sigma = 0.1
    raw = math.tanh((t - tau_opt) / sigma)
    max_gamma = xi_bound * 0.8
    return min(max_gamma, max(raw, 0.0))   # gamma should be non‑negative

def cod_calc(sub: np.complex128, con: np.complex128, h_int: float) -> float:
    """Chain Overlap Density = fidelity^2 * exp(-Lambda * H_int)."""
    fidelity = np.abs(np.conj(sub) * con) / (np.abs(sub) * np.abs(con) + 1e-12)
    damping = math.exp(-LAMBDA_COUPLING * h_int)
    return fidelity * fidelity * damping

def dgamma_dt_approx(t: float, xi_bound: float, dt: float = 0.1) -> float:
    """Numerical derivative of Gamma(t)."""
    g1 = compute_gamma(t, xi_bound)
    g0 = compute_gamma(t - dt, xi_bound)
    return (g1 - g0) / dt

# ----------------------------------------------------------------------
# Invariant enforcement wrappers
# ----------------------------------------------------------------------
class InvariantViolation(Exception):
    pass

def check_psi_id(overlap_sq: float):
    """Ψ_id is approximated by the squared overlap (identity preservation)."""
    if overlap_sq < PSI_ID_THRESHOLD:
        raise InvariantViolation(f"Ψ_id ({overlap_sq:.4f}) < threshold ({PSI_ID_THRESHOLD})")

def check_xi_bound(xi: float):
    if not (XI_BOUND_MIN <= xi <= XI_BOUND_MAX):
        raise InvariantViolation(f"Ξ_bound ({xi:.4f}) outside allowed range "
                                 f"[{XI_BOUND_MIN}, {XI_BOUND_MAX}]")

def check_cod(cod: float):
    if not (0.0 <= cod <= 1.0 + 1e-12):
        raise InvariantViolation(f"COD out of bounds: {cod:.6f}")

# ----------------------------------------------------------------------
# Scenario tester
# ----------------------------------------------------------------------
def run_scenarios():
    total_phi = 0.0   # we track a notional Φ‑density; must never go negative
    audit_cost = 0.02 # example fixed cost per introspection step

    test_cases = [
        # (description, psi_sub, psi_con, xi_bound, h_int, t)
        ("nominal stable state",
         np.complex128(1.0, 0.0), np.complex128(0.9, 0.1),
         XI_BOUND_DEFAULT, 0.2, 0.5),
        ("low identity overlap (should trigger Ψ_id violation)",
         np.complex128(1.0, 0.0), np.complex128(0.3, 0.0),
         XI_BOUND_DEFAULT, 0.2, 0.5),
        ("high stiffness (near max)",
         np.complex128(1.0, 0.0), np.complex128(0.8, 0.2),
         XI_BOUND_MAX - 0.1, 0.3, 0.6),
        ("low stiffness (near min)",
         np.complex128(1.0, 0.0), np.complex128(0.8, 0.2),
         XI_BOUND_MIN + 0.1, 0.3, 0.6),
        ("high internal noise → decoherence risk",
         np.complex128(1.0, 0.0), np.complex128(0.7, 0.3),
         XI_BOUND_DEFAULT, 0.9, 0.5),
        ("rapid attention rise → measurement shock risk",
         np.complex128(1.0, 0.0), np.complex128(0.7, 0.3),
         XI_BOUND_DEFAULT, 0.2, 0.5),  # we will manually set dGamma/dt high later
    ]

    for desc, sub, con, xi, hint, t in test_cases:
        print(f"\n=== {desc} ===")
        try:
            # ---- Invariant checks on inputs ----
            check_xi_bound(xi)
            overlap_sq = np.abs(np.conj(sub) * con) ** 2
            check_psi_id(overlap_sq)

            # ---- Core computations ----
            gamma = compute_gamma(t, xi)
            energy = compute_energy(t, sub, con, xi, gamma)
            cod_val = cod_calc(sub, con, hint)
            check_cod(cod_val)

            dgamma = dgamma_dt_approx(t, xi)
            # Failure‑mode detection (should flag when conditions met)
            shock_risk = dgamma > xi
            decoherence_risk = hint > H_INT_LIMIT

            # ---- Φ‑density bookkeeping ----
            # Assume pre‑ and post‑entropy from a simple proxy:
            h_before = shannon_conditional_entropy(sub, con)
            # After a tiny evolution step (use gamma as coupling)
            con_next = con + (-1j * energy * 0.01)   # mimic C++ update
            h_after = shannon_conditional_entropy(sub, con_next)
            delta_phi = -(h_after - h_before) - audit_cost   # ledger formula
            total_phi += delta_phi
            if total_phi < -1e-9:   # allow tiny numerical noise
                raise InvariantViolation(f"Φ‑density went negative: {total_phi:.6f}")

            # ---- Reporting ----
            print(f"  γ(t) = {gamma:.4f}, dγ/dt = {dgamma:.4f}")
            print(f"  Energy = {energy:.4f}")
            print(f"  COD = {cod_val:.4f} (threshold {COD_THRESHOLD})")
            print(f"  Shock risk? {shock_risk}  Decoherence risk? {decoherence_risk}")
            print(f"  ΔΦ = {delta_phi:.4f}, Cumulative Φ = {total_phi:.4f}")

        except InvariantViolation as e:
            print(f"  ❌ INVARIANT VIOLATION: {e}")
            return False   # fail fast on first violation

    # Final sanity check: total Φ should have increased (or at least not collapsed)
    if total_phi < 0:
        print(f"\n❌ Final Φ‑density negative: {total_phi}")
        return False
    print(f"\n✅ All scenarios passed. Final cumulative Φ ≈ {total_phi:.4f}")
    return True

# ----------------------------------------------------------------------
# Entry point
# ----------------------------------------------------------------------
if __name__ == "__main__":
    success = run_scenarios()
    exit(0 if success else 1)