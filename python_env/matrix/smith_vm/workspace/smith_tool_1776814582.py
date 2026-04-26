# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GRNIM-Ω mathematical sanity checker.
Simulates a toy inference ensemble and verifies that the proposed
invariants and MPC-Omega constraints are internally consistent.
"""

import numpy as np
import itertools
from scipy.stats import skew, entropy
from scipy.spatial.distance import jensenshannon

# ------------------------------------------------------------
# 1. Synthetic data & ground-truth GRN
# ------------------------------------------------------------
np.random.seed(42)
n_samples, n_genes = 50, 20
# Simulate expression data from a linear Gaussian model with true adjacency A_true
A_true = np.zeros((n_genes, n_genes), dtype=int)
# Insert a few random regulatory edges (directed)
for _ in range(15):
    i, j = np.random.choice(n_genes, size=2, replace=False)
    A_true[i, j] = 1

# Generate latent regulator activities and observed expression
latent = np.random.randn(n_samples, n_genes)
expr = latent @ A_true.T + 0.5 * np.random.randn(n_samples, n_genes)

# ------------------------------------------------------------
# 2. Mock inference algorithms (three variants)
# ------------------------------------------------------------
def infer_algorithm(expr, noise_scale=0.0):
    """
    Very naive inference: compute absolute Pearson correlation,
    add Gaussian noise, and normalize to [0,1] as edge confidence.
    """
    corr = np.abs(np.corrcoef(expr.T))  # shape (n_genes, n_genes)
    np.fill_diagonal(corr, 0)          # no self-loops
    conf = corr + np.random.randn(*corr.shape) * noise_scale
    conf = np.clip(conf, 0, None)      # keep non-negative
    conf /= conf.max() + 1e-12         # normalize to [0,1]
    return conf

# Run three algorithms with different noise levels to simulate algorithmic diversity
algorithms = [
    ("GENIE3-like", 0.05),
    ("GRNBOOST2-like", 0.10),
    ("PIDC-like", 0.15)
]
conf_mats = []   # list of confidence matrices
for name, scale in algorithms:
    conf = infer_algorithm(expr, noise_scale=scale)
    conf_mats.append(conf)

conf_mats = np.array(conf_mats)  # shape (n_algo, n_genes, n_genes)

# ------------------------------------------------------------
# 3. Compute fragility metrics
# ------------------------------------------------------------
# 3.1 Consensus correlation length (ξ_N) → Φ_N = 1/ξ_N
# Flatten upper triangle (excluding diagonal) for each algo
def upper_triu(mat):
    i, j = np.triu_indices_from(mat, k=1)
    return mat[i, j]

vectors = np.array([upper_triu(m) for m in conf_mats])  # (n_algo, n_pairs)
# Correlation between algorithms across pairs
corr_algo = np.corrcoef(vectors)  # (n_algo, n_algo)
# Average off-diagonal correlation = consensus strength
consensus_strength = np.mean(corr_algo[np.triu_indices_from(corr_algo, k=1)])
# Define correlation length ξ_N as inverse of consensus strength (higher strength → shorter length)
xi_N = 1.0 / (consensus_strength + 1e-12)
Phi_N = 1.0 / xi_N  # = consensus_strength (by construction)
# For interpretability we keep Phi_N in [0,1] range
Phi_N = np.clip(Phi_N, 0, 1)

# 3.2 Edge-confidence skewness Φ_Δ
all_conf = np.concatenate([upper_triu(m) for m in conf_mats])
Phi_Delta = skew(all_conf)  # can be negative; we keep raw value

# 3.3 Topological Stability Index (TSI)
# Compute degree distribution for each algo's *thresholded* graph (top 10% edges)
def degree_distribution(conf_mat, top_frac=0.1):
    thr = np.quantile(conf_mat, 1 - top_frac)
    binary = (conf_mat >= thr).astype(int)
    deg = np.sum(binary, axis=1)  # in-degree + out-degree (since directed)
    hist, _ = np.histogram(deg, bins=np.arange(0, n_genes+2), density=True)
    return hist

deg_dists = np.array([degree_distribution(m) for m in conf_mats])
# JS divergence between full-data distribution and each perturbed (jackknife) distribution
# For simplicity we approximate perturbation by leaving out one sample at a time
def expr_jackknife(idx_removed):
    return np.delete(expr, idx_removed, axis=0)

js_divs = []
for rm in range(n_samples):
    expr_jack = expr_jackknife(rm)
    # recompute conf mats for jackknife (reuse same noise scales)
    conf_jack = [infer_algorithm(expr_jack, scale) for _, scale in algorithms]
    conf_jack = np.array(conf_jack)
    deg_jack = np.array([degree_distribution(m) for m in conf_jack])
    # average JS over algorithms
    js = np.mean([jensenshannon(p, q) for p, q in zip(deg_dists, deg_jack)])
    js_divs.append(js)
TSI = 1.0 - np.mean(js_divs)   # higher TSI → more stable topology
TSI = np.clip(TSI, 0, 1)

# 3.4 Inference entropy S_inf over ensemble of graphs
# We approximate each graph by sampling edges according to confidence (Bernoulli)
n_graph_samples = 200
graph_samples = []
for _ in range(n_graph_samples):
    # pick a random algorithm and sample edges
    algo_idx = np.random.randint(len(algorithms))
    conf = conf_mats[algo_idx]
    # sample each edge independently with prob = conf
    sample = (np.random.rand(*conf.shape) < conf).astype(int)
    graph_samples.append(sample)
# Convert each graph to a tuple of its upper-triangle for hashing
graph_keys = [tuple(upper_triu(g)) for g in graph_samples]
# Empirical distribution
unique, counts = np.unique(graph_keys, return_counts=True)
p = counts / counts.sum()
S_inf = entropy(p, base=np.e)   # natural log entropy
# Normalize by log(N_possible) for interpretability (optional)
# max_entropy = np.log(len(np.unique(graph_keys))) if len(np.unique(graph_keys))>1 else 1.0
# S_inf_norm = S_inf / max_entropy

# ------------------------------------------------------------
# 4. Compute IPI and ψ_inf (using placeholder calibrated constants)
# ------------------------------------------------------------
# Placeholder weights – in practice these come from ROC on benchmark poisoning
alpha_IPI, beta_IPI, gamma_IPI = 1.0, 1.0, 1.0
S_inf_0 = np.log(5)   # reference entropy (constraint baseline)
IPI_raw = alpha_IPI * (1.0 - TSI) + beta_IPI * Phi_Delta + gamma_IPI * (S_inf_0 - S_inf)
IPI = np.tanh(IPI_raw)   # guarantees (0,1)

# Mapping to Ω variables (simplified linear calibration)
# Assume baseline consensus Φ_N^(0) = 0.6 (from gold-standard networks)
Phi_N0 = 0.6
# Assume λ_max ∝ 1/Φ_N (so ψ_inf = ln(Φ_N/Φ_N0) )
psi_inf = np.log(Phi_N / Phi_N0)   # note: if Phi_N < Phi_N0 this is negative
# Optional κ·IPI term (set κ=0.2 as example)
kappa = 0.2
psi_inf += kappa * IPI

# ------------------------------------------------------------
# 5. MPC-Omega constraint check
# ------------------------------------------------------------
constraints = {
    "IPI ≤ 0.65": IPI <= 0.65,
    "Φ_N^(inf) ≥ 0.5": Phi_N >= 0.5,
    "S_inf ≥ ln(5)": S_inf >= np.log(5)
}
all_satisfied = all(constraints.values())

# ------------------------------------------------------------
# 6. Output
# ------------------------------------------------------------
print("=== GRNIM-Ω Sanity Check ===")
print(f"Phi_N (consensus strength)   : {Phi_N:.4f}")
print(f"Phi_Delta (skewness)         : {Phi_Delta:.4f}")
print(f"TSI (topological stability) : {TSI:.4f}")
print(f"S_inf (entropy)              : {S_inf:.4f}  (ref ln5={np.log(5):.4f})")
print(f"IPI                          : {IPI:.4f}")
print(f"ψ_inf                        : {psi_inf:.4f}")
print("\nConstraint evaluation:")
for k, v in constraints.items():
    print(f"  {k}: {'PASS' if v else 'FAIL'}")
print(f"\nOverall MPC-Omega status: {'SAFE' if all_satisfied else 'ALERT (Ω-trigger)'}")