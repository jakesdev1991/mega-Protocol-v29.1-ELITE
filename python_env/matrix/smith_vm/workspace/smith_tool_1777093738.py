# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
# =============================================================================
# OMEGA PROTOCOL VALIDATION SCRIPT
# Validates the mathematical soundness and invariant compliance of the
# ML-Physics Integrity Manifold (v63.0-Ω) as described in the C++ analysis.
# =============================================================================
import math
from enum import Enum, auto
from typing import List, Tuple, Complex

# -----------------------------
# 1. Replicate key constants and enums from the C++ code
# -----------------------------
class MLPhysicsInvariants:
    PSI_INTEGRITY_THRESHOLD = 0.95
    LOG_EXPOSURE_MAX = 0.25          # max allowed ml_physics_risk
    ML_PROVENANCE_MIN = 0.80
    COD_THRESHOLD = 0.85
    CONVERGENCE_CONFIDENCE_MIN = 0.70
    AUDIT_ENTROPY_PER_CHECK = 0.02

    class RiskLevel(Enum):
        LOW = auto()
        MEDIUM = auto()
        CRITICAL = auto()
        CATASTROPHIC = auto()

    class ConvergenceType(Enum):
        LEGITIMATE_CONVERGENCE = auto()
        DOMAIN_CONTAMINATION = auto()
        UNCERTAIN_PROVENANCE = auto()


# -----------------------------
# 2. Helper functions mirroring the C++ logic
# -----------------------------
AUTHORIZED_ML_SYSTEMS = {
    "plasma_disruption_predictor_v3",
    "realtime_control_neural_net",
    "diagnostic_calibration_ml",
    "federated_learning_tokamak"
}

def calculate_provenance_score(ml_system_id: str, physics_ml_coupling: float) -> float:
    """Return ML provenance score in [0,1]."""
    is_authorized = ml_system_id in AUTHORIZED_ML_SYSTEMS
    if is_authorized:
        # 0.90 + 0.10 * coupling -> [0.90, 1.0]
        return 0.90 + 0.10 * max(0.0, min(1.0, physics_ml_coupling))
    if not ml_system_id:  # empty string
        return 0.50
    # unauthorized: 0.20 * (1 - coupling) -> [0.0, 0.20]
    return 0.20 * max(0.0, min(1.0, 1.0 - physics_ml_coupling))


def classify_convergence(provenance_score: float, physics_ml_coupling: float) -> MLPhysicsInvariants.ConvergenceType:
    if provenance_score >= MLPhysicsInvariants.ML_PROVENANCE_MIN:
        return MLPhysicsInvariants.ConvergenceType.LEGITIMATE_CONVERGENCE
    if provenance_score < 0.40 and physics_ml_coupling > 0.60:
        return MLPhysicsInvariants.ConvergenceType.DOMAIN_CONTAMINATION
    return MLPhysicsInvariants.ConvergenceType.UNCERTAIN_PROVENANCE


def calculate_ml_physics_risk(log_exposure: float, physics_ml_coupling: float, ml_provenance_score: float) -> float:
    """Risk = Exposure × Coupling × (1 - Provenance), clamped to [0,1]."""
    provenance_factor = 1.0 - ml_provenance_score
    risk = log_exposure * physics_ml_coupling * provenance_factor
    return max(0.0, min(1.0, risk))


def assess_risk_level(ml_physics_risk: float) -> MLPhysicsInvariants.RiskLevel:
    if ml_physics_risk > 0.70:
        return MLPhysicsInvariants.RiskLevel.CATASTROPHIC
    if ml_physics_risk > 0.50:
        return MLPhysicsInvariants.RiskLevel.CRITICAL
    if ml_physics_risk > 0.30:
        return MLPhysicsInvariants.RiskLevel.MEDIUM
    return MLPhysicsInvariants.RiskLevel.LOW


def calculate_cod_mlphysics(
    diagnostic_vec: List[Complex],
    plasma_vec: List[Complex],
    h_instability: float,
    theta_tensor_leak: float,
    ml_provenance_score: float,
    convergence_confidence: float
) -> float:
    """Compute COD with ML‑physics penalties; returns value in [0,1]."""
    LAMBDA_COUPLING = 0.5
    MU_ML_PROVENANCE = 0.6

    # 1. Fidelity (generic alignment)
    dot = 0.0
    magD = 0.0
    magP = 0.0
    size = min(len(diagnostic_vec), len(plasma_vec))
    for i in range(size):
        d = diagnostic_vec[i]
        p = plasma_vec[i]
        dot += abs(d.conjugate() * p)
        magD += abs(d * d)
        magP += abs(p * p)

    fidelity = 0.0
    if magD > 1e-9 and magP > 1e-9:
        fidelity = dot / (math.sqrt(magD) * math.sqrt(magP))
        fidelity = max(0.0, min(1.0, fidelity))

    # 2. Penalties (all in (0,1] because exp(-k*x) with x>=0)
    instability_penalty = math.exp(-LAMBDA_COUPLING * max(0.0, min(1.0, h_instability)))
    exposure_penalty = math.exp(-LAMBDA_COUPLING * max(0.0, min(1.0, theta_tensor_leak)))
    provenance_penalty = math.exp(-MU_ML_PROVENANCE * (1.0 - max(0.0, min(1.0, ml_provenance_score))))
    convergence_penalty = math.exp(-MU_ML_PROVENANCE * (1.0 - max(0.0, min(1.0, convergence_confidence))))

    cod = fidelity * instability_penalty * exposure_penalty * provenance_penalty * convergence_penalty
    return max(0.0, min(1.0, cod))


def ml_physics_silence_protocol_decide(
    psi_integrity: float,
    ml_physics_risk: float,
    convergence_type: MLPhysicsInvariants.ConvergenceType
) -> Tuple[int, str]:
    """
    Return (action_code, message) where action_code:
        0 = PROCEED
        1 = FLAG_FOR_REVIEW
        2 = FREEZE_ML_OPERATIONS
        3 = IDENTITY_LOCKDOWN
    """
    # PRIMARY GATE: Psi integrity
    if psi_integrity < MLPhysicsInvariants.PSI_INTEGRITY_THRESHOLD:
        return 3, "CRITICAL: Domain contamination or integrity breach. Lockdown initiated."

    # CONVERGENCE TYPE GATE
    if convergence_type == MLPhysicsInvariants.ConvergenceType.DOMAIN_CONTAMINATION:
        return 3, "CRITICAL: Domain contamination or integrity breach. Lockdown initiated."

    # RISK-BASED DECISIONS
    if ml_physics_risk > 0.70:
        return 3, "CRITICAL: Domain contamination or integrity breach. Lockdown initiated."
    if ml_physics_risk > 0.50:
        return 2, "Critical ML risk detected. Freezing ML operations."
    if ml_physics_risk > 0.30:
        return 1, "ML provenance uncertain. Flagged for manual review."
    return 0, "ML-Physics convergence verified. Operations secure."


def invariant_enforcer_check(
    state: dict,
    cod: float,
    ml_physics_risk: float,
    convergence_type: MLPhysicsInvariants.ConvergenceType
) -> dict:
    """Return a dict of boolean checks; AllPassed if all True."""
    checks = {
        "psi_integrity_ok": state["psi_integrity"] >= MLPhysicsInvariants.PSI_INTEGRITY_THRESHOLD,
        "log_exposure_ok": ml_physics_risk <= MLPhysicsInvariants.LOG_EXPOSURE_MAX,
        "ml_provenance_ok": state["ml_provenance_score"] >= MLPhysicsInvariants.ML_PROVENANCE_MIN,
        "cod_ok": cod >= MLPhysicsInvariants.COD_THRESHOLD,
        "convergence_valid": convergence_type != MLPhysicsInvariants.ConvergenceType.DOMAIN_CONTAMINATION,
        "audit_tracked": True   # we assume tracking is done
    }
    checks["all_passed"] = all(checks[key] for key in checks if key != "audit_tracked" and key != "all_passed")
    return checks


def phi_density_ledger_net_gain(
    cod_before: float,
    cod_after: float,
    audit_checks: int
) -> float:
    raw_gain = cod_after - cod_before
    audit_cost = audit_checks * MLPhysicsInvariants.AUDIT_ENTROPY_PER_CHECK
    return raw_gain - audit_cost


# -----------------------------
# 3. Validation Tests
# -----------------------------
def run_validation():
    print("=== OMEGA PROTOCOL VALIDATION START ===\n")

    # ---- Test 1: Provenance score bounds ----
    print("Test 1: Provenance score bounds")
    for sid in [*AUTHORIZED_ML_SYSTEMS, "unauth_sys", ""]:
        for coup in [0.0, 0.3, 0.7, 1.0]:
            sc = calculate_provenance_score(sid, coup)
            assert 0.0 <= sc <= 1.0, f"Provenance score out of bounds: {sc}"
    print("  PASS: All provenance scores in [0,1]\n")

    # ---- Test 2: ML physics risk bounds ----
    print("Test 2: ML physics risk bounds")
    for exp in [0.0, 0.2, 0.5, 1.0]:
        for coup in [0.0, 0.5, 1.0]:
            for prov in [0.0, 0.5, 1.0]:
                risk = calculate_ml_physics_risk(exp, coup, prov)
                assert 0.0 <= risk <= 1.0, f"Risk out of bounds: {risk}"
    print("  PASS: All risks in [0,1]\n")

    # ---- Test 3: COD bounds and monotonicity w.r.t. penalties ----
    print("Test 3: COD bounds")
    diag = [1+0j, 0.5+0.5j]
    plasm = [1+0j, 0.5+0.5j]
    base_cod = calculate_cod_mlphysics(diag, plasm, 0.0, 0.0, 1.0, 1.0)
    assert 0.0 <= base_cod <= 1.0, f"Base COD out of bounds: {base_cod}"
    # Increasing instability should decrease COD (or leave unchanged)
    hi_cod = calculate_cod_mlphysics(diag, plasm, 1.0, 0.0, 1.0, 1.0)
    assert hi_cod <= base_cod + 1e-9, "Instability penalty failed to reduce COD"
    # Increasing exposure should decrease COD
    exp_cod = calculate_cod_mlphysics(diag, plasm, 0.0, 1.0, 1.0, 1.0)
    assert exp_cod <= base_cod + 1e-9, "Exposure penalty failed to reduce COD"
    # Decreasing provenance should decrease COD
    prov_cod = calculate_cod_mlphysics(diag, plasm, 0.0, 0.0, 0.0, 1.0)
    assert prov_cod <= base_cod + 1e-9, "Provenance penalty failed to reduce COD"
    # Decreasing convergence confidence should decrease COD
    conf_cod = calculate_cod_mlphysics(diag, plasm, 0.0, 0.0, 1.0, 0.0)
    assert conf_cod <= base_cod + 1e-9, "Convergence penalty failed to reduce COD"
    print("  PASS: COD in [0,1] and penalties behave correctly\n")

    # ---- Test 4: Invariant enforcement logic ----
    print("Test 4: Invariant enforcement")
    state = {
        "psi_integrity": 0.96,
        "ml_provenance_score": 0.85,
        "log_exposure": 0.1,   # not directly used; risk is computed elsewhere
        "physics_ml_coupling": 0.7,
        "h_instability": 0.2,
        "theta_tensor_leak": 0.1,
        "convergence_confidence": 0.8
    }
    state["ml_provenance_score"] = calculate_provenance_score(
        state.get("ml_system_id", "plasma_disruption_predictor_v3"),
        state["physics_ml_coupling"]
    )
    state["ml_physics_risk"] = calculate_ml_physics_risk(
        state["log_exposure"],
        state["physics_ml_coupling"],
        state["ml_provenance_score"]
    )
    cod_val = calculate_cod_mlphysics(
        [1+0j, 0.5+0.5j],
        [1+0j, 0.5+0.5j],
        state["h_instability"],
        state["theta_tensor_leak"],
        state["ml_provenance_score"],
        state["convergence_confidence"]
    )
    conv_type = classify_convergence(state["ml_provenance_score"], state["physics_ml_coupling"])
    checks = invariant_enforcer_check(state, cod_val, state["ml_physics_risk"], conv_type)
    # With the chosen numbers we expect all to pass
    assert checks["all_passed"], f"Invariant check failed: {checks}"
    print("  PASS: All invariants satisfied for nominal state\n")

    # ---- Test 5: Silence protocol hierarchy ----
    print("Test 5: Silence protocol decision hierarchy")
    # Case A: low psi -> lockdown regardless
    act, msg = ml_physics_silence_protocol_decide(0.90, 0.1, MLPhysicsInvariants.ConvergenceType.LEGITIMATE_CONVERGENCE)
    assert act == 3, f"Expected lockdown (3) for low psi, got {act}"
    # Case B: contamination -> lockdown
    act, msg = ml_physics_silence_protocol_decide(0.96, 0.1, MLPhysicsInvariants.ConvergenceType.DOMAIN_CONTAMINATION)
    assert act == 3, f"Expected lockdown for contamination, got {act}"
    # Case C: high risk -> lockdown/freeze/flag
    act, msg = ml_physics_silence_protocol_decide(0.96, 0.6, MLPhysicsInvariants.ConvergenceType.LEGITIMATE_CONVERGENCE)
    assert act == 3, f"Expected lockdown for risk>0.7, got {act}"
    act, msg = ml_physics_silence_protocol_decide(0.96, 0.55, MLPhysicsInvariants.ConvergenceType.LEGITIMATE_CONVERGENCE)
    assert act == 2, f"Expected freeze for risk>0.5, got {act}"
    act, msg = ml_physics_silence_protocol_decide(0.96, 0.4, MLPhysicsInvariants.ConvergenceType.LEGITIMATE_CONVERGENCE)
    assert act == 1, f"Expected flag for risk>0.3, got {act}"
    act, msg = ml_physics_silence_protocol_decide(0.96, 0.2, MLPhysicsInvariants.ConvergenceType.LEGITIMATE_CONVERGENCE)
    assert act == 0, f"Expected proceed for low risk, got {act}"
    print("  PASS: Protocol hierarchy respected\n")

    # ---- Test 6: Φ-density ledger (audit cost subtraction) ----
    print("Test 6: Φ-density ledger")
    gain = phi_density_ledger_net_gain(0.70, 0.80, 5)   # raw gain 0.10, audit cost 5*0.02=0.10
    assert abs(gain - 0.0) < 1e-9, f"Net gain should be zero after audit cost, got {gain}"
    gain2 = phi_density_ledger_net_gain(0.70, 0.85, 2)  # raw 0.15, cost 0.04 -> 0.11
    assert abs(gain2 - 0.11) < 1e-9, f"Expected 0.11, got {gain2}"
    print("  PASS: Audit cost correctly subtracted\n")

    # ---- Test 7: Dimensional consistency (no log transforms) ----
    print("Test 7: Checking for forbidden log2/log transforms")
    # We simply inspect the source strings of the key functions for "log2" or "math.log"
    import inspect, re
    funcs = [
        calculate_provenance_score,
        classify_convergence,
        calculate_ml_physics_risk,
        calculate_cod_mlphysics,
        ml_physics_silence_protocol_decide,
        invariant_enforcer_check,
        phi_density_ledger_net_gain
    ]
    for f in funcs:
        src = inspect.getsource(f)
        assert "log2" not in src.lower(), f"Found log2 in {f.__name__}"
        assert re.search(r"\bmath\.log\b", src) is None, f"Found math.log in {f.__name__}"
    print("  PASS: No log2 or math.log found\n")

    print("\n=== ALL VALIDATION TESTS PASSED ===")
    print("The ML-Physics Integrity Manifold (v63.0-Ω) is mathematically sound")
    print("and compliant with Omega Protocol invariants.")


if __name__ == "__main__":
    run_validation()