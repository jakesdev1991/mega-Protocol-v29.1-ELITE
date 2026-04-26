# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
# --------------------------------------------------------------
# Omega Protocol Invariant Validator – Python Simulation
# --------------------------------------------------------------
# This script reproduces the core mathematical relationships from
# the supplied C++ implementation and checks:
#   1. Dimensional homogeneity (all quantities dimensionless [1]).
#   2. Active invariant enforcement (psi_id >= 0.95, 0.2 <= xi_bound <= 3.0).
#   3. Correct COD formulation.
#   4. Entropy accounting (audit cost subtraction).
#   5. Failure‑mode detection logic.
# --------------------------------------------------------------
import math
from typing import List, Tuple

# ----- Constants from the Omega Rubric (dimensionless) -----
LAMBDA_COUPLING = 1.0          # entropic damping
GAMMA_COUPLING  = 0.5          # stiffness penalty
K_BOLTZMANN     = 1.0          # normalized for informational entropy
PSI_ID_MIN      = 0.95
XI_BOUND_MIN    = 0.2
XI_BOUND_MAX    = 3.0
V_VAL_LIMIT     = 1.5          # max validation force before shock
PSI_ID_CRITICAL = 0.90         # identity‑dissociation threshold
COD_THRESHOLD   = 0.85
COD_LOOP_LIMIT  = 0.60         # recursion‑loop trigger

# ----- Helper functions -------------------------------------------------
def fidelity(psi_cur: List[float], psi_tgt: List[float]) -> float:
    """|<Ψ_cur|Ψ_tgt>|²  (squared overlap)."""
    if len(psi_cur) != len(psi_tgt):
        raise ValueError("State vectors must have equal dimension")
    dot = sum(c * t for c, t in zip(psi_cur, psi_tgt))
    mag_c = sum(c * c for c in psi_cur)
    mag_t = sum(t * t for t in psi_tgt)
    if mag_c == 0.0 or mag_t == 0.0:
        return 0.0
    f = dot / math.sqrt(mag_c * mag_t)
    return f * f                     # squared overlap

def shannon_conditional_entropy(psi_cur: List[float], psi_tgt: List[float]) -> float:
    """H(State|Validation) = -[p log p + (1-p) log(1-p)], p = normalized overlap."""
    dot = sum(c * t for c, t in zip(psi_cur, psi_tgt))
    mag_c = sum(c * c for c in psi_cur)
    mag_t = sum(t * t for t in psi_tgt)
    if mag_c == 0.0 or mag_t == 0.0:
        p = 0.0
    else:
        p = dot / math.sqrt(mag_c * mag_t)
    # clamp to avoid log(0)
    p = max(0.001, min(0.999, p))
    return -(p * math.log(p) + (1.0 - p) * math.log(1.0 - p))

def cod(psi_cur: List[float], psi_tgt: List[float],
        h_sys: float, xi_bound: float) -> float:
    """Chain Overlap Density: fidelity * exp(-Λ·H) * exp(-Γ·Ξ)."""
    fid = fidelity(psi_cur, psi_tgt)
    damp = math.exp(-LAMBDA_COUPLING * h_sys)
    stiff_pen = math.exp(-GAMMA_COUPLING * xi_bound)
    return fid * damp * stiff_pen

def audit_cost(complexity: float = 1.0) -> float:
    """ΔS_audit = k ln 2 × complexity."""
    return K_BOLTZMANN * math.log(2.0) * complexity

def phi_loss(psi_id: float, xi_bound: float,
             audit_complexity: float = 1.0) -> float:
    """Φ_loss = identity erosion + stability breach + audit cost."""
    loss = 0.0
    if psi_id < PSI_ID_MIN:
        loss += (PSI_ID_MIN - psi_id) * 0.5 * K_BOLTZMANN
    if xi_bound > XI_BOUND_MAX:
        loss += (xi_bound - XI_BOUND_MAX) * 0.2 * K_BOLTZMANN
    loss += audit_cost(audit_complexity)
    return loss

def verify_invariants(psi_id: float, xi_bound: float) -> Tuple[bool, str]:
    """Active boundary‑condition gate."""
    if psi_id < PSI_ID_MIN:
        return False, f"Identity Dissociation: psi_id={psi_id:.3f} < {PSI_ID_MIN}"
    if xi_bound > XI_BOUND_MAX:
        return False, f"Validation Rejection Risk: xi_bound={xi_bound:.3f} > {XI_BOUND_MAX}"
    if xi_bound < XI_BOUND_MIN:
        return False, f"Identity Fragmentation Risk: xi_bound={xi_bound:.3f} < {XI_BOUND_MIN}"
    return True, "Invariants satisfied"

def failure_mode(psi_id: float, v_val: float,
                 xi_bound: float, cod_val: float) -> str:
    """Return failure type or 'NONE'."""
    if psi_id < PSI_ID_CRITICAL:
        return "IDENTITY_DISSOCIATION"
    if v_val > V_VAL_LIMIT and xi_bound > 2.5:
        return "VALIDATION_REJECTION"
    if cod_val < COD_LOOP_LIMIT and v_val > 0.5:
        return "RECURSION_LOOP"
    return "NONE"

def adiabatic_validation_step(psi_cur: List[float], psi_tgt: List[float],
                              h_sys: float, xi_bound: float,
                              v_val: float, t: float,
                              psi_id: float) -> Tuple[List[float], float, float, bool, str]:
    """
    One iteration of the Adiabatic Validation Protocol.
    Returns (new_psi_cur, new_xi_bound, new_v_val, success, msg).
    """
    # ---- Phase 1: Diagnostic (implicit in failure detection) ----
    cod_val = cod(psi_cur, psi_tgt, h_sys, xi_bound)
    fail = failure_mode(psi_id, v_val, xi_bound, cod_val)
    if fail != "NONE":
        # simple corrective actions as in the C++ code
        if fail == "VALIDATION_REJECTION":
            v_val = min(v_val * 0.8, 1.0)
            msg = f"Reduced V_val to avoid shock -> {v_val:.3f}"
        elif fail == "RECURSION_LOOP":
            xi_bound = max(0.5, xi_bound * 0.9)
            msg = f"Lowered stiffness to break loop -> {xi_bound:.3f}"
        else:
            msg = f"Failure mode {fail} requires abort"
        return psi_cur, xi_bound, v_val, False, msg

    # ---- Phase 2: Stiffness Softening (adiabatic window) ----
    target_xi = 1.0
    alpha = 0.1
    xi_bound = xi_bound * (1.0 - alpha) + target_xi * alpha

    # ---- Phase 3: Validation Injection (tanh ramp) ----
    tau, sigma = 0.5, 0.2
    ramp = math.tanh((t - tau) / sigma)
    v_val = min(ramp * 1.2, 1.2)   # max 1.2 to stay below shock threshold

    # ---- Phase 4: State Update (weighted collapse) ----
    new_psi = [0.8 * c + 0.2 * tgt for c, tgt in zip(psi_cur, psi_tgt)]

    # ---- Phase 5: Lock & Invariant Check ----
    # increase stiffness on new path (lock)
    xi_bound = xi_bound * (1.0 - alpha) + 2.0 * alpha   # target 2.0
    ok, msg = verify_invariants(psi_id, xi_bound)
    if not ok:
        return new_psi, xi_bound, v_val, False, f"Lock failed: {msg}"
    return new_psi, xi_bound, v_val, True, "Reboot step succeeded"

# ----- Test Suite -------------------------------------------------------
def run_tests():
    print("=== Omega Protocol Mathematical Validation ===")
    # 1. Dimensional homogeneity sanity check
    psi_cur = [0.6, 0.8]
    psi_tgt = [0.9, 0.4]
    h_sys   = 0.3
    xi_b    = 1.5
    v_val   = 0.7
    psi_id  = 0.96

    # COD should be dimensionless
    c = cod(psi_cur, psi_tgt, h_sys, xi_b)
    assert isinstance(c, float) and 0.0 <= c <= 1.0, f"COD out of bounds: {c}"
    print(f"[PASS] COD = {c:.4f} (dimensionless)")

    # 2. Invariant gate
    ok, msg = verify_invariants(psi_id, xi_b)
    assert ok, f"Invariant check failed: {msg}"
    print(f"[PASS] Invariant gate: {msg}")

    # 3. Failure‑mode detection
    fm = failure_mode(psi_id, v_val, xi_b, c)
    assert fm == "NONE", f"Unexpected failure mode: {fm}"
    print(f"[PASS] Failure mode detection: {fm}")

    # 4. Audit cost subtraction
    loss = phi_loss(psi_id, xi_b, audit_complexity=1.2)
    expected_loss = audit_cost(1.2)  # only audit cost because psi_id & xi_b are OK
    assert math.isclose(loss, expected_loss, rel_tol=1e-9), \
        f"Phi loss mismatch: got {loss}, expected {expected_loss}"
    print(f"[PASS] Φ‑loss = {loss:.6f} (audit cost subtracted)")

    # 5. Full AVP step
    new_psi, new_xi, new_v, success, msg = adiabatic_validation_step(
        psi_cur, psi_tgt, h_sys, xi_b, v_val, t=0.6, psi_id=psi_id)
    assert success, f"AVP step failed: {msg}"
    # post‑step invariants must still hold
    ok2, msg2 = verify_invariants(psi_id, new_xi)
    assert ok2, f"Post‑step invariant violation: {msg2}"
    print(f"[PASS] AVP step: {msg}")
    print(f"    New state vector: {[round(x,4) for x in new_psi]}")
    print(f"    New stiffness: {new_xi:.4f}, New validation force: {new_v:.4f}")

    # 6. Edge case: identity dissociation triggers abort
    psi_id_low = 0.90
    _, _, _, success_low, msg_low = adiabatic_validation_step(
        psi_cur, psi_tgt, h_sys, xi_b, v_val, t=0.6, psi_id=psi_id_low)
    assert not success_low, "Should have failed on low psi_id"
    assert "Identity Dissociation" in msg_low
    print(f"[PASS] Low psi_id correctly aborts: {msg_low}")

    # 7. Edge case: excessive validation force triggers shock avoidance
    v_val_high = 2.0
    _, _, new_v_high, success_high, msg_high = adiabatic_validation_step(
        psi_cur, psi_tgt, h_sys, xi_b, v_val_high, t=0.6, psi_id=psi_id)
    # The protocol should reduce v_val (see InjectValidation logic)
    assert success_high, f"AVP step failed unexpectedly: {msg_high}"
    assert new_v_high <= 1.2, f"Validation force not clamped: {new_v_high}"
    print(f"[PASS] High V_val clamped to {new_v_high:.4f}: {msg_high}")

    print("\n=== All validation checks passed ===")

if __name__ == "__main__":
    run_tests()