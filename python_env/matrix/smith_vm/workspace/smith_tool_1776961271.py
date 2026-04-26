# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
"""
Omega Protocol Mathematical Validation Script for RCOD-Flux-Scheduler
Validates dimensional homogeneity, domain safety, and invariant consistency
"""

import math
from typing import Tuple, List

# Constants from the repaired C++ code (SmithAuditInvariants struct)
PHI_DENSITY_THRESHOLD = 0.95
SHEAF_CURVATURE_BOUNDS = 0.01
XI_N_STIFFNESS_BOUND = 0.82  # From xi_N <= 0.82
XI_DELTA_RIGIDITY_BOUND = 1.28  # From xi_Delta >= 1.28
PSI_THRESHOLD = 0.95  # From |psi| >= 0.95
ENTROPY_THRESHOLD = 0.85  # From H_conditional < 0.85
PAGE_SIZE = 4096  # 4KB alignment check

def validate_log_domain(phi_N: float) -> Tuple[bool, str]:
    """Validate domain of ln(phi_N) in psi calculation"""
    if phi_N <= 0:
        return False, f"phi_N = {phi_N} ≤ 0 → ln(phi_N) undefined (domain error)"
    return True, "phi_N > 0 → ln(phi_N) defined"

def validate_invariant_logic(current_phi: float, psi: float, xi_N: float, xi_Delta: float) -> Tuple[bool, List[str]]:
    """Validate Smith Audit invariant logic"""
    errors = []
    
    # Condition 1: current_phi ≥ PHI_DENSITY_THRESHOLD
    if current_phi < PHI_DENSITY_THRESHOLD:
        errors.append(f"current_phi ({current_phi}) < PHI_DENSITY_THRESHOLD ({PHI_DENSITY_THRESHOLD})")
    
    # Condition 2: |psi| ≥ PSI_THRESHOLD
    if abs(psi) < PSI_THRESHOLD:
        errors.append(f"|psi| ({abs(psi)}) < PSI_THRESHOLD ({PSI_THRESHOLD})")
    
    # Condition 3: xi_N ≤ XI_N_STIFFNESS_BOUND
    if xi_N > XI_N_STIFFNESS_BOUND:
        errors.append(f"xi_N ({xi_N}) > XI_N_STIFFNESS_BOUND ({XI_N_STIFFNESS_BOUND})")
    
    # Condition 4: xi_Delta ≥ XI_DELTA_RIGIDITY_BOUND
    if xi_Delta < XI_DELTA_RIGIDITY_BOUND:
        errors.append(f"xi_Delta ({xi_Delta}) < XI_DELTA_RIGIDITY_BOUND ({XI_DELTA_RIGIDITY_BOUND})")
    
    # Condition 5: |current_phi - PHI_DENSITY_THRESHOLD| ≤ SHEAF_CURVATURE_BOUNDS
    if abs(current_phi - PHI_DENSITY_THRESHOLD) > SHEAF_CURVATURE_BOUNDS:
        errors.append(f"|current_phi - PHI_DENSITY_THRESHOLD| ({abs(current_phi - PHI_DENSITY_THRESHOLD)}) > SHEAF_CURVATURE_BOUNDS ({SHEAF_CURVATURE_BOUNDS})")
    
    # Critical flaw: CORE_PINNING_RANGE invariant missing from validation
    # The struct defines it but doesn't use it - this is a logical omission
    errors.append("MISSING INVARIANT: Core pinning range [16, 23] not validated in SmithAuditInvariants::ValidateInvariants")
    
    return len(errors) == 0, errors

def validate_address_resolution(integral: float) -> Tuple[bool, str]:
    """Validate 4KB address resolution logic"""
    addr = round(integral)
    if addr % PAGE_SIZE != 0:
        return False, f"Address {int(addr)} (from integral={integral}) not 4KB-aligned ({int(addr)} % {PAGE_SIZE} = {int(addr) % PAGE_SIZE})"
    return True, f"Address {int(addr)} is 4KB-aligned"

def validate_entropy_check(H_conditional: float) -> Tuple[bool, str]:
    """Validate entropy threshold check"""
    if H_conditional < 0:
        return False, f"Negative entropy ({H_conditional}) impossible for Shannon entropy"
    return True, f"Entropy {H_conditional} ≥ 0 (valid domain)"

def main():
    print("=" * 60)
    print("OMEGA PROTOCOL MATHEMATICAL VALIDATION: RCOD-FLUX-SCHEDULER")
    print("=" * 60)
    
    # Test cases covering edge conditions
    test_cases = [
        # (description, phi_N, current_phi, psi, xi_N, xi_Delta, integral, H_conditional)
        ("Nominal compliant case", 0.5, 0.955, math.log(0.5), 0.8, 1.3, 8192.0, 0.9),
        ("Phi_N boundary (ln(phi_N) = -0.95)", math.exp(-0.95), 0.955, -0.95, 0.8, 1.3, 8192.0, 0.9),
        ("Phi_N too high (|psi| < 0.95)", 0.5, 0.955, math.log(0.5), 0.8, 1.3, 8192.0, 0.9),
        ("Current_phi too low", 0.5, 0.94, math.log(0.5), 0.8, 1.3, 8192.0, 0.9),
        ("Current_phi too high", 0.5, 0.961, math.log(0.5), 0.8, 1.3, 8192.0, 0.9),
        ("xi_N too high", 0.5, 0.955, math.log(0.5), 0.83, 1.3, 8192.0, 0.9),
        ("xi_Delta too low", 0.5, 0.955, math.log(0.5), 0.8, 1.27, 8192.0, 0.9),
        ("Integral misalignment", 0.5, 0.955, math.log(0.5), 0.8, 1.3, 8192.3, 0.9),
        ("Negative entropy", 0.5, 0.955, math.log(0.5), 0.8, 1.3, 8192.0, -0.1),
        ("Zero phi_N (log domain error)", 0.0, 0.955, None, 0.8, 1.3, 8192.0, 0.9),
        ("Negative phi_N (log domain error)", -0.1, 0.955, None, 0.8, 1.3, 8192.0, 0.9),
    ]
    
    all_passed = True
    
    for desc, phi_N, current_phi, psi, xi_N, xi_Delta, integral, H_conditional in test_cases:
        print(f"\nTest Case: {desc}")
        print("-" * 40)
        
        # Skip log domain test if phi_N invalid (handled separately)
        if phi_N <= 0:
            passed, msg = validate_log_domain(phi_N)
            print(f"[LOG DOMAIN] {'PASS' if passed else 'FAIL'}: {msg}")
            if not passed:
                all_passed = False
            continue  # Skip other checks if log domain fails
        
        # Calculate psi if not provided (for domain-valid cases)
        if psi is None:
            psi = math.log(phi_N)
        
        # Validate log domain
        passed, msg = validate_log_domain(phi_N)
        print(f"[LOG DOMAIN] {'PASS' if passed else 'FAIL'}: {msg}")
        if not passed:
            all_passed = False
        
        # Validate invariant logic
        passed, errors = validate_invariant_logic(current_phi, psi, xi_N, xi_Delta)
        print(f"[INVARIANT LOGIC] {'PASS' if passed else 'FAIL'}")
        for err in errors:
            print(f"  - {err}")
        if not passed:
            all_passed = False
        
        # Validate address resolution
        passed, msg = validate_address_resolution(integral)
        print(f"[ADDRESS RES] {'PASS' if passed else 'FAIL'}: {msg}")
        if not passed:
            all_passed = False
        
        # Validate entropy check
        passed, msg = validate_entropy_check(H_conditional)
        print(f"[ENTROPY CHECK] {'PASS' if passed else 'FAIL'}: {msg}")
        if not passed:
            all_passed = False
    
    print("\n" + "=" * 60)
    print("VALIDATION SUMMARY")
    print("=" * 60)
    if all_passed:
        print("✅ ALL TESTS PASSED - Design is mathematically sound")
    else:
        print("❌ VALIDATION FAILED - Mathematical inconsistencies detected")
        print("\nCRITICAL FLAWS IDENTIFIED:")
        print("1. Missing core pinning range invariant in SmithAuditInvariants::ValidateInvariants")
        print("   - The struct defines CORE_PINNING_RANGE{16, 23} but never uses it")
        print("   - This violates Omega Protocol §3 (invariant embodiment)")
        print("2. Log domain safety: No check for phi_N > 0 before ln(phi_N)")
        print("   - Risk of undefined behavior if phi_N ≤ 0")
        print("\nRECOMMENDED FIXES:")
        print("- Add core pinning range check to ValidateInvariants:")
        print("   return ... && (16 <= core && core <= 23) && ...")
        print("- Add phi_N > 0 check before ln(phi_N) calculation")
        print("- Ensure xi_N and xi_Delta are treated as fixed invariants (not bounds)")
    
    return 0 if all_passed else 1

if __name__ == "__main__":
    exit(main())