# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
# -*- coding: utf-8 -*-
"""
Omega Protocol v26.0 Strictor Gate – Validation Script
------------------------------------------------------
Checks a submitted C++/Python derivation for:
  - Presence of Omega invariants (psi, xi_N, xi_Delta)
  - Explicit integral evaluation (change of vars, Jacobian, numeric result)
  - Dimensional consistency (hidden scale factor 'a' appears and cancels)
  - Orthogonality proof (Z2 symmetry → block-diagonal Hamiltonian)
  - Entropy bound H >= 0.85 with IR regulation
  - Quantitative cross‑validation (muonium, lattice QED)
  - Reproducibility of ALPHA_FS_CORRECTION from the integral
"""

import re
import math
import numpy as np
from typing import Tuple, Optional

def extract_constants(src: str) -> dict:
    """Pull out numeric constants that look like physics parameters."""
    consts = {}
    # Match lines like: constexpr double LAMBDA = 0.82;
    pattern = r'(?:constexpr\s+)?(?:double|float)\s+(\w+)\s*=\s*([0-9.]+e?[+-]?[0-9]*)\s*;'
    for m in re.finditer(pattern, src):
        name, val = m.group(1), float(m.group(2))
        consts[name] = val
    return consts

def has_invariant(src: str, inv: str) -> bool:
    """Check that the invariant appears as a variable, not just a comment."""
    # Look for the invariant used in an expression (e.g., psi = log(Phi_N);)
    pattern = rf'\b{inv}\b\s*[=+\-*/]'
    return bool(re.search(pattern, src))

def integral_evaluation_present(src: str) -> bool:
    """
    Very loose check: we require a comment or code line that shows:
      - substitution k = Lambda * q
      - Jacobian Lambda^3
      - limits 0 to 1 (or 0 to Lambda)
      - a numeric result (e.g., 0.000318)
    """
    # Look for the pattern of change of variables
    if not re.search(r'k\s*=\s*Lambda\s*\*\s*q', src, re.I):
        return False
    if not re.search(r'Lambda\*\*3|Lambda\s*\*\s*Lambda\s*\*\s*Lambda', src):
        return False
    if not re.search(r'0\s*[:<]\s*q\s*[:<]\s*1|0\s*[:<]\s*k\s*[:<]\s*Lambda', src, re.I):
        return False
    # numeric result somewhere near the integral
    if not re.search(r'0\.\d{5,}', src):
        return False
    return True

def dimensional_check(src: str) -> bool:
    """
    Ensure a hidden lattice spacing 'a' appears and that the final
    expression is dimensionless. We look for 'a' in the integral prefactor
    and its cancellation.
    """
    if not re.search(r'\ba\b', src, re.I):
        return False
    # Check that a^2 appears in denominator with Lambda^2 or similar
    if not re.search(r'a\*\*2|a\s*\*\s*a', src):
        return False
    # Ensure a does NOT appear in the final constant (i.e., after simplification)
    # Simple heuristic: after removing comments, the line defining ALPHA_FS_CORRECTION
    # should not contain 'a'
    lines = [ln for ln in src.splitlines() if not ln.strip().startswith('//')]
    const_line = next((ln for ln in lines if 'ALPHA_FS_CORRECTION' in ln), '')
    if 'a' in const_line:
        return False
    return True

def orthogonality_proof(src: str) -> bool:
    """Look for a derivation that uses Z2 symmetry to block-diagonalize."""
    if not re.search(r'Z2\s*symmetry|Z_2\s*symmetry', src, re.I):
        return False
    # Expect something like: "block-diagonal" or "decouples"
    if not re.search(r'block[-\s]?diagonal|decoupl', src, re.I):
        return False
    # Expect a mode basis transformation mention
    if not re.search(r'mode\s+basis|transformation', src, re.I):
        return False
    return True

def entropy_bound(src: str) -> Tuple[bool, Optional[float]]:
    """
    Extract an entropy calculation, apply IR regulator (finite volume V = L^3,
    L ~ 1/Lambda) and check H >= 0.85.
    Very simplified: we look for a formula resembling:
        H = - sum n_k log n_k   (or bosonic version)
    and then compute with a cutoff.
    """
    # Find any occurrence of entropy or H =
    if not re.search(r'\bH\b|\bentropy\b', src, re.I):
        return False, None
    # Attempt to parse a simple sum/integral expression; for safety we
    # compute a placeholder using the parameters if they exist.
    consts = extract_constants(src)
    Lambda = consts.get('LAMBDA', 0.82)
    # IR cutoff: minimal k = 2π / L, with L = 1/Lambda => k_min = 2π * Lambda
    k_min = 2 * math.pi * Lambda
    # Use a simple Maxwell-Boltzmann-like occupation with chemical potential mu=0.05*Lambda
    mu = 0.05 * Lambda
    # Sample a few k values in [k_min, Lambda] and approximate the integral
    ks = np.linspace(k_min, Lambda, 1000)
    nk = 1.0 / (np.exp((ks**2 - mu**2) / (2 * Lambda**2)) - 1.0)
    # Bosonic von Neumann integrand: (n+1)log(n+1) - n log n
    integrand = (nk + 1) * np.log(nk + 1) - nk * np.log(nk)
    # Approximate 3D integral: 4π ∫ k^2 dk
    dk = ks[1] - ks[0]
    H_approx = 4 * math.pi * np.sum(integrand * ks**2) * dk
    return H_approx >= 0.85, float(H_approx)

def cross_validation(src: str) -> bool:
    """Check for quantitative comparison with muonium hyperfine or lattice QED."""
    patterns = [
        r'muonium\s+hyperfine',
        r'lattice\s+QED',
        r'Δα/α\s*<\s*1e-5',
        r'Δα/α\s*=\s*[0-9.eE+-]+\s*±',
        r'σ\s*[0-9]'
    ]
    return any(re.search(p, src, re.I) for p in patterns)

def recompute_correction(src: str) -> Tuple[bool, Optional[float]]:
    """
    If the integral is explicitly evaluated, recompute Δα/α and compare
    to the hard‑coded ALPHA_FS_CORRECTION.
    """
    consts = extract_constants(src)
    Lambda = consts.get('LAMBDA', 0.82)
    v = consts.get('V', 1.28)  # assume variable named V or v
    PhiRatio = consts.get('PHI_DELTA_OVER_PHI_N', None)
    # If the ratio is not given, we cannot compute; we will treat as unknown.
    # Look for a line that gives the integral value
    integral_val = None
    m = re.search(r'integral\s*[:=]\s*([0-9.eE+-]+)', src, re.I)
    if m:
        integral_val = float(m.group(1))
    else:
        # Try to capture a comment like "yielding 0.000318"
        m = re.search(r'0\.\d{5,}', src)
        if m:
            integral_val = float(m.group(0))
    if integral_val is None:
        return False, None
    # The formula from the comment: Δα/α = (Φ_Delta/Φ_N) * (1/Λ^2) * integral
    if PhiRatio is None:
        # Try to infer from Phi_N and Phi_Delta if present
        Phi_N = consts.get('PHI_N')
        Phi_Delta = consts.get('PHI_DELTA')
        if Phi_N and Phi_Delta:
            PhiRatio = Phi_Delta / Phi_N
        else:
            return False, None
    predicted = PhiRatio * (1.0 / (Lambda ** 2)) * integral_val
    # Extract the hard‑coded constant
    const_line = next((ln for ln in src.splitlines() if 'ALPHA_FS_CORRECTION' in ln), '')
    m = re.search(r'=[\s]*([0-9.eE+-]+)', const_line)
    if not m:
        return False, None
    hardcoded = float(m.group(1))
    # Allow 1% tolerance
    return math.isclose(predicted, hardcoded, rel_tol=1e-2), predicted

def validate(src: str) -> None:
    """Main validation – raises AssertionError on any failure."""
    # 1. Invariants
    for inv in ('psi', 'xi_N', 'xi_Delta'):
        assert has_invariant(src, inv), f"Missing Omega invariant '{inv}' in derivation."
    # 2. Integral evaluation
    assert integral_evaluation_present(src), "Integral evaluation (change of vars, Jacobian, limits, numeric result) not found."
    # 3. Dimensional consistency
    assert dimensional_check(src), "Dimensional analysis with hidden lattice spacing 'a' missing or incorrect."
    # 4. Orthogonality proof
    assert orthogonality_proof(src), "Orthogonality proof from Z2 symmetry not demonstrated."
    # 5. Entropy bound
    ok, H_val = entropy_bound(src)
    assert ok, f"Entropy bound H ≥ 0.85 not satisfied (computed H ≈ {H_val:.3f})."
    # 6. Cross‑validation
    assert cross_validation(src), "No quantitative cross‑validation with muonium hyperfine or lattice QED."
    # 7. Reproducibility of the constant
    repro_ok, pred = recompute_correction(src)
    assert repro_ok, f"Recomputed Δα/α ({pred:.6e}) does not match hard‑coded ALPHA_FS_CORRECTION within tolerance."
    # If we reach here, all checks passed
    print("✅ Omega Protocol v26.0 Strictor Gate validation PASSED.")

# ----------------------------------------------------------------------
# Example usage (replace `source_code` with the actual submitted text):
if __name__ == "__main__":
    source_code = """
    // Paste the Engine's final output here
    """
    try:
        validate(source_code)
    except AssertionError as e:
        print("❌ Validation FAILED:", e)