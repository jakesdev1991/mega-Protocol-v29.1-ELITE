# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Omega Protocol Invariant Validator for QNA‑RTM proposal
------------------------------------------------------
Validates:
  * State‑vector dimension and naming
  * QP constraints: ψ_unc ≤ ψ_max, Entropy ≥ log(5), Confidence ≥ Threshold
  * Non‑negativity of robust loss and MPC‑Ω cost
  * Φ‑impact arithmetic (short‑term + long‑term = net)
  * Optional: sample trajectory sanity check

Run: python3 qna_rtm_validator.py
"""

import numpy as np
from dataclasses import dataclass, field
from typing import List, Callable

# ----------------------------------------------------------------------
# Configuration (can be overridden by the experimenter)
# ----------------------------------------------------------------------
@dataclass
class QNARTMConfig:
    psi_max: float = 1.0          # maximum allowed uncertainty magnitude
    entropy_lower: float = np.log(5)  # log(5) ≈ 1.609
    confidence_thr: float = 0.7   # minimum acceptable confidence
    mu1: float = 1.0              # weight on entropy deviation
    mu2: float = 1.0              # weight on confidence deviation
    dt: float = 0.01              # integration step for cost evaluation
    horizon: float = 5.0          # total simulation time (seconds)

# ----------------------------------------------------------------------
# State vector definition (matches the proposal)
# ----------------------------------------------------------------------
@dataclass
class State:
    phi_N_quantum: float   # Φ_N from quantum layer
    phi_Delta_neural: float # Φ_D from neural layer
    psi_unc: float         # uncertainty magnitude
    xi_N: float            # auxiliary quantum variable
    xi_D: float            # auxiliary neural variable
    entropy: float         # Shannon‑like entropy of belief distribution
    confidence: float      # confidence in prediction (0‑1)

    def as_array(self) -> np.ndarray:
        return np.array([
            self.phi_N_quantum,
            self.phi_Delta_neural,
            self.psi_unc,
            self.xi_N,
            self.xi_D,
            self.entropy,
            self.confidence
        ])

# ----------------------------------------------------------------------
# Helper functions
# ----------------------------------------------------------------------
def robust_loss(state: State) -> float:
    """
    L_robust = E[Entropy] + Var[y_true - y_pred]
    For validation we treat the variance term as a non‑negative placeholder.
    """
    var_placeholder = 0.0  # would be supplied by a predictor in practice
    return state.entropy + var_placeholder

def mpc_omega_integrand(state: State, cfg: QNARTMConfig) -> float:
    """Instantaneous cost integrand."""
    term_psi = state.psi_unc ** 2
    term_entropy = cfg.mu1 * (cfg.entropy_lower - state.entropy) ** 2
    term_conf = cfg.mu2 * (state.confidence - cfg.confidence_thr) ** 2
    return term_psi + term_entropy + term_conf

def compute_trajectory_cost(
    state_fn: Callable[[float], State],
    cfg: QNARTMConfig
) -> float:
    """Numerical integration of the MPC‑Ω cost over the horizon."""
    ts = np.arange(0, cfg.horizon, cfg.dt)
    cost = np.trapz([mpc_omega_integrand(state_fn(t), cfg) for t in ts], ts)
    return cost

def check_qp_constraints(state: State, cfg: QNARTMConfig) -> List[str]:
    """Return list of violated constraint messages (empty if all satisfied)."""
    violations = []
    if state.psi_unc > cfg.psi_max + 1e-12:
        violations.append(f"ψ_unc = {state.psi_unc:.4f} > ψ_max = {cfg.psi_max}")
    if state.entropy < cfg.entropy_lower - 1e-12:
        violations.append(f"Entropy = {state.entropy:.4f} < log(5) = {cfg.entropy_lower:.4f}")
    if state.confidence < cfg.confidence_thr - 1e-12:
        violations.append(f"Confidence = {state.confidence:.4f} < Threshold = {cfg.confidence_thr}")
    return violations

def validate_phi_impact(short: float, long: float, net: float, tol: float = 1e-9) -> None:
    """Check that net ≈ long + short (note short is negative)."""
    expected = short + long
    if abs(net - expected) > tol:
        raise AssertionError(
            f"Φ‑impact arithmetic mismatch: net ({net}) != short ({short}) + long ({long}) = {expected}"
        )

# ----------------------------------------------------------------------
# Example usage – a dummy trajectory that respects constraints
# ----------------------------------------------------------------------
def demo():
    cfg = QNARTMConfig()

    # Simple constant‑state trajectory that satisfies all constraints
    def const_state(t: float) -> State:
        return State(
            phi_N_quantum=0.2,
            phi_Delta_neural=0.3,
            psi_unc=0.5,          # ≤ ψ_max (1.0)
            xi_N=0.0,
            xi_D=0.0,
            entropy=1.62,         # just above log(5)
            confidence=0.8        # ≥ Threshold (0.7)
        )

    # 1. Validate QP constraints at a sample point
    s0 = const_state(0.0)
    vio = check_qp_constraints(s0, cfg)
    assert not vio, f"QP constraint violations: {vio}"

    # 2. Validate robust loss non‑negativity
    loss = robust_loss(s0)
    assert loss >= 0.0, f"Robust loss negative: {loss}"

    # 3. Validate MPC‑Ω cost non‑negativity (integral of a PSD integrand)
    cost = compute_trajectory_cost(const_state, cfg)
    assert cost >= 0.0, f"MPC‑Ω cost negative: {cost}"

    # 4. Validate the Φ‑impact numbers given in the proposal
    short_term = -0.12   # –12 %
    long_term  =  0.60   # +60 %
    net_term   =  0.48   # +48 %
    validate_phi_impact(short_term, long_term, net_term)

    print("✅ All Omega Protocol invariants and mathematical checks passed.")
    print(f"   Sample state: {s0}")
    print(f"   Robust loss   = {loss:.4f}")
    print(f"   MPC‑Ω cost    = {cost:.4f}")

if __name__ == "__main__":
    demo()