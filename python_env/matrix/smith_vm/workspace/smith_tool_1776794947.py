# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
# -*- coding: utf-8 -*-
"""
Validation script for the Credential‑Graph Fragility Monitor (CGFM‑Ω) proposal.
It checks mathematical soundness and Omega‑Protocol invariant compliance.
"""

import math
import numpy as np
import networkx as nx

# ----------------------------------------------------------------------
# Helper functions (stand‑ins for the full Ollivier‑Ricci & spectral gap)
# ----------------------------------------------------------------------
def spectral_gap_laplacian(G: nx.Graph) -> float:
    """Return the smallest non‑zero eigenvalue of the normalized Laplacian."""
    L = nx.normalized_laplacian_matrix(G).astype(float)
    eigvals = np.linalg.eigvalsh(L.toarray())
    # eigenvalues are sorted ascending; first is 0 for connected graph
    return float(eigvals[1]) if len(eigvals) > 1 else 1.0

def ollivier_ricci_edge(G: nx.Graph, u, v) -> float:
    """
    Very rough approximation: Ollivier‑Ricci ≈ 1 - (distance(u,v) / (deg(u)+deg(v))).
    For an unweighted graph this yields a value in [-1,1].
    """
    du, dv = G.degree(u), G.degree(v)
    if du + dv == 0:
        return 0.0
    # shortest path length (should be 1 for an edge)
    d_uv = nx.shortest_path_length(G, source=u, target=v)
    return 1.0 - d_uv / (du + dv)

def average_ollivier_ricci(G: nx.Graph) -> float:
    curvatures = [ollivier_ricci_edge(G, u, v) for u, v in G.edges()]
    return np.mean(curvatures) if curvatures else 0.0

def key_service_bipartite_graph(keys, services, edges):
    """
    keys: iterable of key IDs
    services: iterable of service IDs
    edges: iterable of (key, service) tuples
    Returns a NetworkX graph with bipartite structure.
    """
    G = nx.Graph()
    G.add_nodes_from(keys, bipartite='keys')
    G.add_nodes_from(services, bipartite='services')
    G.add_edges_from(edges)
    return G

def shannon_entropy(dist):
    """dist: iterable of probabilities (should sum to 1)."""
    return -sum(p * math.log(p) for p in dist if p > 0)

# ----------------------------------------------------------------------
# Core CFI computation (as defined in the proposal)
# ----------------------------------------------------------------------
def compute_cfi(G: nx.Graph, key_usage_dist, alpha=0.3, beta=0.3, gamma=0.2, delta=0.2):
    """
    Returns CFI in [0,1] using the formula:
        CFI = tanh[ α * (Σ d_i^2 / Σ d_i) + β * (1/λ1) + γ * (avg |R|) + δ * (1 - S) ]
    """
    # degree sequence for key nodes only (bipartite assumption)
    key_nodes = [n for n, d in G.nodes(data=True) if d.get('bipartite') == 'keys']
    degs = [G.degree(n) for n in key_nodes]
    if not degs:
        deg_hetero = 0.0
    else:
        deg_hetero = (sum(d*d for d in degs) / sum(degs)) if sum(degs) > 0 else 0.0

    # spectral gap of the whole graph Laplacian
    lam1 = spectral_gap_laplacian(G)
    inv_gap = 1.0 / lam1 if lam1 > 0 else 0.0

    # average absolute Ollivier‑Ricci curvature
    avg_abs_curv = abs(average_ollivier_ricci(G))

    # entropy of key‑usage distribution
    S = shannon_entropy(key_usage_dist)
    entropy_loss = 1.0 - S  # S ∈ [0, log N]; we normalise by assuming max entropy = 1 for simplicity

    # linear combination (weights should be tuned; here we use example values)
    lin = (alpha * deg_hetero +
           beta * inv_gap +
           gamma * avg_abs_curv +
           delta * entropy_loss)

    # tanh maps ℝ → (-1,1); shift & scale to [0,1]
    cfi = (math.tanh(lin) + 1.0) / 2.0
    return max(0.0, min(1.0, cfi))  # enforce bounds numerically

# ----------------------------------------------------------------------
# Omega‑Protocol invariant checks
# ----------------------------------------------------------------------
def validate_omega_invariants(cfi, lam1, key_degs, S,
                              Phi_N0=0.8, Phi_Delta0=0.5,
                              eta1=0.4, eta2=0.2, eta3=0.3, eta4=0.1,
                              lambda_=0.5, R0=1.0):
    """
    Checks:
        * 0 ≤ CFI ≤ 1
        * Φ_N^{cred}, Φ_Δ^{cred} stay in [0,1]
        * ψ_cred is real (log of positive argument)
        * Entropy gauge A_μ = ∂_μ S is finite (we just check S≥0)
    """
    assert 0.0 <= cfi <= 1.0, f"CFI out of bounds: {cfi}"

    # Φ_N^{cred} = Φ_N0 - η1*CFI + η2*λ1
    Phi_N_cred = Phi_N0 - eta1 * cfi + eta2 * lam1
    assert 0.0 <= Phi_N_cred <= 1.0, f"Phi_N^{cred} out of bounds: {Phi_N_cred}"

    # Φ_Δ^{cred} = Φ_Δ0 + η3*(max deg / mean deg) - η4*S
    if key_degs:
        max_deg = max(key_degs)
        mean_deg = sum(key_degs) / len(key_degs)
        deg_ratio = max_deg / mean_deg if mean_deg > 0 else 0.0
    else:
        deg_ratio = 0.0
    Phi_Delta_cred = Phi_Delta0 + eta3 * deg_ratio - eta4 * S
    assert 0.0 <= Phi_Delta_cred <= 1.0, f"Phi_Delta^{cred} out of bounds: {Phi_Delta_cred}"

    # ψ_cred = ln(|Σ R_ij| / R0) + λ * CFI
    # Approximate Σ R_ij ≈ E * avg curvature
    avg_curv = average_ollivier_ricci(G) if 'G' in locals() else 0.0
    sum_R = abs(avg_curv * G.number_of_edges()) if 'G' in locals() else 0.0
    assert sum_R > 0.0, "Sum of curvatures must be positive for log"
    psi_cred = math.log(sum_R / R0) + lambda_ * cfi
    # ψ_cred can be any real; just ensure it's not NaN
    assert not math.isnan(psi_cred), "psi_cred is NaN"

    # Entropy gauge: A_μ = ∂_μ S ; we simply require S ≥ 0
    assert S >= 0.0, f"Entropy negative: {S}"

    return {
        "CFI": cfi,
        "Phi_N_cred": Phi_N_cred,
        "Phi_Delta_cred": Phi_Delta_cred,
        "psi_cred": psi_cred,
        "entropy": S
    }

# ----------------------------------------------------------------------
# Example usage with synthetic data
# ----------------------------------------------------------------------
if __name__ == "__main__":
    # Synthetic key‑service bipartite graph
    keys = [f"k{i}" for i in range(5)]
    services = [f"s{j}" for j in range(4)]
    edges = [
        ("k0", "s0"), ("k0", "s1"),
        ("k1", "s1"), ("k1", "s2"),
        ("k2", "s0"), ("k2", "s2"), ("k2", "s3"),
        ("k3", "s3"),
        ("k4", "s0"), ("k4", "s1"), ("k4", "s2"), ("k4", "s3")
    ]
    G = key_service_bipartite_graph(keys, services, edges)
    # Annotate bipartite attribute for later filtering
    for n in keys:
        G.nodes[n]["bipartite"] = "keys"
    for n in services:
        G.nodes[n]["bipartite"] = "services"

    # Synthetic key‑usage distribution (must sum to 1)
    usage = [0.4, 0.2, 0.15, 0.1, 0.15]  # corresponds to keys k0..k4
    assert abs(sum(usage) - 1.0) < 1e-9, "Usage distribution must sum to 1"

    # Compute CFI
    cfi_val = compute_cfi(G, usage, alpha=0.25, beta=0.25, gamma=0.25, delta=0.25)

    # Extract needed quantities for invariant validation
    key_degs = [G.degree(k) for k in keys]
    S_val = shannon_entropy(usage)
    lam1_val = spectral_gap_laplacian(G)

    # Run validation
    result = validate_omega_invariants(
        cfi=cfi_val,
        lam1=lam1_val,
        key_degs=key_degs,
        S=S_val,
        Phi_N0=0.8, Phi_Delta0=0.5,
        eta1=0.4, eta2=0.2, eta3=0.3, eta4=0.1,
        lambda_=0.5, R0=1.0
    )

    print("Validation passed. Computed quantities:")
    for k, v in result.items():
        print(f"  {k}: {v:.4f}")