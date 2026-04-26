# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import math
import random

# === OMEGA PROTOCOL CONSTANTS (v65.0) ===
COD_THRESHOLD = 0.85
COD_FLOOR = 0.39
PSI_INTEGRITY_THRESHOLD = 0.95
TENSOR_LEAK_MAX = 0.50
STIFFNESS_MAX_DELTA = 0.10
PHI_DELTA_MAX = 0.50
B1_HOMOLOGY_MAX = 0.80
LAMBDA_COUPLING = 0.5
KAPPA_CONFINEMENT = 0.5
ETA_TENSOR_LEAK = 0.3
AUDIT_ENTROPY_PER_CHECK = 0.02
TOTAL_AUDIT_COST = 9 * AUDIT_ENTROPY_PER_CHECK  # 0.18

# === COD FUNCTION VALIDATION ===
def calculate_cod(fidelity, h_instability, xi_confinement, theta_tensor_leak):
    """Mirrors PlasmaIntegrityManifold::Calculate_COD_Fusion core logic"""
    instability_penalty = math.exp(-LAMBDA_COUPLING * h_instability)
    confinement_penalty = math.exp(-KAPPA_CONFINEMENT * xi_confinement)
    exposure_penalty = math.exp(-ETA_TENSOR_LEAK * theta_tensor_leak)
    return fidelity * instability_penalty * confinement_penalty * exposure_penalty

def test_cod_bounds():
    """Verify COD output remains in [0,1] for all valid inputs"""
    random.seed(42)
    for _ in range(10000):
        fidelity = random.uniform(0.0, 1.0)
        h = random.uniform(0.0, 1.0)
        xi = random.uniform(0.0, 1.0)
        theta = random.uniform(0.0, 1.0)
        cod = calculate_cod(fidelity, h, xi, theta)
        assert 0.0 <= cod <= 1.0, f"COD out of bounds: {cod} (f={fidelity}, h={h}, xi={xi}, θ={theta})"
    print("✓ COD bounds validation passed")

# === SAFETY GATE HIERARCHY VALIDATION ===
class SilenceProtocolAction:
    PROCEED = 0
    FREEZE_CONFIG = 1
    HALT_EXPERIMENT = 2
    FULL_SILENCE = 3

def decide_action(psi_integrity, cod, b1_homology, theta_tensor_leak, xi_confinement, z_plasma_depth, h_instability):
    """Mirrors SilenceProtocol::Decide logic"""
    # Primary gate: Integrity (non-negotiable)
    if psi_integrity < PSI_INTEGRITY_THRESHOLD:
        return SilenceProtocolAction.HALT_EXPERIMENT
    
    # Secondary gate: Alignment fidelity
    if cod < COD_THRESHOLD:
        return SilenceProtocolAction.FREEZE_CONFIG
    
    # Tertiary gates: Topological/stability checks
    if (b1_homology > B1_HOMOLOGY_MAX or 
        theta_tensor_leak > TENSOR_LEAK_MAX or
        h_instability < 0.15 or h_instability > 0.80 or
        xi_confinement > z_plasma_depth + STIFFNESS_MAX_DELTA):
        return SilenceProtocolAction.FREEZE_CONFIG
    
    return SilenceProtocolAction.PROCEED

def test_safety_gate_hierarchy():
    """Verify integrity gate overrides alignment gate"""
    # Case 1: Integrity failure should halt experiment regardless of COD
    assert decide_action(
        psi_integrity=0.94,  # Below threshold
        cod=0.90,            # Above COD threshold
        b1_homology=0.1,
        theta_tensor_leak=0.1,
        xi_confinement=0.5,
        z_plasma_depth=0.5,
        h_instability=0.5
    ) == SilenceProtocolAction.HALT_EXPERIMENT, "Integrity gate failed to override COD"
    
    # Case 2: COD failure should freeze config when integrity intact
    assert decide_action(
        psi_integrity=0.96,  # Above threshold
        cod=0.80,            # Below COD threshold
        b1_homology=0.1,
        theta_tensor_leak=0.1,
        xi_confinement=0.5,
        z_plasma_depth=0.5,
        h_instability=0.5
    ) == SilenceProtocolAction.FREEZE_CONFIG, "COD gate failed when integrity intact"
    
    # Case 3: Topological failure should freeze config
    assert decide_action(
        psi_integrity=0.96,
        cod=0.90,
        b1_homology=0.85,    # Above B1 threshold
        theta_tensor_leak=0.1,
        xi_confinement=0.5,
        z_plasma_depth=0.5,
        h_instability=0.5
    ) == SilenceProtocolAction.FREEZE_CONFIG, "Topological gate failed"
    
    # Case 4: All gates pass -> proceed
    assert decide_action(
        psi_integrity=0.96,
        cod=0.90,
        b1_homology=0.1,
        theta_tensor_leak=0.1,
        xi_confinement=0.5,
        z_plasma_depth=0.5,
        h_instability=0.5
    ) == SilenceProtocolAction.PROCEED, "Proceed condition failed"
    print("✓ Safety gate hierarchy validation passed")

# === SMITH INVARIANT ENFORCER VALIDATION ===
def check_phi_floor(phi_N):
    """Mirrors SmithInvariantEnforcer::Check phi_floor_ok"""
    return phi_N >= COD_FLOOR

def check_asymmetry(phi_N, xi_confinement, z_plasma_depth):
    """Mirrors SmithInvariantEnforcer::Check asymmetry_ok"""
    phi_delta = phi_N * math.tanh((xi_confinement - z_plasma_depth) / 3.0)
    return phi_delta < PHI_DELTA_MAX * phi_N

def test_smith_invariants():
    """Verify critical Smith invariant calculations"""
    # phi_floor_ok: Direct COD comparison
    assert check_phi_floor(0.39) == True, "phi_floor_ok failed at boundary"
    assert check_phi_floor(0.38) == False, "phi_floor_ok failed below floor"
    
    # asymmetry_ok: Verify formula correctness
    # Case 1: phi_N = 0 -> asymmetry check fails (0 < 0 false)
    assert check_asymmetry(0.0, 0.5, 0.5) == False, "asymmetry_ok failed at phi_N=0"
    
    # Case 2: phi_N > 0 -> asymmetry check passes for |dx| <= 1.0 (since tanh(1/3)≈0.32 < 0.5)
    assert check_asymmetry(0.5, 0.5, 0.5) == True, "asymmetry_ok failed at dx=0"
    assert check_asymmetry(0.5, 1.5, 0.5) == True, "asymmetry_ok failed at dx=1.0"
    assert check_asymmetry(0.5, -0.5, 0.5) == True, "asymmetry_ok failed at dx=-1.0"
    
    # Case 3: Extreme dx should fail asymmetry check (but note: physics bounds dx)
    assert check_asymmetry(0.5, 3.5, 0.5) == False, "asymmetry_ok failed to catch large dx"
    print("✓ Smith invariant validation passed")

# === PHI-DENSITY LEDGER VALIDATION ===
def calculate_phi_net_gain(cod_before, cod_after, audit_checks):
    """Mirrors PhiDensityLedger::CalculateNetGain"""
    raw_gain = cod_after - cod_before
    audit_cost = audit_checks * AUDIT_ENTROPY_PER_CHECK
    return raw_gain - audit_cost

def test_phi_density_ledger():
    """Verify audit cost subtraction in Φ-density accounting"""
    # Baseline: no gain, only audit cost
    assert calculate_phi_net_gain(0.5, 0.5, 9) == -0.18, "Baseline audit cost incorrect"
    
    # Net positive gain after audit cost
    assert calculate_phi_net_gain(0.5, 0.7, 9) == 0.02, "Net gain calculation incorrect"
    
    # Net negative gain (audit cost exceeds raw gain)
    assert calculate_phi_net_gain(0.5, 0.55, 9) == -0.13, "Net loss calculation incorrect"
    print("✓ Φ-density ledger validation passed")

# === MAIN VALIDATION SUITE ===
if __name__ == "__main__":
    try:
        test_cod_bounds()
        test_safety_gate_hierarchy()
        test_smith_invariants()
        test_phi_density_ledger()
        print("\n🎉 ALL VALIDATIONS PASSED - OMEGA PROTOCOL COMPLIANT")
    except AssertionError as e:
        print(f"\n❌ VALIDATION FAILED: {e}")
        exit(1)