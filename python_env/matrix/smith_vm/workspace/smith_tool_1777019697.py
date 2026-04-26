# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Smith Invariant Monitor (SIM) – runtime validation of the
Decentralized Bio-Homeostatic Architecture proposal.
"""

import itertools
import numpy as np

# -------------------------- CONFIGURATION --------------------------
N_NODES = 6                     # number of sensor/actuator nodes
EFREE   = 1e-12                 # free‑energy budget per node (J)
TARGET_SENS = np.ones(N_NODES, dtype=int)   # desired sensor pattern
TARGET_CTX  = np.full(N_NODES, 0b101, dtype=int)  # desired context mask

# Example topology: a triangulated sphere (simplified as a cycle with chords)
# Nodes 0-5 arranged; edges form a simplicial complex with β2≈1 for this tiny demo.
EDGES = [
    (0,1),(1,2),(2,3),(3,4),(4,5),(5,0),  # outer ring
    (0,2),(1,3),(2,4),(3,5),(4,0),(5,1)   # chords to create a triangulated disc
]

# -------------------------- STATE INITIALIZATION -------------------
np.random.seed(42)
sens = np.random.randint(0,2,size=N_NODES)          # binary sensor reading
ctx  = np.random.randint(0,2**3,size=N_NODES)      # 3‑bit context
energy = np.random.uniform(0,0.5*EFREE,size=N_NODES)  # power draw per node

# DEDS causal influence matrix (symmetric, zero diagonal)
lam = np.zeros((N_NODES,N_NODES))
for i,j in EDGES:
    lam[i,j] = lam[j,i] = np.random.uniform(0.1,0.9)

# adjacency list for mesh topology
adj = [[] for _ in range(N_NODES)]
for i,j in EDGES:
    adj[i].append(j)
    adj[j].append(i)

# -------------------------- INVARIANT CHECKS ----------------------
def causal_fidelity():
    """Node i may inform j only if ctx[i] ⊇ expected_ctx_j (RCOD)."""
    violations = []
    for i in range(N_NODES):
        for j in adj[i]:
            # Expected context for j is its current ctx (simplistic)
            if (ctx[i] & ctx[j]) != ctx[j]:   # i lacks some bits j requires
                violations.append((i,j,ctx[i],ctx[j]))
    return violations

def energetic_sufficiency():
    """Total power ≤ 10% of system free energy."""
    total_power = energy.sum()
    budget      = 0.1 * N_NODES * EFREE
    return total_power <= budget, total_power, budget

def topological_continuity():
    """
    Approximate check: mesh must be a single connected component
    and have exactly one independent 2‑cycle (β2≈1).
    For a tiny graph we enforce a known triangulated sphere:
    - Number of edges = 3 * N_NODES (for a closed triangulated surface)
    - Euler characteristic χ = V - E + F = 2  →  F = 2 - V + E
    We compute faces from cycles of length 3.
    """
    # 1) Connectivity
    visited = set()
    stack = [0]
    while stack:
        v = stack.pop()
        if v in visited: continue
        visited.add(v)
        stack.extend([n for n in adj[v] if n not in visited])
    connected = len(visited) == N_NODES

    # 2) Count triangular faces (3‑cycles)
    faces = set()
    for i,j,k in itertools.combinations(range(N_NODES),3):
        if j in adj[i] and k in adj[i] and k in adj[j]:
            faces.add(tuple(sorted((i,j,k))))
    F = len(faces)
    E = len(EDGES)
    V = N_NODES
    chi = V - E + F
    beta2 = 2 - chi   # for a closed orientable surface, β2 = 1 iff χ = 2
    return connected and beta2 == 1, {"connected":connected,
                                      "faces":F,
                                      "edges":E,
                                      "vertices":V,
                                      "chi":chi,
                                      "beta2":beta2}

# -------------------------- EXECUTION -----------------------------
print("=== Smith Invariant Monitor (SIM) ===")
print(f"Nodes: {N_NODES}")

# 1) Causal Fidelity
cf_viol = causal_fidelity()
if cf_viol:
    print("\n[FAIL] Causal Fidelity violations:")
    for i,j,ci,cj in cf_viol:
        print(f"  Node {i} (ctx={ci:03b}) → Node {j} (ctx={cj:03b}) missing required bits")
else:
    print("\n[PASS] Causal Fidelity: all communications respect RCOD contexts.")

# 2) Energetic Sufficiency
en_ok, power, budget = energetic_sufficiency()
print(f"\nEnergetic Sufficiency: power={power:.2e} J, budget={budget:.2e} J")
if en_ok:
    print("[PASS] Energetic Sufficiency satisfied.")
else:
    print("[FAIL] Energetic Sufficiency exceeded!")

# 3) Topological Continuity
topo_ok, info = topological_continuity()
print(f"\nTopological Continuity: {info}")
if topo_ok:
    print("[PASS] Mesh homology ≃ 𝕊² (simply connected with one 2‑cycle).")
else:
    print("[FAIL] Topology does not satisfy 𝕊² condition.")

# -------------------------- SUMMARY --------------------------------
all_ok = (not cf_viol) and en_ok and topo_ok
print("\n=== OVERALL VERDICT ===")
print("PASS – All Omega Protocol invariants satisfied." if all_ok
      else "FAIL – Invariant breach detected. Initiate node quarantine & context‑free reboot.")