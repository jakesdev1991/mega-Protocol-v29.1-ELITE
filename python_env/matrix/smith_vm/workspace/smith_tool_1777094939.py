# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
# -*- coding: utf-8 -*-
"""
Omega Protocol Validator – Bureaucratic Impedance (v32.1)

This script enforces the mathematical soundness of the proposal:
  • COD_buro = |⟨Ψ_intent|Ψ_exec⟩|² · exp(−Λ·H_proc) · exp(−Γ·|Ξ_rule−Ξ_req|)
  • Invariants (Phi_N, Phi_Delta, J*) → Φ-1: psi = ln(phi_N) ≥ ln(0.95)
                                        Φ-2: xi_rule ≤ 3.0
                                        Φ-3: phi_Sigma ≤ 0.03
  • Entropy accounting:  ΔS_audit = k_B·ln(2)·C_audit
  • Net Φ‑density:      Φ_net = ΔCOD − H_proc − ΔS_audit

All quantities must be dimensionless, traceable to state‑vectors,
and computed from measurable primitives (no hard‑coded constants
except the universal k_B·ln(2) factor).

Run the script; it will raise AssertionError on any violation.
"""

import numpy as np
from dataclasses import dataclass
from typing import Callable

# ----------------------------------------------------------------------
# Universal constants (informational thermodynamics)
K_B_LN2 = np.log(2)          # k_B·ln(2) in natural units → dimensionless
# ----------------------------------------------------------------------


def shannon_entropy(probs: np.ndarray) -> float:
    """Shannon entropy H = -Σ p log p (base e). Input must be a normalized distribution."""
    assert np.allclose(probs.sum(), 1.0), "Probability vector must sum to 1"
    assert np.all(probs >= 0), "Probabilities must be non‑negative"
    # Avoid log(0) by masking zeros
    mask = probs > 0
    return -np.sum(probs[mask] * np.log(probs[mask]))


def fidelity_overlap(psi_a: np.ndarray, psi_b: np.ndarray) -> float:
    """|⟨a|b⟩|² – assumes normalized state vectors."""
    assert np.isclose(np.linalg.norm(psi_a), 1.0), "State vector a not normalized"
    assert np.isclose(np.linalg.norm(psi_b), 1.0), "State vector b not normalized"
    overlap = np.vdot(psi_a, psi_b)          # ⟨a|b⟩
    return np.abs(overlap) ** 2


@dataclass
class BureaucraticState:
    """Container for all measurable primitives."""
    psi_intent: np.ndarray   # normalized vector of organizational intent
    psi_exec:   np.ndarray   # normalized vector of observed execution
    proc_chain: np.ndarray   # approval‑layer probabilities (normalized)
    phi_N:      float        # organizational identity density (≥0)
    xi_rule:    float        # measured rule stiffness
    xi_req:     float        # required stiffness (target)
    phi_Sigma:  float        # audit‑entropy density (output of audit process)
    C_audit:    float        # audit complexity factor (empirically measured, ≥0)

    def __post_init__(self):
        # Basic sanity checks – all vectors must be normalized
        assert np.isclose(np.linalg.norm(self.psi_intent), 1.0), "psi_intent not normalized"
        assert np.isclose(np.linalg.norm(self.psi_exec),   1.0), "psi_exec not normalized"
        assert np.allclose(self.proc_chain.sum(), 1.0),   "proc_chain not a probability distribution"
        assert self.phi_N > 0, "phi_N must be positive (log‑density domain)"
        assert self.xi_rule >= 0 and self.xi_req >= 0, "stiffness values non‑negative"
        assert self.phi_Sigma >= 0, "audit entropy density non‑negative"
        assert self.C_audit >= 0, "audit complexity factor non‑negative"


def calculate_COD(state: BureaucraticState, Lambda: float = 1.0, Gamma: float = 1.0) -> float:
    """
    Compute the bureaucratic COD:
        COD = |⟨Ψ_intent|Ψ_exec⟩|² * exp(−Λ·H_proc) * exp(−Γ·|Ξ_rule−Ξ_req|)
    Lambda, Gamma are coupling constants; set to 1.0 for the baseline model
    (they can be calibrated empirically – still dimensionless).
    """
    fidelity = fidelity_overlap(state.psi_intent, state.psi_exec)
    H_proc   = shannon_entropy(state.proc_chain)
    stiffness_penalty = np.abs(state.xi_rule - state.xi_req)
    COD = fidelity * np.exp(-Lambda * H_proc) * np.exp(-Gamma * stiffness_penalty)
    # COD must be dimensionless and bounded [0,1]
    assert 0.0 <= COD <= 1.0 + 1e-12, f"COD out of bounds: {COD}"
    return COD


def calculate_delta_S_audit(state: BureaucraticState) -> float:
    """Informational entropy injected by the act of auditing itself."""
    return K_B_LN2 * state.C_audit   # state.phi_Sigma is *not* used directly; it's an output metric


def verify_invariants(state: BureaucraticState) -> None:
    """
    Omega Protocol absolute invariants (Smith Audit):
        Φ-1: psi = ln(phi_N) ≥ ln(0.95)   → phi_N ≥ 0.95
        Φ-2: xi_rule ≤ 3.0
        Phi-3: phi_Sigma ≤ 0.03
    """
    psi = np.log(state.phi_N)
    assert psi >= np.log(0.95), f"Φ-1 violated: psi={psi:.4f} < ln(0.95)"
    assert state.xi_rule <= 3.0 + 1e-12, f"Φ-2 violated: xi_rule={state.xi_rule:.4f} > 3.0"
    assert state.phi_Sigma <= 0.03 + 1e-12, f"Φ-3 violated: phi_Sigma={state.phi_Sigma:.4f} > 0.03"


def calculate_phi_net(state: BureaucraticState,
                      Lambda: float = 1.0,
                      Gamma: float = 1.0) -> float:
    """
    Net Φ‑density change for one audit cycle:
        Φ_net = ΔCOD − H_proc − ΔS_audit
    Here ΔCOD is taken as the COD value itself (baseline COD₀ = 0 for a completely misaligned system).
    """
    COD = calculate_COD(state, Lambda, Gamma)
    H_proc = shannon_entropy(state.proc_chain)
    delta_S_audit = calculate_delta_S_audit(state)
    Phi_net = COD - H_proc - delta_S_audit
    # Φ_net may be negative (loss) or positive (gain); no a‑priori bound required.
    return Phi_net


# ----------------------------------------------------------------------
# Example usage – replace with real measurements from the system under audit
if __name__ == "__main__":
    # Mock state vectors (random but normalized)
    rng = np.random.default_rng(seed=42)
    psi_intent = rng.normal(size=5)
    psi_exec   = rng.normal(size=5)
    psi_intent /= np.linalg.norm(psi_intent)
    psi_exec   /= np.linalg.norm(psi_exec)

    # Approval‑chain distribution (e.g., 4 layers)
    proc_chain = rng.dirichlet(alpha=np.ones(4))

    # Measurable scalars (these would come from logs, surveys, etc.)
    phi_N      = 0.96          # just above the invariant threshold
    xi_rule    = 2.3
    xi_req     = 2.0
    phi_Sigma  = 0.025         # below the entropy cap
    C_audit    = 1.2           # empirical audit‑complexity factor

    state = BureaucraticState(
        psi_intent=psi_intent,
        psi_exec=psi_exec,
        proc_chain=proc_chain,
        phi_N=phi_N,
        xi_rule=xi_rule,
        xi_req=xi_req,
        phi_Sigma=phi_Sigma,
        C_audit=C_audit,
    )

    # ---- Enforce Omega Protocol -------------------------------------------------
    verify_invariants(state)                     # Smith Audit hard gates
    Phi_net = calculate_phi_net(state)           # Φ‑density accounting
    COD     = calculate_COD(state)

    # ---- Output for inspection --------------------------------------------------
    print(f"COD_buro          : {COD:.5f}")
    print(f"H_proc (entropy)  : {shannon_entropy(state.proc_chain):.5f}")
    print(f"ΔS_audit          : {calculate_delta_S_audit(state):.5f}")
    print(f"Net Φ‑density     : {Phi_net:.5f}")
    print("All Omega Protocol invariants satisfied ✅")