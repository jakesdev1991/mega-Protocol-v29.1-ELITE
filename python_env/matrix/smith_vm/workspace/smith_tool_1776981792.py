# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
#!/usr/bin/env python3
"""
Omega Protocol Validation Script for the Q-Systemic Self Sales Model
-------------------------------------------------------------------
This script checks the mathematical soundness and invariant compliance
of the derivation presented in the C++ snippet.

It does **not** execute the original C++ code; instead it re‑implements
the key formulas in Python and validates them against the Omega Protocol
invariants (Φ_N, Φ_Δ, J*) and rubric requirements.

Usage:
    python3 validate_omega_sales.py
"""

import numpy as np
from typing import Tuple

# ----------------------------------------------------------------------
# Protocol Constants (as per the derivation)
# ----------------------------------------------------------------------
PSI_ID_COEFF = 1.0          # Prospect Identity Potential (should scale energy)
XI_CRITICAL = 0.4           # Minimum allowed risk stiffness
XI_BOUND_NOMINAL = 1.0      # Nominal stiffness value (will be tested)
TAU_OPT = 0.5               # Optimal validation window (norm. time)
SIGMA = 0.1                 # Width of the tanh coupling
PHI_DELTA_HORIZON = 2.0     # Maximum allowed decision latency (norm. time)
DT = 0.01                   # Integration timestep used in the ARP operator

# ----------------------------------------------------------------------
# Helper Functions
# ----------------------------------------------------------------------
def gamma_t(t: float) -> float:
    """Strategic Resonance Coupling (SRC) as defined in the derivation."""
    return np.tanh((t - TAU_OPT) / SIGMA)

def dgamma_dt(t: float) -> float:
    """Analytic derivative of Gamma(t)."""
    x = (t - TAU_OPT) / SIGMA
    return (1.0 / SIGMA) * (1.0 - np.tanh(x) ** 2)

def shannon_conditional_entropy(p_y_given_x: float) -> float:
    """
    Proper Shannon conditional entropy for a binary outcome:
        H = - [ p log p + (1-p) log (1-p) ]
    Clamps p to [eps, 1-eps] to avoid log(0).
    """
    eps = 1e-12
    p = np.clip(p_y_given_x, eps, 1.0 - eps)
    return - (p * np.log(p) + (1.0 - p) * np.log(1.0 - p))

def overlap_sq(need: np.ndarray, buy: np.ndarray) -> float:
    """|⟨need|buy⟩|² (assumes normalized vectors)."""
    return np.abs(np.vdot(need, buy)) ** 2

def hamiltonian_energy(
    need: np.ndarray,
    buy: np.ndarray,
    t: float,
    xi_bound: float = XI_BOUND_NOMINAL,
    psi_id_coeff: float = PSI_ID_COEFF,
) -> float:
    """
    Effective Hamiltonian:
        H_eff = H_need + H_stiff + Gamma(t) * H_couple - H_cond
    where:
        H_need      = 0   (baseline, as in the snippet)
        H_stiff     = xi_bound * |⟨need|status_quo⟩|²
                      (we approximate status_quo ≈ need for simplicity)
        H_couple    = |⟨need|buy⟩|   (the interaction term)
        H_cond      = Shannon conditional entropy of the decision.
    The identity potential ψ_id should scale the *need* term:
        H_id = ψ_id_coeff * |need|²
    """
    # Identity Potential term (active scaling of need energy)
    H_id = psi_id_coeff * np.vdot(need, need).real   # ⟨need|need⟩ = 1 if normalized

    # Stiffness term: resistance to deviating from the status quo (need)
    # We use the projector onto |need⟩ as a proxy for status quo.
    H_stiff = xi_bound * overlap_sq(need, need)   # = xi_bound * 1 = xi_bound

    # Coupling term (linear in overlap, as in the snippet)
    H_couple = overlap_sq(need, buy) ** 0.5       # sqrt gives |⟨need|buy⟩|

    # Entropy term: need a conditional probability p(buy|need)
    # For a two-level system we take p = |⟨need|buy⟩|²
    p_buy_given_need = overlap_sq(need, buy)
    H_cond = shannon_conditional_entropy(p_buy_given_need)

    # Total effective energy (note: entropy subtracts, as in the snippet)
    return H_id + H_stiff + gamma_t(t) * H_couple - H_cond

def adiabatic_condition_holds(xi_bound: float, t_samples: np.ndarray) -> Tuple[bool, float]:
    """
    Checks |dΓ/dt| << ξ_bound over a time window.
    Returns (True/False, max_ratio) where max_ratio = max|dΓ/dt| / xi_bound.
    The << relation is interpreted as ratio < 0.1 (an order of magnitude smaller).
    """
    dgamma = np.abs([dgamma_dt(t) for t in t_samples])
    max_ratio = np.max(dgamma) / xi_bound if xi_bound > 0 else np.inf
    return max_ratio < 0.1, max_ratio

def check_invariants(
    need: np.ndarray,
    buy: np.ndarray,
    xi_bound: float = XI_BOUND_NOMINAL,
    total_time: float = PHI_DELTA_HORIZON,
) -> None:
    """
    Runs a battery of tests and prints compliance status.
    """
    print("=== Omega Protocol Invariant Audit ===")
    # 1. Φ_N (Identity Potential) appears in Hamiltonian?
    H0 = hamiltonian_energy(need, buy, t=0.0, xi_bound=xi_bound)
    H_no_id = hamiltonian_energy(need, buy, t=0.0,
                                 xi_bound=xi_bound,
                                 psi_id_coeff=0.0)  # turn off ψ_id
    identity_active = not np.isclose(H0, H_no_id, rtol=1e-6)
    print(f"[Φ_N] Identity Potential active in Hamiltonian: {identity_active}"
          f"{' ✅' if identity_active else ' ❌'}")

    # 2. Φ_Δ (Risk Stiffness) invariant: xi_bound >= xi_critical
    stiffness_ok = xi_bound >= XI_CRITICAL
    print(f"[Φ_Δ] xi_bound ({xi_bound:.3f}) >= xi_critical ({XI_CRITICAL}): "
          f"{stiffness_ok}{' ✅' if stiffness_ok else ' ❌'}")

    # 3. J* (SRC) adiabatic condition
    t_grid = np.linspace(0.0, total_time, int(total_time / DT) + 1)
    adiabatic_ok, max_ratio = adiabatic_condition_holds(xi_bound, t_grid)
    print(f"[J*] Adiabatic condition |dΓ/dt| << ξ_bound: "
          f"max ratio = {max_ratio:.3f} (<0.1 required) "
          f"{'✅' if adiabatic_ok else '❌'}")

    # 4. Entropy Compliance: Φ‑density update = -ΔH_cond
    # Compute energy at t=0 and t=total_time (ignoring explicit time dependence in H_id/H_stiff)
    E_initial = hamiltonian_energy(need, buy, t=0.0, xi_bound=xi_bound)
    E_final   = hamiltonian_energy(need, buy, t=total_time, xi_bound=xi_bound)
    # Approximate ΔH_cond from the entropy part only (other terms cancel if need/buy static)
    p_initial = overlap_sq(need, buy)
    p_final   = overlap_sq(need, buy)  # unchanged if vectors static
    # In a realistic scenario need/buy evolve; we approximate ΔH_cond via entropy difference:
    H_cond_i = shannon_conditional_entropy(p_initial)
    H_cond_f = shannon_conditional_entropy(p_final)
    delta_H_cond = H_cond_f - H_cond_i
    delta_Phi_from_entropy = -delta_H_cond   # Φ ∝ -H
    # Actual ΔΦ from Hamiltonian difference (should match if only entropy changes)
    delta_Phi_from_H = E_final - E_initial
    entropy_compliant = np.isclose(delta_Phi_from_H, delta_Phi_from_entropy, rtol=1e-3)
    print(f"[Entropy] ΔΦ ≈ -ΔH_cond holds: "
          f"ΔΦ_H={delta_Phi_from_H:.6f}, -ΔH_cond={-delta_H_cond:.6f} "
          f"{'✅' if entropy_compliant else '❌'}")

    # 5. ΦΔ‑Horizon (decision latency) safety: total_time must be ≤ horizon
    horizon_ok = total_time <= PHI_DELTA_HORIZON
    print(f"[ΦΔ‑Horizon] total evolution time {total_time:.3f} ≤ horizon {PHI_DELTA_HORIZON:.3f}: "
          f"{horizon_ok}{' ✅' if horizon_ok else ' ❌'}")

    # Overall verdict
    all_ok = (identity_active and stiffness_ok and adiabatic_ok
              and entropy_compliant and horizon_ok)
    print("\n=== OVERALL COMPLIANCE ===")
    print("PASS" if all_ok else "FAIL")
    if not all_ok:
        print("Failed invariants:")
        if not identity_active: print("  - Φ_N (Identity Potential) not active")
        if not stiffness_ok:    print("  - Φ_Δ (Risk Stiffness) below critical")
        if not adiabatic_ok:    print("  - J* (SRC) violates adiabatic condition")
        if not entropy_compliant: print("  - Entropy/Φ‑density relation broken")
        if not horizon_ok:      print("  - Evolution exceeds ΦΔ‑horizon")

# ----------------------------------------------------------------------
# Example Usage
# ----------------------------------------------------------------------
if __name__ == "__main__":
    # Random normalized state vectors in a 2‑D Hilbert space (need, buy)
    need_vec = np.array([1.0, 0.0], dtype=complex)   # |need⟩ = |0⟩
    # Create a buy state with controllable overlap
    theta = np.pi / 3  # 60° gives |⟨need|buy⟩|² = cos²(theta) = 0.25
    buy_vec = np.array([np.cos(theta), np.sin(theta)], dtype=complex)  # normalized

    # Test with nominal stiffness
    print("\n--- Test 1: Nominal stiffness (xi_bound = 1.0) ---")
    check_invariants(need_vec, buy_vec, xi_bound=XI_BOUND_NOMINAL, total_time=1.0)

    # Test with low stiffness (should fail Φ_Δ)
    print("\n--- Test 2: Low stiffness (xi_bound = 0.2) ---")
    check_invariants(need_vec, buy_vec, xi_bound=0.2, total_time=1.0)

    # Test with high stiffness but too fast coupling (violates adiabatic)
    print("\n--- Test 3: High stiffness, but we shrink sigma to make Gamma fast ---")
    global SIGMA
    SIGMA = 0.01  # make Gamma vary quickly -> large dGamma/dt
    check_invariants(need_vec, buy_vec, xi_bound=XI_BOUND_NOMINAL, total_time=1.0)
    SIGMA = 0.1   # reset for any further use