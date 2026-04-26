# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
# -*- coding: utf-8 -*-
"""
IsomorphicAttackGraph.py
Demonstrates how ATS‑Ω's topological invariants fail to catch a semantic trap.
"""
import numpy as np
import networkx as nx
import math
import random

# ------------------------------------------------------------
# 1. Build two graphs with identical topology (same nodes/edges)
# ------------------------------------------------------------
def build_safe():
    G = nx.DiGraph()
    G.add_node(0, op='input')
    G.add_node(1, op='add')
    G.add_node(2, op='mul')
    G.add_node(3, op='output')
    G.add_edges_from([(0,1), (1,2), (2,3)])
    return G

def build_malicious():
    G = nx.DiGraph()
    G.add_node(0, op='input')
    G.add_node(1, op='add')
    # Semantic trap: division by zero (same degree as mul)
    G.add_node(2, op='div')
    G.add_node(3, op='output')
    G.add_edges_from([(0,1), (1,2), (2,3)])
    return G

# ------------------------------------------------------------
# 2. Topological invariants (Betti numbers + Ricci curvature)
# ------------------------------------------------------------
def topological_signature(G):
    # Undirected view for invariants
    H = nx.to_undirected(G)
    n, m = H.number_of_nodes(), H.number_of_edges()
    c = nx.number_connected_components(H)
    beta0 = c
    beta1 = m - n + c   # cyclomatic number

    # Approximate Ricci curvature per edge (simple degree‑based)
    ricci = {}
    for u, v in H.edges():
        ricci[(u, v)] = 2 - H.degree(u) - H.degree(v)
    total_curvature = sum(abs(v) for v in ricci.values())
    return beta0, beta1, total_curvature, ricci

# ------------------------------------------------------------
# 3. ATS‑Ω's Algorithmic Topology Integrity (ATI) metric
# ------------------------------------------------------------
def ati(G, G_ref, S_alg):
    # Curvature preservation ratio
    _, _, curv, _ = topological_signature(G)
    _, _, curv_ref, _ = topological_signature(G_ref)
    curv_ratio = curv / curv_ref if curv_ref != 0 else 1.0

    # Cycle integrity ratio (beta1)
    _, beta1, _, _ = topological_signature(G)
    _, beta1_ref, _, _ = topological_signature(G_ref)
    cycle_ratio = beta1 / beta1_ref if beta1_ref != 0 else 1.0

    # Path‑diversity penalty (entropy term)
    ati_val = curv_ratio * cycle_ratio * math.exp(-S_alg)
    return ati_val

# ------------------------------------------------------------
# 4. Measurement poisoning simulator
# ------------------------------------------------------------
def poisoned_measurements(G, attack=False, noise_scale=0.1):
    """
    Simulates the integrity field B_i (one per node).
    Under attack, we artificially inflate variance (Φ_N) and
    suppress entropy (S_alg) to keep ATI high.
    """
    n = G.number_of_nodes()
    # Base integrity = 1 (safe)
    B = np.ones(n)

    if attack:
        # Adversary injects large timing noise -> inflates Φ_N
        B += np.random.normal(scale=5.0, size=n)
        # Force low entropy by making all nodes look identical
        S_alg = 0.01
    else:
        B += np.random.normal(scale=noise_scale, size=n)
        S_alg = 0.5   # normal entropy

    # Covariance matrix (diagonal for simplicity)
    cov = np.diag(np.var(B) * np.ones(n))
    eigenvals = np.linalg.eigvalsh(cov)
    phi_N = math.sqrt(max(eigenvals)) if eigenvals.size else 0.0

    # Skewness as a proxy for Φ_Δ
    mean, std = np.mean(B), np.std(B)
    skew = np.mean((B - mean)**3) / (std**3) if std > 0 else 0.0
    phi_Delta = skew

    return phi_N, phi_Delta, S_alg

# ------------------------------------------------------------
# 5. Shield decision logic
# ------------------------------------------------------------
def shield_decision(ati_val, phi_N):
    # ATS‑Ω thresholds from the proposal
    return ati_val >= 0.6 and phi_N >= 0.5

# ------------------------------------------------------------
# 6. Run the attack demonstration
# ------------------------------------------------------------
if __name__ == "__main__":
    random.seed(0)
    np.random.seed(0)

    # Reference graph (safe)
    G_ref = build_safe()

    # Safe case
    G_safe = build_safe()
    S_alg_safe = 0.5
    ati_safe = ati(G_safe, G_ref, S_alg_safe)
    phi_N_safe, _, _ = poisoned_measurements(G_safe, attack=False)

    # Malicious case (topologically identical but semantically trapped)
    G_mal = build_malicious()
    # Poison measurements to keep ATI high
    phi_N_mal, _, S_alg_mal = poisoned_measurements(G_mal, attack=True)
    ati_mal = ati(G_mal, G_ref, S_alg_mal)   # S_alg_mal is low (entropy suppressed)

    print("=== ATS‑Ω Shield Evaluation ===")
    print(f"Safe graph   – ATI: {ati_safe:.3f}, Φ_N: {phi_N_safe:.3f}")
    print(f"Malicious graph – ATI: {ati_mal:.3f}, Φ_N: {phi_N_mal:.3f}")

    safe_ok = shield_decision(ati_safe, phi_N_safe)
    mal_ok = shield_decision(ati_mal, phi_N_mal)

    print(f"Shield classifies safe graph as safe?   {safe_ok}")
    print(f"Shield classifies malicious graph as safe? {mal_ok}")

    if mal_ok:
        print("\n[DISRUPTION CONFIRMED] The shield fails to detect the semantic trap.")
        print("Topological invariants are blind to the division‑by‑zero payload.")
        print("Measurement poisoning masks the attack by inflating Φ_N and suppressing entropy.")
    else:
        print("\nShield correctly flagged the malicious graph.")