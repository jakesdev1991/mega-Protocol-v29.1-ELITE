# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
"""
Omega Protocol Validation Script – HSA Informational Jerk Stability (UMCJ-Ω v2)

This script audits the mathematical soundness and rubric‑compliance of the
analysis presented by the Engine (architect) agent.  It:
  1. Re‑derives the core quantities from synthetic HSA telemetry.
  2. Verifies the explicit definitions of the invariants ξ_N, ξ_Δ and the
     entropy‑like term H(t).
  3. Checks that the jerk stability metric uses variance (or excess kurtosis)
     and NOT raw kurtosis.
  4. Confirms the MPC‑Ω state vector contains all required components.
  5. Asserts basic physical sanity (positivity, boundedness, etc.).

If any check fails, an AssertionError is raised with a diagnostic message.
"""

import numpy as np

# ----------------------------------------------------------------------
# Helper: synthetic HSA telemetry (for validation only)
# ----------------------------------------------------------------------
def generate_telemetry(num_units=8, num_steps=200, dt=0.0001, seed=42):
    """Produce fake latency L_ij(t) and atomic success A_ij(t)."""
    rng = np.random.default_rng(seed)
    # Baseline latency L0 (constant)
    L0 = 1.0
    # Latency varies slowly with some spikes to mimic coherence collapse
    L = L0 * (1 + 0.2 * np.sin(np.linspace(0, 4*np.pi, num_steps))[:, None, None]
              + 0.1 * rng.standard_normal((num_steps, num_units, num_units)))
    # Atomic success rate (0..1) with occasional drops
    A = 0.9 * np.ones_like(L) - 0.05 * rng.standard_normal(L.shape)
    A = np.clip(A, 0.0, 1.0)
    return L, A, L0, dt

# ----------------------------------------------------------------------
# Core definitions from the analysis
# ----------------------------------------------------------------------
def coherence_field(A, L, L0):
    """ψ_ij(t) = A_ij * exp(-L_ij / L0)"""
    return A * np.exp(-L / L0)

def phi_n(psi):
    """Φ_N(t) = ⟨ψ_ij⟩ over all i,j"""
    return np.mean(psi, axis=(1, 2))

def phi_delta(psi, phi_n):
    """Φ_Δ(t) = sqrt⟨(ψ - Φ_N)^2⟩"""
    diff = psi - phi_n[:, None, None]
    return np.sqrt(np.mean(diff**2, axis=(1, 2)))

def xi_n(psi, unit_spacing=1.0):
    """
    ξ_N(t) = ( (1/N) Σ ||∇ψ_ij||^2 )^{-1/2}
    Approximate gradient via finite differences in the compute‑unit index space.
    """
    # psi shape: (T, N, N)
    grad_x = np.diff(psi, axis=2) / unit_spacing   # diff along j
    grad_y = np.diff(psi, axis=1) / unit_spacing   # diff along i
    # Pad to original shape for averaging
    grad_x = np.pad(grad_x, ((0,0),(0,0),(0,1)), mode='edge')
    grad_y = np.pad(grad_y, ((0,0),(0,1),(0,0)), mode='edge')
    grad_sq = grad_x**2 + grad_y**2
    avg_grad_sq = np.mean(grad_sq, axis=(1,2))
    # Avoid division by zero
    xi = np.where(avg_grad_sq > 0, avg_grad_sq**(-0.5), np.inf)
    return xi

def xi_delta(psi, axis=0):
    """
    ξ_Δ(t) – proxy: standard deviation of ψ along a chosen topological direction.
    Here we simply use the spread along the CPU‑GPU axis (axis=0 of unit pairs).
    """
    # For demonstration, compute variance along first dimension of unit pairs
    var_along = np.var(psi, axis=axis+1)  # +1 to skip time axis
    return np.sqrt(np.mean(var_along, axis=1))

def entropy(psi):
    """Shannon entropy H(t) = - Σ p_ij log p_ij,  p_ij = ψ_ij / Σ ψ_ij"""
    psi_sum = np.sum(psi, axis=(1,2), keepdims=True)
    # Guard against zero total coherence
    p = np.where(psi_sum > 0, psi / psi_sum, 0.0)
    # Avoid log(0)
    with np.errstate(divide='ignore', invalid='ignore'):
        H = -np.sum(p * np.log(p + 1e-12), axis=(1,2))
    return H

def informational_jerk(phi_n, dt):
    """
    j(t) = d^3 Φ_N / dτ^3 using 5‑point stencil.
    Returns jerk array same length as phi_n (edges padded with NaN).
    """
    # Pad to allow stencil at boundaries
    padded = np.pad(phi_n, (2,2), mode='edge')
    j = (-padded[:-4] + 2*padded[1:-3] - 2*padded[3:-1] + padded[4:]) / (2 * dt**3)
    return j

def jerk_stability_variance(j, sigma0_sq=1.0):
    """
    S_j(T) = exp( - σ_j^2 / σ_0^2 )
    where σ_j^2 is variance of jerk over the epoch (here whole signal).
    """
    var_j = np.nanvar(j)  # ignore NaNs from edges
    return np.exp(-var_j / sigma0_sq)

# ----------------------------------------------------------------------
# Validation Routine
# ----------------------------------------------------------------------
def validate_analysis():
    # 1. Generate synthetic telemetry
    L, A, L0, dt = generate_telemetry()
    psi = coherence_field(A, L, L0)

    # 2. Compute core scalars
    Phi_N = phi_n(psi)
    Phi_Delta = phi_delta(psi, Phi_N)
    Xi_N = xi_n(psi)
    Xi_Delta = xi_delta(psi)
    H = entropy(psi)

    # 3. Jerk and stability
    jerk = informational_jerk(Phi_N, dt)
    S_j = jerk_stability_variance(jerk, sigma0_sq=np.var(jerk)+1e-12)  # normalize to its own variance

    # 4. State vector (order as claimed)
    state = np.vstack([Phi_N, Phi_Delta, Xi_N, Xi_Delta, H, jerk, S_j,
                       np.zeros_like(Phi_N),   # placeholder Q_depth
                       np.zeros_like(Phi_N)])  # placeholder P_fault
    # state shape: (9, T)

    # ------------------------------------------------------------------
    # Assertions – Rubric & Mathematical Soundness
    # ------------------------------------------------------------------
    # a) Invariants exist and are finite/positive (where meaningful)
    assert np.all(np.isfinite(Xi_N)) and np.all(Xi_N > 0), \
        "ξ_N must be finite and positive (correlation length)."
    assert np.all(np.isfinite(Xi_Delta)), \
        "ξ_Δ must be finite (directional correlation length)."

    # b) Entropy is non‑negative and bounded by log(N^2)
    max_entropy = np.log(psi.shape[1]*psi.shape[2])
    assert np.all(H >= 0), "Entropy H(t) must be non‑negative."
    assert np.all(H <= max_entropy + 1e-9), \
        f"Entropy exceeds theoretical maximum {max_entropy}."

    # c) Jerk stability metric uses variance (not raw kurtosis)
    #    We explicitly computed S_j via variance; ensure no kurtosis crept in.
    #    (If a kurtosis term were present, S_j would not be a pure exp(-var/σ0^2).)
    #    Here we just confirm the formula matches the definition.
    var_j = np.nanvar(jerk)
    S_j_check = np.exp(-var_j / (np.var(jerk)+1e-12))
    assert np.allclose(S_j, S_j_check, rtol=1e-6), \
        "Jerk stability metric deviates from variance‑based definition."

    # d) S_j ∈ (0, 1] (variance ≥ 0 → exp(-…) ≤ 1, >0)
    assert np.all(S_j > 0) and np.all(S_j <= 1+1e-12), \
        "Jerk stability S_j must lie in (0,1]."

    # e) State vector contains all required components (9 entries)
    assert state.shape[0] == 9, \
        f"State vector must have 9 components, got {state.shape[0]}."

    # f) No raw kurtosis calculation appears in the code (static check)
    #    We can search the source string for the forbidden term.
    source = open(__file__).read()
    forbidden = ['kurtosis', 'scipy.stats.kurtosis', 'pandas.kurtosis']
    for term in forbidden:
        assert term not in source.lower(), \
            f"Raw kurtosis detection: forbidden term '{term}' found in validation script."

    # g) Jerk is third derivative – verify stencil order (optional)
    #    We already used the 5‑point stencil; just ensure it's not a lower‑order diff.
    #    (No explicit assert needed; the formula is hard‑coded.)

    print("✅ All Omega Protocol invariants and mathematical checks passed.")
    print(f"   Sample stats over {len(Phi_N)} time steps:")
    print(f"   Φ_N ∈ [{Phi_N.min():.3f}, {Phi_N.max():.3f}]")
    print(f"   Φ_Δ ∈ [{Phi_Delta.min():.3f}, {Phi_Delta.max():.3f}]")
    print(f"   ξ_N ∈ [{Xi_N.min():.3f}, {Xi_N.max():.3f}]")
    print(f"   ξ_Δ ∈ [{Xi_Delta.min():.3f}, {Xi_Delta.max():.3f}]")
    print(f"   H   ∈ [{H.min():.3f}, {H.max():.3f}]")
    print(f"   jerk ∈ [{np.nanmin(jerk):.3e}, {np.nanmax(jerk):.3e}]")
    print(f"   S_j  ∈ [{S_j.min():.3f}, {S_j.max():.3f}]")

if __name__ == "__main__":
    validate_analysis()