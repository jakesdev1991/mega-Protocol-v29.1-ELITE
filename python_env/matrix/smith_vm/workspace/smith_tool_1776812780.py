# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
#!/usr/bin/env python3
"""
ETS-Ω Invariant Validator
-------------------------
Validates that a given protocol snapshot satisfies the Omega Protocol
invariants (Phi_N, Phi_Delta, psi) and the ETS-Ω MPC constraints.
"""

import math
import numpy as np
import networkx as nx
from typing import Dict, Tuple

# ----------------------------------------------------------------------
# Helper functions (topological metrics)
# ----------------------------------------------------------------------
def betweenness_centrality(G: nx.DiGraph) -> Dict[str, float]:
    """Normalized betweenness (in [0,1])."""
    return nx.betweenness_centrality(G, normalized=True, weight='weight')

def modularity(G: nx.DiGraph, weight='weight') -> float:
    """Newman-Girvan modularity for directed graphs (approx)."""
    # Use community detection via Louvain (requires python-louvain). 
    # For simplicity, we approximate with the fraction of intra‑community weight.
    try:
        import community as community_louvain  # pip install python-louvain
    except ImportError:
        raise RuntimeError("python-louvain package required for modularity")
    # Convert to undirected for community detection (common approximation)
    G_und = nx.Graph(G)
    partition = community_louvain.best_partition(G_und, weight=weight)
    return community_louvain.modularity(partition, G_und, weight=weight)

def flow_entropy(G: nx.DiGraph) -> Tuple[float, Dict[Tuple[str,str], float]]:
    """Shannon entropy of normalized edge flows."""
    flows = np.array([data.get('weight', 1.0) for _, _, data in G.edges(data=True)], dtype=float)
    total = flows.sum()
    if total == 0:
        return 0.0, {}
    probs = flows / total
    # Avoid log(0)
    probs = np.where(probs > 0, probs, 1e-12)
    S = -np.sum(probs * np.log(probs))
    # Map back to edge->prob for possible inspection
    edge_prob = {(u, v): p for (u, v, _), p in zip(G.edges(data=False), probs)}
    return float(S), edge_prob

def clustering_coefficient(G: nx.DiGraph, weight='weight') -> float:
    """Average weighted clustering coefficient (Newman 2001)."""
    return nx.average_clustering(G.to_undirected(), weight=weight)

# ----------------------------------------------------------------------
# ETS‑Ω core calculations
# ----------------------------------------------------------------------
def compute_ets_metrics(G: nx.DiGraph,
                        Phi_N0: float = 1.0,
                        Phi_Delta0: float = 0.0,
                        eta1: float = 0.3,
                        eta2: float = 0.2,
                        eta3: float = 0.25,
                        eta4: float = 0.15,
                        lam: float = 0.5,
                        C0: float = 0.1) -> Dict[str, float]:
    """
    Returns a dict with ETI, Phi_N, Phi_Delta, psi, S_econ, and auxiliary metrics.
    """
    # Topological quantities
    bet = betweenness_centrality(G)
    max_bet = max(bet.values()) if bet else 1.0
    mod = modularity(G)
    S_econ, _ = flow_entropy(G)
    clust = clustering_coefficient(G)

    # ETI ∈ [0,1]
    ETI = (1.0 / max_bet) * mod * math.exp(-S_econ)

    # Phi_N and Phi_Delta (using lagged values approximated by current snapshot)
    Phi_N = Phi_N0 - eta1 * (1.0 - ETI) + eta2 * mod
    Phi_Delta = Phi_Delta0 + eta3 * (np.std(list(bet.values())) if bet else 0.0) - eta4 * ETI

    # psi_econ (two equivalent forms)
    psi_from_Phi = math.log(Phi_N / Phi_N0) if Phi_N > 0 else -float('inf')
    psi_from_clust = math.log(clust / C0) + lam * ETI if clust > 0 else -float('inf')
    # In practice they should match; we keep the Phi‑based version as canonical
    psi = psi_from_Phi

    return {
        "ETI": ETI,
        "max_betweenness": max_bet,
        "modularity": mod,
        "flow_entropy": S_econ,
        "clustering": clust,
        "Phi_N": Phi_N,
        "Phi_Delta": Phi_Delta,
        "psi": psi,
        "psi_from_clust": psi_from_clust,
    }

# ----------------------------------------------------------------------
# Invariant & constraint checker
# ----------------------------------------------------------------------
def validate_ets(snapshot: nx.DiGraph) -> Tuple[bool, str]:
    """
    Returns (pass, message).  pass=True if all Omega invariants and ETS‑Ω constraints hold.
    """
    metrics = compute_ets_metrics(snapshot)

    # Omega invariants: single, well‑defined (we already have scalar values)
    # Additional physics‑based sanity: Phi_N > 0 (for log), S_econ >= 0
    if metrics["Phi_N"] <= 0:
        return False, f"Phi_N non-positive ({metrics['Phi_N']:.4f}) -> log undefined"

    # ETS‑Ω MPC constraints (hard bounds)
    constraints = [
        ("ETI >= 0.6", metrics["ETI"] >= 0.6),
        ("Phi_N >= 0.5", metrics["Phi_N"] >= 0.5),
        ("S_econ >= ln(2)", metrics["flow_entropy"] >= math.log(2)),
    ]

    failed = [desc for desc, ok in constraints if not ok]
    if failed:
        return False, f"Failed constraints: {', '.join(failed)}"

    # Optional: check that psi from two formulations agree (tolerance)
    if not math.isclose(metrics["psi"], metrics["psi_from_clust"], rel_tol=1e-3, abs_tol=1e-3):
        return False, f"psi inconsistency: Phi-based {metrics['psi']:.4f} vs clust-based {metrics['psi_from_clust']:.4f}"

    return True, "All Omega invariants and ETS‑Ω constraints satisfied."

# ----------------------------------------------------------------------
# Example usage (synthetic protocol graph)
# ----------------------------------------------------------------------
if __name__ == "__main__":
    # Build a simple directed weighted graph representing a DeFi protocol:
    #   nodes: contracts, oracles, governance, bridge
    #   edges: token flows (weight = volume), governance influence, data feed
    G = nx.DiGraph()
    G.add_edge("LoanContract", "Oracle", weight=12.0)   # data feed
    G.add_edge("Oracle", "LoanContract", weight=1.0)    # feedback
    G.add_edge("LoanContract", "Governance", weight=5.0)# influence
    G.add_edge("Governance", "LoanContract", weight=3.0)# control
    G.add_edge("Bridge", "LoanContract", weight=8.0)    # liquidity inflow
    G.add_edge("LoanContract", "Bridge", weight=7.0)    # outflow

    passed, msg = validate_ets(G)
    print("ETS‑Ω Validation Result:", "PASS" if passed else "FAIL")
    print("Message:", msg)
    print("\nMetrics:")
    for k, v in compute_ets_metrics(G).items():
        if isinstance(v, float):
            print(f"  {k}: {v:.4f}")