# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
#!/usr/bin/env python3
"""
Omega Protocol Invariant Validator for the HSA Informational Jerk Analysis
-----------------------------------------------------------------------
This script checks the mathematical soundness and rubric compliance of the
analysis described in the Engine output.  It is deliberately minimal: it
does not require external libraries beyond the Python standard library.

Usage:
    >>> from omega_validator import validate_analysis
    >>> result = validate_analysis(state_dict)
    >>> print(result["status"])
    PASS
    >>> print(result["messages"])
    [...]
"""

import math
from typing import Dict, Any, Tuple, List

# ----------------------------------------------------------------------
# Helper functions
# ----------------------------------------------------------------------
def _is_close(a: float, b: float, rel_tol: float = 1e-9, abs_tol: float = 0.0) -> bool:
    return math.isclose(a, b, rel_tol=rel_tol, abs_tol=abs_tol)

def _variance(data: List[float]) -> float:
    if not data:
        return 0.0
    mu = sum(data) / len(data)
    return sum((x - mu) ** 2 for x in data) / len(data)

def _excess_kurtosis(data: List[float]) -> float:
    """Return excess kurtosis (kurtosis - 3). Requires at least 4 samples."""
    n = len(data)
    if n < 4:
        raise ValueError("need at least 4 samples for kurtosis")
    mu = sum(data) / n
    var = sum((x - mu) ** 2 for x in data) / n
    if var == 0.0:
        return 0.0
    fourth = sum((x - mu) ** 4 for x in data) / n
    kurt = fourth / (var * var)
    return kurt - 3.0

# ----------------------------------------------------------------------
# Core validation
# ----------------------------------------------------------------------
def validate_analysis(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Parameters
    ----------
    state : dict
        Must contain the following keys (values can be placeholder objects;
        the validator only checks for presence and basic mathematical
        properties):
        - 'psi'          : callable(i, j, t) -> coherence value
        - 'Phi_N'        : float or callable(t) -> consensus field
        - 'Phi_Delta'    : float or callable(t) -> novelty field
        - 'xi_N'         : float or callable(t) -> radial correlation length
        - 'xi_Delta'     : float or callable(t) -> poloidal correlation length
        - 'H'            : float or callable(t) -> entropy
        - 'j'            : float or callable(t) -> informational jerk
        - 'S_j'          : float or callable(t, T) -> jerk stability metric
        - 'Q_depth'      : float or callable(t) -> queue depth
        - 'P_fault'      : float or callable(t) -> page‑fault rate
        - 'jerk_samples' : list of recent jerk values (used for metric test)
        - 'sigma0_sq'    : float, expected jerk variance under normal op.
        - 'xi_Delta_def' : optional explicit definition (see below)

    Returns
    -------
    dict
        {
            "status": "PASS" | "FAIL",
            "messages": list of strings explaining each check
        }
    """
    msgs: List[str] = []
    fail = False

    # ------------------------------------------------------------------
    # 1. Presence of required scalars
    # ------------------------------------------------------------------
    required = ['Phi_N', 'Phi_Delta', 'xi_N', 'xi_Delta', 'H',
                'j', 'S_j', 'Q_depth', 'P_fault']
    for key in required:
        if key not in state:
            msgs.append(f"MISSING: required state component '{key}' not found")
            fail = True

    # ------------------------------------------------------------------
    # 2. Coherence field definition (structural check)
    # ------------------------------------------------------------------
    if 'psi' not in state or not callable(state['psi']):
        msgs.append("INVALID: coherence field ψ(i,j,t) must be a callable")
        fail = True
    else:
        # spot‑check a few arbitrary indices to ensure it returns a number
        try:
            val = state['psi'](0, 0, 0.0)
            if not isinstance(val, (int, float)):
                raise TypeError
        except Exception as e:
            msgs.append(f"INVALID: ψ evaluation failed ({e})")
            fail = True

    # ------------------------------------------------------------------
    # 3. Entropy – must be Shannon of a normalized distribution
    # ------------------------------------------------------------------
    if 'H' in state:
        # We cannot compute the full distribution here, but we can verify
        # that the claimed entropy is non‑negative (Shannon entropy ≥ 0)
        H_val = state['H'] if not callable(state['H']) else state['H'](0.0)
        if not isinstance(H_val, (int, float)) or H_val < -1e-12:  # allow tiny neg due to fp
            msgs.append(f"INVALID: entropy H(t) = {H_val} must be ≥ 0")
            fail = True
        else:
            msgs.append(f"OK: entropy H(t) = {H_val:.4f} (≥0)")

    # ------------------------------------------------------------------
    # 4. Invariants ξ_N and ξ_Δ
    # ------------------------------------------------------------------
    # ξ_N: should be positive (length scale)
    if 'xi_N' in state:
        xiN = state['xi_N'] if not callable(state['xi_N']) else state['xi_N'](0.0)
        if not isinstance(xiN, (int, float)) or xiN <= 0:
            msgs.append(f"INVALID: ξ_N = {xiN} must be > 0")
            fail = True
        else:
            msgs.append(f"OK: ξ_N = {xiN:.4f} (>0)")

    # ξ_Δ: require an explicit definition; if missing, flag.
    if 'xi_Delta' in state:
        xiD = state['xi_Delta'] if not callable(state['xi_Delta']) else state['xi_Delta'](0.0)
        if not isinstance(xiD, (int, float)):
            msgs.append("INVALID: ξ_Δ must be a real number")
            fail = True
        else:
            msgs.append(f"OK: ξ_Δ = {xiD:.4f}")

        # Check for explicit definition supplied by the user
        if 'xi_Delta_def' in state and state['xi_Delta_def']:
            # Expect a string describing the formula; we just verify it's present.
            def_str = state['xi_Delta_def']
            if not isinstance(def_str, str) or len(def_str.strip()) == 0:
                msgs.append("WARNING: ξ_Δ definition supplied but empty/invalid")
            else:
                msgs.append(f"INFO: ξ_Δ definition provided: '{def_str[:60]}...'")
        else:
            msgs.append("FAIL: ξ_Δ lacks an explicit mathematical definition (required by rubric)")
            fail = True

    # ------------------------------------------------------------------
    # 5. Jerk calculation – verify stencil coefficients (5‑point central)
    # ------------------------------------------------------------------
    if 'j' in state:
        # We cannot recompute j without Φ_N(t) history, but we can at least
        # ensure the metric uses the correct stencil if the user supplies it.
        # For simplicity, we assume the user has provided a callable 'j_stencil'
        # that returns the stencil coefficients; if missing we just note.
        if 'j_stencil' in state:
            coeffs = state['j_stencil']
            expected = [-1, 2, -2, 1]  # numerator coefficients for 2Δτ denominator
            if not isinstance(coeffs, (list, tuple)) or len(coeffs) != 4:
                msgs.append("INVALID: j_stencil must be a 4‑element list/tuple")
                fail = True
            else:
                if not all(_is_close(c, e) for c, e in zip(coeffs, expected)):
                    msgs.append(f"INVALID: j_stencil coefficients {coeffs} do not match 5‑point central stencil")
                    fail = True
                else:
                    msgs.append("OK: jerk stencil matches 5‑point central formula")
        else:
            msgs.append("INFO: no custom j_stencil supplied; assuming correct implementation")

    # ------------------------------------------------------------------
    # 6. Jerk‑stability metric – rubric compliance test
    # ------------------------------------------------------------------
    if 'S_j' in state and 'jerk_samples' in state and 'sigma0_sq' in state:
        # Grab a function or scalar for S_j
        Sj = state['S_j']
        samples = state['jerk_samples']
        sigma0_sq = state['sigma0_sq']

        # If S_j is callable, evaluate it with the supplied samples & sigma0_sq
        if callable(Sj):
            try:
                Sj_val = Sj(samples, sigma0_sq) if isinstance(samples, list) else Sj(0.0, sigma0_sq)
            except Exception as e:
                msgs.append(f"INVALID: S_j evaluation failed ({e})")
                fail = True
                Sj_val = None
        else:
            Sj_val = Sj  # assume pre‑computed scalar

        if Sj_val is not None:
            # Test 1: constant jerk (zero variance) → S_j should be 1
            const_j = [5.0] * len(samples)  # arbitrary constant
            Sj_const = Sj(const_j, sigma0_sq) if callable(Sj) else Sj_val
            if not _is_close(Sj_const, 1.0, rel_tol=1e-6):
                msgs.append(f"FAIL: S_j for constant jerk = {Sj_const:.6f} (expected ≈1.0)")
                fail = True
            else:
                msgs.append("OK: S_j → 1 for constant jerk")

            # Test 2: Gaussian jerk with variance = sigma0_sq → S_j should be 1
            # Generate a Gaussian sample with the target variance
            import random
            random.seed(0)
            gauss_samples = [random.gauss(0.0, math.sqrt(sigma0_sq)) for _ in range(max(50, len(samples)))]
            Sj_gauss = Sj(gauss_samples, sigma0_sq) if callable(Sj) else Sj_val
            if not _is_close(Sj_gauss, 1.0, rel_tol=1e-6):
                msgs.append(f"FAIL: S_j for Gaussian jerk (var=σ₀²) = {Sj_gauss:.6f} (expected ≈1.0)")
                fail = True
            else:
                msgs.append("OK: S_j → 1 for Gaussian jerk with variance σ₀²")

            # Test 3: Heavy‑tailed (e.g., Laplace) jerk → S_j < 1
            laplace_samples = [random.laplace(0.0, math.sqrt(sigma0_sq/2.0)) for _ in range(max(50, len(samples)))]
            Sj_laplace = Sj(laplace_samples, sigma0_sq) if callable(Sj) else Sj_val
            if Sj_laplace >= 1.0:
                msgs.append(f"FAIL: S_j for heavy‑tailed jerk = {Sj_laplace:.6f} (should be <1)")
                fail = True
            else:
                msgs.append(f"OK: S_j < 1 for heavy‑tailed jerk (value={Sj_laplace:.6f})")
    else:
        msgs.append("INFO: insufficient data to test jerk‑stability metric")

    # ------------------------------------------------------------------
    # 7. MPC‑Ω cost function structure (basic sanity)
    # ------------------------------------------------------------------
    if 'cost_function' in state:
        cf = state['cost_function']
        if not isinstance(cf, str):
            msgs.append("WARNING: cost_function provided but not a string; cannot verify form")
        else:
            # Very loose check: should contain terms (1‑S_j)^2, α H^2, λ P^2
            needed = ["(1 - S_j)", "H**2", "P**2"]
            missing = [term for term in needed if term not in cf]
            if missing:
                msgs.append(f"WARNING: cost_function may be missing terms: {missing}")
            else:
                msgs.append("OK: cost_function contains expected quadratic terms")
    else:
        msgs.append("INFO: no cost_function supplied for structural check")

    # ------------------------------------------------------------------
    # Final verdict
    # ------------------------------------------------------------------
    status = "PASS" if not fail else "FAIL"
    return {"status": status, "messages": msgs}


# ----------------------------------------------------------------------
# Example usage (can be removed when imported as a module)
# ----------------------------------------------------------------------
if __name__ == "__main__":
    # Mock state for a quick sanity test
    import random
    random.seed(42)

    def dummy_psi(i, j, t):
        return math.exp(-abs(i - j) * 0.1)  # placeholder

    def dummy_Phi_N(t):
        return 0.8

    def dummy_Phi_Delta(t):
        return 0.1

    def dummy_xi_N(t):
        return 2.5

    def dummy_xi_Delta(t):
        return 1.3  # placeholder; definition supplied below

    def dummy_H(t):
        return 0.42

    def dummy_j(t):
        return 0.0

    def dummy_Sj(samples, sigma0_sq):
        # Example of a rubric‑compliant metric: exponential of negative excess kurtosis
        ek = _excess_kurtosis(samples)
        return math.exp(-max(0.0, ek))  # 1 for Gaussian or platykurtic, <1 for leptokurtic

    state = {
        "psi": dummy_psi,
        "Phi_N": dummy_Phi_N,
        "Phi_Delta": dummy_Phi_Delta,
        "xi_N": dummy_xi_N,
        "xi_Delta": dummy_xi_Delta,
        "xi_Delta_def": "ratio of variance along CPU‑GPU axis to variance within GPU‑GPU axis",
        "H": dummy_H,
        "j": dummy_j,
        "S_j": dummy_Sj,
        "Q_depth": lambda t: 10.0,
        "P_fault": lambda t: 0.001,
        "jerk_samples": [random.gauss(0, 0.05) for _ in range(30)],  # ~Gaussian
        "sigma0_sq": 0.0025,
        "cost_function": "(1 - S_j)^2 + alpha * H**2 + lambda * P**2",
        "j_stencil": [-1, 2, -2, 1]  # correct 5‑point central stencil numerator
    }

    result = validate_analysis(state)
    print("=== Omega Protocol Validation ===")
    print("Status:", result["status"])
    for m in result["messages"]:
        print("-", m)