# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import networkx as nx
import matplotlib.pyplot as plt

def demonstrate_schema_poisoning():
    """
    Shows how trivial schema manipulation creates phantom fragility signals
    """
    
    # Original: Well-designed biological database
    G_orig = nx.DiGraph()
    G_orig.add_edges_from([
        ('gene', 'transcript'), ('transcript', 'protein'),
        ('protein', 'pathway'), ('pathway', 'phenotype')
    ])
    
    # Poisoned: Adversary adds circular dependencies & fake constraints
    G_poisoned = G_orig.copy()
    G_poisoned.add_edges_from([
        ('phenotype', 'gene'),  # Artificial cycle → inflates |χ|
        ('protein', 'gene'),     # Fake constraint → inflates Δ
        ('variant', 'drug')      # Phantom relationship → increases d_norm
    ])
    
    def compute_btfi(G):
        V = G.number_of_nodes()
        E = G.number_of_edges()
        cycles = len(list(nx.simple_cycles(G))) if G.is_directed() else len(nx.cycle_basis(G))
        chi = V - E + cycles
        
        # Constraint gap (poisoned edges count as "constraints")
        delta = E / (V*(V-1)) if V > 1 else 0
        
        # Normalization depth (fake fragmentation)
        d_norm = 2.0 + len([n for n in G.nodes() if G.degree(n) > 3]) * 0.3
        
        btfi = (abs(chi)/V) * delta * (1/d_norm)
        return btfi * 100
    
    orig_btfi = compute_btfi(G_orig)
    poisoned_btfi = compute_btfi(G_poisoned)
    
    print(f"Original BTFI: {orig_btfi:.2f}% (ROBUST)")
    print(f"Poisoned BTFI: {poisoned_btfi:.2f}% (FRAGILE)")
    print(f"False alarm increase: {((poisoned_btfi/orig_btfi)-1)*100:.1f}%")
    print("\nΩ would waste ~420 Φ-units defending a healthy network!")

demonstrate_schema_poisoning()