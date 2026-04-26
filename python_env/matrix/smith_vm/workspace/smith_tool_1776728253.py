# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
# -*- coding: utf-8 -*-
"""
CLTM-Ω Invariant Validator
--------------------------
Validates the mathematical soundness of the hidden‑layer Omega variables
derived from leaked PowerPoint data and enforces the Omega Protocol
invariants (Phi_N, Phi_Delta, J*).

Usage:
    python validate_cltm_omega.py   # runs a self‑test with dummy data
"""

import itertools
import math
from collections import defaultdict
from typing import Dict, List, Tuple, Set

import networkx as nx


# ----------------------------------------------------------------------
# Helper functions – darkness score and node aggregation
# ----------------------------------------------------------------------
def darkness_score(protected_slides: int, total_slides: int,
                   sensitive_terms: int) -> float:
    """
    Compute γ_d for a single document.
    γ_d = (protected_slides / total_slices) * log(1 + sensitive_terms)
    """
    if total_slides == 0:
        return 0.0
    return (protected_slides / total_slides) * math.log1p(sensitive_terms)


def aggregate_node_darkness(docs: List[Tuple[int, int, int]]) -> float:
    """
    Sum γ_d over all documents associated with a node.
    Each doc tuple = (protected_slides, total_slides, sensitive_terms)
    """
    return sum(darkness_score(p, t, s) for p, t, s in docs)


# ----------------------------------------------------------------------
# Core CLTM-Ω mathematics
# ----------------------------------------------------------------------
def build_hidden_network(node_docs: Dict[str, List[Tuple[int, int, int]]],
                         cooccur_threshold: int = 1) -> nx.Graph:
    """
    Build the hidden correlation network G_H.
    Nodes = financial entities.
    Edge weight = sum of γ_d for documents where both nodes co‑occur.
    """
    G = nx.Graph()
    # add nodes with darkness attribute
    for node, docs in node_docs.items():
        gamma = aggregate_node_darkness(docs)
        G.add_node(node, gamma=gamma)

    # co‑occurrence edges
    nodes = list(node_docs.keys())
    for i, j in itertools.combinations(nodes, 2):
        # simple co‑occurrence: if any document mentions both nodes
        # (in a real implementation we would parse slide text)
        shared = 0
        for docs in node_docs.values():
            # placeholder: assume each doc mentions all nodes for demo
            shared += len(docs)
        if shared >= cooccur_threshold:
            # edge weight = average darkness of the two nodes
            w = (node_docs[i][0][0] + node_docs[j][0][0]) / 2.0  # dummy
            G.add_edge(i, j, weight=w)
    return G


def percolation_failure(G: nx.Graph,
                        removal_fraction: float = 0.2) -> Tuple[int, int]:
    """
    Simulate random removal of a fraction of nodes proportional to their
    darkness (gamma). Returns (size_of_LCC, total_nodes).
    """
    if G.number_of_nodes() == 0:
        return 0, 0
    # removal probability weighted by gamma
    gammas = nx.get_node_attributes(G, 'gamma')
    total_gamma = sum(gammas.values())
    probs = {n: gammas[n] / total_gamma for n in G.nodes()}
    # select nodes to remove
    to_remove = set()
    for node, p in probs.items():
        if p * G.number_of_nodes() * removal_fraction > 0.5:  # crude threshold
            to_remove.add(node)
    G_copy = G.copy()
    G_copy.remove_nodes_from(to_remove)
    if G_copy.number_of_nodes() == 0:
        lcc_size = 0
    else:
        lcc = max(nx.connected_components(G_copy), key=len)
        lcc_size = len(lcc)
    return lcc_size, G.number_of_nodes()


def bottleneck_mincut(G: nx.Graph) -> Set[str]:
    """
    Find a minimum cut (bottleneck) using Stoer‑Wagner algorithm.
    Returns the set of nodes on the source side of the min cut.
    """
    if G.number_of_nodes() < 2:
        return set(G.nodes())
    cut_value, partition = nx.stoer_wagner(G)
    # partition is a tuple (setA, setB); we return the smaller side as bottleneck
    A, B = partition
    return A if len(A) <= len(B) else B


def compute_hidden_omega(node_docs: Dict[str, List[Tuple[int, int, int]]],
                         removal_fraction: float = 0.2) -> Dict[str, float]:
    """
    Compute Φ_N^(hidden), Φ_Δ^(hidden) and J* from the leaked data.
    """
    G = build_hidden_network(node_docs)
    # Φ_N hidden
    lcc_size, total_nodes = percolation_failure(G, removal_fraction)
    phi_N_hidden = 1.0 - (lcc_size / total_nodes if total_nodes > 0 else 0.0)

    # Φ_Δ hidden
    bottleneck = bottleneck_mincut(G)
    gamma_sum_total = sum(
        aggregate_node_darkness(docs) for docs in node_docs.values()
    )
    gamma_sum_bottleneck = sum(
        aggregate_node_darkness(node_docs[n]) for n in bottleneck
    )
    phi_Delta_hidden = (
        gamma_sum_bottleneck / gamma_sum_total
        if gamma_sum_total > 0 else 0.0
    )

    # J* (example invariant: product must stay below a threshold)
    J_star = phi_N_hidden * phi_Delta_hidden

    return {
        "phi_N_hidden": phi_N_hidden,
        "phi_Delta_hidden": phi_Delta_hidden,
        "J_star": J_star,
        "gamma_sum_total": gamma_sum_total,
        "bottleneck_size": len(bottleneck),
        "lcc_size": lcc_size,
        "total_nodes": total_nodes,
    }


# ----------------------------------------------------------------------
# Invariant enforcement (Omega Protocol)
# ----------------------------------------------------------------------
def validate_omega_invariants(metrics: Dict[str, float],
                              phi_N_min: float = 0.7,
                              j_star_max: float = 0.5) -> Tuple[bool, List[str]]:
    """
    Returns (is_valid, list_of_violations).
    """
    violations = []
    phi_N = metrics["phi_N_hidden"]
    phi_D = metrics["phi_Delta_hidden"]
    J = metrics["J_star"]

    if not (0.0 <= phi_N <= 1.0):
        violations.append(f"Phi_N_hidden out of bounds: {phi_N}")
    if not (0.0 <= phi_D <= 1.0):
        violations.append(f"Phi_Delta_hidden out of bounds: {phi_D}")
    if phi_N < phi_N_min:
        violations.append(
            f"Phi_N_hidden ({phi_N}) below MPC‑Ω stability floor ({phi_N_min})"
        )
    if J > j_star_max:
        violations.append(
            f"J* = Phi_N * Phi_Delta ({J}) exceeds allowed maximum ({j_star_max})"
        )
    return len(violations) == 0, violations


# ----------------------------------------------------------------------
# Self‑test with dummy data
# ----------------------------------------------------------------------
def _dummy_data() -> Dict[str, List[Tuple[int, int, int]]]:
    """
    Create a tiny synthetic dataset:
    - 4 institutions (A, B, C, D)
    - Each has 2‑3 dummy PowerPoint entries.
    """
    return {
        "A": [(2, 10, 5), (1, 8, 3)],          # moderate darkness
        "B": [(4, 12, 7), (0, 5, 0), (1, 9, 2)],
        "C": [(0, 6, 0), (1, 7, 1)],           # low darkness
        "D": [(3, 9, 4), (2, 10, 6)],          # high darkness
    }


def _run_self_test():
    data = _dummy_data()
    metrics = compute_hidden_omega(data, removal_fraction=0.25)
    print("=== CLTM-Ω Hidden‑Layer Metrics ===")
    for k, v in metrics.items():
        if isinstance(v, float):
            print(f"{k:20}: {v:.4f}")
        else:
            print(f"{k:20}: {v}")

    ok, violations = validate_omega_invariants(
        metrics, phi_N_min=0.7, j_star_max=0.5
    )
    print("\n=== Validation Result ===")
    if ok:
        print("PASS – All Omega Protocol invariants satisfied.")
    else:
        print("FAIL – Violations detected:")
        for v in violations:
            print(" -", v)


if __name__ == "__main__":
    _run_self_test()