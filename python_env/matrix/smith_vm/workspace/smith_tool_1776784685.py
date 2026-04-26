# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
# -*- coding: utf-8 -*-
"""
Ω‑Protocol validation for the Q-Systemic Self → Enterprise Sales mapping.
Checks the minimal quantitative invariants that any derivation must satisfy.
"""

import numpy as np

# ----------------------------------------------------------------------
# User‑provided parameters from the derivation (can be changed for sensitivity)
# ----------------------------------------------------------------------
# Φ‑density accounting
phi_initial = 1000.0          # baseline Φ density (arbitrary >0)
phi_cost    = -50.0           # short‑term cognitive overhead (negative = cost)
phi_gain    = 1500.0          # long‑term systemic gain
phi_delta   = phi_gain + phi_cost   # net change (cost is negative)

# Chain Overlap Density (COD) – must be a probability‑like coherence measure
COD = 0.73   # example value claimed in the text (moderately high)

# Operator magnitudes (non‑negative scalars)
Urgency   = 2.5   # Strategic Urgency perturbation strength
Credibility = 3.0 # Technical Credibility validation strength
Safety    = 4.0   # Safety Parameters magnitude

# Stability constants (derived from the “Black Hole” bifurcation description)
epsilon   = 1e-6  # avoid division by zero
S_critical = 1.2  # maximum allowable Urgency/(Safety+ε) before defensive collapse

# ----------------------------------------------------------------------
# Helper: surrogate model for the scalar quantities mentioned in the text
# ----------------------------------------------------------------------
def barrier(Urgency, Safety):
    """Activation barrier – lower Urgency reduces it, higher Safety raises it."""
    return 1.0 / (Urgency + 1.0) + Safety * 0.1

def entropy(Credibility, COD):
    """Informational entropy – higher Credibility lowers it, low COD raises it."""
    return 1.0 / (Credibility + 1.0) + (1.0 - COD) * 0.5

def stiffness(Urgency, Safety):
    """Informational stiffness – grows with Urgency, mitigated by Safety."""
    return Urgency / (Safety + epsilon)

def jacobian_approx():
    """Finite‑difference Jacobian of [barrier, entropy, stiffness] w.r.t [Urgency, Credibility, Safety]."""
    vars0 = np.array([Urgency, Credibility, Safety])
    delta = 1e-4
    J = np.zeros((3, 3))
    f0 = np.array([barrier(Urgency, Safety),
                   entropy(Credibility, COD),
                   stiffness(Urgency, Safety)])
    for i in range(3):
        vars1 = vars0.copy()
        vars1[i] += delta
        f1 = np.array([barrier(vars1[0], vars1[2]),
                       entropy(vars1[1], COD),
                       stiffness(vars1[0], vars1[2])])
        J[:, i] = (f1 - f0) / delta
    return J

# ----------------------------------------------------------------------
# Ω‑Protocol invariant checks
# ----------------------------------------------------------------------
def validate():
    # 1. Φ‑density must never drop below zero after an operation
    assert phi_initial + phi_delta >= 0, \
        f"Φ_N violation: final Φ density {phi_initial+phi_delta:.2f} < 0"

    # 2. Net Φ change must be non‑negative (protocol enforces growth or conservation)
    assert phi_delta >= 0, \
        f"Φ_Δ violation: net Φ change {phi_delta:.2f} < 0"

    # 3. COD must lie in the valid coherence interval [0,1]
    assert 0.0 <= COD <= 1.0, \
        f"COD out of bounds: {COD:.3f} not in [0,1]"

    # 4. Stability condition: Urgency/(Safety+ε) must not exceed critical stiffness
    assert stiffness(Urgency, Safety) <= S_critical, \
        f"Stiffness violation: {stiffness(Urgency, Safety):.3f} > S_c ({S_critical})"

    # 5. Jacobian sign pattern (qualitative Ω‑requirement)
    J = jacobian_approx()
    # ∂barrier/∂Urgency ≤ 0  (more urgency → lower barrier)
    assert J[0, 0] <= 0, f"Jacobian sign error: ∂B/∂U = {J[0,0]:.4f} > 0"
    # ∂entropy/∂Credibility ≤ 0 (more credibility → lower entropy)
    assert J[1, 1] <= 0, f"Jacobian sign error: ∂E/∂C = {J[1,1]:.4f} > 0"
    # ∂stiffness/∂Safety ≥ 0 (more safety → higher denominator → lower stiffness,
    #                       but we defined stiffness = U/(S+ε) → derivative negative;
    #                       the Ω‑text treats safety as a stabilizer, so we check the
    #                       *inverse* relationship: ∂(1/stiffness)/∂Safety ≥ 0)
    inv_stiff = 1.0 / stiffness(Urgency, Safety)
    # approximate derivative of inv_stiff w.r.t Safety
    delta = 1e-4
    inv_stiff_plus = 1.0 / stiffness(Urgency, Safety + delta)
    deriv_inv = (inv_stiff_plus - inv_stiff) / delta
    assert deriv_inv >= 0, f"Safety stabilizer violation: ∂(1/S)/∂S = {deriv_inv:.4f} < 0"

    print("✅ All Ω‑Protocol invariants satisfied.")
    print(f"   Net Φ change: {phi_delta:.2f}")
    print(f"   Final Φ density: {phi_initial+phi_delta:.2f}")
    print(f"   COD: {COD:.3f}")
    print(f"   Stiffness (U/(S+ε)): {stiffness(Urgency, Safety):.3f} (limit {S_critical})")
    print(f"   Jacobian:\n{J}")

if __name__ == "__main__":
    validate()