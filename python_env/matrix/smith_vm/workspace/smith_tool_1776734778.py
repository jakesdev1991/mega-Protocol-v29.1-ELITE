# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Omega Protocol Validator – Informational Jerk Stability for Linux HSA Unified Memory
--------------------------------------------------------------------------------
This script audits the mathematical soundness of the thought:
  * Verifies the third‑order finite‑difference estimator for 𝒥ᵢ.
  * Computes σ²𝒥ᵢ and compares to the physics‑derived threshold Θ.
  * Checks that the stiffness invariants ξₙ, ξΔ and ψ obey their definitions.
  * Raises AssertionError on any invariant violation (protocol enforcement).

Usage:
    python3 omega_validator.py   # runs a self‑contained synthetic test
"""

import numpy as np

# ----------------------------------------------------------------------
# Helper functions
# ----------------------------------------------------------------------
def third_order_fdjerk(S_h, dt=1.0):
    """
    Compute Informational Jerk 𝒥ᵢ[t] ≈ d³S_h/dt³ using the stencil:
        𝒥ᵢ[n] = S_h[n] - 3*S_h[n-1] + 3*S_h[n-2] - S_h[n-3]
    Returns an array aligned with the original time series (first three
    entries set to NaN because the stencil needs four points).
    """
    S = np.asarray(S_h, dtype=float)
    jerk = np.full_like(S, np.nan)
    jerk[3:] = S[3:] - 3 * S[2:-1] + 3 * S[1:-2] - S[0:-3]
    return jerk / dt**3  # scale by dt³ for physical units


def variance_over_window(arr, window):
    """
    Sliding‑window variance (population variance) of `arr`.
    Returns an array same length as `arr` with NaN where window not full.
    """
    arr = np.asarray(arr, dtype=float)
    var = np.full_like(arr, np.nan)
    for i in range(window - 1, len(arr)):
        segment = arr[i - window + 1 : i + 1]
        var[i] = np.nanvar(segment)
    return var


def stiffness_invariants(Phi_N, Phi_Delta, lam, I0):
    """
    Compute ξₙ⁻² and ξΔ⁻² from the definitions:
        ξₙ⁻² = λ (3Φₙ² + ΦΔ² - I0²)
        ξΔ⁻² = λ (Φₙ² + 3ΦΔ² - I0²)
    Returns (xi_N, xi_Delta) where xi = 1 / sqrt(inv_sq) if inv_sq>0 else NaN.
    """
    inv_N_sq = lam * (3 * Phi_N**2 + Phi_Delta**2 - I0**2)
    inv_D_sq = lam * (Phi_N**2 + 3 * Phi_Delta**2 - I0**2)

    xi_N = np.where(inv_N_sq > 0, 1.0 / np.sqrt(inv_N_sq), np.nan)
    xi_D = np.where(inv_D_sq > 0, 1.0 / np.sqrt(inv_D_sq), np.nan)
    return xi_N, xi_D


def metric_coupling(Phi_N, I0):
    """ψ = ln(Φₙ / I₀)"""
    return np.log(Phi_N / I0)


def jerk_threshold(lam, I0, g_Delta):
    """
    Θ = (λ I0² / 4π) * (1 + 3 gΔ² / 4π)
    """
    return (lam * I0**2) / (4 * np.pi) * (1 + 3 * g_Delta**2 / (4 * np.pi))


# ----------------------------------------------------------------------
# Synthetic data generation (for self‑test)
# ----------------------------------------------------------------------
def synthetic_Sh(t, A=10.0, w=0.1, noise_std=0.02):
    """Sₕ(t) = A + sin(w t) + Gaussian noise."""
    return A + np.sin(w * t) + np.random.normal(0, noise_std, size=t.shape)


# ----------------------------------------------------------------------
# Main validation routine
# ----------------------------------------------------------------------
def main():
    # Simulation parameters
    T_total = 200.0          # total time (arb. units)
    dt = 0.5                 # sampling interval
    t = np.arange(0, T_total, dt)
    N = len(t)

    # Generate entropy stream
    np.random.seed(42)       # reproducibility
    S_h = synthetic_Sh(t)

    # ---- 1. Verify Jerk estimator ----
    jerk = third_order_fdjerk(S_h, dt)

    # Analytic jerk for the noise‑free sinusoid part:
    # S_h_ideal = A + sin(w t) => d³S_h/dt³ = -w³ cos(w t)
    S_h_ideal = 10.0 + np.sin(0.1 * t)
    jerk_analytic = -0.1**3 * np.cos(0.1 * t)   # -0.001 * cos(0.1 t)

    # Compare where both are defined (ignore first three points & noise)
    mask = ~np.isnan(jerk) & (np.abs(jerk_analytic) > 1e-12)
    rmse = np.sqrt(np.mean((jerk[mask] - jerk_analytic[mask])**2))
    assert rmse < 0.02, f"Jerk estimator RMSE too high: {rmse:.6f}"
    print(f"[OK] Jerk estimator RMSE = {rmse:.6f} (threshold 0.02)")

    # ---- 2. Stability test (variance vs threshold) ----
    window = 20  # number of samples over which variance is evaluated
    var_jerk = variance_over_window(jerk, window)

    # Example Omega‑Protocol parameters (could be extracted from profiling)
    lam = 0.05          # λ  (coupling of the double‑well potential)
    I0 = 10.0           # reference information content (bits)
    g_Delta = 0.3       # Archive‑mode coupling

    Theta = jerk_threshold(lam, I0, g_Delta)
    print(f"[INFO] Jerk variance threshold Θ = {Theta:.6e}")

    # Determine stability: system is stable if *all* variance samples < Θ
    stable = np.all(var_jerk[~np.isnan(var_jerk)] < Theta)
    if stable:
        print("[PASS] σ²𝒥ᵢ < Θ for entire window → Informational Jerk stable.")
    else:
        # Identify first violating index for debugging
        viol = np.where(var_jerk >= Theta)[0]
        if viol.size:
            idx = viol[0]
            print(
                f"[FAIL] σ²𝒥ᵢ[{idx}] = {var_jerk[idx]:.6e} ≥ Θ ({Theta:.6e})"
                " → Potential Shredding Event."
            )
        else:
            print("[FAIL] Variance check failed (all NaN?).")
    # Enforce the invariant: if unstable, raise AssertionError (protocol violation)
    assert stable, "Omega Protocol violation: Informational Jerk unbounded."

    # ---- 3. Verify stiffness invariants & metric coupling ----
    # For demonstration, construct plausible mode amplitudes from I(t)
    # Let I(t) = S_h(t) (information content approximated by entropy)
    I_t = S_h  # placeholder; in reality I(t) would be measured directly
    Phi_N = I_t * 0.6   # arbitrary scaling to ensure positivity
    Phi_Delta = I_t * 0.4

    xi_N, xi_Delta = stiffness_invariants(Phi_N, Phi_Delta, lam, I0)
    psi = metric_coupling(Phi_N, I0)

    # Check that the defining relations hold (within tolerance)
    inv_N_sq_check = lam * (3 * Phi_N**2 + Phi_Delta**2 - I0**2)
    inv_D_sq_check = lam * (Phi_N**2 + 3 * Phi_Delta**2 - I0**2)

    tol = 1e-10
    assert np.allclose(
        1.0 / xi_N**2, inv_N_sq_check, rtol=0, atol=tol
    ), "ξₙ invariant mismatch"
    assert np.allclose(
        1.0 / xi_Delta**2, inv_D_sq_check, rtol=0, atol=tol
    ), "ξΔ invariant mismatch"
    assert np.allclose(psi, np.log(Phi_N / I0), rtol=0, atol=tol), "ψ definition mismatch"

    print("[PASS] Stiffness invariants and metric coupling satisfy Omega definitions.")

    # ---- 4. Φ‑density impact (qualitative) ----
    # Short‑term dip: cost of computing S_h and 𝒥ᵢ
    # Long‑term gain: prevention of shredding (quantified by avoided variance spikes)
    # We simply report the variance reduction factor if we were to clamp jerk.
    jerk_clipped = np.clip(jerk, -np.sqrt(Theta), np.sqrt(Theta))
    var_clipped = variance_over_window(jerk_clipped, window)
    reduction = 1.0 - np.nanmean(var_clipped) / np.nanmean(var_jerk)
    print(
        f"[INFO] Hypothetical jerk clipping reduces variance by {reduction*100:.1f}% "
        "(proxy for long‑term Φ gain)."
    )

    print("\n=== Omega Protocol Validation Completed Successfully ===")


if __name__ == "__main__":
    main()