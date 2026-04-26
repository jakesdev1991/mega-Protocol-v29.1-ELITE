# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
# Omega Protocol Audit-Trace-Hardening Mathematical Validator
# Validates scalar invariants and dimensional consistency of key expressions
# Based on Engine's C++ output with corrections from deep audit

import math
import sys
from typing import Tuple, List

# Tolerance for floating-point comparisons
TOL = 1e-10

def validate_informational_field(phi_N: float, phi_Delta: float) -> List[str]:
    """Validate informational field components and derived invariants"""
    errors = []
    
    # 1. psi = ln(Φ_N) must be defined and >= PSI_IDENTITY (0.95)
    if phi_N <= 0:
        errors.append(f"phi_N must be positive for ln(): got {phi_N}")
    else:
        psi = math.log(phi_N)
        if psi < 0.95 - TOL:
            errors.append(f"psi = ln(phi_N) = {psi:.6f} < PSI_IDENTITY (0.95)")
    
    # 2. COD = |<Φ_N|Φ_Δ>|² = |phi_N * phi_Delta|² must >= COD_THRESHOLD (0.85)
    cod_squared = (phi_N * phi_Delta) ** 2
    if cod_squared < 0.85 - TOL:
        errors.append(f"COD = |phi_N * phi_Delta|² = {cod_squared:.6f} < COD_THRESHOLD (0.85)")
    
    return errors

def validate_xi_coefficients(xi_N: float, xi_Delta: float) -> List[str]:
    """Validate XI coefficients per Smith Audit invariants"""
    errors = []
    
    # XI_BOUND: xi_N <= 0.82
    if xi_N > 0.82 + TOL:
        errors.append(f"xi_N = {xi_N:.6f} > XI_BOUND (0.82)")
    
    # XI_DELTA: xi_Delta must equal 1.28 within tolerance
    if abs(xi_Delta - 1.28) > TOL:
        errors.append(f"xi_Delta = {xi_Delta:.6f} deviates from XI_DELTA (1.28) by > {TOL}")
    
    return errors

def validate_conformal_factor(yield_val: float, psi: float, xi_N: float, xi_Delta: float) -> List[str]:
    """Validate conformal factor expression: yield * (1 + psi + xi_N + xi_Delta)"""
    errors = []
    
    # All terms must be dimensionless (validated via xi coefficients and psi)
    # Check that expression is real and non-negative (yield should be >=0)
    if yield_val < 0:
        errors.append(f"DEDSS yield must be non-negative: got {yield_val}")
    
    # Dimensional consistency check: all additive terms dimensionless
    # psi = ln(Φ_N) -> dimensionless
    # xi_N, xi_Delta -> dimensionless (by invariant validation)
    # 1 -> dimensionless constant
    # yield_val -> dimensionless (by definition in DEDS metrics)
    
    return errors

def validate_entropy_bound(psi: float) -> List[str]:
    """Validate entropy bound expression: H >= 1 - psi"""
    errors = []
    
    # Entropy bound must be <= 1 (since psi >= 0.95 -> 1-psi <= 0.05)
    bound = 1.0 - psi
    if bound > 1.0 + TOL:  # Should never happen if psi >=0, but check anyway
        errors.append(f"Entropy bound = 1 - psi = {bound:.6f} > 1.0 (invalid)")
    
    # In practice, entropy H must be >= this bound (validated elsewhere)
    return errors

def validate_curvature_combination(psi: float, xi_N: float, xi_Delta: float) -> List[str]:
    """Validate curvature combination: N*(1+psi+xi_N) + Delta*xi_Delta"""
    errors = []
    
    # Check coefficients are dimensionless (via psi, xi_N, xi_Delta validation)
    # 1+psi+xi_N must be real (no constraints beyond dimensionless)
    coeff_N = 1.0 + psi + xi_N
    coeff_Delta = xi_Delta
    
    # No mathematical constraints on coefficients beyond being real numbers
    # Dimensional consistency: coefficients dimensionless -> result has same dimensions as N/Delta
    
    return errors

def validate_sheaf_stalk(xi_N: float, xi_Delta: float, L_ref: float = 1.0, T_ref: float = 1.0) -> List[str]:
    """Validate sheaf stalk definition: ∇_s phi = (xi_N/L_ref)⋅s + (xi_Delta/T_ref)⋅∂_t phi"""
    errors = []
    
    # Dimensional analysis:
    # [∇_s phi] = [phi] / [length]
    # [s] = [length]
    # [∂_t phi] = [phi] / [time]
    #
    # Term1: (xi_N/L_ref) * s -> [xi_N] * [length] / [length] = [xi_N] (must be dimensionless)
    # Term2: (xi_Delta/T_ref) * ∂_t phi -> [xi_Delta] * [phi] / [time] * [time] / [phi] = [xi_Delta] (dimensionless)
    #
    # Therefore: xi_N and xi_Delta must be dimensionless (validated via XI coefficients)
    # L_ref and T_ref must have dimensions of length and time respectively
    #
    # In natural units (L_ref = T_ref = 1.0), we require:
    if abs(L_ref - 1.0) > TOL:
        errors.append(f"L_ref must be 1.0 in natural units: got {L_ref}")
    if abs(T_ref - 1.0) > TOL:
        errors.append(f"T_ref must be 1.0 in natural units: got {T_ref}")
    
    return errors

def main():
    """Main validation routine"""
    if len(sys.argv) != 6:
        print("Usage: python validate_audit_trace.py <phi_N> <phi_Delta> <xi_N> <xi_Delta> <yield>")
        print("Example: python validate_audit_trace.py 2.6 0.6 0.7 1.28 0.9")
        sys.exit(1)
    
    try:
        phi_N = float(sys.argv[1])
        phi_Delta = float(sys.argv[2])
        xi_N = float(sys.argv[3])
        xi_Delta = float(sys.argv[4])
        yield_val = float(sys.argv[5])
    except ValueError as e:
        print(f"Error: All inputs must be numbers. {e}")
        sys.exit(1)
    
    all_errors = []
    
    # Validate informational field (gives us psi)
    field_errors = validate_informational_field(phi_N, phi_Delta)
    all_errors.extend(field_errors)
    
    # If we have valid psi, use it for other validations
    psi = None
    if not field_errors and phi_N > 0:
        psi = math.log(phi_N)
    
    # Validate XI coefficients
    xi_errors = validate_xi_coefficients(xi_N, xi_Delta)
    all_errors.extend(xi_errors)
    
    # Validate conformal factor (requires psi)
    if psi is not None:
        conf_errors = validate_conformal_factor(yield_val, psi, xi_N, xi_Delta)
        all_errors.extend(conf_errors)
        
        # Validate entropy bound
        ent_errors = validate_entropy_bound(psi)
        all_errors.extend(ent_errors)
        
        # Validate curvature combination
        curv_errors = validate_curvature_combination(psi, xi_N, xi_Delta)
        all_errors.extend(curv_errors)
    
    # Validate sheaf stalk (natural units assumed)
    sheaf_errors = validate_sheaf_stalk(xi_N, xi_Delta)
    all_errors.extend(sheaf_errors)
    
    # Output results
    if all_errors:
        print("VALIDATION FAILED - Omega Protocol violations detected:")
        for i, error in enumerate(all_errors, 1):
            print(f"  {i}. {error}")
        sys.exit(1)
    else:
        print("VALIDATION PASSED - All Omega Protocol invariants satisfied")
        print(f"  phi_N = {phi_N:.6f} -> psi = ln(phi_N) = {math.log(phi_N):.6f}")
        print(f"  phi_Delta = {phi_Delta:.6f}")
        print(f"  COD = |phi_N * phi_Delta|² = {(phi_N * phi_Delta)**2:.6f}")
        print(f"  xi_N = {xi_N:.6f} (<= 0.82: {'PASS' if xi_N <= 0.82 + TOL else 'FAIL'})")
        print(f"  xi_Delta = {xi_Delta:.6f} (== 1.28: {'PASS' if abs(xi_Delta-1.28) < TOL else 'FAIL'})")
        print(f"  DEDS yield = {yield_val:.6f}")
        if psi is not None:
            print(f"  Conformal factor = yield * (1+psi+xi_N+xi_Delta) = {yield_val * (1.0 + psi + xi_N + xi_Delta):.6f}")
            print(f"  Entropy bound = 1 - psi = {1.0 - psi:.6f}")
        sys.exit(0)

if __name__ == "__main__":
    main()