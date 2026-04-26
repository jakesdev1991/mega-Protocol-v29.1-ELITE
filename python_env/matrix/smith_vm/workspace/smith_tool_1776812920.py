# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
#!/usr/bin/env python3
"""
Omega‑Protocol compliance checker for GRNIM‑Ω.
Validates:
  - ψ_inf = ln(Φ_N_inf/Φ_N0)
  - ψ_inf = ln(λ_max/λ0) + κ·IPI
  - IPI ∈ [0,1]
  - MPC‑Ω constraints: IPI ≤ 0.65, Φ_N_inf ≥ 0.5, S_inf ≥ ln(5)
  - Φ_N_inf > 0, λ_max > 0
Run: python3 grnim_omega_check.py
"""

import numpy as np

# ----------------------------------------------------------------------
# Helper functions (mock implementations of the inference pipeline)
# ----------------------------------------------------------------------
def mock_inference_ensemble(n_genes=50, n_algo=4, n_bootstrap=120, seed=0):
    """
    Returns:
        edge_conf  : shape (n_algo, n_bootstrap, n_genes, n_genes)  in [0,1]
        posterior  : shape (n_algo, n_bootstrap)                  dummy scores
    """
    rng = np.random.default_rng(seed)
    # Simulate a ground‑truth sparse adjacency (0/1)
    true_adj = rng.binomial(1, 0.05, size=(n_genes, n_genes))
    np.fill_diagonal(true_adj, 0)

    # Generate noisy confidence matrices around the truth
    conf = np.clip(
        true_adj[None, None, :, :] + rng.normal(0, 0.15, size=(n_algo, n_bootstrap, n_genes, n_genes)),
        0, 1,
    )
    # Dummy posterior scores (higher = better)
    posterior = rng.uniform(0.8, 1.0, size=(n_algo, n_bootstrap))
    return conf, posterior, true_adj

def consensus_correlation_length(conf):
    """
    ξ_N = average pairwise Pearson correlation of flattened confidence matrices
    Φ_N = 1/ξ_N
    """
    n_algo, n_boot, n_genes, _ = conf.shape
    flat = conf.reshape(n_algo * n_boot, -1)          # (n_algo*n_boot, n_genes^2)
    corr_mat = np.corrcoef(flat)                     # (N,N)
    # exclude self‑correlation
    mask = ~np.eye(corr_mat.shape[0], dtype=bool)
    xi = np.mean(corr_mat[mask])
    # Guard against degenerate case
    xi = max(xi, 1e-6)
    return 1.0 / xi, xi

def edge_confidence_skewness(conf):
    """Φ_Δ = skewness of all confidence values."""
    vals = conf.ravel()
    # scipy.stats.skew not available; use moment formula
    m = np.mean(vals)
    s = np.std(vals)
    if s == 0:
        return 0.0
    return np.mean(((vals - m) / s) ** 3)

def js_divergence(p, q):
    """Jensen‑Shannon divergence for 1‑D histograms."""
    p = np.asarray(p)
    q = np.asarray(q)
    p = p / p.sum() if p.sum() > 0 else p
    q = q / q.sum() if q.sum() > 0 else q
    m = 0.5 * (p + q)
    def kl(a,b):
        return np.sum(np.where(a>0, a * np.log(a / b), 0.0))
    return 0.5 * (kl(p, m) + kl(q, m))

def topological_stability_index(conf, true_adj=None):
    """
    TSI = 1 - D_JSD( P_deg(full) || P_deg(pert) )
    We approximate by jackknifing one bootstrap sample at a time.
    """
    n_algo, n_boot, n_genes, _ = conf.shape
    # Degree distribution from the median confidence graph across algos & bootstraps
    median_conf = np.median(conf, axis=(0,1))          # (n_genes, n_genes)
    np.fill_diagonal(median_conf, 0)
    deg_full = np.sum(median_conf > 0.5, axis=1)      # binary threshold
    hist_full, _ = np.histogram(deg_full, bins=np.arange(-0.5, n_genes+1.5, 1), density=True)

    # Perturbed: leave‑one‑bootstrap‑out
    tsi_vals = []
    for b in range(n_boot):
        conf_loo = np.delete(conf, b, axis=1)        # remove bootstrap b
        median_loo = np.median(conf_loo, axis=(0,1))
        np.fill_diagonal(median_loo, 0)
        deg_loo = np.sum(median_loo > 0.5, axis=1)
        hist_loo, _ = np.histogram(deg_loo, bins=np.arange(-0.5, n_genes+1.5, 1), density=True)
        tsi_vals.append(1 - js_divergence(hist_full, hist_loo))
    return np.mean(tsi_vals)

def inference_entropy(conf):
    """
    S_inf = Shannon entropy over the ensemble of inferred graphs.
    We treat each bootstrap‑algo pair as a sample graph (binary after threshold).
    """
    n_algo, n_boot, n_genes, _ = conf.shape
    graphs = (conf > 0.5).astype(int)                # (n_algo, n_boot, n_genes, n_genes)
    # Flatten each graph to a bit‑string and count unique patterns
    patterns = np.apply_along_axis(lambda x: np.packbits(x.reshape(-1)), axis=2, arr=graphs)
    patterns = patterns.reshape(-1)                  # (n_algo*n_boot,)
    uniq, counts = np.unique(patterns, return_counts=True)
    probs = counts / counts.sum()
    return -np.sum(probs * np.log(probs + 1e-12))

def compute_ipi(tsi, phi_delta, s_inf, s0, alpha=1.0, beta=1.0, gamma=1.0):
    """IPI = tanh[ α(1‑TSI) + β·Φ_Δ + γ·(S0‑S_inf) ]"""
    arg = alpha * (1.0 - tsi) + beta * phi_delta + gamma * (s0 - s_inf)
    return np.tanh(arg)

def dominant_hessian_eigenvalue(conf):
    """
    Mock λ_max: we approximate curvature of the average log‑posterior.
    For simplicity we use the variance of edge confidences across the ensemble:
    low variance → sharp peak → large λ_max.
    """
    var = np.var(conf)
    # Map variance to eigenvalue (inverse relationship, scaled)
    lam0 = 1.0                     # baseline eigenvalue for clean data
    lam = lam0 / (var + 1e-6)      # avoid division by zero
    return lam, lam0

# ----------------------------------------------------------------------
# Main validation routine
# ----------------------------------------------------------------------
def main():
    # Simulate data
    conf, posterior, true_adj = mock_inference_ensemble(seed=42)

    # Extract metrics
    phi_n_inf, xi_N = consensus_correlation_length(conf)
    phi_delta_inf = edge_confidence_skewness(conf)
    tsi = topological_stability_index(conf)
    s_inf = inference_entropy(conf)
    s0 = inference_entropy(conf) * 1.2   # baseline entropy (slightly higher for clean data)

    # IPI
    ipi = compute_ipi(tsi, phi_delta_inf, s_inf, s0)

    # Invariant via Φ_N
    Phi_N0 = 1.0   # baseline consensus length (chosen arbitrarily)
    psi_inf_phi = np.log(phi_n_inf / Phi_N0)

    # Invariant via curvature (λ_max)
    lam_max, lam0 = dominant_hessian_eigenvalue(conf)
    kappa = 0.5    # coupling constant (chosen for demo)
    psi_inf_lam = np.log(lam_max / lam0) + kappa * ipi

    # ------------------------------------------------------------------
    # Assertions – Omega Protocol compliance
    # ------------------------------------------------------------------
    # 1. Basic domain requirements
    assert phi_n_inf > 0, f"Φ_N^(inf) must be >0 (got {phi_n_inf})"
    assert lam_max > 0, f"λ_max must be >0 (got {lam_max})"
    assert 0.0 <= ipi <= 1.0, f"IPI must be in [0,1] (got {ipi})"

    # 2. Invariant equality (tolerance for numerical error)
    tol = 1e-6
    assert abs(psi_inf_psi - psi_inf_lam) < tol, \
        f"ψ_inf mismatch: from Φ_N={psi_inf_phi:.6f}, from λ_max={psi_inf_lam:.6f}"

    # 3. MPC‑Ω constraints
    assert ipi <= 0.65 + 1e-9, f"IPI exceeds safety threshold: {ipi}"
    assert phi_n_inf >= 0.5 - 1e-9, f"Φ_N^(inf) below minimum: {phi_n_inf}"
    assert s_inf >= np.log(5) - 1e-9, f"S_inf too low: {s_inf} (need ≥ ln5≈{np.log(5):.3f})"

    # 4. Additional sanity: Φ_Δ should be finite
    assert np.isfinite(phi_delta_inf), f"Φ_Δ^(inf) is not finite: {phi_delta_inf}"

    print("All Omega‑Protocol checks passed.")
    print(f"  Φ_N^(inf) = {phi_n_inf:.4f}")
    print(f"  Φ_Δ^(inf) = {phi_delta_inf:.4f}")
    print(f"  TSI       = {tsi:.4f}")
    print(f"  S_inf     = {s_inf:.4f}")
    print(f"  IPI       = {ipi:.4f}")
    print(f"  ψ_inf (Φ_N) = {psi_inf_phi:.6f}")
    print(f"  ψ_inf (λ)   = {psi_inf_lam:.6f}")

if __name__ == "__main__":
    main()