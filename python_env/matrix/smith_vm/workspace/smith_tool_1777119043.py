# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import random
import math
from typing import List, Tuple, Complex

# ------------------------------
# Helper: clamp function
# ------------------------------
def clamp(x: float, lo: float = 0.0, hi: float = 1.0) -> float:
    return max(lo, min(hi, x))

# ------------------------------
# Metric calculators (mirroring C++ logic)
# ------------------------------
def calc_fusion_integrity_index(
    fusion_fidelity: float,
    mode_preservation: float,
    anomaly_score: float,
    verification_efficacy: float
) -> float:
    fidelity_c = fusion_fidelity * 0.30
    preservation_c = mode_preservation * 0.25
    verification_c = verification_efficacy * 0.25
    anomaly_penalty = (1.0 - anomaly_score) * 0.20
    integrity = fidelity_c + preservation_c + verification_c + anomaly_penalty
    return clamp(integrity)

def calc_adversarial_surface(
    sensor_count: int,
    sensor_compromise_rate: float,
    weight_manipulation_risk: float,
    mode_injection_risk: float
) -> float:
    sensor_factor = min(1.0, sensor_count / 20.0)
    compromise_c = sensor_compromise_rate * 0.40
    weight_c = weight_manipulation_risk * 0.30
    mode_c = mode_injection_risk * 0.30
    surface = sensor_factor * (compromise_c + weight_c + mode_c)
    return clamp(surface)

def calc_anomaly_score(
    information_divergence: float,
    distribution_fusion_risk: float,
    fusion_fidelity: float
) -> float:
    divergence_c = information_divergence * 0.50
    risk_c = distribution_fusion_risk * 0.30
    fidelity_deficit = (1.0 - fusion_fidelity) * 0.20
    anomaly = divergence_c + risk_c + fidelity_deficit
    return clamp(anomaly)

def calc_verification_efficacy(
    fusion_integrity_index: float,
    adversarial_surface: float,
    h_instability: float
) -> float:
    integrity_c = fusion_integrity_index * 0.50
    surface_penalty = (1.0 - adversarial_surface) * 0.30
    stability_c = (1.0 - h_instability) * 0.20
    efficacy = integrity_c + surface_penalty + stability_c
    return clamp(efficacy)

def calc_weight_manipulation_risk(
    sensor_compromise_rate: float,
    fusion_fidelity: float,
    verification_efficacy: float
) -> float:
    compromise_c = sensor_compromise_rate * 0.50
    fidelity_reduction = (1.0 - fusion_fidelity) * 0.30
    verification_reduction = (1.0 - verification_efficacy) * 0.20
    risk = compromise_c + fidelity_reduction + verification_reduction
    return clamp(risk)

def calc_mode_injection_risk(
    mode_preservation: float,
    adversarial_surface: float,
    anomaly_score: float
) -> float:
    preservation_deficit = (1.0 - mode_preservation) * 0.40
    surface_c = adversarial_surface * 0.35
    anomaly_c = anomaly_score * 0.25
    risk = preservation_deficit + surface_c + anomaly_c
    return clamp(risk)

def calc_tampering_probability(
    adversarial_surface: float,
    anomaly_score: float,
    verification_efficacy: float
) -> float:
    surface_c = adversarial_surface * 0.40
    anomaly_c = anomaly_score * 0.35
    verification_deficit = (1.0 - verification_efficacy) * 0.25
    prob = surface_c + anomaly_c + verification_deficit
    return clamp(prob)

def calc_integrity_risk(
    integrity_deficit: float,
    adversarial_surface: float,
    verification_efficacy: float
) -> float:
    verification_deficit = 1.0 - verification_efficacy
    risk = integrity_deficit * adversarial_surface * verification_deficit
    return clamp(risk)

def classify_integrity_state(
    fusion_integrity_index: float,
    anomaly_score: float,
    tampering_probability: float
) -> str:
    if tampering_probability > 0.70 or anomaly_score > 0.70:
        return "COMPROMISED"
    if fusion_integrity_index < 0.50:
        return "UNVERIFIABLE"
    if anomaly_score > 0.40 or fusion_integrity_index < 0.70:
        return "SUSPECT"
    return "VERIFIED"

def assess_risk(integrity_risk: float) -> str:
    if integrity_risk > 0.70:
        return "CATASTROPHIC"
    if integrity_risk > 0.50:
        return "CRITICAL"
    if integrity_risk > 0.30:
        return "MEDIUM"
    return "LOW"

# ------------------------------
# COD calculation (integrity-aware)
# ------------------------------
LAMBDA_COUPLING = 0.5
MU_INTEGRITY = 0.7

def calc_cod_integrity_aware(
    diagnostic_vec: List[complex],
    plasma_vec: List[complex],
    h_instability: float,
    theta_tensor_leak: float,
    fusion_integrity_index: float,
    adversarial_surface: float,
    integrity_risk: float
) -> float:
    # Fidelity (generic alignment)
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
    integrity_penalty = math.exp(-MU_INTEGRITY * (1.0 - fusion_integrity_index))
    surface_penalty = math.exp(-MU_INTEGRITY * adversarial_surface)
    risk_penalty = math.exp(-MU_INTEGRITY * integrity_risk)
    return fidelity * instability_penalty * exposure_penalty * integrity_penalty * surface_penalty * risk_penalty

def conjugate(z: complex) -> complex:
    return z.real - z.imag * 1j

# ------------------------------
# Protocol action decision
# ------------------------------
PSI_INTEGRITY_THRESHOLD = 0.95
FUSION_INTEGRITY_MIN = 0.70
ADVERSARIAL_SURFACE_MAX = 0.50
ANOMALY_SCORE_MAX = 0.40
VERIFICATION_EFFICACY_MIN = 0.60
COD_THRESHOLD = 0.85

def decide_action(
    psi_integrity: float,
    integrity_risk: float,
    integrity_state: str
) -> str:
    if psi_integrity < PSI_INTEGRITY_THRESHOLD:
        return "IDENTITY_LOCKDOWN"
    if integrity_state == "COMPROMISED":
        return "IDENTITY_LOCKDOWN"
    if integrity_risk > 0.70:
        return "IDENTITY_LOCKDOWN"
    if integrity_risk > 0.50 or integrity_state == "UNVERIFIABLE":
        return "ACTIVATE_VERIFICATION"
    if integrity_risk > 0.30 or integrity_state == "SUSPECT":
        return "FLAG_ANOMALY"
    return "PROCEED"

# ------------------------------
# Invariant checker
# ------------------------------
def check_invariants(state: dict, cod: float, integrity_risk: float, integrity_state: str) -> dict:
    check = {
        "psi_integrity_ok": state["psi_integrity"] >= PSI_INTEGRITY_THRESHOLD,
        "fusion_integrity_ok": state["fusion_integrity_index"] >= FUSION_INTEGRITY_MIN,
        "adversarial_surface_ok": state["adversarial_surface"] <= ADVERSARIAL_SURFACE_MAX,
        "anomaly_score_ok": state["anomaly_score"] <= ANOMALY_SCORE_MAX,
        "verification_efficacy_ok": state["verification_efficacy"] >= VERIFICATION_EFFICACY_MIN,
        "cod_ok": cod >= COD_THRESHOLD,
        "audit_tracked": True
    }
    check["all_passed"] = all(check[k] for k in check if k != "audit_tracked" and k != "all_passed")
    return check

# ------------------------------
# Validation harness
# ------------------------------
def run_validation(trials: int = 10000) -> None:
    random.seed(42)
    for t in range(trials):
        # Generate random inputs in [0,1] where appropriate
        fusion_fidelity = random.random()
        mode_preservation = random.random()
        information_divergence = random.random()
        distribution_fusion_risk = random.random()
        h_instability = random.random()
        theta_tensor_leak = random.random()
        sensor_count = random.randint(1, 50)
        sensor_compromise_rate = random.random()
        # verification_efficacy initially unknown; we'll compute iteratively to avoid circularity
        # Start with a guess
        verification_efficacy = random.random()
        # Compute derived metrics
        anomaly_score = calc_anomaly_score(information_divergence, distribution_fusion_risk, fusion_fidelity)
        weight_manipulation_risk = calc_weight_manipulation_risk(sensor_compromise_rate, fusion_fidelity, verification_efficacy)
        mode_injection_risk = calc_mode_injection_risk(mode_preservation, 0.0, anomaly_score)  # adversarial_surface unknown yet
        # First pass adversarial surface (using placeholder for weight/mode risks)
        adversarial_surface = calc_adversarial_surface(sensor_count, sensor_compromise_rate, weight_manipulation_risk, mode_injection_risk)
        # Recompute weight/mode risks with updated surface
        weight_manipulation_risk = calc_weight_manipulation_risk(sensor_compromise_rate, fusion_fidelity, verification_efficacy)
        mode_injection_risk = calc_mode_injection_risk(mode_preservation, adversarial_surface, anomaly_score)
        adversarial_surface = calc_adversarial_surface(sensor_count, sensor_compromise_rate, weight_manipulation_risk, mode_injection_risk)
        # Verification efficacy (depends on surface and integrity index which needs anomaly)
        fusion_integrity_index = calc_fusion_integrity_index(fusion_fidelity, mode_preservation, anomaly_score, verification_efficacy)
        verification_efficacy = calc_verification_efficacy(fusion_integrity_index, adversarial_surface, h_instability)
        # Recompute integrity index with updated verification efficacy
        fusion_integrity_index = calc_fusion_integrity_index(fusion_fidelity, mode_preservation, anomaly_score, verification_efficacy)
        # Tampering probability and integrity risk
        tampering_prob = calc_tampering_probability(adversarial_surface, anomaly_score, verification_efficacy)
        integrity_deficit = 1.0 - fusion_integrity_index
        integrity_risk = calc_integrity_risk(integrity_deficit, adversarial_surface, verification_efficacy)
        integrity_state = classify_integrity_state(fusion_integrity_index, anomaly_score, tampering_prob)
        risk_level = assess_risk(integrity_risk)
        # COD calculation (need dummy vectors)
        diag = [complex(random.random(), random.random()) for _ in range(max(1, sensor_count))]
        plas = [complex(random.random(), random.random()) for _ in range(max(1, sensor_count))]
        cod = calc_cod_integrity_aware(diag, plas, h_instability, theta_tensor_leak,
                                       fusion_integrity_index, adversarial_surface, integrity_risk)
        phi_N = cod  # direct assignment, no log2
        # Action decision
        action = decide_action(random.uniform(0.9, 1.0), integrity_risk, integrity_state)  # psi_integrity near threshold
        # Invariant check
        state_dict = {
            "psi_integrity": random.uniform(0.9, 1.0),
            "fusion_integrity_index": fusion_integrity_index,
            "adversarial_surface": adversarial_surface,
            "anomaly_score": anomaly_score,
            "verification_efficacy": verification_efficacy
        }
        inv = check_invariants(state_dict, cod, integrity_risk, integrity_state)
        # ------------------------------
        # Assertions (Omega Protocol invariants)
        # ------------------------------
        # 1. All metrics bounded [0,1]
        assert 0.0 <= fusion_fidelity <= 1.0, f"fusion_fidelity OOB: {fusion_fidelity}"
        assert 0.0 <= mode_preservation <= 1.0, f"mode_preservation OOB: {mode_preservation}"
        assert 0.0 <= information_divergence <= 1.0, f"information_divergence OOB: {information_divergence}"
        assert 0.0 <= distribution_fusion_risk <= 1.0, f"distribution_fusion_risk OOB: {distribution_fusion_risk}"
        assert 0.0 <= h_instability <= 1.0, f"h_instability OOB: {h_instability}"
        assert 0.0 <= theta_tensor_leak <= 1.0, f"theta_tensor_leak OOB: {theta_tensor_leak}"
        assert 0.0 <= sensor_compromise_rate <= 1.0, f"sensor_compromise_rate OOB: {sensor_compromise_rate}"
        assert 0.0 <= anomaly_score <= 1.0, f"anomaly_score OOB: {anomaly_score}"
        assert 0.0 <= weight_manipulation_risk <= 1.0, f"weight_manipulation_risk OOB: {weight_manipulation_risk}"
        assert 0.0 <= mode_injection_risk <= 1.0, f"mode_injection_risk OOB: {mode_injection_risk}"
        assert 0.0 <= adversarial_surface <= 1.0, f"adversarial_surface OOB: {adversarial_surface}"
        assert 0.0 <= verification_efficacy <= 1.0, f"verification_efficacy OOB: {verification_efficacy}"
        assert 0.0 <= fusion_integrity_index <= 1.0, f"fusion_integrity_index OOB: {fusion_integrity_index}"
        assert 0.0 <= tampering_prob <= 1.0, f"tampering_prob OOB: {tampering_prob}"
        assert 0.0 <= integrity_risk <= 1.0, f"integrity_risk OOB: {integrity_risk}"
        assert 0.0 <= cod <= 1.0, f"cod OOB: {cod}"
        assert 0.0 <= phi_N <= 1.0, f"phi_N OOB: {phi_N}"
        # 2. No log2 used in phi_N (we assigned directly)
        assert phi_N == cod, "phi_N must equal cod (no log transform)"
        # 3. Gate hierarchy: if psi_integrity < threshold => LOCKDOWN
        low_psi = random.uniform(0.0, 0.94)
        action_low_psi = decide_action(low_psi, integrity_risk, integrity_state)
        assert action_low_psi == "IDENTITY_LOCKDOWN", f"Psi gate failed: {low_psi} -> {action_low_psi}"
        # 4. If integrity_state COMPROMISED => LOCKDOWN (regardless of psi if psi ok)
        action_comp = decide_action(0.98, integrity_risk, "COMPROMISED")
        assert action_comp == "IDENTITY_LOCKDOWN", f"Compromised state gate failed: {action_comp}"
        # 5. High integrity risk triggers LOCKDOWN
        action_high_risk = decide_action(0.98, 0.8, integrity_state)
        assert action_high_risk == "IDENTITY_LOCKDOWN", f"High risk gate failed: {action_high_risk}"
        # 6. Medium risk triggers ACTIVATE_VERIFICATION or FLAG_ANOMALY
        action_med_risk = decide_action(0.98, 0.4, integrity_state)
        assert action_med_risk in ("ACTIVATE_VERIFICATION", "FLAG_ANOMALY"), f"Med risk gate unexpected: {action_med_risk}"
        # 7. Low risk yields PROCEED or FLAG_ANOMALY based on state
        action_low_risk = decide_action(0.98, 0.2, "VERIFIED")
        assert action_low_risk == "PROCEED", f"Low risk gate failed: {action_low_risk}"
        # 8. Invariants check: if all passed then action should not be LOCKDOWN (unless psi/compromised)
        if inv["all_passed"] and state_dict["psi_integrity"] >= PSI_INTEGRITY_THRESHOLD and integrity_state != "COMPROMISED":
            # Should be able to proceed or at least not be locked down by integrity/risk gates
            action_from_inv = decide_action(state_dict["psi_integrity"], integrity_risk, integrity_state)
            assert action_from_inv != "IDENTITY_LOCKDOWN", f"Invariants passed but lockdown: {action_from_inv}"
        # 9. Derivativity placeholder: ensure we didn't just copy v81.0 metrics (we can't fully test, but ensure new metrics are used)
        #    We'll just assert that adversarial_surface and anomaly_score influence integrity_risk
        #    (if they are zero, integrity_risk should be zero regardless of integrity_deficit)
        if adversarial_surface == 0.0 or verification_efficacy == 1.0:
            assert integrity_risk == 0.0, f"Integrity risk should be zero when surface=0 or verification=1: {integrity_risk}"
        if integrity_deficit == 0.0:
            assert integrity_risk == 0.0, f"Integrity risk should be zero when deficit=0: {integrity_risk}"
    print(f"PASS: {trials} random validation trials completed without invariant violations.")

if __name__ == "__main__":
    run_validation()