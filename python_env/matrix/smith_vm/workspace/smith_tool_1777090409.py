# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
#!/usr/bin/env python3
"""
Omega Protocol Validator for CredentialChainManifold (v62.0-Ω)

This script reproduces the key mathematical operations from the C++ submission
and checks compliance with the Omega Protocol invariants:
- All metrics bounded in [0,1]
- Safety‑gate hierarchy (Psi -> CredentialRisk -> Action)
- Invariant gates (psi_integrity, credential_exposure, access_chain, COD, chain_integrity)
- Phi‑density accounting with audit‑cost subtraction
- Detection of the fidelity bug in COD calculation
"""

import math
from typing import Tuple, List, NamedTuple

# ----------------------------------------------------------------------
# Constants (mirroring the C++ constants)
# ----------------------------------------------------------------------
PSI_INTEGRITY_THRESHOLD = 0.95
CREDENTIAL_EXPOSURE_MAX = 0.20
ACCESS_CHAIN_MAX = 0.50
COD_THRESHOLD = 0.85
CHAIN_INTEGRITY_MIN = 0.70
AUDIT_ENTROPY_PER_CHECK = 0.02
LAMBDA_COUPLING = 0.5
MU_CREDENTIAL = 0.7

# ----------------------------------------------------------------------
# Helper data structures
# ----------------------------------------------------------------------
class State(NamedTuple):
    psi_integrity: float          # [0,1]
    h_instability: float          # [0,1]
    theta_tensor_leak: float      # [0,1]
    credential_exposure: float    # [0,1]
    access_chain_length: float    # [0,1]
    chain_integrity: float        # [0,1]
    credential_rotation_rate: float  # [0,1]
    cod: float                    # [0,1] (will be overwritten)
    phi_N: float                  # [0,1] (will be overwritten)
    credential_delegation_risk: float = 0.0  # computed
    access_chain_risk: float = 0.0          # computed

class Action:
    PROCEED = 0
    FREEZE_CREDENTIALS = 1
    HALT_ACCESS = 2
    IDENTITY_LOCKDOWN = 3

ACTION_MSG = {
    Action.PROCEED: "Credential chain integrity verified. Secure.",
    Action.FREEZE_CREDENTIALS: "Credential exposure elevated. Freezing credential use.",
    Action.HALT_ACCESS: "Critical exposure detected. Halting all access.",
    Action.IDENTITY_LOCKDOWN: "CRITICAL: Identity delegation breached. Lockdown initiated."
}

class RiskLevel:
    LOW = 0
    MEDIUM = 1
    CRITICAL = 2
    CATASTROPHIC = 3

# ----------------------------------------------------------------------
# Core mathematical functions (exact replicas of the C++ logic)
# ----------------------------------------------------------------------
def calc_access_chain_risk(chain_len: float, rotation: float) -> float:
    """chain_length * (1 - rotation_rate)"""
    return max(0.0, min(1.0, chain_len * (1.0 - rotation)))

def calc_credential_delegation_risk(exposure: float, access_risk: float, chain_int: float) -> float:
    """exposure * access_chain_risk * (1 - chain_integrity)"""
    return max(0.0, min(1.0, exposure * access_risk * (1.0 - chain_int)))

def assess_risk_level(cred_deleg_risk: float) -> int:
    if cred_deleg_risk > 0.70: return RiskLevel.CATASTROPHIC
    if cred_deleg_risk > 0.50: return RiskLevel.CRITICAL
    if cred_deleg_risk > 0.30: return RiskLevel.MEDIUM
    return RiskLevel.LOW

def cos_similarity_complex(diag: List[complex], plasma: List[complex]) -> float:
    """
    Proper complex inner product fidelity:
    Re( <diag|plasma> ) / (||diag|| * ||plasma||)
    Returns 0.0 if either norm is zero.
    """
    if not diag or not plasma:
        return 0.0
    dot = sum((d.conjugate() * p).real for d, p in zip(diag, plasma))
    norm_d = math.sqrt(sum(abs(d)**2 for d in diag))
    norm_p = math.sqrt(sum(abs(p)**2 for p in plasma))
    if norm_d == 0.0 or norm_p == 0.0:
        return 0.0
    fidelity = dot / (norm_d * norm_p)
    return max(0.0, min(1.0, fidelity))

def calc_cod_faulty(diag: List[complex], plasma: List[complex],
                    h_inst: float, theta_leak: float, cred_deleg_risk: float) -> float:
    """
    Exact replica of the buggy C++ fidelity:
    dot = Σ |conj(d)*p|
    fidelity = dot / (sqrt(magD)*sqrt(magP))  (clamped)
    """
    if not diag or not plasma:
        return 0.0   # as in the C++ code when vectors are empty
    dot = sum(abs(d.conjugate() * p) for d, p in zip(diag, plasma))
    magD = sum(abs(d)**2 for d in diag)
    magP = sum(abs(p)**2 for p in plasma)
    if magD == 0.0 or magP == 0.0:
        fidelity = 0.0
    else:
        fidelity = dot / (math.sqrt(magD) * math.sqrt(magP))
        fidelity = max(0.0, min(1.0, fidelity))   # clamp as in C++
    instability_pen = math.exp(-LAMBDA_COUPLING * h_inst)
    exposure_pen   = math.exp(-LAMBDA_COUPLING * theta_leak)
    cred_pen       = math.exp(-MU_CREDENTIAL * cred_deleg_risk)
    return fidelity * instability_pen * exposure_pen * cred_pen

def calc_cod_correct(diag: List[complex], plasma: List[complex],
                     h_inst: float, theta_leak: float, cred_deleg_risk: float) -> float:
    """
    Fixed COD using proper cosine similarity.
    """
    fidelity = cos_similarity_complex(diag, plasma)
    instability_pen = math.exp(-LAMBDA_COUPLING * h_inst)
    exposure_pen   = math.exp(-LAMBDA_COUPLING * theta_leak)
    cred_pen       = math.exp(-MU_CREDENTIAL * cred_deleg_risk)
    return fidelity * instability_pen * exposure_pen * cred_pen

def decide_action(psi: float, cred_deleg_risk: float) -> int:
    if psi < PSI_INTEGRITY_THRESHOLD:
        return Action.IDENTITY_LOCKDOWN
    if cred_deleg_risk > 0.70: return Action.IDENTITY_LOCKDOWN
    if cred_deleg_risk > 0.50: return Action.HALT_ACCESS
    if cred_deleg_risk > 0.30: return Action.FREEZE_CREDENTIALS
    return Action.PROCEED

def check_invariants(state: State, cod_val: float, cred_deleg_risk: float) -> Tuple[bool, dict]:
    """
    Returns (all_passed, dict_of_individual_checks)
    """
    access_risk = calc_access_chain_risk(state.access_chain_length, state.credential_rotation_rate)
    checks = {
        "psi_integrity_ok": state.psi_integrity >= PSI_INTEGRITY_THRESHOLD,
        "credential_exposure_ok": cred_deleg_risk <= CREDENTIAL_EXPOSURE_MAX,
        "access_chain_ok": access_risk <= ACCESS_CHAIN_MAX,
        "cod_ok": cod_val >= COD_THRESHOLD,
        "chain_integrity_ok": state.chain_integrity >= CHAIN_INTEGRITY_MIN,
    }
    all_passed = all(checks.values())
    return all_passed, checks

def phi_density_ledger(cod_before: float, cod_after: float, audit_checks: int = 9) -> float:
    raw_gain = cod_after - cod_before
    audit_cost = audit_checks * AUDIT_ENTROPY_PER_CHECK
    return raw_gain - audit_cost

def operate(state: State, dt_hours: float = 1.0,
            diag_vec: List[complex] = None,
            plasma_vec: List[complex] = None) -> dict:
    """
    Replicates the Operate method (without threading locks).
    Returns a dict with all intermediate values for inspection.
    """
    if diag_vec is None: diag_vec = []
    if plasma_vec is None: plasma_vec = []

    # --- Phase 1: Diagnostic ---
    cod_before = state.cod

    # Access chain risk
    access_risk = calc_access_chain_risk(state.access_chain_length,
                                         state.credential_rotation_rate)

    # Credential delegation risk
    cred_deleg_risk = calc_credential_delegation_risk(
        state.credential_exposure, access_risk, state.chain_integrity)

    risk_level = assess_risk_level(cred_deleg_risk)

    # --- Phase 2: Credential Silence Protocol ---
    action = decide_action(state.psi_integrity, cred_deleg_risk)
    message = ACTION_MSG[action]

    # --- Phase 3: Invariant Enforcement ---
    # Note: the C++ code passes the *pre‑update* cod and cred_deleg_risk to the checker
    invariants_passed, inv_details = check_invariants(state, cod_before, cred_deleg_risk)
    audit_checks = 9   # hard‑coded in the C++ version

    # --- Phase 4: Modulation (if not lockdown) ---
    if action != Action.IDENTITY_LOCKDOWN:
        # Simulate decay of exposure and leak over time
        decay = math.exp(-0.15 * dt_hours)
        new_exposure = state.credential_exposure * decay
        new_leak     = state.theta_tensor_leak * decay

        # Improve chain integrity
        impr = 1.0 - math.exp(-0.05 * dt_hours)
        new_chain_int = min(1.0,
                            state.chain_integrity +
                            impr * (1.0 - state.chain_integrity))

        # Re‑calculate COD (using the *buggy* formula as in the submission)
        cod_after = calc_cod_faulty(diag_vec, plasma_vec,
                                    new_leak, new_leak,  # note: they passed theta_tensor_leak twice in the C++ code
                                    cred_deleg_risk)   # Actually they passed state.theta_tensor_leak twice; we mirror that.
        # For completeness we also compute the *correct* COD
        cod_after_correct = calc_cod_correct(diag_vec, plasma_vec,
                                             new_leak, new_leak,
                                             cred_deleg_risk)

        # Update state (only the fields that the C++ version mutates)
        updated_state = state._replace(
            credential_exposure=new_exposure,
            theta_tensor_leak=new_leak,
            chain_integrity=new_chain_int,
            cod=cod_after,
            phi_N=cod_after   # they assign phi_N = cod
        )
    else:
        updated_state = state
        cod_after = cod_before
        cod_after_correct = cod_before

    # --- Phase 5: Φ‑density accounting ---
    phi_net_gain = phi_density_ledger(cod_before, cod_after, audit_checks)

    # --- Phase 6: Success condition ---
    success = invariants_passed or (action == Action.FREEZE_CREDENTIALS)

    return {
        "input_state": state,
        "access_chain_risk": access_risk,
        "cred_deleg_risk": cred_deleg_risk,
        "risk_level": risk_level,
        "action": action,
        "action_msg": message,
        "invariants_passed": invariants_passed,
        "inv_details": inv_details,
        "cod_before": cod_before,
        "cod_after": cod_after,
        "cod_after_correct": cod_after_correct,
        "phi_net_gain": phi_net_gain,
        "audit_checks": audit_checks,
        "success": success,
        "updated_state": updated_state if action != Action.IDENTITY_LOCKDOWN else None
    }

# ----------------------------------------------------------------------
# Validation routine
# ----------------------------------------------------------------------
def validate_run(result: dict) -> List[str]:
    """
    Returns a list of human‑readable violation messages.
    An empty list means the run is fully compliant.
    """
    msgs = []

    s = result["input_state"]
    # 1. Basic range checks
    for name, val in [("psi_integrity", s.psi_integrity),
                      ("h_instability", s.h_instability),
                      ("theta_tensor_leak", s.theta_tensor_leak),
                      ("credential_exposure", s.credential_exposure),
                      ("access_chain_length", s.access_chain_length),
                      ("chain_integrity", s.chain_integrity),
                      ("credential_rotation_rate", s.credential_rotation_rate)]:
        if not (0.0 <= val <= 1.0):
            msgs.append(f"[RANGE] {name} = {val:.4f} outside [0,1]")

    # 2. Derived metrics must also be in [0,1]
    for name, val in [("access_chain_risk", result["access_chain_risk"]),
                      ("cred_deleg_risk", result["cred_deleg_risk"]),
                      ("cod_before", result["cod_before"]),
                      ("cod_after", result["cod_after"]),
                      ("cod_after_correct", result["cod_after_correct"])]:
        if not (0.0 <= val <= 1.0):
            msgs.append(f"[DERIVED] {name} = {val:.4f} outside [0,1]")

    # 3. Risk level mapping sanity
    rl = result["risk_level"]
    cdr = result["cred_deleg_risk"]
    if rl == RiskLevel.LOW and not (0.0 <= cdr <= 0.30):
        msgs.append(f"[RISK] LOW assigned but cred_deleg_risk={cdr:.3f}")
    if rl == RiskLevel.MEDIUM and not (0.30 < cdr <= 0.50):
        msgs.append(f"[RISK] MEDIUM assigned but cred_deleg_risk={cdr:.3f}")
    if rl == RiskLevel.CRITICAL and not (0.50 < cdr <= 0.70):
        msgs.append(f"[RISK] CRITICAL assigned but cred_deleg_risk={cdr:.3f}")
    if rl == RiskLevel.CATASTROPHIC and not (cdr > 0.70):
        msgs.append(f"[RISK] CATASTROPHIC assigned but cred_deleg_risk={cdr:.3f}")

    # 4. Action consistency with psi_integrity and cred_deleg_risk
    act = result["action"]
    psi = s.psi_integrity
    if act == Action.IDENTITY_LOCKDOWN:
        if not (psi < PSI_INTEGRITY_THRESHOLD or cdr > 0.70):
            msgs.append(f"[ACTION] IDENTITY_LOCKDOWN but psi={psi:.3f} (≥{PSI_INTEGRITY_THRESHOLD}) and cdr={cdr:.3f} (≤0.70)")
    elif act == Action.HALT_ACCESS:
        if not (0.50 < cdr <= 0.70 and psi >= PSI_INTEGRITY_THRESHOLD):
            msgs.append(f"[ACTION] HALT_ACCESS but cdr={cdr:.3f} not in (0.5,0.7] or psi<{PSI_INTEGRITY_THRESHOLD}")
    elif act == Action.FREEZE_CREDENTIALS:
        if not (0.30 < cdr <= 0.50 and psi >= PSI_INTEGRITY_THRESHOLD):
            msgs.append(f"[ACTION] FREEZE_CREDENTIALS but cdr={cdr:.3f} not in (0.3,0.5] or psi<{PSI_INTEGRITY_THRESHOLD}")
    elif act == Action.PROCEED:
        if not (cdr <= 0.30 and psi >= PSI_INTEGRITY_THRESHOLD):
            msgs.append(f"[ACTION] PROCEED but cdr={cdr:.3f}>0.30 or psi={psi:.3f}<{PSI_INTEGRITY_THRESHOLD}")

    # 5. Invariant checks vs. success condition
    inv_pass = result["invariants_passed"]
    act_freeze = (result["action"] == Action.FREEZE_CREDENTIALS)
    success = result["success"]
    if success != (inv_pass or act_freeze):
        msgs.append(f"[SUCCESS] mismatched: invariants_passed={inv_pass}, action FREEZE?={act_freeze}, reported success={success}")

    # 6. Φ‑density accounting sanity
    audit_cost = result["audit_checks"] * AUDIT_ENTROPY_PER_CHECK
    expected_phi = (result["cod_after"] - result["cod_before"]) - audit_cost
    if not math.isclose(result["phi_net_gain"], expected_phi, rel_tol=1e-9, abs_tol=1e-12):
        msgs.append(f"[PHI] net gain mismatch: computed={result['phi_net_gain']:.6f}, expected={expected_phi:.6f}")

    # 7. COD fidelity bug detection (compare buggy vs. correct)
    if not math.isclose(result["cod_after"], result["cod_after_correct"], rel_tol=1e-9, abs_tol=1e-12):
        msgs.append(f"[COD] Buggy vs. correct COD differ: buggy={result['cod_after']:.6f}, correct={result['cod_after_correct']:.6f}")

    return msgs

# ----------------------------------------------------------------------
# Example usage / test harness
# ----------------------------------------------------------------------
if __name__ == "__main__":
    # Example state that should be safe (high integrity, low exposure)
    example_state = State(
        psi_integrity=0.98,
        h_instability=0.10,
        theta_tensor_leak=0.05,
        credential_exposure=0.05,
        access_chain_length=0.20,
        chain_integrity=0.85,
        credential_rotation_rate=0.60,
        cod=0.90,   # placeholder; will be overwritten
        phi_N=0.90
    )

    # Provide some non‑empty diagnostic/plasma vectors so COD isn't forced to zero
    diag = [1+0j, 0.5+0.5j, 0.2-0.1j]
    plasma = [0.9+0.1j, 0.4+0.4j, 0.15-0.05j]

    res = operate(example_state, dt_hours=0.5, diag_vec=diag, plasma_vec=plasma)

    print("=== Omega Protocol Validation Run ===")
    print(f"Action: {ACTION_MSG[res['action']]}")
    print(f"Risk level: {res['risk_level']} (cred_deleg_risk={res['cred_deleg_risk']:.3f})")
    print(f"Invariants passed: {res['invariants_passed']}")
    for k, v in res["inv_details"].items():
        print(f"  {k}: {v}")
    print(f"COD before/after: {res['cod_before']:.4f} → {res['cod_after']:.4f} (correct COD would be {res['cod_after_correct']:.4f})")
    print(f"Φ‑density net gain: {res['phi_net_gain']:.6f}")
    print(f"Success: {res['success']}")

    violations = validate_run(res)
    if violations:
        print("\n--- VIOLATIONS DETECTED ---")
        for v in violations:
            print(v)
    else:
        print("\n✅ All checks passed – the run is compliant with Omega Protocol invariants.")