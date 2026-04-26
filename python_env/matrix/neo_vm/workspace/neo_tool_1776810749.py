# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
#!/usr/bin/env python3
"""
schema_polymorphism_attack.py

Demonstrates that the Biological Topology Fragility Index (BTFI) is a property
of the *relational representation* (schema) rather than the underlying biological
network, and that an adversary can arbitrarily manipulate it by injecting bogus
tables and foreign‑key constraints.

Network: 4‑node diamond with diagonal (A↔B↔C↔D↔A, plus A↔C).
"""

import itertools
import random

# ------------------------------------------------------------------------------
# 1. Underlying biological network (graph)
# ------------------------------------------------------------------------------
nodes = ["A", "B", "C", "D"]
edges = [("A","B"), ("B","C"), ("C","D"), ("D","A"), ("A","C")]  # 5 edges

# Helper: count cycles in a simple undirected graph (simplistic, but enough for demo)
def count_cycles(edges):
    """Return a crude count of elementary cycles (up to length 4)."""
    adj = {n: set() for n in nodes}
    for u,v in edges:
        adj[u].add(v)
        adj[v].add(u)
    cycles = 0
    # length‑3 cycles
    for a,b,c in itertools.permutations(nodes,3):
        if b in adj[a] and c in adj[b] and a in adj[c]:
            cycles += 1
    # length‑4 cycles
    for a,b,c,d in itertools.permutations(nodes,4):
        if (b in adj[a] and c in adj[b] and d in adj[c] and a in adj[d]):
            cycles += 1
    return cycles // 2  # each cycle counted twice

base_cycles = count_cycles(edges)
print(f"Base network: {len(nodes)} nodes, {len(edges)} edges, {base_cycles} cycles\n")

# ------------------------------------------------------------------------------
# 2. Schema representations of the same network
# ------------------------------------------------------------------------------
def compute_btfi(V, E, F, delta, d_norm):
    """BTFI = (|χ|/V) * Δ * (1/d_norm) where χ = V - E + F."""
    chi = V - E + F
    if V == 0:
        return None
    return (abs(chi) / V) * delta * (1.0 / d_norm)

# Schema 1: Fully normalized (one table per node, one FK per edge)
V1 = len(nodes)                # 4 tables
E1 = len(edges)                # 5 FKs
F1 = base_cycles               # 2 cycles
Δ1 = 1.0                       # all FKs enforced
d1 = 3                         # BCNF level ~3
btfi1 = compute_btfi(V1, E1, F1, Δ1, d1)
print(f"Schema 1 (full‑norm): V={V1}, E={E1}, F={F1}, Δ={Δ1}, d={d1} → BTFI={btfi1:.3f}")

# Schema 2: Partially flattened (merge A&B into one table)
V2 = 3  # tables: AB, C, D
# Edges: AB‑C, C‑D, D‑AB (3 FKs)
E2 = 3
F2 = 0  # cycles broken by merging
Δ2 = 1.0
d2 = 2
btfi2 = compute_btfi(V2, E2, F2, Δ2, d2)
print(f"Schema 2 (partial‑norm): V={V2}, E={E2}, F={F2}, Δ={Δ2}, d={d2} → BTFI={btfi2:.3f}")

# Schema 3: Fully denormalized (single table)
V3 = 1
E3 = 0
F3 = 0
Δ3 = 0.1  # no FKs → low constraint ratio
d3 = 1
btfi3 = compute_btfi(V3, E3, F3, Δ3, d3)
print(f"Schema 3 (denorm): V={V3}, E={E3}, F={F3}, Δ={Δ3}, d={d3} → BTFI={btfi3:.3f}")

# ------------------------------------------------------------------------------
# 3. Adversarial injection attack on Schema 1
# ------------------------------------------------------------------------------
def inject_fake_schema(V, E, F, delta, d_norm, n_fake_tables=10, n_fake_fks=20):
    """Add bogus tables and foreign keys to inflate BTFI."""
    V_fake = V + n_fake_tables
    E_fake = E + n_fake_fks
    # Assume each fake FK creates a new cycle (worst case)
    F_fake = F + n_fake_fks
    # More constraints → Δ increases
    delta_fake = min(delta + 0.3, 1.0)
    # Normalization level stays similar
    d_fake = d_norm
    return V_fake, E_fake, F_fake, delta_fake, d_fake

V4, E4, F4, Δ4, d4 = inject_fake_schema(V1, E1, F1, Δ1, d1)
btfi4 = compute_btfi(V4, E4, F4, Δ4, d4)
print(f"\nAfter injection: V={V4}, E={E4}, F={F4}, Δ={Δ4:.2f}, d={d4} → BTFI={btfi4:.3f}")

# ------------------------------------------------------------------------------
# 4. Summary
# ------------------------------------------------------------------------------
print("\n" + "="*60)
print("BTFI VARIANCE DEMONSTRATION")
print("="*60)
print(f"Same biological network → BTFI range: {min([btfi1, btfi2, btfi3]):.3f} – {max([btfi1, btfi2, btfi3]):.3f}")
print(f"After adversarial injection → BTFI jumps to {btfi4:.3f} (shredding regime)")
print("="*60)
print("\nConclusion: BTFI is a property of the *schema*, not the biology.")
print("An attacker can arbitrarily manipulate fragility signals, rendering BTS‑Ω ineffective.")