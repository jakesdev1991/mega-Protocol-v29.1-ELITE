# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
# --------------------------------------------------------------
# Omega Protocol Invariant & Mathematical Consistency Validator
# --------------------------------------------------------------
# This script checks a candidate derivation (provided as a string)
# for:
#   1. Presence of the required Omega‑Protocol invariants:
#        ψ = ln(Φ_N),   ξ_N,   ξ_Δ
#   2. Dimensional consistency of the claimed correction:
#        Δα/α = (Φ_Δ/Φ_N) * (1/Λ²) * I
#      where I = ∫_{k<Λ} e^{-k²/(2Λ²)} / (1+(k·v)²) d³k
#   3. Numerical magnitude of I (and thus Δα/α) for the
#      Engine‑quoted parameters Λ = 0.82, v = 1.28.
#   4. Entropy bound H ≥ 0.85 for the IR‑mode occupation
#      n_k = 1/(exp(k²/(2Λ²))-1) (with a simple IR cutoff).
#
# The script does **not** prove correctness; it only flags
# obvious violations of the rubric and gross numerical mismatches.
# --------------------------------------------------------------

import numpy as np
import re

# ------------------------------------------------------------------
# Helper: numeric evaluation of the 3‑D integral I
# ------------------------------------------------------------------
def compute_integral(Lambda: float, v: float, samples: int = 2_000_000) -> float:
    """
    Monte‑Carlo evaluation of
        I = ∫_{|k|<Λ} exp(-k²/(2Λ²)) / (1 + (k·v)²) d³k
    using isotropic sampling inside a sphere of radius Λ.
    """
    # generate random points uniformly in the sphere
    # radius distribution: r = Λ * u^{1/3}, u∈[0,1]
    u = np.random.rand(samples)
    r = Lambda * u ** (1.0/3.0)
    # random direction on unit sphere
    z = np.random.uniform(-1, 1, samples)
    phi = np.random.uniform(0, 2*np.pi, samples)
    x = r * np.sqrt(1 - z**2) * np.cos(phi)
    y = r * np.sqrt(1 - z**2) * np.sin(phi)
    z = r * z

    k2 = x*x + y*y + z*z
    kv = x*v[0] + y*v[1] + z*v[2]   # v is taken as a scalar magnitude along a fixed axis
    # we align v with the z‑axis without loss of generality (dot product depends only on |k|·|v|·cosθ)
    # => (k·v)² = k² * v² * cos²θ = k² * v² * ẑ² ; but we already sampled isotropic,
    #    so we can simply use (k·v)² = k² * v² * (z_component/|k|)² = v² * z²
    kv_sq = (v**2) * (z**2)

    integrand = np.exp(-k2/(2*Lambda**2)) / (1.0 + kv_sq)
    # volume element: d³k = 4π r² dr ; MC weight = (Volume of sphere)/samples
    volume_sphere = (4.0/3.0) * np.pi * Lambda**3
    I_est = volume_sphere * np.mean(integrand)
    return I_est, volume_sphere

# ------------------------------------------------------------------
# Helper: entropy estimate for IR modes (with simple IR cutoff)
# ------------------------------------------------------------------
def entropy_estimate(Lambda: float, cutoff_ratio: float = 1e-3, samples: int = 1_000_000) -> float:
    """
    Approximate the von‑Neumann entropy
        H = -∫ n_k ln n_k d³k / (2π)³
    for n_k = 1/(exp(k²/(2Λ²))-1) .
    An IR cutoff k_min = cutoff_ratio * Λ removes the 1/k² divergence.
    """
    k_min = cutoff_ratio * Lambda
    # sample k uniformly in [k_min, Λ] with weight 4πk²
    u = np.random.rand(samples)
    k = k_min + (Lambda - k_min) * u
    # weight factor for spherical shell: 4πk² dk
    weight = 4.0 * np.pi * k**2 * (Lambda - k_min)   # constant factor times dk approximated by sample width
    nk = 1.0 / (np.exp(k**2/(2*Lambda**2)) - 1.0)
    # avoid log(0) for huge nk (should not happen with cutoff)
    integrand = -nk * np.log(nk + 1e-30)
    H_est = np.mean(integrand * weight) / (2.0*np.pi)**3   # divide by (2π)³ as per standard phase‑space measure
    return H_est

# ------------------------------------------------------------------
# Main validation routine
# ------------------------------------------------------------------
def validate_derivation(derivation_text: str) -> dict:
    """
    Returns a dictionary with flags and numeric results.
    """
    report = {}

    # 1. Invariant presence (case‑insensitive, allow underscores)
    inv_patterns = {
        r'\\bpsi\\b': 'ψ',
        r'\\bxi[ _]?N\\b': 'ξ_N',
        r'\\bxi[ _]?Δ\\b': 'ξ_Δ',
        r'\\bxi[ _]?Delta\\b': 'ξ_Δ'   # allow written form
    }
    found = {}
    for pat, name in inv_patterns.items():
        if re.search(pat, derivation_text, flags=re.IGNORECASE):
            found[name] = True
        else:
            found[name] = False
    report['invariants_found'] = found
    report['all_invariants_present'] = all(found.values())

    # 2. Extract claimed parameters (look for typical assignments)
    #    We search for patterns like Lambda = 0.82 , v = 1.28
    def grab_float(name):
        m = re.search(rf'{name}\s*=\s*([0-9]*\.?[0-9]+(?:[eE][+-]?[0-9]+)?)', derivation_text, re.IGNORECASE)
        return float(m.group(1)) if m else None

    Lambda = grab_float(r'\\bLambda\\b')
    v_val  = grab_float(r'\\bv\\b')
    report['Lambda'] = Lambda
    report['v'] = v_val

    # 3. Compute integral I and compare to implied constant
    if Lambda is not None and v_val is not None:
        I, vol = compute_integral(Lambda, v_val, samples=500_000)
        # The Engine claims: Δα/α ≈ (Φ_Δ/Φ_N) * 0.0000321
        # => (1/Λ²) * I should equal 0.0000321 (assuming Φ_Δ/Φ_N = 1 for the check)
        implied = 0.0000321
        derived = I / (Lambda**2)
        report['integral_I'] = I
        report['derived_(1/Λ²)*I'] = derived
        report['implied_constant'] = implied
        report['relative_error'] = abs(derived - implied) / implied if implied != 0 else np.inf
        report['integral_ok'] = report['relative_error'] < 0.20   # 20% tolerance given crude MC
    else:
        report['integral_I'] = None
        report['derived_(1/Λ²)*I'] = None
        report['integral_ok'] = False

    # 4. Entropy check
    if Lambda is not None:
        H = entropy_estimate(Lambda, cutoff_ratio=1e-4, samples=400_000)
        report['entropy_H'] = H
        report['entropy_ok'] = H >= 0.85
    else:
        report['entropy_H'] = None
        report['entropy_ok'] = False

    # Overall compliance (very rough)
    report['overall_pass'] = (
        report['all_invariants_present'] and
        report.get('integral_ok', False) and
        report.get('entropy_ok', False)
    )
    return report

# ------------------------------------------------------------------
# Example usage (replace the string with the Engine's *corrected* derivation)
# ------------------------------------------------------------------
if __name__ == "__main__":
    # Placeholder: the Engine should supply a corrected derivation here.
    # For demonstration we use a minimal mock that includes the invariants.
    mock_derivation = """
    // Omega‑Protocol compliant derivation
    const double psi   = log(Phi_N);          // ψ = ln(Φ_N)
    const double xi_N  = 1.0;                 // stiffness invariant
    const double xi_D  = 0.5;                 // ξ_Δ invariant
    const double Lambda = 0.82;
    const double v      = 1.28;
    // ... integral evaluation omitted for brevity ...
    // Entropy calculation with IR cutoff ensures H >= 0.85
    """
    result = validate_derivation(mock_derivation)
    print("Validation Report:")
    for k, v in result.items():
        print(f"{k:30}: {v}")
    # If overall_pass is True, the derivation satisfies the basic rubric checks.
    # Otherwise, the Engine must revise and resubmit.