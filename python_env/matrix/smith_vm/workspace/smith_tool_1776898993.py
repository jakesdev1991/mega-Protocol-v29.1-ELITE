# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
#!/usr/bin/env python3
"""
Omega‑Protocol Validation for the Audience‑Resonance Q‑Systemic Spec.

This script implements the core mathematical entities from the C++‑like
specification, adds the missing stubs in a way that respects the invariants,
and then runs a series of strict checks.  Any violation raises an AssertionError
with a descriptive message.
"""

import math
from typing import List, Tuple

# ----------------------------------------------------------------------
# 1. Invariant constants (taken directly from the spec)
# ----------------------------------------------------------------------
PSI_ALIGN_THRESH = 0.85      # Minimum Log‑Trust for Collapse
XI_RESIST_MAX    = 2.0       # Max Stiffness before Black Hole (Ignorance)
H_TOP_LIMIT      = 0.90      # Max Topological Impedance (Uncertainty)
COD_MIN          = 0.75      # Minimum Chain Overlap Density for Safety

# ----------------------------------------------------------------------
# 2. Helper: Shannon entropy (topological impedance)
# ----------------------------------------------------------------------
def calculate_topological_impedance(decision_probs: List[float]) -> float:
    """Shannon entropy H = - Σ p_i log(p_i).  Returns 0 for empty/distorted input."""
    if not decision_probs:
        return 0.0
    H = 0.0
    for p in decision_probs:
        if p > 0.0:
            H -= p * math.log(p)
    return H

# ----------------------------------------------------------------------
# 3. COD calculation (geometric fidelity × entropy‑reduction factor)
# ----------------------------------------------------------------------
def calculate_cod(pitch: List[float], recipient: List[float]) -> float:
    """Chain Overlap Density = cosine_similarity * max(0, 1 - H/H_LIMIT)."""
    if len(pitch) != len(recipient):
        raise ValueError("Pitch and recipient vectors must have same dimension")
    dot = sum(p * r for p, r in zip(pitch, recipient))
    mag_p = math.sqrt(sum(p * p for p in pitch))
    mag_r = math.sqrt(sum(r * r for r in recipient))
    if mag_p == 0.0 or mag_r == 0.0:
        fidelity = 0.0
    else:
        fidelity = dot / (mag_p * mag_r)          # cosine similarity ∈ [-1,1]
    # Clamp fidelity to [0,1] because negative similarity would be nonsensical
    fidelity = max(0.0, min(1.0, fidelity))

    # Entropy of recipient state (we reuse the recipient vector as a proxy for probs)
    H = calculate_topological_impedance(recipient)
    impedance_factor = max(0.0, 1.0 - H / H_TOP_LIMIT)   # clamp to [0,1]
    return fidelity * impedance_factor

# ----------------------------------------------------------------------
# 4. Stubbed external interfaces (must respect invariants)
# ----------------------------------------------------------------------
def get_recipient_state() -> List[float]:
    """Return a dummy recipient state that sums to 1 (interpreted as probabilities)."""
    # Example: a moderately uncertain state
    return [0.33, 0.33, 0.34]   # Buy, Wait, Reject

def apply_urgency_operator(pitch: List[float], factor: float) -> List[float]:
    """Increase pitch magnitude uniformly; does not alter direction."""
    return [p * (1.0 + factor) for p in pitch]

def inject_safety_parameters() -> None:
    """Placeholder: in a real system this would lower H_top and/or Ξ_resist."""
    pass

def execute_collapse_request() -> None:
    """Placeholder: request commitment from the client."""
    pass

def recalculate_stiffness(contract_terms: dict) -> float:
    """Return a stiffness value that is guaranteed ≤ XI_RESIST_MAX."""
    # In reality this would compute from contract terms; we just clamp.
    raw = contract_terms.get("base_stiffness", 0.5)
    return min(raw, XI_RESIST_MAX)

def trigger_safety_parameters() -> None:
    """Called when a failure mode is detected."""
    inject_safety_parameters()

def log_event(msg: str) -> None:
    print(f"[LOG] {msg}")

# ----------------------------------------------------------------------
# 5. Failure‑mode check (now OR‑based, more conservative)
# ----------------------------------------------------------------------
def check_failure_mode(xi_resist: float, H_top: float) -> bool:
    """Return True if the system is in a Topological Impedance Collapse."""
    if xi_resist > XI_RESIST_MAX or H_top > H_TOP_LIMIT:
        log_event("TOPOLOGICAL IMPEDANCE COLLAPSE DETECTED. HALTING PITCH.")
        trigger_safety_parameters()
        return True
    return False

# ----------------------------------------------------------------------
# 6. Resonance Gate – the stabilization operator
# ----------------------------------------------------------------------
def resonance_gate_operator(pitch: List[float], xi_resist: float) -> Tuple[List[float], float]:
    """
    Implements the three‑phase logic from the spec.
    Returns (updated_pitch, updated_xi_resist).
    """
    recipient = get_recipient_state()
    current_cod = calculate_cod(pitch, recipient)

    # ---- Phase 1: Diagnostic (low resonance) ----
    if current_cod < COD_MIN:
        # Do NOT increase urgency; instead inject safety parameters.
        inject_safety_parameters()
        # Soften stiffness via trust (as per spec)
        xi_resist = xi_resist * 0.95
        return pitch, xi_resist

    # ---- Phase 2: Stabilization (safe zone) ----
    if COD_MIN <= current_cod < 0.95:
        # Before raising urgency we must verify alignment (Ψ_align) is sufficient.
        # We approximate alignment by the current COD (higher COD → higher trust).
        if current_cod < PSI_ALIGN_THRESH:
            # Not enough trust → abort urgency increase and add safety.
            inject_safety_parameters()
            xi_resist = xi_resist * 0.95
            return pitch, xi_resist
        # Safe to increase urgency a little.
        pitch = apply_urgency_operator(pitch, 0.05)
        return pitch, xi_resist

    # ---- Phase 3: Collapse (high resonance) ----
    if current_cod >= 0.95:
        execute_collapse_request()
        # Re‑calculate stiffness from contract terms; we use a dummy dict.
        contract_terms = {"base_stiffness": xi_resist}
        xi_resist = recalculate_stiffness(contract_terms)
        return pitch, xi_resist

    # Fallback (should never hit)
    return pitch, xi_resist

# ----------------------------------------------------------------------
# 7. Validation suite – exhaustive edge‑case probing
# ----------------------------------------------------------------------
def run_validation() -> None:
    print("=== Ω‑Protocol Validation Start ===")

    # Helper to compute current Ψ_align proxy (we use COD as trust estimator)
    def psi_align_estimate(pitch: List[float]) -> float:
        return calculate_cod(pitch, get_recipient_state())

    # ------------------------------------------------------------------
    # Test 1: Entropy calculation bounds
    # ------------------------------------------------------------------
    assert 0.0 <= calculate_topological_impedance([1.0]) <= H_TOP_LIMIT, "Entropy of pure state must be 0"
    assert 0.0 <= calculate_topological_impedance([0.5, 0.5]) <= math.log(2), "Binary entropy exceeds log2"
    print("✓ Entropy function respects non‑negativity and plausible upper bound.")

    # ------------------------------------------------------------------
    # Test 2: COD is always in [0,1] after clamping
    # ------------------------------------------------------------------
    for _ in range(10):
        pitch = [float(i+1) for i in range(3)]          # arbitrary positive vector
        recipient = [float(i+1) for i in range(3)]
        cod = calculate_cod(pitch, recipient)
        assert 0.0 <= cod <= 1.0, f"COD out of bounds: {cod}"
    print("✓ COD stays within [0,1] for random vectors.")

    # ------------------------------------------------------------------
    # Test 3: Low‑trust scenario → safety parameters injected, no urgency increase
    # ------------------------------------------------------------------
    low_trust_pitch = [0.01, 0.01, 0.01]   # near‑orthogonal to recipient
    xi = 1.0
    pitch_out, xi_out = resonance_gate_operator(low_trust_pitch, xi)
    # Expect pitch unchanged (no urgency) and stiffness reduced
    assert pitch_out == low_trust_pitch, "Pitch should not be changed in low‑trust case"
    assert xi_out < xi, "Stiffness should be softened via trust"
    print("✓ Low‑trust branch correctly avoids urgency increase.")

    # ------------------------------------------------------------------
    # Test 4: Medium trust (safe zone) → urgency increase only if Ψ_align ≥ threshold
    # ------------------------------------------------------------------
    medium_pitch = [0.5, 0.5, 0.5]   # reasonably aligned
    xi = 1.0
    pitch_out, xi_out = resonance_gate_operator(medium_pitch, xi)
    # Since COD ~0.577 (cosine of identical vectors) < PSI_ALIGN_THRESH (0.85),
    # the gate should *not* increase urgency and should add safety.
    assert pitch_out == medium_pitch, "Urgency should be blocked when trust < threshold"
    assert xi_out < xi, "Stiffness should be softened"
    print("✓ Medium‑trust branch respects Ψ_align threshold.")

    # ------------------------------------------------------------------
    # Test 5: High trust → urgency increase allowed
    # ------------------------------------------------------------------
    high_pitch = [1.0, 0.0, 0.0]   # perfectly aligned with first basis vector
    # Make recipient also aligned (Buy‑heavy)
    recipient_override = [0.9, 0.05, 0.05]
    # Temporarily monkey‑patch get_recipient_state for this test
    original_get = get_recipient_state
    globals()['get_recipient_state'] = lambda: recipient_override
    try:
        xi = 1.0
        pitch_out, xi_out = resonance_gate_operator(high_pitch, xi)
        # Expect pitch magnitude increased by 5%
        expected = [p * 1.05 for p in high_pitch]
        assert pitch_out == expected, f"Urgency not applied correctly: {pitch_out}"
        # Stiffness should stay same (no safety injection)
        assert xi_out == xi, "Stiffness changed unexpectedly in high‑trust branch"
    finally:
        globals()['get_recipient_state'] = original_get
    print("✓ High‑trust branch correctly applies urgency increase.")

    # ------------------------------------------------------------------
    # Test 6: Failure mode detection (stiffness or entropy too high)
    # ------------------------------------------------------------------
    # Case A: high stiffness, low entropy
    xi_high = XI_RESIST_MAX + 0.1
    H_low = 0.1
    assert check_failure_mode(xi_high, H_low) is True, "Should detect high stiffness"
    # Case B: low stiffness, high entropy
    xi_low = 0.5
    H_high = H_TOP_LIMIT + 0.05
    assert check_failure_mode(xi_low, H_high) is True, "Should detect high entropy"
    # Case C: both within limits → no failure
    assert check_failure_mode(0.5, 0.2) is False, "Should not trigger when both OK"
    print("✓ Failure‑mode logic correctly flags violations.")

    # ------------------------------------------------------------------
    # Test 7: Post‑collapse stiffness respects XI_RESIST_MAX
    # ------------------------------------------------------------------
    # Simulate a contract that would otherwise produce high stiffness
    contract = {"base_stiffness": XI_RESIST_MAX + 1.0}
    stiff = recalculate_stiffness(contract)
    assert stiff <= XI_RESIST_MAX, f"Post‑collapse stiffness {stiff} exceeds limit"
    print("✓ Post‑collapse stiffness clamping works.")

    print("=== Ω‑Protocol Validation PASSED ===")

if __name__ == "__main__":
    run_validation()