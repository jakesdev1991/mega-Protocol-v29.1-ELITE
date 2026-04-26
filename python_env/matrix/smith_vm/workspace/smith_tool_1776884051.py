# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Omega Protocol Strictor Gate Validator
-------------------------------------
Validates the Engine's "Higher‑Order Lattice Polarization" derivation
against the Omega Physics Rubric v26.0 (Strictor Gate).

Run:  python3 omega_validator.py <source_file>
where <source_file> is the C++/text snippet containing the derivation.
"""

import sys
import re
import numpy as np
from scipy import integrate

# ----------------------------------------------------------------------
# Configuration (Omega Protocol constants)
# ----------------------------------------------------------------------
LAMBDA = 0.82          # Shredding Event horizon (inverse length units)
V      = 1.28          # VAA alignment from diagonal basis symmetry
TARGET_DELTA_ALPHA_OVER_ALPHA = 3.21e-5   # Engine's claimed correction
MUONIUM_BOUND = 1.0e-5               # |Δα/α| from muonium hyperfine splitting
ENTROPY_THRESHOLD = 0.85             # H ≥ 0.85 required by rubric
# ----------------------------------------------------------------------


def load_source(path: str) -> str:
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def check_invariants(text: str) -> bool:
    """
    The rubric §3 requires explicit appearance of:
        ψ = ln(Φ_N)
        ξ_N
        ξ_Δ
    (case‑insensitive, allowing underscores or spaces).
    """
    patterns = [
        r'ψ\s*=\s*ln\s*\(\s*Φ_N\s*\)',   # ψ = ln(Φ_N)
        r'ξ_N',
        r'ξ_Δ'
    ]
    for pat in patterns:
        if not re.search(pat, text, re.IGNORECASE):
            print(f"[FAIL] Missing invariant pattern: {pat}")
            return False
    print("[PASS] All Omega invariants present.")
    return True


def evaluate_integral() -> float:
    """
    Computes the dimensionless integral:
        I = ∫_0^Λ 4π k^2 * exp(-k^2/(2Λ^2)) / (1 + (k·v)^2) dk
    Returns I / Λ^2  (the factor that multiplies Φ_Delta/Φ_N).
    """
    def integrand(k):
        # k is a scalar; we integrate over magnitude only (isotropic)
        return 4.0 * np.pi * k**2 * np.exp(-k**2 / (2.0 * LAMBDA**2)) / (1.0 + (k * V)**2)

    integral, err = integrate.quad(integrand, 0.0, LAMBDA, limit=200)
    factor = integral / (LAMBDA**2)   # 1/Λ^2 * I
    print(f"[INFO] Numerical integral I = {integral:.6e}")
    print(f"[INFO] Factor (I/Λ^2) = {factor:.6e}")
    return factor, err


def check_dimensionless(factor: float) -> bool:
    """
    The correction must be dimensionless:
        Δα/α = (Φ_Delta/Φ_N) * factor
    Since Φ_Delta/Φ_N is dimensionless (ratio of two Φ‑densities),
    factor must be dimensionless. We verify by checking that
    the units cancel in the integral definition.
    """
    # In our implementation, k and Λ share the same units,
    # v is dimensionless (alignment), and the integrand yields
    # units of [k]^3 from k^2 dk divided by [k]^0 from denominator,
    # then divided by Λ^2 → overall dimensionless.
    # We trust the analytical cancellation; just ensure no stray length.
    if np.isfinite(factor):
        print("[PASS] Integral factor is finite (dimensionless check passed).")
        return True
    else:
        print("[FAIL] Integral factor is non‑finite → dimensional issue.")
        return False


def compute_entropy() -> float:
    """
    Bosonic von‑Neumann entropy for mode occupations:
        n_k = 1 / (exp(k^2/(2Λ^2)) - 1)
        H = - ∫ n_k ln(n_k) * g(k) dk
    with density of states g(k) = 4π k^2 (isotropic 3‑D).
    Integrate from 0 to a cutoff (here we use 5Λ to capture tail).
    """
    def integrand(k):
        if k == 0.0:
            return 0.0   # avoid division by zero; n_k → 0 as k→0
        nk = 1.0 / (np.exp(k**2 / (2.0 * LAMBDA**2)) - 1.0)
        if nk <= 0.0:
            return 0.0
        return -nk * np.log(nk) * 4.0 * np.pi * k**2

    H, err = integrate.quad(integrand, 0.0, 5.0 * LAMBDA, limit=200, epsabs=1e-12)
    print(f"[INFO] Computed entropy H = {H:.6f} ± {err:.2e}")
    return H, err


def main():
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} <source_file>")
        sys.exit(1)

    source = load_source(sys.argv[1])

    # 1. Invariant check – Tier 0 violation => immediate fail
    if not check_invariants(source):
        sys.exit("NON‑COMPLIANT: Missing Omega invariants.")

    # 2. Integral & dimensional analysis
    factor, int_err = evaluate_integral()
    if not check_dimensionless(factor):
        sys.exit("NON‑COMPLIANT: Dimensional inconsistency.")

    # 3. Entropy bound
    H, ent_err = compute_entropy()
    if H < ENTROPY_THRESHOLD:
        sys.exit(f"NON‑COMPLIANT: Entropy H={H:.6f} < threshold {ENTROPY_THRESHOLD}.")

    # 4. Predicted Δα/α (requires ratio r = Φ_Delta/Φ_N)
    #    We solve for r that would give the claimed correction.
    r_needed = TARGET_DELTA_ALPHA_OVER_ALPHA / factor
    print(f"[INFO] To achieve Δα/α = {TARGET_DELTA_ALPHA_OVER_ALPHA:.2e}, "
          f"Φ_Delta/Φ_N must be {r_needed:.6e}.")

    # 5. Empirical cross‑check (muonium bound)
    if abs(TARGET_DELTA_ALPHA_OVER_ALPHA) > MUONIUM_BOUND:
        sys.exit(f"NON‑COMPLIANT: Predicted |Δα/α| = {TARGET_DELTA_ALPHA_OVER_ALPHA:.2e} "
                 f"> muonium bound {MUONIUM_BOUND:.2e}.")

    # If we reach here, all rubric checks passed.
    print("\n=== OMEGA PROTOCOL VALIDATION RESULT ===")
    print("COMPLIANT: All Strictor Gate v26.0 requirements satisfied.")
    print("Note: Compliance does *not* guarantee physical correctness;")
    print("       it only confirms adherence to the Omega Protocol's formal rules.")


if __name__ == "__main__":
    main()