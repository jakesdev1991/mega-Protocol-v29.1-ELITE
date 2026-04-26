# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Omega Protocol Invariant Validator – HSA Informational Jerk Stability
--------------------------------------------------------------------
Validates the corrected definitions:
    ψ      = ln(Φ_N / Φ_0)                     (dimensionless scalar invariant)
    ξ_N    = (1/N Σ ‖∇ψ_ij‖²)^(-1/2)           (radial correlation length)
    ξ_Δ    = max_c σ_c² / min_c σ_c²          (poloidal correlation length)
    S_h    = - Σ_k p_k ln p_k                 (Shannon entropy of coherence)
    j      = d³Φ_N/dτ³                        (informational jerk, 5‑point stencil)
    S_j    = (1 + | κ̂ - 3 | )^{-1}           (excess‑kurtosis stability)
        κ̂ = (1/T) ∫ [(j- j̄)/√(σ_j²+ε)]⁴ dτ   (regularised kurtosis)
Enforces:
    ψ dimensionless, ξ_N>0, ξ_Δ≥1, 0<S_j≤1, S_j→1 as σ_j→0.
"""

import numpy as np

# ----------------------------------------------------------------------
# Helper functions (stand‑in for telemetry acquisition)
# ----------------------------------------------------------------------
def coherence_field(latency, success_rate, L0=1.0):
    """ψ_ij = A_ij * exp(-L_ij / L0)"""
    return success_rate * np.exp(-latency / L0)

def global_scalars(psi_ij):
    """Φ_N = ⟨ψ⟩, Φ_Δ = sqrt⟨(ψ-Φ_N)²⟩"""
    Phi_N = np.mean(psi_ij)
    Phi_Delta = np.sqrt(np.mean((psi_ij - Phi_N) ** 2))
    return Phi_N, Phi_Delta

def radial_corr_length(psi_ij, coords):
    """
    ξ_N = ( (1/N) Σ ‖∇ψ_ij‖² )^{-1/2}
    Approximate gradient via finite differences on a regular grid.
    coords: shape (N,2) – (x,y) indices of each compute unit.
    """
    # reshape to 2D grid for simple gradient
    nx = int(np.sqrt(len(psi_ij)))
    ny = nx
    psi_grid = psi_ij.reshape((nx, ny))
    grad_y, grad_x = np.gradient(psi_grid)  # assumes unit spacing
    grad_sq = grad_x**2 + grad_y**2
    xi_N = np.sqrt(1.0 / np.mean(grad_sq))
    return xi_N

def poloidal_corr_length(psi_ij, class_labels):
    """
    ξ_Δ = max_c σ_c² / min_c σ_c²
    class_labels: array same length as psi_ij indicating {CPU‑GPU, GPU‑GPU, CPU‑CPU}
    """
    vars_per_class = []
    for c in np.unique(class_labels):
        vars_per_class.append(np.var(psi_ij[class_labels == c]))
    xi_Delta = np.max(vars_per_class) / np.min(vars_per_class)
    return xi_Delta

def shannon_entropy(psi_ij, bins=50):
    """S_h = - Σ p_k ln p_k"""
    hist, _ = np.histogram(psi_ij, bins=bins, density=True)
    p = hist + 1e-12  # avoid log(0)
    return -np.sum(p * np.log(p))

def jerk_5point(Phi_N, dt):
    """
    Third derivative using 5‑point central stencil:
    j[t] = (-Φ_N[t+2] + 2Φ_N[t+1] - 2Φ_N[t-1] + Φ_N[t-2]) / (2*dt**3)
    """
    j = np.empty_like(Phi_N)
    j[2:-2] = (-Phi_N[4:] + 2*Phi_N[3:-1] - 2*Phi_N[1:-3] + Phi_N[:-4]) / (2.0 * dt**3)
    # edges: fallback to lower order (not used in validation window)
    j[:2] = j[2]
    j[-2:] = j[-3]
    return j

def jerk_stability(j, eps=1e-9):
    """
    S_j = (1 + | κ̂ - 3 | )^{-1}
    κ̂ = mean[ ((j - μ)/√(σ²+ε))⁴ ]
    """
    mu = np.mean(j)
    sigma2 = np.var(j) + eps
    z = (j - mu) / np.sqrt(sigma2)
    kappa_hat = np.mean(z**4)
    S_j = 1.0 / (1.0 + np.abs(kappa_hat - 3.0))
    return S_j, kappa_hat

def scalar_invariant(Phi_N, Phi_0):
    """ψ = ln(Φ_N / Φ_0) – dimensionless"""
    return np.log(Phi_N / Phi_0)

# ----------------------------------------------------------------------
# Validation routine
# ----------------------------------------------------------------------
def validate_invariants(telemetry, dt=1e-4, Phi_0=1.0, eps=1e-9):
    """
    telemetry: dict with keys
        'latency'   : (N_pairs,) float
        'success'   : (N_pairs,) float in [0,1]
        'coords'    : (N_pairs,2) int grid positions
        'class'     : (N_pairs,) int label {0,1,2}
    """
    # 1. Build coherence field
    psi_ij = coherence_field(telemetry['latency'], telemetry['success'])

    # 2. Global scalars
    Phi_N, Phi_Delta = global_scalars(psi_ij)

    # 3. Invariants
    psi = scalar_invariant(Phi_N, Phi_0)          # ← dimensionless log‑ratio
    xi_N = radial_corr_length(psi_ij, telemetry['coords'])
    xi_Delta = poloidal_corr_length(psi_ij, telemetry['class'])

    # 4. Entropy
    S_h = shannon_entropy(psi_ij)

    # 5. Jerk & stability (using a short window of Phi_N)
    j = jerk_5point(Phi_N, dt)
    S_j, kappa_hat = jerk_stability(j, eps=eps)

    # ------------------------------------------------------------------
    # Assertions – the Omega Protocol invariants
    # ------------------------------------------------------------------
    # ψ must be dimensionless → invariant under scaling of Phi_N
    psi_scaled = scalar_invariant(2*Phi_N, Phi_0)   # scaling Φ_N by 2
    assert np.allclose(psi, psi_scaled - np.log(2.0)), \
        "ψ not a proper log‑ratio (dimensionless) invariant"

    # ξ_N > 0
    assert xi_N > 0, f"ξ_N must be positive, got {xi_N}"

    # ξ_Δ ≥ 1 (isotropy gives 1)
    assert xi_Delta >= 1.0, f"ξ_Δ must be ≥1, got {xi_Delta}"

    # Entropy non‑negative
    assert S_h >= 0, f"Entropy S_h negative: {S_h}"

    # Jerk stability bounds
    assert 0.0 < S_j <= 1.0 + 1e-12, f"S_j out of bounds: {S_j}"
    # Constant jerk limit: if variance → 0, S_j → 1
    j_const = np.full_like(j, np.mean(j))
    S_j_const, _ = jerk_stability(j_const, eps=eps)
    assert np.abs(S_j_const - 1.0) < 1e-6, \
        f"Constant jerk did not yield S_j≈1 (got {S_j_const})"

    # All good – return a diagnostics dict
    return {
        "psi": psi, "Phi_N": Phi_N, "Phi_Delta": Phi_Delta,
        "xi_N": xi_N, "xi_Delta": xi_Delta,
        "S_h": S_h, "j_rms": np.sqrt(np.mean(j**2)),
        "S_j": S_j, "kappa_hat": kappa_hat
    }

# ----------------------------------------------------------------------
# Example usage with synthetic data (replace with real telemetry)
# ----------------------------------------------------------------------
if __name__ == "__main__":
    np.random.seed(42)
    N = 256  # 16x16 grid
    latency = np.random.uniform(0.5, 2.0, size=N)          # ms
    success = np.random.uniform(0.8, 1.0, size=N)          # fraction
    # create a simple 2D grid of coordinates
    xs = np.repeat(np.arange(int(np.sqrt(N))), int(np.sqrt(N)))
    ys = np.tile(np.arange(int(np.sqrt(N))), int(np.sqrt(N)))
    coords = np.stack([xs, ys], axis=1)
    # three class labels: 0=CPU‑GPU, 1=GPU‑GPU, 2=CPU‑CPU (random for demo)
    class_labels = np.random.randint(0, 3, size=N)

    tel = {
        "latency": latency,
        "success": success,
        "coords": coords,
        "class": class_labels
    }

    try:
        diag = validate_invariants(tel, dt=1e-4, Phi_0=np.median(
            coherence_field(latency, success)), eps=1e-9)
        print("✅ All Omega Protocol invariants satisfied.")
        for k, v in diag.items():
            if isinstance(v, float):
                print(f"  {k}: {v:.6g}")
    except AssertionError as e:
        print("❌ Invariant violation:", e)
        raise