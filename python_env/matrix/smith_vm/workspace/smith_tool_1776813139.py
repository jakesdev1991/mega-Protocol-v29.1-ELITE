# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GRNIM-Ω mathematical compliance checker.
Validates the internal consistency of the proposed invariants and QP constraints.
"""

import numpy as np
from scipy.stats import skew, entropy
from scipy.spatial.distance import jensenshannon

# -------------------------- Synthetic data generation --------------------------
def generate_synthetic_ensemble(M=5, B=120, G=50, poison_level=0.0):
    """
    M   : number of inference algorithms
    B   : number of bootstrap slices
    G   : number of genes (=> G*(G-1)/2 possible directed edges)
    poison_level : fraction of edges whose confidence is deliberately shifted
    Returns:
        confs : shape (M, B, E) edge-confidence matrices in [0,1]
    """
    E = G * (G - 1)  # directed edges
    base = np.random.beta(2, 5, size=(M, B, E))  # realistic sparse confidences
    if poison_level > 0:
        mask = np.random.rand(M, B, E) < poison_level
        base[mask] = np.clip(base[mask] + np.random.uniform(0.2, 0.5, size=mask.sum()), 0, 1)
    return base

# -------------------------- Metric implementations --------------------------
def consensus_correlation_length(confs):
    """
    Compute inverse correlation length ξ_N from pairwise Pearson correlation
    of confidence matrices across (algorithm, slice) dimension.
    Returns Φ_N = 1/ξ_N.
    """
    M, B, E = confs.shape
    # flatten to (M*B, E)
    flat = confs.reshape(M * B, E)
    # correlation matrix
    corr = np.corrcoef flat  # shape (M*B, M*B)
    # exclude self-correlation
    np.fill_diagonal(corr, 0)
    # average absolute correlation as proxy for inverse length
    xi_N = np.mean(np.abs(corr))
    # avoid division by zero
    return 1.0 / max(xi_N, 1e-8)

def edge_confidence_skewness(confs):
    """Skewness of the pooled confidence distribution."""
    return skew(confs.flatten())

def degree_distribution_from_conf(conf, threshold=0.5):
    """Binary adjacency from confidence > threshold, return out-degree distribution."""
    adj = (conf > threshold).astype(int)
    out_deg = adj.sum(axis=1)  # shape (G,)
    # histogram normalized
    hist, _ = np.histogram(out_deg, bins=np.arange(-0.5, adj.shape[1]+1.5), density=True)
    return hist

def topological_stability_index(confs, threshold=0.5):
    """
    TSI = 1 - JSD( P_deg(full) || P_deg(pert) )
    where pert = jackknife leave-one-slice-out.
    """
    M, B, E = confs.shape
    G = int((1 + np.sqrt(1 + 4*E)) / 2)  # invert E = G*(G-1)
    # full-data confidence (average over algorithms & slices)
    conf_full = confs.mean(axis=(0,1))
    deg_full = degree_distribution_from_conf(conf_full, threshold)
    # jackknife: leave each slice out, recompute average, collect divergence
    jsds = []
    for b in range(B):
        conf_jk = confs[:, np.arange(B) != b, :].mean(axis=(0,1))
        deg_jk = degree_distribution_from_conf(conf_jk, threshold)
        jsd = jensenshannon(deg_full, deg_jk)
        jsds.append(jsd)
    TSI = 1.0 - np.mean(jsds)
    return np.clip(TSI, 0.0, 1.0)

def inference_entropy(confs, threshold=0.5):
    """
    Shannon entropy over the ensemble of inferred binary graphs.
    Each graph is treated as an equally likely sample.
    """
    M, B, E = confs.shape
    # binarize
    graphs = (confs > threshold).astype(int)  # (M,B,E)
    # flatten each graph to a bitstring and count unique occurrences
    flat = graphs.reshape(M * B, E)
    # convert rows to tuples for hashing
    unique, counts = np.unique([tuple(row) for row in flat], axis=0, return_counts=True)
    probs = counts / counts.sum()
    return entropy(probs, base=np.e)

def compute_IPI(TSI, Phi_Delta, S_inf, S0, alpha=1.0, beta=1.0, gamma=1.0):
    """IPI = tanh[ α(1-TSI) + β*Phi_Delta + γ*(S0 - S_inf) ]"""
    term = alpha * (1.0 - TSI) + beta * Phi_Delta + gamma * (S0 - S_inf)
    return np.tanh(term)

def linear_response_update(Phi_N_prev, Phi_Delta_prev, IPI_prev,
                           eta1=0.3, eta2=0.2, eta3=0.25, eta4=0.15,
                           Phi_N0=0.7, Phi_Delta0=0.1):
    """
    Φ_N(t) = Φ_N0 - η1·IPI(t-τ) + η2·TSI(t-τ)
    Φ_Δ(t) = Φ_Δ0 + η3·IPI(t-τ) - η4·S_inf(t-τ)
    For validation we approximate TSI and S_inf from current step.
    """
    # In a real implementation TSI and S_inf would be lagged; here we use same-step for simplicity.
    TSI = topological_stability_index(confs)  # placeholder, will be overwritten
    S_inf = inference_entropy(confs)
    Phi_N = Phi_N0 - eta1 * IPI_prev + eta2 * TSI
    Phi_Delta = Phi_Delta0 + eta3 * IPI_prev - eta4 * S_inf
    return Phi_N, Phi_Delta, TSI, S_inf

# -------------------------- Validation routine --------------------------
def validate_grnim_omega():
    global confs  # make accessible to helper functions
    np.random.seed(42)
    confs = generate_synthetic_ensemble(M=6, B=100, G=30, poison_level=0.02)

    # 1. Compute raw metrics
    Phi_N_raw = consensus_correlation_length(confs)
    Phi_Delta_raw = edge_confidence_skewness(confs)
    TSI = topological_stability_index(confs)
    S_inf = inference_entropy(confs)
    S0 = np.log(5)  # reference entropy

    # 2. IPI
    IPI = compute_IPI(TSI, Phi_Delta_raw, S_inf, S0, alpha=1.0, beta=1.0, gamma=1.0)

    # 3. Linear-response updated Φ's (using lag=0 for simplicity)
    Phi_N, Phi_Delta, TSI_used, S_inf_used = linear_response_update(
        Phi_N_raw, Phi_Delta_raw, IPI,
        eta1=0.3, eta2=0.2, eta3=0.25, eta4=0.15,
        Phi_N0=0.7, Phi_Delta0=0.1
    )
    # Overwrite TSI and S_inf used in the update (they should match the recomputed ones)
    TSI = TSI_used
    S_inf = S_inf_used

    # 4. Invariant ψ_inf from two definitions
    Phi_N0_baseline = 0.7  # baseline consensus from gold-standard
    psi_inf_consensus = np.log(Phi_N / Phi_N0_baseline)

    # Approximate λ_max via curvature of average log-posterior.
    # For a binary edge model with independent Bernoulli(p) priors,
    # log-posterior ∑ [x_ij log p_ij + (1-x_ij) log(1-p_ij)].
    # The Hessian w.r.t. p is diagonal with entries -[x_ij/p_ij^2 + (1-x_ij)/(1-p_ij)^2].
    # Its maximum magnitude (most negative) gives λ_max.
    avg_conf = confs.mean(axis=(0,1))
    # avoid zeros/ones
    avg_conf = np.clip(avg_conf, 1e-6, 1-1e-6)
    diag = -(avg_conf/(avg_conf**2) + (1-avg_conf)/((1-avg_conf)**2))
    lambda_max = -np.min(diag)  # positive curvature magnitude
    lambda0 = -np.min(-(Phi_N0_baseline/(Phi_N0_baseline**2) + (1-Phi_N0_baseline)/((1-Phi_N0_baseline)**2)))
    kappa = 1.0  # chosen to satisfy consistency
    psi_inf_curvature = np.log(lambda_max / lambda0) + kappa * IPI

    # 5. Check consistency
    tol = 1e-3
    invar_ok = np.abs(psi_inf_consensus - psi_inf_curvature) < tol

    # 6. QP constraints
    qp1 = IPI <= 0.65 + 1e-9
    qp2 = Phi_N >= 0.5 - 1e-9
    qp3 = S_inf >= np.log(5) - 1e-9

    # 7. Report
    print("=== GRNIM-Ω Validation Report ===")
    print(f"Phi_N (consensus)      : {Phi_N:.5f}")
    print(f"Phi_Delta (skewness)   : {Phi_Delta:.5f}")
    print(f"TSI                    : {TSI:.5f}")
    print(f"S_inf                  : {S_inf:.5f}  (ref ln5={np.log(5):.5f})")
    print(f"IPI                    : {IPI:.5f}")
    print(f"psi_inf (consensus)    : {psi_inf_consensus:.5f}")
    print(f"psi_inf (curvature)    : {psi_inf_curvature:.5f}")
    print(f"Invariant equality OK? : {invar_ok}")
    print(f"QP IPI ≤ 0.65?         : {qp1}  (IPI={IPI:.5f})")
    print(f"QP Phi_N ≥ 0.5?        : {qp2}  (Phi_N={Phi_N:.5f})")
    print(f"QP S_inf ≥ ln5?        : {qp3}  (S_inf={S_inf:.5f})")
    overall = invar_ok and qp1 and qp2 and qp3
    print(f"OVERALL COMPLIANCE    : {'PASS' if overall else 'FAIL'}")
    if not overall:
        print("\nViolations:")
        if not invar_ok:
            print(" - Invariant mismatch")
        if not qp1:
            print(" - IPI exceeds 0.65")
        if not qp2:
            print(" - Phi_N below 0.5")
        if not qp3:
            print(" - S_inf below ln(5)")
    return overall

if __name__ == "__main__":
    validate_grnim_omega()