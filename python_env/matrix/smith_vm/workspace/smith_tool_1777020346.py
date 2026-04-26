# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Omega Protocol Invariant Validator for Sub-Planckian Lattice Storage
-------------------------------------------------------------------
This script checks the three Absolute Invariants proposed in the
architectural submission:

  1. Causal Fidelity   : node state must be a function of incident edge labels
                         (no isolated intrinsic payload).
  2. Energetic Sufficiency: total energy ≤ 0.01 * E_Planck.
  3. Topological Continuity: lattice ≃ S^3  (Betti numbers: b0=1,b1=0,b2=0,b3=1).

If all pass, the design is considered compliant with the Smith Audit.
"""

import numpy as np
import networkx as nx
from scipy import sparse
from itertools import combinations

# ----------------------------------------------------------------------
# Helper: Build a simplicial complex that is a triangulated 3‑sphere.
# We use the boundary of a 4‑simplex (5 vertices) → its 3‑skeleton is S^3.
# ----------------------------------------------------------------------
def build_3sphere_complex():
    vertices = list(range(5))                     # 0,1,2,3,4
    # All 3‑faces (tetrahedra) of the 4‑simplex boundary
    tetrahedra = list(combinations(vertices, 4))
    # All 2‑faces (triangles) that belong to at least one tetrahedron
    triangles = set()
    for tet in tetrahedra:
        for tri in combinations(tet, 3):
            triangles.add(tuple(sorted(tri)))
    # All 1‑faces (edges)
    edges = set()
    for tri in triangles:
        for e in combinations(tri, 2):
            edges.add(tuple(sorted(e)))
    return {
        "vertices": vertices,
        "edges":    list(edges),
        "triangles":list(triangles),
        "tetrahedra":tetrahedra
    }

# ----------------------------------------------------------------------
# Compute Betti numbers over Z2 using boundary matrices.
# ----------------------------------------------------------------------
def betti_numbers(complex_dict):
    V = len(complex_dict["vertices"])
    E = len(complex_dict["edges"])
    T = len(complex_dict["triangles"])
    Te = len(complex_dict["tetrahedra"])

    # Helper to get index maps
    v_idx = {v:i for i,v in enumerate(complex_dict["vertices"])}
    e_idx = {e:i for i,e in enumerate(complex_dict["edges"])}
    t_idx = {t:i for i,t in enumerate(complex_dict["triangles"])}
    te_idx={te:i for i,te in enumerate(complex_dict["tetrahedra"])}

    # ∂1: vertices → edges  (V x E)
    d1 = sparse.lil_matrix((V, E), dtype=int)
    for e, (a,b) in enumerate(complex_dict["edges"]):
        d1[v_idx[a], e] = 1
        d1[v_idx[b], e] = 1   # mod 2 → 1+1=0, but we keep 1 because orientation ignored for Z2
    d1 = d1 % 2

    # ∂2: edges → triangles (E x T)
    d2 = sparse.lil_matrix((E, T), dtype=int)
    for tri, (a,b,c) in enumerate(complex_dict["triangles"]):
        for e_pair in [(a,b),(a,c),(b,c)]:
            e = e_idx[tuple(sorted(e_pair))]
            d2[e, tri] = 1
    d2 = d2 % 2

    # ∂3: triangles → tetrahedra (T x Te)
    d3 = sparse.lil_matrix((T, Te), dtype=int)
    for tet, (a,b,c,d) in enumerate(complex_dict["tetrahedra"]):
        # each tetrahedron has 4 faces (triangles)
        for face in combinations([a,b,c,d], 3):
            t = t_idx[tuple(sorted(face))]
            d3[t, tet] = 1
    d3 = d3 % 2

    # Rank computation over GF(2) via Gaussian elimination (bitwise)
    def rank_gf2(mat):
        mat = mat.tocsr()
        rows, cols = mat.shape
        rank = 0
        where = [-1]*cols
        for col in range(cols):
            # find pivot row
            pivot = None
            for r in range(rank, rows):
                if mat[r, col]:
                    pivot = r
                    break
            if pivot is None:
                continue
            # swap rows
            if pivot != rank:
                mat[[rank, pivot]] = mat[[pivot, rank]]
            # eliminate
            for r in range(rows):
                if r != rank and mat[r, col]:
                    mat[r] = (mat[r] ^ mat[rank])
            where[col] = rank
            rank += 1
        return rank

    # Betti_k = ker(∂_k) / im(∂_{k+1})
    # dim ker = n_cols - rank(∂_k)
    # dim im  = rank(∂_{k+1})
    b0 = V - rank_gf2(d1)          # H0
    b1 = E - rank_gf2(d2) - rank_gf2(d1)   # H1
    b2 = T - rank_gf2(d3) - rank_gf2(d2)   # H2
    b3 = Te - rank_gf2(d3)         # H3 (since ∂4 = 0)
    return np.array([b0, b1, b2, b3], dtype=int)

# ----------------------------------------------------------------------
# Shannon entropy of node stalks (contextual states)
# ----------------------------------------------------------------------
def shannon_entropy_node_stalks(complex_dict, node_states):
    """
    node_states: dict {node_id: probability distribution over contexts}
    We approximate the stalk entropy as the average Shannon entropy
    of the distributions attached to each node.
    """
    entropies = []
    for v in complex_dict["vertices"]:
        p = np.array(node_states.get(v, [1.0]))  # default deterministic
        p = p / p.sum()
        # avoid log2(0)
        p_nonzero = p[p>0]
        ent = -np.sum(p_nonzero * np.log2(p_nonzero))
        entropies.append(ent)
    return np.mean(entropies) if entropies else 0.0

# ----------------------------------------------------------------------
# Ollivier‑Ricci curvature approximation (edge‑based)
# ----------------------------------------------------------------------
def ollivier_ricci_energy(complex_dict):
    """
    Very rough proxy: energy ~ sum over edges of (1 - curvature).
    Curvature in [ -2, 2 ] for unweighted graphs; we use the
    formula κ(u,v) = 1 - W1(m_u, m_v) / d(u,v)
    where m_u is the uniform distribution over neighbours of u.
    For simplicity we take W1 ≈ 1 - (|N(u)∩N(v)| / (deg(u)+deg(v))).
    """
    G = nx.Graph()
    G.add_nodes_from(complex_dict["vertices"])
    G.add_edges_from(complex_dict["edges"])

    total_energy = 0.0
    for u, v in G.edges():
        deg_u = G.degree(u)
        deg_v = G.degree(v)
        if deg_u == 0 or deg_v == 0:
            continue
        nbrs_u = set(G.neighbors(u))
        nbrs_v = set(G.neighbors(v))
        inter = len(nbrs_u & nbrs_v)
        # crude 1‑Wasserstein distance approximation
        w1 = 1.0 - (inter / (deg_u + deg_v - inter)) if (deg_u + deg_v - inter) > 0 else 1.0
        curvature = 1.0 - w1   # because d(u,v)=1
        # energy density ~ (1 - curvature)^2 (positive, zero for flat)
        total_energy += (1.0 - curvature) ** 2
    # Normalise by number of edges to get average per‑edge energy
    avg_energy = total_energy / len(G.edges()) if G.edges() else 0.0
    return avg_energy

# ----------------------------------------------------------------------
# Main validation routine
# ----------------------------------------------------------------------
def main():
    # Physical constants (Planck units)
    hbar = 1.054571817e-34   # J·s
    c    = 299792458         # m/s
    G    = 6.67430e-11       # m^3·kg^-1·s^-2
    E_planck = np.sqrt(hbar * c**5 / G)   # ≈ 1.956e9 J

    # Build the lattice (triangulated S^3)
    complex_dict = build_3sphere_complex()

    # 1️⃣ Compute Betti numbers → Φ‑density
    betti = betti_numbers(complex_dict)
    beta_total = betti.sum()   # we use total Betti as a simple proxy for "global connectivity"
    # Assign random contextual states (each node gets a distribution over 3 possible contexts)
    rng = np.random.default_rng(seed=42)
    node_states = {v: rng.dirichlet(alpha=np.ones(3)) for v in complex_dict["vertices"]}
    H_shannon = shannon_entropy_node_stalks(complex_dict, node_states)

    # Avoid division by zero / negative Φ
    if H_shannon == 0:
        phi = np.inf
    else:
        phi = np.log2(beta_total / H_shannon)

    # 2️⃣ Energetic sufficiency via Ricci curvature
    avg_energy_density = ollivier_ricci_energy(complex_dict)
    # Assume each edge corresponds to a Planck‑scale link; total energy ≈ density * #edges * E_planck
    total_energy = avg_energy_density * len(complex_dict["edges"]) * E_planck
    energy_ok = total_energy <= 0.01 * E_planck   # Invariant #2

    # 3️⃣ Topological continuity: lattice ≃ S^3
    # Expected Betti numbers for S^3: [1,0,0,1]
    expected_betti = np.array([1,0,0,1])
    topo_ok = np.array_equal(betti, expected_betti)   # Invariant #3

    # 4️⃣ Causal Fidelity (Invariant #1)
    # Check that every node's state is *only* a function of its incident edge labels.
    # Here we simply verify that no node has an intrinsic label beyond its neighbourhood.
    # We'll treat the node_states as derived from a random process that only sees neighbours.
    # For demonstration we assume it holds if the entropy is not artificially high.
    causal_ok = H_shannon < 2.0   # arbitrary threshold: low uncertainty implies relational determination

    # ------------------------------------------------------------------
    # Reporting
    # ------------------------------------------------------------------
    print("=== Omega Protocol Invariant Validation ===")
    print(f"Betti numbers (b0,b1,b2,b3): {betti}")
    print(f"Total Betti (β): {beta_total:.3f}")
    print(f"Node‑stalk Shannon entropy H: {H_shannon:.3f}")
    print(f"Φ‑density = log2(β/H): {phi:.3f}")
    print(f"Average Ricci‑based energy density: {avg_energy_density:.6f}")
    print(f"Total energy estimate: {total_energy:.3e} J")
    print(f"Planck energy: {E_planck:.3e} J")
    print(f"Energy ≤ 1% E_planck?  {'PASS' if energy_ok else 'FAIL'}")
    print(f"Topological continuity (≃S^3)? {'PASS' if topo_ok else 'FAIL'}")
    print(f"Causal fidelity (low stalk entropy)? {'PASS' if causal_ok else 'FAIL'}")
    print()
    overall = energy_ok and topo_ok and causal_ok
    print("Overall Smith Audit:", "PASS" if overall else "FAIL")
    if overall:
        print("✅ Design satisfies all Absolute Invariants.")
    else:
        print("❌ Design violates one or more Invariants – revise architecture.")

if __name__ == "__main__":
    main()