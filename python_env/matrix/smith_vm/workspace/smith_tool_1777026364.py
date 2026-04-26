# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Omega Protocol Φ‑Density Validator for Sub‑Planckian Lattice Storage
--------------------------------------------------------------------
Assumes the proposal supplies:
    - nodes: list of node identifiers (e.g., integers)
    - edges: list of tuples (src, dst, weight) where weight > 0
      representing causal links with informational weight.
The graph must be a DAG (causal order preservation).
"""

from __future__ import annotations
import itertools
import math
from collections import defaultdict
from typing import List, Tuple, Dict

Number = float
Node = int
Edge = Tuple[Node, Node, Number]   # (src, dst, weight)

def is_dag(nodes: List[Node], edges: List[Edge]) -> bool:
    """Kahn's algorithm for DAG detection."""
    indeg: Dict[Node, int] = {n: 0 for n in nodes}
    adj: Dict[Node, List[Node]] = defaultdict(list)
    for u, v, _ in edges:
        adj[u].append(v)
        indeg[v] += 1
    zero = [n for n in nodes if indeg[n] == 0]
    cnt = 0
    while zero:
        n = zero.pop()
        cnt += 1
        for m in adj[n]:
            indeg[m] -= 1
            if indeg[m] == 0:
                zero.append(m)
    return cnt == len(nodes)

def compute_phi_n(edges: List[Edge]) -> Number:
    """Newtonian fidelity – log of total causal link count."""
    L = len(edges)
    return math.log(L + 1e-12)   # avoid log(0)

def compute_phi_delta(edges: List[Edge]) -> Number:
    """Differential entropy – Shannon entropy of normalized link weights."""
    if not edges:
        return 0.0
    total = sum(w for _, _, w in edges)
    probs = [w / total for _, _, w in edges]
    # Shannon entropy H = - Σ p log p
    return -sum(p * math.log(p + 1e-15) for p in probs)

def compute_j_star(edges: List[Edge]) -> Number:
    """Action‑like term – sum of causal link weights."""
    return sum(w for _, _, w in edges)

def smith_audit_pass(phi_n: Number, phi_delta: Number,
                     j_star: Number, edges: List[Edge],
                     nodes: List[Node]) -> Tuple[bool, List[str]]:
    """Check the six Smith Audit invariants."""
    fails = []
    # 1. Metric Non‑Degeneracy – approximated by non‑zero Jacobian of edge weights
    #    (here we simply require at least one edge with weight>0)
    if not any(w > 0 for _, _, w in edges):
        fails.append("Metric Non‑Degeneracy: all link weights zero.")
    # 2. Causal Order Preservation – DAG check
    if not is_dag(nodes, edges):
        fails.append("Causal Order Preservation: graph contains a cycle.")
    # 3. Identity Continuity – each node must have at least one incident edge
    incident = set()
    for u, v, _ in edges:
        incident.add(u); incident.add(v)
    missing = set(nodes) - incident
    if missing:
        fails.append(f"Identity Continuity: isolated nodes {missing}.")
    # 4. Energy Envelope – total informational work bounded
    #    (we enforce an arbitrary upper bound; in practice set by spec)
    MAX_J = 1e6
    if j_star > MAX_J:
        fails.append(f"Energy Envelope: J*={j_star} > {MAX_J}.")
    # 5. Information Conservation – Φ_N >= Φ_Δ (no information destruction)
    if phi_n < phi_delta - 1e-9:
        fails.append(f"Information Conservation: Φ_N ({phi_n}) < Φ_Δ ({phi_delta}).")
    # 6. Temporal Coherence – monotonic increase of Φ_N with added edges
    #    (tested by removing any edge and checking Φ_N does not increase)
    for i, (_, _, w) in enumerate(edges):
        reduced = edges[:i] + edges[i+1:]
        if compute_phi_n(reduced) > compute_phi_n(edges) + 1e-9:
            fails.append(f"Temporal Coherence: removing edge {i} increases Φ_N.")
            break
    return (len(fails) == 0, fails)

def omega_rubric_pass(phi_n: Number, phi_delta: Number) -> Tuple[bool, List[str]]:
    """Check Omega Physics Rubric v26.0 (Strictor Gate) §§2‑§6."""
    fails = []
    # §2: Φ_N/Φ_Δ decomposition, ψ = ln(Φ_N) coupling, stiffness terms ξ_N, ξ_Δ
    #    We enforce ψ = ln(Φ_N) and require ξ_N, ξ_Δ > 0 (placeholder)
    if phi_n <= 0:
        fails.append("Rubric §2: Φ_N must be > 0 for ψ = ln(Φ_N).")
    # §4: References to Shredding Event and Informational Freeze (horizon boundaries)
    #    We model a horizon as a maximum allowable Φ_Δ; exceeding it is a "freeze".
    HORIZON_PHI_DELTA = 10.0   # arbitrary horizon value
    if phi_delta > HORIZON_PHI_DELTA:
        fails.append(f"Rubric §4: Φ_Δ ({phi_delta}) exceeds horizon ({HORIZON_PHI_DELTA}).")
    # §5: Shannon conditional entropy and topological impedance for gauge emergence
    #    Already captured in Φ_Δ; we require Φ_Δ < Φ_N (information not lost)
    if phi_delta >= phi_n:
        fails.append("Rubric §5: Φ_Δ must be < Φ_N for gauge emergence.")
    # §6: Asymmetry bound Φ_Δ < 0.5·Φ_N
    if phi_delta >= 0.5 * phi_n:
        fails.append(f"Rubric §6: Asymmetry bound violated: Φ_Δ={phi_delta} >= 0.5·Φ_N={0.5*phi_n}.")
    # §1‑§3 etc. are implicitly covered by Smith Audit; we stop here.
    return (len(fails) == 0, fails)

def phi_density_gain(phi_n: Number, phi_delta: Number, j_star: Number) -> Number:
    """Informational‑First Φ‑density gain (higher is better)."""
    if j_star == 0:
        return -math.inf
    return (phi_n - phi_delta) / j_star

def validate_proposal(nodes: List[Node], edges: List[Edge]) -> Dict:
    """Run the full validation suite."""
    if not nodes or not edges:
        return {"pass": False, "reason": "Empty node/edge set."}
    phi_n = compute_phi_n(edges)
    phi_delta = compute_phi_delta(edges)
    j_star = compute_j_star(edges)

    smith_ok, smith_msgs = smith_audit_pass(phi_n, phi_delta, j_star, edges, nodes)
    rubric_ok, rubric_msgs = omega_rubric_pass(phi_n, phi_delta)

    gain = phi_density_gain(phi_n, phi_delta, j_star)

    passed = smith_ok and rubric_ok and gain >= 0
    report = {
        "pass": passed,
        "phi_N": phi_n,
        "phi_Delta": phi_delta,
        "J_star": j_star,
        "phi_density_gain": gain,
        "smith_audit": {"pass": smith_ok, "messages": smith_msgs},
        "omega_rubric": {"pass": rubric_ok, "messages": rubric_msgs},
    }
    return report

# ----------------------------------------------------------------------
# Example usage (replace with the proposal's actual lattice):
if __name__ == "__main__":
    # Dummy lattice: 4 nodes, 5 causal links with random weights
    example_nodes = [0, 1, 2, 3]
    example_edges = [
        (0, 1, 2.0),
        (1, 2, 1.5),
        (2, 3, 3.0),
        (0, 2, 0.5),
        (1, 3, 1.2)
    ]
    result = validate_proposal(example_nodes, example_edges)
    print("=== Ω‑Protocol Validation Report ===")
    for k, v in result.items():
        if isinstance(v, dict):
            print(f"{k}:")
            for subk, subv in v.items():
                print(f"  {subk}: {subv}")
        else:
            print(f"{k}: {v}")