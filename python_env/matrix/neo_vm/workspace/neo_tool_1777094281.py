# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
#!/usr/bin/env python3
"""
Demonstrates the fatal flaw in the Omega Protocol's ML-Provenance Gate:
static ID-based trust is trivially spoofed, while a behavioral check
reveals the true risk.
"""

AUTHORIZED_ML_SYSTEMS = {
    "plasma_disruption_predictor_v3",
    "realtime_control_neural_net",
    "diagnostic_calibration_ml",
    "federated_learning_tokamak"
}

# Protocol logic (direct translation from C++ code)
def calc_provenance_score(ml_system_id: str, physics_ml_coupling: float) -> float:
    if ml_system_id in AUTHORIZED_ML_SYSTEMS:
        return 0.90 + 0.10 * physics_ml_coupling
    elif ml_system_id == "":
        return 0.50
    else:
        return 0.20 * (1.0 - physics_ml_coupling)

def classify_convergence(provenance_score: float, physics_ml_coupling: float):
    if provenance_score >= 0.80:
        return "LEGITIMATE_CONVERGENCE"
    elif provenance_score < 0.40 and physics_ml_coupling > 0.60:
        return "DOMAIN_CONTAMINATION"
    else:
        return "UNCERTAIN_PROVENANCE"

def calc_ml_physics_risk(log_exposure: float, physics_ml_coupling: float,
                         provenance_score: float) -> float:
    # Risk = exposure * coupling * (1 - provenance)
    return log_exposure * physics_ml_coupling * (1.0 - provenance_score)

def assess_risk(risk: float):
    if risk > 0.70:
        return "CATASTROPHIC"
    if risk > 0.50:
        return "CRITICAL"
    if risk > 0.30:
        return "MEDIUM"
    return "LOW"

def decide(psi_integrity: float, ml_physics_risk: float,
           convergence_type: str):
    # Primary gate: psi integrity
    if psi_integrity < 0.95:
        return "IDENTITY_LOCKDOWN"
    if convergence_type == "DOMAIN_CONTAMINATION":
        return "IDENTITY_LOCKDOWN"
    if ml_physics_risk > 0.70:
        return "IDENTITY_LOCKDOWN"
    if ml_physics_risk > 0.50:
        return "FREEZE_ML_OPERATIONS"
    if ml_physics_risk > 0.30:
        return "FLAG_FOR_REVIEW"
    return "PROCEED"

# Behavioral mock: simulate model output distribution check
def behavioral_check(ml_system_id: str, true_behavior_id: str) -> float:
    """
    Returns a behavioral fidelity score in [0,1].
    A score < 0.70 indicates a mismatch between claimed ID and actual behavior.
    """
    # In reality this would compare cryptographic attestations or output embeddings.
    # Here we simply penalize if the true behavior deviates from the claimed ID.
    if ml_system_id == true_behavior_id:
        return 1.0
    # Malicious payload disguised as authorized: low fidelity
    if true_behavior_id == "malicious_payload":
        return 0.55
    return 0.70

# Scenario simulation
def simulate(ml_system_id: str, true_behavior_id: str,
             physics_ml_coupling: float, log_exposure: float,
             psi_integrity: float = 0.99):
    print(f"\n[Scenario] Claimed ID: '{ml_system_id}' | True Behavior: '{true_behavior_id}'")
    provenance = calc_provenance_score(ml_system_id, physics_ml_coupling)
    convergence = classify_convergence(provenance, physics_ml_coupling)
    risk = calc_ml_physics_risk(log_exposure, physics_ml_coupling, provenance)
    action = decide(psi_integrity, risk, convergence)
    behavior_fidelity = behavioral_check(ml_system_id, true_behavior_id)

    print(f"  Provenance Score: {provenance:.3f} | Convergence: {convergence}")
    print(f"  ML-Physics Risk: {risk:.3f} ({assess_risk(risk)})")
    print(f"  Protocol Action: {action}")
    print(f"  Behavioral Fidelity: {behavior_fidelity:.3f}")

    # Decision based on behavioral fidelity
    if behavior_fidelity < 0.70:
        print("  → BEHAVIORAL ALERT: Payload mismatch detected! Recommend LOCKDOWN.")
    else:
        print("  → Behavioral check passes.")

# Run scenarios
if __name__ == "__main__":
    # 1. Legitimate authorized system
    simulate(
        ml_system_id="plasma_disruption_predictor_v3",
        true_behavior_id="plasma_disruption_predictor_v3",
        physics_ml_coupling=0.5,
        log_exposure=0.1
    )

    # 2. Unauthorized system (no spoofing)
    simulate(
        ml_system_id="malicious_ml_system",
        true_behavior_id="malicious_ml_system",
        physics_ml_coupling=0.5,
        log_exposure=0.1
    )

    # 3. SPOOFING ATTACK: adversary uses authorized ID while running malicious payload
    simulate(
        ml_system_id="plasma_disruption_predictor_v3",  # spoofed ID
        true_behavior_id="malicious_payload",             # actual behavior
        physics_ml_coupling=0.9,                         # high coupling for max provenance
        log_exposure=0.05                                 # low exposure to minimize risk
    )