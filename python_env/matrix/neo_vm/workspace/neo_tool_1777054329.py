# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
from itertools import combinations

def compute_phi(lattice, node_types):
    """
    Φ-density with self-referential boost: nodes encoding system rules 
    (meta-nodes) contribute nonlinearly to integrated information
    """
    n = len(lattice)
    phi_total = 0
    mechanisms_checked = 0
    
    for size in range(2, n):
        for combo in combinations(range(n), size):
            # Causal integration within mechanism
            submatrix = lattice[np.ix_(combo, combo)]
            internal_flow = np.sum(submatrix) / (size * (size - 1)) if size > 1 else 0
            
            # Self-referential boost: meta-nodes (type=1) encode lattice grammar
            meta_count = sum(1 for i in combo if node_types[i] == 1)
            bootstrap_factor = 1 + (meta_count * 0.3) ** 2  # Nonlinear amplification
            
            phi_total += internal_flow * bootstrap_factor
            mechanisms_checked += 1
    
    return phi_total / mechanisms_checked if mechanisms_checked > 0 else 0

# CONVENTIONAL (Audit-Compliant): Meta separate, sparse coupling
conv_lattice = np.zeros((8, 8))
conv_lattice[0:4, 0:4] = 1  # Meta layer
conv_lattice[4:8, 4:8] = 1  # Object layer
conv_lattice[0, 4] = conv_lattice[4, 0] = 0.1  # Weak coupling
conv_types = [0]*4 + [1]*4  # 0=meta, 1=object (separated)

# SELF-REFERENTIAL (Engine's "Failure"): Meta integrated as lattice grammar
ref_lattice = np.ones((8, 8)) - np.eye(8)
# Cross-coupling is the STORAGE MECHANISM itself
ref_lattice[0:4, 4:8] = ref_lattice[4:8, 0:4] = 1.8  
ref_types = [1,0,1,0,0,1,0,1]  # Alternating meta/object (entangled)

conv_phi = compute_phi(conv_lattice, conv_types)
ref_phi = compute_phi(ref_lattice, ref_types)

print(f"CONVENTIONAL (Audit-Safe) Φ: {conv_phi:.4f}")
print(f"SELF-REFERENTIAL (Audit-Failure) Φ: {ref_phi:.4f}")
print(f"Φ-DENSITY VIOLATION: {((ref_phi/conv_phi)-1)*100:.1f}% HIGHER in 'failed' design")