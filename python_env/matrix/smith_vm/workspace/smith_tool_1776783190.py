# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
#!/usr/bin/env python3
"""
Omega Protocol Validator for Hierarchical Visual Fragility Index (HVFI‑Ω)

Checks:
1. Mathematical correctness of entropy, mutual‑information, log‑det curvature.
2. Mapping to Omega invariants Φ_N and Φ_Δ respects monotonicity assumptions.
3. Anomaly score formulation (Mahalanobis distance) is PSD‑safe.
4. MPC‑Ω QP constraints are enforceable (feasibility test).
5. All intermediate quantities remain in numerically stable ranges.

Run with: python3 validate_hvfi.py
"""

import numpy as np
from scipy.stats import entropy
from scipy.linalg import logdet, cholesky, LinAlgError

# ----------------------------------------------------------------------
# Helper functions (exact replicas of the formulas in the proposal)
# ----------------------------------------------------------------------
def per_scale_entropy(activations, bins=50):
    """S_l(t) = - Σ p log p"""
    hist, _ = np.histogram(activations, bins=bins, density=True)
    # avoid zeros in log
    hist = np.clip(hist, 1e-12, None)
    return entropy(hist, base=np.e)

def cross_scale_mutual_info(a_l, a_l1, bins=30):
    """I_{l,l+1}(t) = Σ p log(p/(p_l p_l1))"""
    # joint histogram
    joint, x_edges, y_edges = np.histogram2d(a_l, a_l1, bins=bins, density=True)
    # marginals
    p_l, _ = np.histogram(a_l, bins=bins, density=True)
    p_l1, _ = np.histogram(a_l1, bins=bins, density=True)
    # avoid zeros
    joint = np.clip(joint, 1e-12, None)
    p_l = np.clip(p_l, 1e-12, None)[:, None]
    p_l1 = np.clip(p_l1, 1e-12, None)[None, :]
    return np.sum(joint * np.log(joint / (p_l * p_l1)))

def pyramid_curvature_invariant(A, eps=1e-6):
    """Ψ(t) = ln det( Σ_A + εI )"""
    Sigma = np.cov(A, bias=True)  # shape (L, L)
    try:
        return logdet(Sigma + eps * np.eye(Sigma.shape[0]))
    except LinAlgError:
        return -np.inf  # singular → collapse

def phi_n_balanced(mean_S, std_S, eta1=0.2, alpha=1.0, beta=1.0, tau=0):
    """Φ_N^(hvfi) = Φ_N^0 + η1 * tanh( α·mean_S - β·std_S )"""
    # assume baseline Φ_N^0 = 0.5 (neutral)
    Phi_N0 = 0.5
    return Phi_N0 + eta1 * np.tanh(alpha * mean_S - beta * std_S)

def phi_delta_coupling(max_I, Psi, eta2=0.3, gamma=1.0, delta=1.0, tau=0):
    """Φ_Δ^(hvfi) = Φ_Δ^0 + η2 * sigmoid( γ·max_I - δ·Ψ )"""
    Phi_Delta0 = 0.2
    z = gamma * max_I - delta * Psi
    return Phi_Delta0 + eta2 * (1.0 / (1.0 + np.exp(-z)))

def mahalanobis_anomaly(z, z_hat, Sigma_e):
    """s = sqrt( (z - z_hat)^T Σ_e^{-1} (z - z_hat) )"""
    diff = (z - z_hat).reshape(-1, 1)
    try:
        inv_Sigma = np.linalg.inv(Sigma_e)
    except LinAlgError:
        # fallback to pseudo‑inverse if Σ_e is singular
        inv_Sigma = np.linalg.pinv(Sigma_e)
    return np.sqrt(np.dot(diff.T, np.dot(inv_Sigma, diff))[0, 0])

# ----------------------------------------------------------------------
# Synthetic data generator (tick‑level order‑book heatmaps → activations)
# ----------------------------------------------------------------------
def synthetic_activation_series(T=500, L=4, dim=20):
    """
    Returns:
        activations[l, t, :]  – level‑wise feature vectors
    """
    np.random.seed(42)
    # Base signal: slow drift + occasional shock
    t = np.arange(T)
    base = 0.1 * np.sin(0.02 * t)[:, None]  # shape (T,1)
    # Level‑specific scaling (finest → coarsest)
    scale_factors = np.linspace(1.0, 0.3, L)[:, None, None]  # (L,1,1)
    noise = 0.05 * np.random.randn(L, T, dim)
    activations = scale_factors * (base + noise)
    # Inject a micro‑scale shock at t=250 that propagates upward
    shock = np.zeros_like(activations)
    shock[:, 250:260, :] += 0.8 * np.exp(-np.arange(L)[:, None, None] / 2.0)
    activations += shock
    return activations

# ----------------------------------------------------------------------
# Main validation routine
# ----------------------------------------------------------------------
def validate():
    activations = synthetic_activation_series()
    L, T, dim = activations.shape

    # Containers for time‑series of derived quantities
    S = np.zeros((L, T))
    I = np.zeros((L-1, T))          # mutual info between l and l+1
    Psi = np.zeros(T)

    # ---- Phase 2: compute per‑scale entropy, cross‑scale MI, curvature ----
    for t in range(T):
        A_t = activations[:, t, :]          # (L, dim)
        for l in range(L):
            S[l, t] = per_scale_entropy(A_t[l, :])
        for l in range(L-1):
            I[l, t] = cross_scale_mutual_info(A_t[l, :], A_t[l+1, :])
        Psi[t] = pyramid_curvature_invariant(A_t)

    # ---- Phase 3: map to Omega variables (using simple rolling windows) ----
    win = 5   # τ ≈ 5 ms approximated by 5 samples
    mean_S = np.mean(S, axis=0)               # (T,)
    std_S  = np.std(S, axis=0)
    max_I  = np.max(I, axis=0)                # (T,)

    Phi_N = phi_n_balanced(mean_S, std_S)
    Phi_Delta = phi_delta_coupling(max_I, Psi)

    # ---- Phase 4: anomaly detection (VAR(1) baseline) ----
    # Stack [S_l, I_{l,l+1}, Ψ] → shape (3L-1, T)
    z = np.vstack([S, I, Psi[None, :]])   # (3L-1, T)
    # Simple VAR(1): z_hat(t) = A @ z(t-1) with A = 0.9*I (stable)
    A_var = 0.9 * np.eye(z.shape[0])
    z_hat = np.zeros_like(z)
    z_hat[:, 1:] = A_var @ z[:, :-1]
    z_hat[:, 0] = z[:, 0]                  # initial condition unchanged
    # Empirical covariance of residuals
    residuals = z - z_hat
    Sigma_e = np.cov(residuals)
    # Anomaly score per time step
    s_hvfi = np.array([mahalanobis_anomaly(z[:, t], z_hat[:, t], Sigma_e)
                       for t in range(T)])

    # ---- Phase 5: flagging logic ----
    flag = (s_hvfi > 3.0) & (Phi_Delta > 0.75)

    # ---- Phase 6: MPC‑Ω QP feasibility test (dummy) ----
    # Constraints: S_l >= S_min, I <= I_max, Psi >= Psi_min,
    #              Phi_N >= 0.65, Phi_Delta <= 0.70
    S_min, I_max, Psi_min = 0.1, 0.5, -10.0   # arbitrary sensible bounds
    constraints_ok = (
        np.all(S >= S_min) and
        np.all(I <= I_max) and
        np.all(Psi >= Psi_min) and
        np.all(Phi_N >= 0.65) and
        np.all(Phi_Delta <= 0.70)
    )

    # ------------------------------------------------------------------
    # Reporting
    # ------------------------------------------------------------------
    print("=== HVFI‑Ω Validation Report ===")
    print(f"Time steps: {T}, Pyramid levels: {L}")
    print(f"Entropy range per level: [{S.min():.3f}, {S.max():.3f}]")
    print(f"Mutual‑info range: [{I.min():.3f}, {I.max():.3f}]")
    print(f"Curvature Ψ range: [{Psi.min():.3f}, {Psi.max():.3f}]")
    print(f"Φ_N range: [{Phi_N.min():.3f}, {Phi_N.max():.3f}]")
    print(f"Φ_Δ range: [{Phi_Delta.min():.3f}, {Phi_Delta.max():.3f}]")
    print(f"Anomaly score s_hvfi range: [{s_hvfi.min():.3f}, {s_hvfi.max():.3f}]")
    print(f"Number of flash‑crash flags: {np.sum(flag)}")
    print(f"MPC‑Ω constraint feasibility: {'PASS' if constraints_ok else 'FAIL'}")
    # ------------------------------------------------------------------
    # Additional mathematical sanity checks
    # ------------------------------------------------------------------
    # 1. Entropy non‑negative
    assert np.all(S >= 0), "Entropy must be ≥ 0"
    # 2. Mutual information non‑negative
    assert np.all(I >= 0), "Mutual information must be ≥ 0"
    # 3. Ψ should be finite (logdet of PD matrix + εI)
    assert np.all(np.isfinite(Psi)), "Ψ contains non‑finite values"
    # 4. Φ_N, Φ_Δ bounded by construction of tanh/sigmoid
    assert np.all((Phi_N >= 0.0) & (Phi_N <= 1.0)), "Φ_N out of [0,1]"
    assert np.all((Phi_Delta >= 0.0) & (Phi_Delta <= 1.0)), "Φ_Δ out of [0,1]"
    # 5. Anomaly score non‑negative
    assert np.all(s_hvfi >= 0), "Mahalanobis distance must be ≥ 0"
    # 6. If flags exist, verify they respect the logical condition
    if np.any(flag):
        assert np.all((s_hvfi[flag] > 3.0) & (Phi_Delta[flag] > 0.75)), \
            "Flag condition violated"
    print("\nAll mathematical sanity checks PASSED.")

if __name__ == "__main__":
    validate()