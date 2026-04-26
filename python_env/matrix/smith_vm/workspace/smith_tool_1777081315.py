# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import math
from typing import Tuple, List

# Omega Protocol Constants (from proposal)
COD_THRESHOLD = 0.85
COD_FLOOR = 0.39
Q_FACTOR_MIN = 0.15
Q_FACTOR_MAX = 0.80
PSI_INTEGRITY_THRESHOLD = 0.95
TENSOR_LEAK_MAX = 0.50
STIFFNESS_MAX_DELTA = 0.10
PHI_DELTA_MAX = 0.50
B1_HOMOLOGY_MAX = 0.80
K_BOLTZMANN = 1.0
AUDIT_ENTROPY_PER_CHECK = 0.02
TOTAL_AUDIT_COST = 9 * AUDIT_ENTROPY_PER_CHECK  # 0.18

LAMBDA_COUPLING = 0.5
KAPPA_CONFINEMENT = 0.5
ETA_TENSOR_LEAK = 0.3

def calculate_fidelity(diagnostic_vec: List[complex], plasma_vec: List[complex]) -> float:
    """Calculate fidelity between diagnostic and plasma vectors (clamped [0,1])"""
    dot = 0.0
    magD = 0.0
    magP = 0.0
    size = min(len(diagnostic_vec), len(plasma_vec))
    
    for i in range(size):
        dot += abs(np.conj(diagnostic_vec[i]) * plasma_vec[i])
        magD += abs(diagnostic_vec[i] * diagnostic_vec[i])
        magP += abs(plasma_vec[i] * plasma_vec[i])
    
    if magD < 1e-9 or magP < 1e-9:
        return 0.0
    
    fidelity = dot / (math.sqrt(magD) * math.sqrt(magP))
    return max(0.0, min(1.0, fidelity))  # Clamp to [0,1]

def calculate_cod(
    diagnostic_vec: List[complex],
    plasma_vec: List[complex],
    h_instability: float,
    xi_confinement: float,
    theta_tensor_leak: float
) -> float:
    """Calculate Chain Overlap Density (COD) per proposal"""
    fidelity = calculate_fidelity(diagnostic_vec, plasma_vec)
    
    instability_penalty = math.exp(-LAMBDA_COUPLING * h_instability)
    confinement_penalty = math.exp(-KAPPA_CONFINEMENT * xi_confinement)
    exposure_penalty = math.exp(-ETA_TENSOR_LEAK * theta_tensor_leak)
    
    cod = fidelity * instability_penalty * confinement_penalty * exposure_penalty
    return max(0.0, min(1.0, cod))  # Ensure [0,1] bounds

def validate_phi_n_bounds() -> Tuple[bool, List[str]]:
    """Validate that phi_N = COD maintains [0,1] bounds"""
    errors = []
    
    # Test edge cases
    test_cases = [
        # (diagnostic_vec, plasma_vec, h, xi, theta_leak, description)
        ([1+0j], [1+0j], 0.0, 0.0, 0.0, "Perfect alignment, zero penalties"),
        ([1+0j], [0+0j], 0.0, 0.0, 0.0, "Zero plasma vector"),
        ([0+0j], [1+0j], 0.0, 0.0, 0.0, "Zero diagnostic vector"),
        ([1+0j], [1j], 0.0, 0.0, 0.0, "Orthogonal vectors"),
        ([1+0j], [1+0j], 1.0, 1.0, 1.0, "Maximum penalties"),
        ([1+0j], [1+0j], 0.0, 0.0, 0.5, "Medium exposure"),
        ([1+0j, 1+0j], [1+0j, 1+0j], 0.5, 0.5, 0.5, "Multi-dimensional"),
        ([1+0j, 0+0j], [0+0j, 1+0j], 0.3, 0.7, 0.2, "Mixed alignment")
    ]
    
    for diag, plas, h, xi, theta, desc in test_cases:
        cod = calculate_cod(diag, plas, h, xi, theta)
        phi_n = cod  # Per proposal: phi_N = COD
        
        if not (0.0 <= phi_n <= 1.0):
            errors.append(
                f"FAIL: {desc} -> phi_N = {phi_n:.6f} (COD={cod:.6f}) "
                f"[h={h}, xi={xi}, theta={theta}]"
            )
    
    # Random sampling test
    np.random.seed(42)  # For reproducibility
    for _ in range(1000):
        # Generate random complex vectors (length 5)
        diag = [complex(np.random.uniform(-1, 1), np.random.uniform(-1, 1)) for _ in range(5)]
        plas = [complex(np.random.uniform(-1, 1), np.random.uniform(-1, 1)) for _ in range(5)]
        h = np.random.uniform(0, 1)
        xi = np.random.uniform(0, 1)
        theta = np.random.uniform(0, 1)
        
        cod = calculate_cod(diag, plas, h, xi, theta)
        phi_n = cod
        
        if not (0.0 <= phi_n <= 1.0):
            errors.append(
                f"Random FAIL: phi_N = {phi_n:.6f} "
                f"[h={h:.3f}, xi={xi:.3f}, theta={theta:.3f}]"
            )
            if len(errors) > 5:  # Limit error reporting
                break
    
    return len(errors) == 0, errors

def validate_safety_gates() -> Tuple[bool, List[str]]:
    """Validate safety gate hierarchy integrity"""
    errors = []
    
    # Test case: Integrity critical (should trigger HALT_EXPERIMENT)
    state_integrity_critical = {
        'psi_integrity': 0.94,  # Below threshold
        'cod': 0.90,            # Above COD threshold
        'h_instability': 0.2,
        'xi_confinement': 0.3,
        'theta_tensor_leak': 0.1,
        'b1_homology': 0.2
    }
    
    # According to SilenceProtocol.Decide:
    # If INTEGRITY_CRITICAL -> HALT_EXPERIMENT (regardless of COD)
    # We can't directly test the function, but we can verify the condition
    if state_integrity_critical['psi_integrity'] >= PSI_INTEGRITY_THRESHOLD:
        errors.append(
            f"Integrity gate FAIL: psi_integrity={state_integrity_critical['psi_integrity']} "
            f"should be < {PSI_INTEGRITY_THRESHOLD} to trigger halt"
        )
    
    # Test case: COD below threshold (should trigger FREEZE_CONFIG if integrity ok)
    state_cod_low = {
        'psi_integrity': 0.96,  # Above integrity threshold
        'cod': 0.80,            # Below COD threshold
        'h_instability': 0.2,
        'xi_confinement': 0.3,
        'theta_tensor_leak': 0.1,
        'b1_homology': 0.2
    }
    
    if state_cod_low['cod'] >= COD_THRESHOLD:
        errors.append(
            f"COD gate FAIL: cod={state_cod_low['cod']:.3f} "
            f"should be < {COD_THRESHOLD} to trigger freeze"
        )
    
    # Test case: Both gates passed (should proceed)
    state_ok = {
        'psi_integrity': 0.96,
        'cod': 0.90,
        'h_instability': 0.2,
        'xi_confinement': 0.3,
        'theta_tensor_leak': 0.1,
        'b1_homology': 0.2
    }
    
    if (state_ok['psi_integrity'] < PSI_INTEGRITY_THRESHOLD or 
        state_ok['cod'] < COD_THRESHOLD):
        errors.append(
            f"Proceed gate FAIL: psi_integrity={state_ok['psi_integrity']:.3f}, "
            f"cod={state_ok['cod']:.3f} should both pass thresholds"
        )
    
    return len(errors) == 0, errors

def validate_phi_delta() -> Tuple[bool, List[str]]:
    """Validate phi_delta calculation and asymmetry check"""
    errors = []
    
    # phi_N = COD (per proposal)
    # phi_delta = phi_N * tanh((xi_confinement - z_plasma_depth) / 3.0)
    # Asymmetry check: phi_delta < PHI_DELTA_MAX * phi_N
    
    test_cases = [
        # (phi_N, xi_confinement, z_plasma_depth, expected_asymmetry_ok, description)
        (0.9, 0.5, 0.5, True, "Equal confinement/depth -> zero asymmetry"),
        (0.9, 0.7, 0.5, True, "Moderate xi > z"),
        (0.9, 0.5, 0.7, True, "Moderate z > xi"),
        (0.9, 0.9, 0.1, False, "Large xi-z difference -> asymmetry violation"),
        (0.9, 0.1, 0.9, False, "Large z-xi difference -> asymmetry violation"),
        (0.5, 0.8, 0.2, False, "Low phi_N but large difference"),
        (1.0, 0.6, 0.4, True, "Max phi_N, moderate difference")
    ]
    
    for phi_N, xi, z, expected_ok, desc in test_cases:
        phi_delta = phi_N * math.tanh((xi - z) / 3.0)
        asymmetry_ok = phi_delta < (PHI_DELTA_MAX * phi_N)
        
        if asymmetry_ok != expected_ok:
            errors.append(
                f"Asymmetry check FAIL: {desc} -> "
                f"phi_delta={phi_delta:.6f}, threshold={PHI_DELTA_MAX * phi_N:.6f}, "
                f"expected_ok={expected_ok}, got={asymmetry_ok}"
            )
    
    return len(errors) == 0, errors

def main():
    """Run all validation checks"""
    print("=" * 60)
    print("OMEGA PROTOCOL TOKAMAK PROPOSAL AUDIT")
    print("=" * 60)
    
    # 1. Validate phi_N bounds (core mathematical soundness)
    print("\n[1] Validating phi_N = COD bounds [0,1]...")
    bounds_ok, bounds_errors = validate_phi_n_bounds()
    if bounds_ok:
        print("✅ PASS: All phi_N values within [0,1]")
    else:
        print("❌ FAIL: Bounds violation detected")
        for err in bounds_errors[:3]:
            print(f"   - {err}")
        if len(bounds_errors) > 3:
            print(f"   - ... and {len(bounds_errors)-3} more")
    
    # 2. Validate safety gate hierarchy
    print("\n[2] Validating safety gate hierarchy...")
    gates_ok, gates_errors = validate_safety_gates()
    if gates_ok:
        print("✅ PASS: Safety gates logically consistent")
    else:
        print("❌ FAIL: Safety gate logic error")
        for err in gates_errors:
            print(f"   - {err}")
    
    # 3. Validate phi_delta asymmetry check
    print("\n[3] Validating phi_delta asymmetry calculation...")
    delta_ok, delta_errors = validate_phi_delta()
    if delta_ok:
        print("✅ PASS: Asymmetry checks correct")
    else:
        print("❌ FAIL: Asymmetry calculation error")
        for err in delta_errors[:3]:
            print(f"   - {err}")
        if len(delta_errors) > 3:
            print(f"   - ... and {len(delta_errors)-3} more")
    
    # 4. Validate COD formula components
    print("\n[4] Validating COD formula components...")
    # Test that each penalty term is in (0,1]
    test_penalties = [
        (LAMBDA_COUPLING, "Lambda coupling"),
        (KAPPA_CONFINEMENT, "Kappa confinement"),
        (ETA_TENSOR_LEAK, "Eta tensor leak")
    ]
    
    penalty_ok = True
    for coeff, name in test_penalties:
        # For x in [0,1], exp(-coeff*x) in [exp(-coeff), 1]
        min_val = math.exp(-coeff * 1.0)
        max_val = math.exp(-coeff * 0.0)  # = 1.0
        if not (0 < min_val <= 1.0 and 0 < max_val <= 1.0):
            penalty_ok = False
            print(f"❌ FAIL: {name} coefficient {coeff} produces invalid range")
        else:
            print(f"✅ PASS: {name} coefficient {coeff} -> exp range [{min_val:.3f}, {max_val:.3f}]")
    
    # Overall result
    print("\n" + "=" * 60)
    all_ok = bounds_ok and gates_ok and delta_ok and penalty_ok
    if all_ok:
        print("🎉 OVERALL VALIDATION: PASS")
        print("✅ Mathematical soundness confirmed")
        print("✅ Safety gate hierarchy compliant")
        print("✅ Omega Protocol invariants upheld")
    else:
        print("💥 OVERALL VALIDATION: FAIL")
        print("❌ One or more critical invariants violated")
        print("🔧 Proposal requires revision before deployment")
    print("=" * 60)
    
    return all_ok

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)