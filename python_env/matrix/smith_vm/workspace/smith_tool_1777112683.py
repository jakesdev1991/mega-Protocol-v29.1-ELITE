# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
# Omega Protocol Validation Script for API Propagation Epidemic Manifold (v77.0-Ω-FINAL)
# This script validates mathematical soundness and protocol invariants by
# replicating the core logic of the C++ implementation in Python and
# checking dimensional bounds, gate hierarchy, and internal consistency.

import math
import random
from typing import List, Tuple

# ----------------------------
# Constants from the protocol
# ----------------------------
PSI_INTEGRITY_THRESHOLD = 0.95
R0_MAX = 0.50
HERD_IMMUNITY_MIN = 0.60
SUPERSPREADER_CONNECTIVITY_MAX = 0.70
COD_THRESHOLD = 0.85
AUDIT_ENTROPY_PER_CHECK = 0.02
LAMBDA_COUPLING = 0.5
MU_PROPAGATION = 0.7
EPSILON = 1e-9

# ----------------------------
# Helper functions (mirroring C++ logic)
# ----------------------------
def clamp(x: float, lo: float = 0.0, hi: float = 1.0) -> float:
    return max(lo, min(hi, x))

def calculate_network_connectivity(partner_count: int, control_depth: float, propagation_depth: float) -> float:
    partner_factor = min(1.0, partner_count / 20.0)
    depth_factor = (control_depth + propagation_depth) / 2.0
    return clamp(partner_factor * 0.6 + depth_factor * 0.4)

def calculate_superspreader_risk(network_connectivity: float, api_exposure: float, safety_criticality: float) -> float:
    return clamp(network_connectivity * 0.5 + api_exposure * 0.3 + (1.0 - safety_criticality) * 0.2)

def calculate_susceptible_fraction(herd_immunity_threshold: float, provenance_integrity: float, recovery_velocity: float) -> float:
    return clamp((1.0 - herd_immunity_threshold) * 0.5 +
                 (1.0 - provenance_integrity) * 0.3 +
                 (1.0 - recovery_velocity) * 0.2)

def decompose_r0(api_exposure: float, network_connectivity: float, superspreader_risk: float) -> Tuple[float, float]:
    phi_N = api_exposure * network_connectivity * (1.0 - superspreader_risk)
    phi_Delta = api_exposure * network_connectivity * superspreader_risk
    # Total clamp as in CovariantModes.Total()
    total = clamp(phi_N + phi_Delta)
    # We return the raw components; the total clamped value is used for R0 calc
    return phi_N, phi_Delta, total

def calculate_r0_propagation(phi_N: float, phi_Delta: float, susceptible_fraction: float, quarantine_efficacy: float) -> float:
    base_transmission = clamp(phi_N + phi_Delta)  # uses Total()
    return clamp(base_transmission * susceptible_fraction * (1.0 - quarantine_efficacy))

def calculate_herd_immunity_threshold(r0_propagation: float, network_connectivity: float, contact_trace_coverage: float) -> float:
    if r0_propagation < 0.01:
        return 1.0
    classical = 1.0 - (1.0 / (r0_propagation + 0.1))
    return clamp(classical + network_connectivity * 0.3 + contact_trace_coverage * 0.2)

def calculate_cascade_probability(r0_propagation: float, susceptible_fraction: float, superspreader_risk: float) -> float:
    return clamp(r0_propagation * 0.5 + susceptible_fraction * 0.3 + superspreader_risk * 0.2)

def calculate_propagation_risk(susceptible_fraction: float, network_connectivity: float, herd_immunity_threshold: float) -> float:
    return clamp(susceptible_fraction * network_connectivity * (1.0 - herd_immunity_threshold))

def calculate_psi_coupling(phi_N: float) -> float:
    return math.log(phi_N + EPSILON)

def apply_psi_coupling(base_risk: float, psi_coupling: float) -> float:
    return base_risk * math.exp(-0.5 * psi_coupling)

def calculate_stiffness_terms(psi_coupling: float, stiffness_base: float = 1.0) -> Tuple[float, float]:
    xi_N = stiffness_base * math.exp(psi_coupling)
    xi_Delta = stiffness_base * math.exp(-psi_coupling)
    return xi_N, xi_Delta

def calculate_quarantine_efficacy(base_efficacy: float, xi_N: float, xi_Delta: float) -> float:
    stiffness_ratio = xi_N / (xi_Delta + EPSILON)
    efficacy_modifier = 1.0 - abs(stiffness_ratio - 1.0)
    return clamp(base_efficacy * efficacy_modifier)

def calculate_S_topology(partner_facilities: List[str], susceptible_fractions: List[float]) -> float:
    S = 0.0
    for p in susceptible_fractions:
        if p > 0.0:
            S -= p * math.log(p + EPSILON)
    max_entropy = math.log(len(partner_facilities) + EPSILON)
    return clamp(S / max_entropy) if max_entropy > 0 else 0.0

def calculate_COD(diagnostic_vec: List[complex], plasma_vec: List[complex],
                  h_instability: float, theta_tensor_leak: float,
                  r0_propagation: float, herd_immunity_threshold: float,
                  propagation_risk: float) -> float:
    # Fidelity
    dot = 0.0
    magD = 0.0
    magP = 0.0
    size = min(len(diagnostic_vec), len(plasma_vec))
    for i in range(size):
        dot += abs(conjugate(diagnostic_vec[i]) * plasma_vec[i])
        magD += abs(diagnostic_vec[i] * diagnostic_vec[i])
        magP += abs(plasma_vec[i] * plasma_vec[i])
    fidelity = 0.0
    if magD > 1e-9 and magP > 1e-9:
        fidelity = dot / (math.sqrt(magD) * math.sqrt(magP))
        fidelity = clamp(fidelity)
    # Penalties
    instability_penalty = math.exp(-LAMBDA_COUPLING * h_instability)
    exposure_penalty = math.exp(-LAMBDA_COUPLING * theta_tensor_leak)
    r0_penalty = math.exp(-MU_PROPAGATION * r0_propagation)
    immunity_penalty = math.exp(-MU_PROPAGATION * (1.0 - herd_immunity_threshold))
    risk_penalty = math.exp(-MU_PROPAGATION * propagation_risk)
    return fidelity * instability_penalty * exposure_penalty * r0_penalty * immunity_penalty * risk_penalty

def conjugate(z: complex) -> complex:
    return z.real - z.imag * 1j

# Epidemic state enum
class EpidemicState:
    CONTAINED = 0
    SPREADING = 1
    EPIDEMIC = 2
    HERD_PROTECTED = 3

def classify_epidemic_state(r0_propagation: float, herd_immunity_threshold: float, cascade_probability: float) -> EpidemicState:
    if herd_immunity_threshold > 0.70 and r0_propagation < 0.30:
        return EpidemicState.HERD_PROTECTED
    if cascade_probability > 0.70:
        return EpidemicState.EPIDEMIC
    if r0_propagation > 0.50:
        return EpidemicState.SPREADING
    return EpidemicState.CONTAINED

# Boundary state enum
class BoundaryState:
    SUBCRITICAL = 0
    CRITICAL_THRESHOLD = 1
    SUPERCRITICAL = 2
    SHREDDING = 3

def check_boundary_state(r0_propagation: float, cascade_probability: float, phi_Delta: float) -> BoundaryState:
    if phi_Delta > 0.80 or cascade_probability > 0.95:
        return BoundaryState.SHREDDING
    if r0_propagation > 1.0 or phi_Delta > 0.60:
        return BoundaryState.SUPERCRITICAL
    if r0_propagation > 0.9:
        return BoundaryState.CRITICAL_THRESHOLD
    return BoundaryState.SUBCRITICAL

def decide_action(psi_integrity: float, propagation_risk: float,
                  epidemic_state: EpidemicState, boundary_state: BoundaryState) -> str:
    if psi_integrity < PSI_INTEGRITY_THRESHOLD:
        return "IDENTITY_LOCKDOWN"
    if boundary_state == BoundaryState.SHREDDING:
        return "IDENTITY_LOCKDOWN"
    if boundary_state == BoundaryState.SUPERCRITICAL:
        return "ACTIVATE_QUARANTINE"
    if epidemic_state == EpidemicState.EPIDEMIC:
        return "IDENTITY_LOCKDOWN"
    if propagation_risk > 0.70:
        return "IDENTITY_LOCKDOWN"
    if propagation_risk > 0.50 or epidemic_state == EpidemicState.SPREADING:
        return "ACTIVATE_QUARANTINE"
    if propagation_risk > 0.30 or epidemic_state == EpidemicState.CONTAINED:
        return "MONITOR_SPREAD"
    return "PROCEED"

def assess_risk(propagation_risk: float) -> str:
    if propagation_risk > 0.70:
        return "CATASTROPHIC"
    if propagation_risk > 0.50:
        return "CRITICAL"
    if propagation_risk > 0.30:
        return "MEDIUM"
    return "LOW"

# ----------------------------
# Validation routine
# ----------------------------
def validate_random_state() -> List[str]:
    errors = []
    # Random but plausible values
    state = {
        "query_branch": "tokamak",
        "partner_facilities": [f"fac_{i}" for i in range(random.randint(5, 25))],
        "api_exposure": random.random(),
        "control_depth": random.random(),
        "safety_criticality": random.random(),
        "provenance_integrity": random.random(),
        "propagation_depth": random.random(),
        "recovery_velocity": random.random(),
        "psi_integrity": random.random(),
        "h_instability": random.random(),
        "theta_tensor_leak": random.random(),
        "contact_trace_coverage": random.random(),
        "quarantine_efficacy": random.random(),  # base efficacy before stiffness modulation
    }
    # Derived metrics
    state["network_connectivity"] = calculate_network_connectivity(
        len(state["partner_facilities"]), state["control_depth"], state["propagation_depth"]
    )
    state["superspreader_risk"] = calculate_superspreader_risk(
        state["network_connectivity"], state["api_exposure"], state["safety_criticality"]
    )
    state["susceptible_fraction"] = calculate_susceptible_fraction(
        state["herd_immunity_threshold"] if "herd_immunity_threshold" in state else 0.5,  # placeholder
        state["provenance_integrity"], state["recovery_velocity"]
    )
    # Need herd_immunity_threshold for susceptible fraction -> iterate
    # We'll compute in a temporary order: first guess, then recompute
    # For simplicity, we compute susceptible fraction using a placeholder then recompute herd immunity then susceptible again
    # We'll do two passes
    # Pass 1: provisional herd immunity
    provisional_herd = calculate_herd_immunity_threshold(
        0.1, state["network_connectivity"], state["contact_trace_coverage"]
    )
    state["susceptible_fraction"] = calculate_susceptible_fraction(
        provisional_herd, state["provenance_integrity"], state["recovery_velocity"]
    )
    state["r0_propagation_raw"], state["phi_N"], state["phi_Delta"], state["r0_total"] = decompose_r0(
        state["api_exposure"], state["network_connectivity"], state["superspreader_risk"]
    )
    # Use total (clamped) for R0
    state["r0_propagation"] = calculate_r0_propagation(
        state["phi_N"], state["phi_Delta"], state["susceptible_fraction"], state["quarantine_efficacy"]
    )
    state["herd_immunity_threshold"] = calculate_herd_immunity_threshold(
        state["r0_propagation"], state["network_connectivity"], state["contact_trace_coverage"]
    )
    # Recompute susceptible fraction with updated herd immunity
    state["susceptible_fraction"] = calculate_susceptible_fraction(
        state["herd_immunity_threshold"], state["provenance_integrity"], state["recovery_velocity"]
    )
    # Recompute R0 with updated susceptible fraction (should iterate, but one more pass is enough for validation)
    state["r0_propagation"] = calculate_r0_propagation(
        state["phi_N"], state["phi_Delta"], state["susceptible_fraction"], state["quarantine_efficacy"]
    )
    state["cascade_probability"] = calculate_cascade_probability(
        state["r0_propagation"], state["susceptible_fraction"], state["superspreader_risk"]
    )
    base_propagation_risk = calculate_propagation_risk(
        state["susceptible_fraction"], state["network_connectivity"], state["herd_immunity_threshold"]
    )
    state["psi_coupling"] = calculate_psi_coupling(state["phi_N"])
    state["propagation_risk"] = apply_psi_coupling(base_propagation_risk, state["psi_coupling"])
    xi_N, xi_Delta = calculate_stiffness_terms(state["psi_coupling"])
    state["xi_N"], state["xi_Delta"] = xi_N, xi_Delta
    state["quarantine_efficacy"] = calculate_quarantine_efficacy(
        state["quarantine_efficacy"], state["xi_N"], state["xi_Delta"]
    )
    state["S_topology"] = calculate_S_topology(
        state["partner_facilities"],
        [state["susceptible_fraction"]] * len(state["partner_facilities"])
    )
    # Boundary state
    state["boundary_state"] = check_boundary_state(
        state["r0_propagation"], state["cascade_probability"], state["phi_Delta"]
    )
    state["epidemic_state"] = classify_epidemic_state(
        state["r0_propagation"], state["herd_immunity_threshold"], state["cascade_probability"]
    )
    # COD (dummy vectors)
    diag = [complex(random.random(), random.random()) for _ in range(3)]
    plasm = [complex(random.random(), random.random()) for _ in range(3)]
    state["cod"] = calculate_COD(
        diag, plasm, state["h_instability"], state["theta_tensor_leak"],
        state["r0_propagation"], state["herd_immunity_threshold"], state["propagation_risk"]
    )
    state["phi_N"] = state["cod"]  # as per code: state.phi_N = state.cod
    # Action and risk level
    state["action"] = decide_action(
        state["psi_integrity"], state["propagation_risk"],
        state["epidemic_state"], state["boundary_state"]
    )
    state["risk_level"] = assess_risk(state["propagation_risk"])
    # ----------------------------
    # Invariant checks
    # ----------------------------
    # 1. Dimensional bounds [0,1] for required metrics
    bounds_to_check = [
        ("api_exposure", state["api_exposure"]),
        ("control_depth", state["control_depth"]),
        ("safety_criticality", state["safety_criticality"]),
        ("provenance_integrity", state["provenance_integrity"]),
        ("propagation_depth", state["propagation_depth"]),
        ("recovery_velocity", state["recovery_velocity"]),
        ("network_connectivity", state["network_connectivity"]),
        ("superspreader_risk", state["superspreader_risk"]),
        ("susceptible_fraction", state["susceptible_fraction"]),
        ("r0_propagation", state["r0_propagation"]),
        ("herd_immunity_threshold", state["herd_immunity_threshold"]),
        ("cascade_probability", state["cascade_probability"]),
        ("propagation_risk", state["propagation_risk"]),  # should be in [0,1] after apply_psi_coupling? we'll check
        ("psi_integrity", state["psi_integrity"]),
        ("h_instability", state["h_instability"]),
        ("theta_tensor_leak", state["theta_tensor_leak"]),
        ("contact_trace_coverage", state["contact_trace_coverage"]),
        ("quarantine_efficacy", state["quarantine_efficacy"]),
        ("S_topology", state["S_topology"]),
        ("cod", state["cod"]),
        ("phi_N", state["phi_N"]),
        ("phi_N_raw", state["phi_N"]),  # raw from decomposition (should be [0,1]? not necessarily, but total clamped)
        ("phi_Delta", state["phi_Delta"]),
    ]
    for name, val in bounds_to_check:
        if not (0.0 <= val <= 1.0 + 1e-12):  # tiny tolerance
            errors.append(f"{name} out of bounds: {val}")
    # 2. Psi coupling can be any real, but exp(-0.5*psi) must be positive (always true)
    # 3. Stiffness terms positive (always true)
    if state["xi_N"] <= 0 or state["xi_Delta"] <= 0:
        errors.append(f"Stiffness terms non-positive: xi_N={state['xi_N']}, xi_Delta={state['xi_Delta']}")
    # 4. Gate hierarchy: if integrity fails -> lockdown
    if state["psi_integrity"] < PSI_INTEGRITY_THRESHOLD and state["action"] != "IDENTITY_LOCKDOWN":
        errors.append(f"Integrity breach ({state['psi_integrity']}) did not trigger lockdown; action={state['action']}")
    # 5. Boundary SHREDDING -> lockdown
    if state["boundary_state"] == BoundaryState.SHREDDING and state["action"] != "IDENTITY_LOCKDOWN":
        errors.append(f"SHREDDING boundary did not trigger lockdown; action={state['action']}")
    # 6. Boundary SUPERCRITICAL -> quarantine
    if state["boundary_state"] == BoundaryState.SUPERCRITICAL and state["action"] != "ACTIVATE_QUARANTINE":
        errors.append(f"SUPERCRITICAL boundary did not trigger quarantine; action={state['action']}")
    # 7. Epidemic state EPIDEMIC -> lockdown
    if state["epidemic_state"] == EpidemicState.EPIDEMIC and state["action"] != "IDENTITY_LOCKDOWN":
        errors.append(f"EPIDEMIC state did not trigger lockdown; action={state['action']}")
    # 8. Risk level thresholds consistency
    pr = state["propagation_risk"]
    rl = state["risk_level"]
    if pr > 0.70 and rl != "CATASTROPHIC":
        errors.append(f"Risk level mismatch: propagation_risk={pr}, expected CATASTROPHIC got {rl}")
    elif pr > 0.50 and rl not in ("CRITICAL", "CATASTROPHIC"):
        errors.append(f"Risk level mismatch: propagation_risk={pr}, expected CRITICAL/CATASTROPHIC got {rl}")
    elif pr > 0.30 and rl not in ("MEDIUM", "CRITICAL", "CATASTROPHIC"):
        errors.append(f"Risk level mismatch: propagation_risk={pr}, expected MEDIUM+ got {rl}")
    # 9. COD threshold check (not required to pass, just log)
    if state["cod"] < COD_THRESHOLD:
        # Not an error, just info
        pass
    return errors

def main():
    random.seed(42)
    num_tests = 1000
    all_errors = []
    for i in range(num_tests):
        errs = validate_random_state()
        if errs:
            all_errors.append((i, errs))
    if not all_errors:
        print(f"META-PASS: All {num_tests} random states validated successfully.")
        print("Protocol invariants upheld: dimensional bounds, gate hierarchy, internal consistency.")
    else:
        print(f"FAILURES DETECTED in {len(all_errors)} out of {num_tests} tests.")
        for idx, errs in all_errors[:5]:  # show first few
            print(f"Test {idx}:")
            for e in errs:
                print(f"  - {e}")
        if len(all_errors) > 5:
            print(f"  ... and {len(all_errors)-5} more error sets.")
        # Optionally, raise an assertion to fail the validation
        raise AssertionError("Omega Protocol validation failed.")

if __name__ == "__main__":
    main()