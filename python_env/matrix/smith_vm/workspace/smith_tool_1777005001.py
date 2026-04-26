# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
"""
Omega Protocol Audit: Bureaucratic Decision Manifold (v27.2-Ω-POLARIZED)
Validates mathematical soundness and invariant compliance.
"""

import numpy as np
import itertools
from typing import List, Tuple

# ------------------------------
# 1. Core Invariants (from rubric)
# ------------------------------
PSI_ID_THRESHOLD = 0.95
XI_SYS_MIN, XI_SYS_MAX = 0.5, 3.0
LAMBDA_COUPLING = 1.0
GAMMA_COUPLING = 0.5
K_BOLTZMANN = 1.0  # dimensionless per rubric

# ------------------------------
# 2. Helper Functions (mirroring the spec)
# ------------------------------
def topological_impedance(path: List[Tuple[float, float]]) -> float:
    """
    H_top = sum(Cost_i * Variance_i) / sum(Cost_i)  (clamped to [0,1])
    """
    if not path:
        return 0.0
    num = sum(c * v for c, v in path)
    den = sum(c for c, _ in path)
    raw = num / den if den != 0 else 0.0
    return float(np.clip(raw, 0.0, 1.0))

def cod_decision(intent: np.ndarray, outcome: np.ndarray,
                 H_top: float, Xi_sys: float) -> float:
    """
    COD = |⟨Ψ_intent|Ψ_outcome⟩|² * exp(-Λ·H_top) * exp(-Γ·Ξ_sys) * Ψ_id^org
    Note: Ψ_id^org is applied later as a hard gate; here we compute the core.
    """
    # fidelity term (overlap squared)
    dot = np.dot(intent, outcome)
    norm_i = np.linalg.norm(intent)
    norm_o = np.linalg.norm(outcome)
    if norm_i == 0 or norm_o == 0:
        fidelity = 0.0
    else:
        fidelity = (dot / (norm_i * norm_o)) ** 2
    fidelity = float(np.clip(fidelity, 0.0, 1.0))

    # damping & stiffness penalty
    damping = np.exp(-LAMBDA_COUPLING * H_top)
    stiffness = np.exp(-GAMMA_COUPLING * Xi_sys)

    return fidelity * damping * stiffness  # Ψ_id^org multiplied later as gate

def phi_density_ledger(H_top: float, cod_gain: float,
                       audit_complexity: float = 1.0) -> float:
    """
    Φ_gain = ΔCOD - 0.5*H_top - ΔS_audit
    where ΔS_audit = k_B * ln(2) * audit_complexity
    """
    noise_cost = 0.5 * H_top
    audit_entropy = K_BOLTZMANN * np.log(2.0) * audit_complexity
    return cod_gain - noise_cost - audit_entropy

def identity_gate(psi_id_org: float) -> bool:
    """Hard gate: Ψ_id^org must be ≥ 0.95."""
    return psi_id_org >= PSI_ID_THRESHOLD

def stiffness_modulation(H_top: float, Xi_sys: float) -> float:
    """
    Adiabatic control:
      if H_top < 0.5*H_LIMIT → Xi_sys *= 1.1 (max 3.0)
      else                     → Xi_sys *= 0.9 (min 0.5)
    H_LIMIT from spec = 0.85
    """
    H_LIMIT = 0.85
    if H_top < 0.5 * H_LIMIT:
        return min(XI_SYS_MAX, Xi_sys * 1.1)
    else:
        return max(XI_SYS_MIN, Xi_sys * 0.9)

# ------------------------------
# 3. Validation Tests
# ------------------------------
def run_validation():
    rng = np.random.default_rng(seed=42)
    errors = []

    # --- Test 1: Dimensional Consistency & Range Checks ---
    for _ in range(1000):
        # random path: cost, variance in [0,1]
        path = [(rng.random(), rng.random()) for _ in range(rng.integers(1, 10))]
        H = topological_impedance(path)
        if not (0.0 <= H <= 1.0):
            errors.append(f"H_top out of bounds: {H}")

        # random intent/outcome vectors (4-dim)
        intent = rng.random(4)
        outcome = rng.random(4)
        Xi = rng.uniform(XI_SYS_MIN, XI_SYS_MAX)
        cod = cod_decision(intent, outcome, H, Xi)
        if not (0.0 <= cod <= 1.0):
            errors.append(f"COD out of bounds: {cod}")

        # Ψ_id^org gate
        psi_id = rng.uniform(0.8, 1.0)
        if not identity_gate(psi_id) and psi_id < PSI_ID_THRESHOLD:
            # gate should reject
            pass
        elif identity_gate(psi_id) and psi_id >= PSI_ID_THRESHOLD:
            pass
        else:
            errors.append(f"Identity gate misbehaved: psi_id={psi_id}")

        # stiffness modulation bounds
        new_Xi = stiffness_modulation(H, Xi)
        if not (XI_SYS_MIN <= new_Xi <= XI_SYS_MAX):
            errors.append(f"Stiffness modulation out of bounds: {new_Xi}")

        # Φ ledger: gain can be negative, but audit cost always positive
        audit = rng.uniform(0.5, 2.0)
        phi = phi_density_ledger(H, cod_gain=cod, audit_complexity=audit)
        # no range restriction, just ensure it's a float
        if not isinstance(phi, float):
            errors.append(f"Φ not a float: {phi}")

    # --- Test 2: Invariant Violations Trigger Gates ---
    # Low identity should be rejected by gate
    assert not identity_gate(0.94), "Identity gate failed to block <0.95"
    assert identity_gate(0.95), "Identity gate incorrectly blocked ≥0.95"

    # Stiffness modulation respects bounds
    assert stiffness_modulation(0.1, 3.0) == XI_SYS_MAX, "Upper bound clamp failed"
    assert stiffness_modulation(0.9, 0.5) == XI_SYS_MIN, "Lower bound clamp failed"

    # COD formula reduces to fidelity when H_top=0, Xi_sys=0
    intent = np.array([1.0, 0.0, 0.0, 0.0])
    outcome = np.array([1.0, 0.0, 0.0, 0.0])
    assert np.isclose(cod_decision(intent, outcome, 0.0, 0.0), 1.0), "COD fidelity test failed"
    outcome_orth = np.array([0.0, 1.0, 0.0, 0.0])
    assert np.isclose(cod_decision(intent, outcome_orth, 0.0, 0.0), 0.0), "COD orthogonality test failed"

    # Φ ledger subtracts audit cost correctly
    base = phi_density_ledger(0.2, 0.5, audit_complexity=0.0)
    with_audit = phi_density_ledger(0.2, 0.5, audit_complexity=1.0)
    expected_diff = K_BOLTZMANN * np.log(2.0)
    assert np.isclose(with_audit, base - expected_diff), "Audit cost subtraction failed"

    # --- Test 3: Procedural Black Hole Detection Logic ---
    # From spec: H_top > H_LIMIT (0.85) AND F_urg < ∇H_top (approx H_top*0.5)
    H_LIMIT = 0.85
    def is_black_hole(H_top, F_urg):
        return H_top > H_LIMIT and F_urg < (H_TOP_LIMIT * 0.5)

    assert is_black_hole(0.9, 0.2) == True, "Black hole detection false negative"
    assert is_black_hole(0.8, 0.2) == False, "Black hole detection false positive"
    assert is_black_hole(0.9, 0.5) == False, "Black hole detection false positive (urgency high)"

    # --- Summary ---
    if errors:
        raise AssertionError(f"Validation failed with {len(errors)} errors:\n" + "\n".join(errors[:5]))
    else:
        print("✅ All Omega Protocol invariants and mathematical checks passed.")

if __name__ == "__main__":
    run_validation()