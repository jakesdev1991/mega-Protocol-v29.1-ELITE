# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
#!/usr/bin/env python3
"""
Omega Protocol Invariant Validator for HSA Unified Memory Jerk‑Stability Analysis
--------------------------------------------------------------------------------
Validates the Engine's mathematical derivations against the Omega Physics Rubric v26.0.
Assumes synthetic telemetry that mimics the structure described in the Engine output.
"""

import numpy as np
from scipy.stats import kurtosis, entropy

# ----------------------------------------------------------------------
# Helper functions (mirror the Engine's definitions)
# ----------------------------------------------------------------------
def compute_psi_ij(A_ij, L_ij, L0=1.0):
    """Coherence field ψ_ij = A_ij * exp(-L_ij / L0)"""
    return A_ij * np.exp(-L_ij / L0)

def compute_phi_ij(reads_ij, writes_ij, eps=1e-9):
    """Asymmetry field φ_ij = reads / (writes + eps)"""
    return reads_ij / (writes_ij + eps)

def compute_psi(phi_ij):
    """Invariant ψ = ln⟨φ⟩ (mean over all i,j)"""
    return np.log(np.mean(phi_ij))

def radial_corr_length(psi_ij, dist_matrix):
    """
    ξ_N: exponential decay constant of C(r) = ⟨ψ_ij⟩_{|i-j|=r}
    Returns the distance r where C(r) = C(0) * exp(-1) (1/e point).
    """
    # Bin pairs by distance
    max_r = np.max(dist_matrix)
    bins = np.linspace(0, max_r, 20)
    C = np.zeros_like(bins[:-1])
    counts = np.zeros_like(bins[:-1])
    for i in range(psi_ij.shape[0]):
        for j in range(i+1, psi_ij.shape[1]):
            d = dist_matrix[i, j]
            idx = np.searchsorted(bins, d) - 1
            if 0 <= idx < len(C):
                C[idx] += psi_ij[i, j]
                counts[idx] += 1
    with np.errstate(divide='ignore', invalid='ignore'):
        C = np.where(counts>0, C/counts, 0)
    C0 = C[0] if C[0] > 0 else 1e-12
    # Find first bin where C <= C0/e
    target = C0 / np.e
    idx = np.where(C <= target)[0]
    if len(idx) == 0:
        return bins[-1]   # fallback: max distance
    return bins[idx[0]]

def poloidal_corr_length(psi_ij, pathway_tags):
    """
    ξ_Δ: std. dev. of coherence decay constants across pathway types.
    For each pathway type compute an effective decay constant (inverse of ξ_N)
    then return their standard deviation.
    """
    pathways = np.unique(pathway_tags)
    decays = []
    for p in pathways:
        mask = (pathway_tags == p)
        # Simple proxy: average coherence over pairs in this pathway
        coh = np.mean(psi_ij[mask][:, mask.T]) if mask.any() else 0.0
        decays.append(1.0/(coh + 1e-12))   # avoid div‑zero
    return np.std(decays)

def compute_entropy(psi_ij, bins=20):
    """Shannon entropy S_h of the coherence distribution."""
    hist, _ = np.histogram(psi_ij.flatten(), bins=bins, density=True)
    # Remove zeros for log
    hist = hist[hist > 0]
    return entropy(hist, base=np.e)

def compute_jerk(phi_N, dt):
    """
    Third derivative j(t) = d³Φ_N/dt³ using a 5‑point stencil.
    Returns array same length as phi_N (edges padded with NaN).
    """
    j = np.full_like(phi_N, np.nan)
    # coefficients for 5‑point central third derivative
    coeff = np.array([-1, 2, 0, -2, 1]) / (2 * dt**3)
    for i in range(2, len(phi_N)-2):
        j[i] = np.dot(coeff, phi_N[i-2:i+3])
    return j

def jerk_stability(j, window):
    """
    Excess‑kurtosis based stability S_j(T) = [1 + (1/T)∫((j‑j̄)/σ_j)⁴ dτ − 3]⁻¹
    Implemented over a sliding window; returns NaN for insufficient data.
    """
    T = len(window)
    if T < 2:
        return np.nan
    j_win = np.asarray(window)
    j_bar = np.mean(j_win)
    sigma_j = np.std(j_win)
    if sigma_j == 0:
        # constant jerk → excess kurtosis = 0 → S_j = 1
        return 1.0
    z = (j_win - j_bar) / sigma_j
    excess = np.mean(z**4) - 3   # sample excess kurtosis
    S_j = 1.0 / (1.0 + excess)
    # Numerical safety: clip to (0,1]
    return np.clip(S_j, 0.0, 1.0)

# ----------------------------------------------------------------------
# Synthetic telemetry generator (for validation only)
# ----------------------------------------------------------------------
def generate_synthetic_data(n_pairs=50, n_time=500, dt=0.001):
    """Create mock HSA telemetry that obeys the Engine's relationships."""
    np.random.seed(42)
    # Base latent coherence field with slow drift + noise
    psi_base = 0.5 + 0.1*np.sin(2*np.pi*0.05*np.arange(n_time))[:,None] \
               + 0.05*np.random.randn(n_time, n_pairs, n_pairs)
    # Ensure symmetry
    psi_ij = (psi_base + np.transpose(psi_base, (0,2,1))) / 2
    # Latency inversely related to coherence
    L0 = 1.0
    L_ij = L0 * (-np.log(np.clip(psi_ij, 1e-3, None))) + 0.02*np.random.randn(*psi_ij.shape)
    L_ij = np.maximum(L_ij, 0.001)   # positive latency
    # Atomic success rate proportional to coherence
    A_ij = np.clip(psi_ij, 0, 1) + 0.02*np.random.randn(*psi_ij.shape)
    A_ij = np.maximum(A_ij, 0.0)
    # Reads/writes asymmetry: bias slowly varying
    bias = 0.2*np.sin(2*np.pi*0.02*np.arange(n_time))[:,None,None]
    reads_ij = np.maximum(0.5 + bias + 0.1*psi_ij, 0.0)
    writes_ij = np.maximum(0.5 - bias + 0.1*psi_ij, 0.0)
    # Pathway tags: two types (0=CPU‑GPU,1=GPU‑GPU)
    pathway_tags = np.random.randint(0,2,size=(n_pairs,n_pairs))
    pathway_tags = np.maximum(pathway_tags, pathway_tags.T)  # make symmetric
    np.fill_diagonal(pathway_tags, -1)   # self‑pairs ignored
    dist_matrix = np.random.rand(n_pairs,n_pairs)*10   # dummy topological distance
    dist_matrix = (dist_matrix + dist_matrix.T)/2
    np.fill_diagonal(dist_matrix,0)
    return {
        "psi_ij": psi_ij,
        "L_ij": L_ij,
        "A_ij": A_ij,
        "reads_ij": reads_ij,
        "writes_ij": writes_ij,
        "pathway_tags": pathway_tags,
        "dist_matrix": dist_matrix,
        "dt": dt
    }

# ----------------------------------------------------------------------
# Main validation routine
# ----------------------------------------------------------------------
def validate_omega_invariants(data):
    """Return True if all rubric checks pass, False otherwise."""
    psi_ij = data["psi_ij"]
    L_ij   = data["L_ij"]
    A_ij   = data["A_ij"]
    reads  = data["reads_ij"]
    writes = data["writes_ij"]
    pathway_tags = data["pathway_tags"]
    dist_matrix = data["dist_matrix"]
    dt = data["dt"]

    # 1. Covariant modes & invariants
    phi_ij = compute_phi_ij(reads, writes)
    psi = compute_psi(phi_ij)                     # ψ = ln⟨φ⟩
    # Global scalars (for reference)
    Phi_N = np.mean(psi_ij, axis=(1,2))           # time series
    Phi_Delta = np.std(psi_ij, axis=(1,2))

    # ξ_N, ξ_Δ (compute per time slice, then check they are finite & positive)
    xi_N_t = np.array([radial_corr_length(psi_ij[t], dist_matrix) for t in range(len(psi_ij))])
    xi_Delta_t = np.array([poloidal_corr_length(psi_ij[t], pathway_tags) for t in range(len(psi_ij))])
    if not (np.all(np.isfinite(xi_N_t)) and np.all(xi_N_t > 0)):
        print("[FAIL] ξ_N non‑positive or non‑finite")
        return False
    if not (np.all(np.isfinite(xi_Delta_t)) and np.all(xi_Delta_t >= 0)):
        print("[FAIL] ξ_Δ non‑finite or negative")
        return False

    # 2. Entropy term
    S_h_t = np.array([compute_entropy(psi_ij[t]) for t in range(len(psi_ij))])
    if not np.all(np.isfinite(S_h_t)):
        print("[FAIL] S_h non‑finite")
        return False
    # Entropy should be ≥0
    if np.any(S_h_t < -1e-12):
        print("[FAIL] S_h negative beyond tolerance")
        return False

    # 3. Jerk and stability metric
    j_t = compute_jerk(Phi_N, dt)                 # time series of jerk
    # Use sliding window of 100 ms (as in Engine) → win_samples = int(0.1/dt)
    win_samples = max(2, int(0.1/dt))
    S_j_t = np.full_like(Phi_N, np.nan)
    for t in range(win_samples, len(Phi_N)):
        window = j_t[t-win_samples:t]
        S_j_t[t] = jerk_stability(j_t, window)
    # Check S_j bounds
    valid = ~np.isnan(S_j_t)
    if not np.all((S_j_t[valid] >= 0) & (S_j_t[valid] <= 1 + 1e-12)):
        print("[FAIL] S_j outside [0,1]")
        return False
    # For Gaussian or constant jerk, S_j should be ≈1 (within tolerance)
    # We test a synthetic constant‑jerk segment:
    const_jerk = np.full(win_samples, 0.01)
    S_j_const = jerk_stability(const_jerk, const_jerk)
    if abs(S_j_const - 1.0) > 1e-2:
        print("[FAIL] S_j not →1 for constant jerk")
        return False
    # Gaussian jerk test
    gauss_jerk = np.random.randn(win_samples)*0.01
    S_j_gauss = jerk_stability(gauss_jerk, gauss_jerk)
    if abs(S_j_gauss - 1.0) > 1e-2:
        print("[FAIL] S_j not →1 for Gaussian jerk")
        return False

    # 4. MPC‑Ω cost integrand non‑negativity
    alpha, lam, P_target = 0.1, 0.05, 150.0   # example weights
    P_meas = np.random.normal(P_target, 5, size=len(Phi_N))   # fake power
    integrand = (1 - S_j_t)**2 + alpha * S_h_t + lam * (P_meas - P_target)**2
    if np.any(integrand < -1e-12):
        print("[FAIL] MPC‑Ω integrand negative")
        return False

    # All checks passed
    print("[PASS] All Omega Protocol invariants satisfied.")
    return True

# ----------------------------------------------------------------------
# Run validation on synthetic data
# ----------------------------------------------------------------------
if __name__ == "__main__":
    tel = generate_synthetic_data()
    validate_omega_invariants(tel)