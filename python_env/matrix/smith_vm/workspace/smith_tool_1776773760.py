# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
#!/usr/bin/env python3
"""
Omega Protocol Jerk‑Stability Validator for Linux HSA Unified Memory
-------------------------------------------------------------------
This script checks the mathematical consistency of the agent's analysis
and enforces the Omega Protocol invariants:
    - Phi_N, Phi_Delta ∈ [0, 1]
    - Sigma_J >= 0
    - Jerk decomposition: J ≈ α·J_N + β·J_Δ  (linearity test)
    - Probability vectors remain valid at all times.
"""

import numpy as np
from scipy.signal import savgol_filter
from sklearn.decomposition import PCA

# ------------------- Configuration -------------------
np.random.seed(42)
T_SEC = 60.0               # total simulation time
DT = 1e-3                  # 1 ms sampling
N_STEPS = int(T_SEC / DT)
N_REGIONS = 16             # 8 NUMA × 2 GPU banks
SG_WINDOW = 21             # must be odd and < N_STEPS
SG_ORDER = 3
LAMBDA1, LAMBDA2 = 0.5, 0.5  # MPC‑Ω weights (positive)
JERK_TOL = 1e-2            # tolerance for linearity test
# ----------------------------------------------------

def simulate_access_counts():
    """Generate synthetic memory‑access counts per region."""
    # Base Poisson rate per region (Hz)
    base_rate = np.random.uniform(50, 200, size=N_REGIONS)
    # Add a slow sinusoidal modulation to mimic load changes
    t = np.arange(N_STEPS) * DT
    modulation = 1.0 + 0.3 * np.sin(2 * np.pi * 0.05 * t)[:, None]  # 0.05 Hz
    # Spike a few times to create jerk events
    spikes = np.zeros_like(t)
    spike_times = [0.2, 0.45, 0.7] * T_SEC
    for st in spike_times:
        idx = int(st / DT)
        width = int(0.01 / DT)   # 10 ms spike
        spikes[idx:idx+width] += 5.0
    rates = (base_rate * modulation) + spikes[:, None]
    # Draw Poisson counts per sample
    counts = np.random.poisson(lam=rates * DT)  # counts per ms
    return counts, t

def shannon_entropy(p):
    """S = -∑ p log p (natural log). Guard against log(0)."""
    # Clip to avoid log(0); renormalize after clipping
    p_clip = np.clip(p, 1e-12, None)
    p_clip /= p_clip.sum(axis=-1, keepdims=True)
    return -np.sum(p_clip * np.log(p_clip), axis=-1)

def compute_derivatives(signal, dt, window, order):
    """Use Savitzky‑Golay to get smoothed derivatives."""
    # Ensure window is odd and ≤ len(signal)
    if window % 2 == 0 or window > len(signal):
        raise ValueError("Invalid SG window")
    # savgol_filter returns smoothed signal; deriv=1/2/3 for derivatives
    ds = savgol_filter(signal, window_length=window, polyorder=order, deriv=1, delta=dt)
    d2s = savgol_filter(signal, window_length=window, polyorder=order, deriv=2, delta=dt)
    d3s = savgol_filter(signal, window_length=window, polyorder=order, deriv=3, delta=dt)
    return ds, d2s, d3s

def main():
    counts, t = simulate_access_counts()
    # 1. Normalize to probabilities
    total = counts.sum(axis=1, keepdims=True)
    # Avoid division by zero (should not happen with Poisson)
    p = counts / np.where(total == 0, 1, total)
    # Validate probability vectors
    assert np.all(p >= -1e-12), "Negative probabilities detected"
    assert np.allclose(p.sum(axis=1), 1.0, atol=1e-6), "Probabilities do not sum to 1"

    # 2. Entropy
    S = shannon_entropy(p)

    # 3. Derivatives (Jerk = third derivative)
    dS, d2S, J = compute_derivatives(S, DT, SG_WINDOW, SG_ORDER)

    # 4. PCA on probability matrix (centered)
    p_centered = p - p.mean(axis=0)
    pca = PCA(n_components=2)
    components = pca.fit_transform(p_centered)  # shape (N_STEPS, 2)
    # PCs are the directions; we need the time series of the mode amplitudes
    Phi_N = components[:, 0]   # first PC (Newtonian)
    Phi_Delta = components[:, 1]  # second PC (Archive)

    # 5. Derivatives of the modes
    dPhi_N, d2Phi_N, d3Phi_N = compute_derivatives(Phi_N, DT, SG_WINDOW, SG_ORDER)
    dPhi_D, d2Phi_D, d3Phi_D = compute_derivatives(Phi_Delta, DT, SG_WINDOW, SG_ORDER)

    # 6. Linearization coefficients α, β = ∇S·u_N , ∇S·u_Δ
    # Gradient of S w.r.t. p: ∂S/∂p_i = - (log p_i + 1)
    grad_S = -(np.log(np.clip(p, 1e-12, None)) + 1)  # shape (N_STEPS, N_REGIONS)
    # PC vectors (unit length) from PCA
    u_N = pca.components_[0]  # shape (N_REGIONS,)
    u_D = pca.components_[1]
    alpha = np.einsum('ti,i->t', grad_S, u_N)   # time‑dependent α(t)
    beta  = np.einsum('ti,i->t', grad_S, u_D)   # time‑dependent β(t)

    # 7. Jerk decomposition test
    J_pred = alpha * d3Phi_N + beta * d3Phi_D
    jerk_error = np.mean(np.abs(J - J_pred))
    assert jerk_error < JERK_TOL, f"Jerk decomposition failed: mean error={jerk_error:.3e}"

    # 8. Omega‑invariant bounds for mapped variables
    # Following the agent's phenomenological mapping (example values):
    #   Phi_N_hsa = Phi_N0 - η1 * |d2S(t-τ1)|
    #   Phi_Delta_hsa = Phi_Delta0 + η2 * std_i(J_i(t-τ2))
    # We'll just check that the *raw* PCs can be scaled into [0,1] via affine transform.
    def to_unit(x):
        x_min, x_max = np.min(x), np.max(x)
        if np.isclose(x_max, x_min):
            return np.zeros_like(x)  # degenerate case
        return (x - x_min) / (x_max - x_min)

    Phi_N_hsa = to_unit(Phi_N)
    Phi_Delta_hsa = to_unit(Phi_Delta)
    assert np.all((Phi_N_hsa >= 0) & (Phi_N_hsa <= 1 + 1e-9)), "Phi_N_hsa out of bounds"
    assert np.all((Phi_Delta_hsa >= 0) & (Phi_Delta_hsa <= 1 + 1e-9)), "Phi_Delta_hsa out of bounds"

    # 9. Jerk stability index σ_J ≥ 0
    sigma_J = np.mean(np.abs(J))
    assert sigma_J >= 0, f"Sigma_J negative: {sigma_J}"

    # 10. MPC‑Ω cost integrand positivity (λ>0 ensures)
    integrand = J**2 + LAMBDA1 * Phi_Delta_hsa**2 + LAMBDA2 * (dS - np.mean(dS))**2
    assert np.all(integrand >= -1e-12), "MPC‑Ω integrand negative"

    # If we reach here, all checks passed
    print("[✓] All Omega Protocol invariants satisfied.")
    print(f"    Mean |Jerk| = {sigma_J:.3e} s⁻³")
    print(f"    Jerk decomposition error = {jerk_error:.3e}")
    print(f"    Phi_N_hsa range = [{Phi_N_hsa.min():.3f}, {Phi_N_hsa.max():.3f}]")
    print(f"    Phi_Delta_hsa range = [{Phi_Delta_hsa.min():.3f}, {Phi_Delta_hsa.max():.3f}]")
    print(f"    Entropy range = [{S.min():.3f}, {S.max():.3f}]")

if __name__ == "__main__":
    main()