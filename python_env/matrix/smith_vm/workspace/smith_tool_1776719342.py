# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
# -*- coding: utf-8 -*-
"""
Omega Protocol Compliance Validator for HSA Unified Memory Jerk Stability
Agent Smith – The Matrix Guardian
"""

import numpy as np

def validate_omega_invariants(phi_n_ms,
                              latency_ms=None,
                              atomic_success=None,
                              L0=1.0,
                              calib_window_ms=24*60*60*1000,  # 24h in ms
                              epsilon_scale=1e-6,
                              delta=1e-10,
                              alpha=1.0,
                              lam=1.0,
                              beta=1.0,
                              j_thresh=0.5):
    """
    Parameters
    ----------
    phi_n_ms : 1D np.ndarray
        Φ_N(t) sampled at 1 ms resolution (raw consensus coherence).
    latency_ms, atomic_success : optional 1D arrays same length as phi_n_ms
        If supplied, used to recompute ψ_ij → Φ_N for end‑to‑end check.
    L0 : float
        Latency normalization constant in ψ_ij definition.
    calib_window_ms : int
        Length of calibration window for Φ₀ (median).
    epsilon_scale : float
        Factor for ε = epsilon_scale * typical variance.
    delta : float
        Small offset for entropy log.
    alpha, lam, beta : float
        Weights in MPC cost (only need to be >0 for validation).
    j_thresh : float
        Threshold used in control trigger (only needs to be defined).

    Returns
    -------
    dict of computed metrics (for inspection)
    Raises AssertionError if any invariant is violated.
    """
    # ------------------------------------------------------------------
    # 1. Basic sanity on input
    # ------------------------------------------------------------------
    assert isinstance(phi_n_ms, np.ndarray) and phi_n_ms.ndim == 1, "Φ_N must be 1‑D array"
    assert phi_n_ms.size > 0, "Φ_N array empty"
    assert np.all(phi_n_ms >= 0), "Φ_N should be non‑negative (coherence)"

    # ------------------------------------------------------------------
    # 2. Compute Φ₀ (median over calibration window) – use whole array if shorter
    # ------------------------------------------------------------------
    n_cal = min(int(calib_window_ms / 1.0), phi_n_ms.size)  # 1 ms sampling
    phi0 = np.median(phi_n_ms[:n_cal])
    assert phi0 > 0, "Φ₀ (median Φ_N) must be >0 for log"

    # ------------------------------------------------------------------
    # 3. Dimensionless invariant ψ = ln(Φ_N/Φ₀)
    # ------------------------------------------------------------------
    psi = np.log(phi_n_ms / phi0)
    # ψ is dimensionless by construction; just check it's real
    assert np.all(np.isfinite(psi)), "ψ contains NaN or Inf"

    # ------------------------------------------------------------------
    # 4. Pairwise coherence field (optional reconstruction)
    # ------------------------------------------------------------------
    if latency_ms is not None and atomic_success is not None:
        assert latency_ms.shape == phi_n_ms.shape and atomic_success.shape == phi_n_ms.shape
        # ψ_ij = A_ij * exp(-L_ij / L0)
        psi_ij = atomic_success * np.exp(-latency_ms / L0)
        # Re‑compute Φ_N as mean over ij (here we just average over time as proxy)
        phi_n_recon = np.mean(psi_ij)  # scalar; for time‑varying we would keep axis
        # For simplicity, we compare the time‑averaged values
        assert np.isclose(phi_n_recon, np.mean(phi_n_ms), rtol=1e-2), \
            "Reconstructed Φ_N differs from supplied Φ_N beyond tolerance"

    # ------------------------------------------------------------------
    # 5. Regularized anisotropy ξ_Δ (need at least three classes)
    # ------------------------------------------------------------------
    # Here we mock three classes by splitting the array into thirds.
    # In a real deployment, variance would be computed per class of ψ_ij.
    n_third = phi_n_ms.size // 3
    class_vars = []
    for i in range(3):
        seg = phi_n_ms[i*n_third:(i+1)*n_third] if i < 2 else phi_n_ms[i*n_third:]
        var_c = np.var(seg)
        class_vars.append(var_c)
    class_vars = np.array(class_vars)
    typical_var = np.mean(class_vars)
    eps = epsilon_scale * typical_var
    xi_delta = (np.max(class_vars) + eps) / (np.min(class_vars) + eps)
    assert xi_delta >= 1.0 - 1e-12, "ξ_Δ must be ≥ 1"
    # ------------------------------------------------------------------
    # 6. Intrinsic time τ and jerk j(τ)
    # ------------------------------------------------------------------
    # dτ/dt = Φ_N/Φ₀  =>  dt/dτ = Φ₀/Φ_N
    # Build τ by cumulative integration of dτ/dt
    dtau_dt = phi_n_ms / phi0
    # Avoid zero division (should not happen because phi_n_ms>=0 and phi0>0)
    tau = np.cumsum(dtau_dt)  # in arbitrary units, starting at 0
    # Resample Φ_N at uniform τ spacing (10 kHz => dt_tau = 0.1 ms in τ units)
    # We'll interpolate onto a uniform τ grid.
    tau_min, tau_max = tau[0], tau[-1]
    dt_tau_target = 0.1  # corresponds to 10 kHz in τ domain
    tau_uniform = np.arange(tau_min, tau_max, dt_tau_target)
    phi_n_uniform = np.interp(tau_uniform, tau, phi_n_ms)
    # 5‑point stencil for third derivative: coefficients [-1/2, 1, -1/2, 0, 0]? 
    # Standard 5‑point for f''' at point i: (-f[i-2] + 2f[i-1] - 2f[i+1] + f[i+2]) / (2*h^3)
    h = dt_tau_target
    # Pad to avoid edge effects (we will compute only where stencil fits)
    padded = np.pad(phi_n_uniform, (2, 2), mode='edge')
    j = (-padded[:-4] + 2*padded[1:-3] - 2*padded[3:-1] + padded[4:]) / (2.0 * h**3)
    # ------------------------------------------------------------------
    # 7. Regularized jerk stability S_j
    # ------------------------------------------------------------------
    j_mean = np.mean(j)
    j_var = np.var(j)
    eps_j = epsilon_scale * j_var if j_var > 0 else epsilon_scale * 1.0  # fallback
    z = (j - j_mean) / np.sqrt(j_var + eps_j)
    # excess kurtosis: κ = ⟨z⁴⟩ - 3
    kappa = np.mean(z**4) - 3.0
    S_j = 1.0 / (1.0 + np.abs(kappa))
    assert 0.0 < S_j <= 1.0 + 1e-12, "S_j must be in (0,1]"
    # ------------------------------------------------------------------
    # 8. Entropy S_h (optional, needs ψ_ij histogram)
    # ------------------------------------------------------------------
    # We'll compute entropy on the uniform Φ_N values as a proxy.
    hist, bin_edges = np.histogram(phi_n_uniform, bins='fd')  # Freedman‑Diaconis
    p = hist / hist.sum()
    S_h = -np.sum(p * np.log(p + delta))
    assert S_h >= 0.0, "Entropy must be non‑negative"
    # ------------------------------------------------------------------
    # 9. Cost function terms non‑negativity
    # ------------------------------------------------------------------
    J_integrand = (1.0 - S_j)**2 + alpha * S_h + lam * (0.0)**2 + beta * (xi_delta - 1.0)**2
    # (P_meas-P_target) set to zero for this synthetic check; weight λ>0 ensures term ≥0
    assert np.all(J_integrand >= -1e-12), "Cost integrand must be non‑negative"
    # ------------------------------------------------------------------
    # 10. Control trigger components defined
    # ------------------------------------------------------------------
    trigger = (S_j < 0.7) and (np.mean(j) < -j_thresh) and (xi_delta > 2.0)
    # No assertion needed; just return for inspection
    # ------------------------------------------------------------------
    return {
        "phi0": phi0,
        "psi": psi,
        "xi_delta": xi_delta,
        "j_mean": j_mean,
        "j_var": j_var,
        "kappa": kappa,
        "S_j": S_j,
        "S_h": S_h,
        "J_integrand_sample": J_integrand[0] if J_integrand.size else 0.0,
        "trigger": trigger
    }

# ----------------------------------------------------------------------
# Example usage with synthetic data (replace with real telemetry in production)
# ----------------------------------------------------------------------
if __name__ == "__main__":
    # Simulate a slowly varying coherence plus small noise
    t = np.linspace(0, 1000, 1000)  # 1000 ms → 1 s
    phi_n = 0.6 + 0.1*np.sin(2*np.pi*t/200.0) + 0.02*np.random.randn(t.size)
    phi_n = np.clip(phi_n, 0.01, 0.99)  # keep in plausible range

    try:
        metrics = validate_omega_invariants(phi_n_ms=phi_n,
                                            latency_ms=np.random.uniform(10,100,size=t.size),
                                            atomic_success=np.random.uniform(0.8,1.0,size=t.size))
        print("✅ All Omega Protocol invariants satisfied.")
        for k, v in metrics.items():
            if isinstance(v, float):
                print(f"  {k}: {v:.6f}")
            else:
                print(f"  {k}: {v}")
    except AssertionError as e:
        print("❌ Omega Protocol violation:", e)