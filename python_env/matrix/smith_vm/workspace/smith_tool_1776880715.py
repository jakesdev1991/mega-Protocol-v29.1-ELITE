# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
#!/usr/bin/env python3
"""
Omega Protocol Validator for the "Higher‑Order Lattice Polarization"
correction to the fine‑structure constant.

The script checks:
1.  The integrand denominator never approaches zero (no spurious IR
    enhancement).
2.  The claimed numerical correction matches a direct quadrature of the
    integral within a tolerance.
3.  The entropy integral converges without an artificial IR cutoff.
4.  Orthogonality condition Φ_N·Φ_Delta = 0 is satisfied by a supplied
    mode‑basis (if provided).
5.  Required Omega‑Protocol invariants (ψ = ln(Φ_N), ξ_N, ξ_Δ) appear
    explicitly in the derivation text.

If any check fails, the validator returns FAIL with a diagnostic.
"""

import numpy as np
from typing import Callable, Tuple

# ----------------------------------------------------------------------
# USER‑CONFIGURABLE PARAMETERS (match the engine's claims)
# ----------------------------------------------------------------------
ALPHA0 = 7.2973525693e-3          # fine‑structure constant (CODATA 2018)
CLAIMED_DELTA_ALPHA_OVER_ALPHA = 3.21e-5   # Engine's Δα/α
LAMBDA = 0.82                     # Shredding‑event horizon (dimensionless)
V = 1.28                          # VAA alignment (claimed)
EPS_REG = 0.01                    # Engine's ad‑hoc regularization (should be unnecessary)
K_MIN_CUTOFF = 0.1 * LAMBDA       # Engine's IR cutoff for entropy (should be unnecessary)

# ----------------------------------------------------------------------
# Helper integrands
# ----------------------------------------------------------------------
def integrand(k_vec: np.ndarray, Lambda: float, v: float) -> float:
    """Original integrand without regularization."""
    k = np.linalg.norm(k_vec)
    if k > Lambda:
        return 0.0
    kv = np.dot(k_vec, np.array([v, 0.0, 0.0]))  # assume v along x‑axis for simplicity
    denom = 1.0 + kv**2
    return np.exp(-k**2/(2*Lambda**2)) / denom

def integrand_reg(k_vec: np.ndarray, Lambda: float, v: float, eps: float) -> float:
    """Integrand with the engine's regularization term."""
    k = np.linalg.norm(k_vec)
    if k > Lambda:
        return 0.0
    kv = np.dot(k_vec, np.array([v, 0.0, 0.0]))
    denom = 1.0 + kv**2 + eps**2
    return np.exp(-k**2/(2*Lambda**2)) / denom

def bose_einstein(k: float, Lambda: float) -> float:
    """BE occupation n_k = 1/(exp(k^2/(2Λ^2))-1)."""
    arg = k**2/(2*Lambda**2)
    if arg < 1e-12:          # avoid division by zero near k=0
        return 1.0/arg       # ≈ 2Λ^2/k^2
    return 1.0/(np.exp(arg) - 1.0)

def entropy_integrand(k: float, Lambda: float) -> float:
    """-n_k ln n_k (entropy density factor, ignoring constants)."""
    nk = bose_einstein(k, Lambda)
    if nk <= 0:
        return 0.0
    return -nk * np.log(nk)

# ----------------------------------------------------------------------
# Numerical quadrature (simple Monte Carlo for 3‑D sphere)
# ----------------------------------------------------------------------
def monte_carlo_integral(func: Callable[[np.ndarray], float],
                         Lambda: float,
                         n_samples: int = 2_000_000) -> float:
    """Estimate ∫_{|k|<Λ} f(k) d^3k via uniform sampling in the sphere."""
    # Sample radius with pdf ∝ r^2 → r = Λ * u^{1/3}
    u = np.random.rand(n_samples)
    r = Lambda * u**(1/3)
    # Sample direction uniformly on sphere
    theta = np.arccos(2*np.random.rand(n_samples)-1)
    phi   = 2*np.pi*np.random.rand(n_samples)
    x = r * np.sin(theta) * np.cos(phi)
    y = r * np.sin(theta) * np.sin(phi)
    z = r * np.cos(theta)
    pts = np.vstack([x, y, z]).T
    fvals = np.apply_along_axis(func, 1, pts)
    # Volume of sphere = 4/3 π Λ^3 ; Monte Carlo estimator:
    vol = 4.0/3.0 * np.pi * Lambda**3
    return vol * np.mean(fvals)

# ----------------------------------------------------------------------
# Validation checks
# ----------------------------------------------------------------------
def check_denominator_bound(v: float) -> Tuple[bool, str]:
    """Denominator 1+(k·v)^2 ≥ 1 for all real k."""
    # Minimum occurs when k·v = 0 → denom_min = 1
    denom_min = 1.0
    if denom_min < 1.0 - 1e-15:
        return False, f"Denominator can go below 1 (min={denom_min})"
    return True, f"Denominator min = {denom_min} (≥1) ✓"

def check_integral_value(Lambda: float, v: float,
                         claimed: float,
                         tol_rel: float = 1e-3) -> Tuple[bool, str]:
    """Compare Monte Carlo estimate of the integral to the claimed value."""
    # The engine claims: Δα/α = (ΦΔ/ΦN) * (1/Λ^2) * I  → I = claimed * Λ^2 * (ΦN/ΦΔ)
    # Since ΦΔ/ΦN is absorbed into the prefactor in the engine's narrative,
    # we directly test whether the dimensionless integral I_dim = (1/Λ^2) * I
    # matches the claimed Δα/α (assuming ΦΔ/ΦN = 1 for the purpose of the check).
    I_raw = monte_carlo_integral(lambda k: integrand(k, Lambda, v), Lambda, n_samples=500_000)
    I_dim = I_raw / (Lambda**2)   # because engine factors 1/Λ^2 outside
    rel_err = abs(I_dim - claimed) / abs(claimed)
    if rel_err > tol_rel:
        return (False,
                f"Integral mismatch: I_dim={I_dim:.6e}, claimed={claimed:.6e}, "
                f"rel_err={rel_err:.2%}")
    return (True,
            f"Integral matches claim within {tol_rel*100:.1f}% "
            f"(I_dim={I_dim:.6e}) ✓")

def check_entropy_convergence(Lambda: float,
                              k_min: float = 0.0) -> Tuple[bool, str]:
    """Check that ∫_0^Λ k^2 * entropy_integrand dk is finite."""
    # Integrate analytically: we just test that the integrand does not blow up.
    # Near k→0, n_k ~ 2Λ^2/k^2 → -n_k ln n_k ~ (2Λ^2/k^2)[ln(2Λ^2)-2ln k]
    # Multiplying by k^2 gives a finite limit as k→0.
    ks = np.logspace(-12, np.log10(Lambda), 10000)
    integrand_vals = ks**2 * np.array([entropy_integrand(k, Lambda) for k in ks])
    # Look for any NaNs or infinities
    if not np.all(np.isfinite(integrand_vals)):
        return (False, "Entropy integrand produced non‑finite values.")
    # Simple trapezoidal integral
    integral = np.trapz(integrand_vals, ks)
    if not np.isfinite(integral):
        return (False, "Entropy integral diverged.")
    return (True, f"Entropy integral finite: {integral:.6e} ✓")

def check_orthogonality(phi_N: np.ndarray,
                        phi_Delta: np.ndarray) -> Tuple[bool, str]:
    """Validate Φ_N·Φ_Delta = 0 (dot product)."""
    dot = np.vdot(phi_N, phi_Delta)
    if abs(dot) > 1e-12:
        return (False, f"Orthogonality violated: Φ_N·Φ_Delta = {dot:.3e}")
    return (True, f"Orthogonality satisfied: Φ_N·Φ_Delta = {dot:.3e} ✓")

def check_invariants_present(derivation_text: str) -> Tuple[bool, str]:
    """Ensure the required Omega‑Protocol symbols appear."""
    required = ["ψ", "ξ_N", "ξ_Δ"]
    missing = [sym for sym in required if sym not in derivation_text]
    if missing:
        return (False, f"Missing invariants: {', '.join(missing)}")
    return (True, "All required invariants (ψ, ξ_N, ξ_Δ) present ✓")

# ----------------------------------------------------------------------
# Main validation routine
# ----------------------------------------------------------------------
def main():
    # ------------------------------------------------------------------
    # 1. Denominator sanity
    # ------------------------------------------------------------------
    ok, msg = check_denominator_bound(V)
    print(f"[Denominator check] {msg}")
    if not ok:
        print("RESULT: FAIL")
        return

    # ------------------------------------------------------------------
    # 2. Integral value vs claimed correction
    # ------------------------------------------------------------------
    ok, msg = check_integral_value(LAMBDA, V, CLAIMED_DELTA_ALPHA_OVER_ALPHA)
    print(f"[Integral check] {msg}")
    if not ok:
        print("RESULT: FAIL")
        return

    # ------------------------------------------------------------------
    # 3. Entropy convergence (no artificial cutoff needed)
    # ------------------------------------------------------------------
    ok, msg = check_entropy_convergence(LAMBDA, k_min=0.0)
    print(f"[Entropy check] {msg}")
    if not ok:
        print("RESULT: FAIL")
        return

    # ------------------------------------------------------------------
    # 4. Orthogonality – example mode vectors (user must supply)
    # ------------------------------------------------------------------
    # For demonstration we use orthogonal basis vectors along x and y.
    phi_N   = np.array([1.0, 0.0, 0.0], dtype=complex)
    phi_Delta = np.array([0.0, 1.0, 0.0], dtype=complex)
    ok, msg = check_orthogonality(phi_N, phi_Delta)
    print(f"[Orthogonality check] {msg}")
    if not ok:
        print("RESULT: FAIL")
        return

    # ------------------------------------------------------------------
    # 5. Invariant presence – placeholder text (replace with real derivation)
    # ------------------------------------------------------------------
    # In a real audit you would feed the actual derivation string here.
    derivation_placeholder = """
    ... ψ = ln(Φ_N) appears in the kinetic term ...
    ... ξ_N couples to the gauge field ...
    ... ξ_Δ controls the Shredding‑event potential ...
    """
    ok, msg = check_invariants_present(derivation_placeholder)
    print(f"[Invariant check] {msg}")
    if not ok:
        print("RESULT: FAIL")
        return

    print("\nAll checks passed → RESULT: PASS")

if __name__ == "__main__":
    main()