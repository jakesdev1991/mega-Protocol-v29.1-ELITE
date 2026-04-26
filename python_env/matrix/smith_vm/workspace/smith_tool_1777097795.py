# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
from scipy.sparse import csr_matrix
from scipy.sparse.csgraph import connected_components

def validate_omega_invariants(psi_sub, conscious_outcome_idx, phi_n, causal_lattice_edges, num_nodes):
    """
    Validate Omega Protocol invariants for Q-Systemic Self framework.
    
    Args:
        psi_sub: np.array, normalized subconscious state vector (complex or real)
        conscious_outcome_idx: int, index of measured conscious outcome (basis state)
        phi_n: float, normalized identity coherence score [0,1]
        causal_lattice_edges: list of tuples (i,j) representing edges in Causal Lattice graph
        num_nodes: int, number of nodes in Causal Lattice (RCOD ontologies)
    
    Returns:
        bool: True if all invariants satisfied, False otherwise
        dict: detailed validation results
    """
    results = {}
    
    # 1. Validate COD >= 0.85
    # COD = |<psi_sub|k>|^2 where |k> is conscious outcome basis state
    if conscious_outcome_idx < 0 or conscious_outcome_idx >= len(psi_sub):
        raise ValueError("conscious_outcome_idx out of bounds")
    
    cod = np.abs(psi_sub[conscious_outcome_idx])**2
    results['COD'] = cod
    results['COD_valid'] = cod >= 0.85
    
    # 2. Validate H_collapse < 0.3
    # H_collapse = Shannon entropy of measurement probabilities from psi_sub
    probs = np.abs(psi_sub)**2
    # Avoid log2(0) by masking zeros
    with np.errstate(divide='ignore', invalid='ignore'):
        entropy = -np.sum(probs * np.log2(probs, where=probs>0))
    results['H_collapse'] = entropy
    results['H_collapse_valid'] = entropy < 0.3
    
    # 3. Validate psi = ln(phi_n) >= ln(0.95) -> phi_n >= 0.95
    results['phi_n'] = phi_n
    results['phi_n_valid'] = phi_n >= 0.95
    
    # 4. Validate topological continuity: Betti_1 = 0 (no 1-cycles in Causal Lattice)
    # For graph (1-skeleton), Betti_1 = E - V + C
    # where E=edges, V=nodes, C=connected components
    # We require Betti_1 = 0 => E - V + C = 0 => graph is a forest (acyclic)
    
    if num_nodes == 0:
        results['betti_1'] = 0
        results['topological_valid'] = True
    else:
        # Build adjacency matrix
        adj = np.zeros((num_nodes, num_nodes), dtype=int)
        for u, v in causal_lattice_edges:
            if 0 <= u < num_nodes and 0 <= v < num_nodes:
                adj[u, v] = 1
                adj[v, u] = 1  # undirected
        
        # Compute connected components
        n_components, labels = connected_components(csr_matrix(adj), directed=False, return_labels=True)
        num_edges = len(causal_lattice_edges)
        betti_1 = num_edges - num_nodes + n_components
        results['betti_1'] = betti_1
        results['topological_valid'] = (betti_1 == 0)
    
    # Overall validation: all invariants must hold
    all_valid = (
        results['COD_valid'] and 
        results['H_collapse_valid'] and 
        results['phi_n_valid'] and 
        results['topological_valid']
    )
    
    return all_valid, results

# --- Test Cases ---

def test_validation():
    print("Running Omega Protocol Invariant Validation Tests\n")
    
    # Test Case 1: Valid state (should PASS)
    print("Test Case 1: Valid quantum state")
    psi_sub = np.array([np.sqrt(0.9), np.sqrt(0.1)])  # |0> dominant
    conscious_outcome_idx = 0  # measured |0>
    phi_n = 0.96
    causal_lattice_edges = [(0,1), (1,2)]  # acyclic chain: 0-1-2
    num_nodes = 3
    
    valid, results = validate_omega_invariants(
        psi_sub, conscious_outcome_idx, phi_n, causal_lattice_edges, num_nodes
    )
    print(f"COD: {results['COD']:.3f} (>=0.85? {results['COD_valid']})")
    print(f"H_collapse: {results['H_collapse']:.3f} (<0.3? {results['H_collapse_valid']})")
    print(f"Phi_N: {results['phi_n']:.3f} (>=0.95? {results['phi_n_valid']})")
    print(f"Betti_1: {results['betti_1']} (==0? {results['topological_valid']})")
    print(f"OVERALL: {'PASS' if valid else 'FAIL'}\n")
    assert valid == True
    
    # Test Case 2: Low COD (should FAIL)
    print("Test Case 2: Low COD (measurement shock)")
    psi_sub = np.array([np.sqrt(0.6), np.sqrt(0.4)])  # balanced superposition
    conscious_outcome_idx = 0
    phi_n = 0.96
    causal_lattice_edges = [(0,1), (1,2)]
    num_nodes = 3
    
    valid, results = validate_omega_invariants(
        psi_sub, conscious_outcome_idx, phi_n, causal_lattice_edges, num_nodes
    )
    print(f"COD: {results['COD']:.3f} (>=0.85? {results['COD_valid']})")
    print(f"H_collapse: {results['H_collapse']:.3f} (<0.3? {results['H_collapse_valid']})")
    print(f"OVERALL: {'PASS' if valid else 'FAIL'}\n")
    assert valid == False  # COD=0.6 < 0.85
    
    # Test Case 3: High entropy (should FAIL)
    print("Test Case 3: High measurement entropy")
    psi_sub = np.array([np.sqrt(0.5), np.sqrt(0.5)])  # max entropy for 2-state
    conscious_outcome_idx = 0
    phi_n = 0.96
    causal_lattice_edges = [(0,1), (1,2)]
    num_nodes = 3
    
    valid, results = validate_omega_invariants(
        psi_sub, conscious_outcome_idx, phi_n, causal_lattice_edges, num_nodes
    )
    print(f"H_collapse: {results['H_collapse']:.3f} (<0.3? {results['H_collapse_valid']})")
    print(f"OVERALL: {'PASS' if valid else 'FAIL'}\n")
    assert valid == False  # H_collapse=1.0 >= 0.3
    
    # Test Case 4: Low phi_n (should FAIL)
    print("Test Case 4: Low identity coherence")
    psi_sub = np.array([np.sqrt(0.9), np.sqrt(0.1)])
    conscious_outcome_idx = 0
    phi_n = 0.94  # below threshold
    causal_lattice_edges = [(0,1), (1,2)]
    num_nodes = 3
    
    valid, results = validate_omega_invariants(
        psi_sub, conscious_outcome_idx, phi_n, causal_lattice_edges, num_nodes
    )
    print(f"Phi_N: {results['phi_n']:.3f} (>=0.95? {results['phi_n_valid']})")
    print(f"OVERALL: {'PASS' if valid else 'FAIL'}\n")
    assert valid == False
    
    # Test Case 5: Cyclic lattice (should FAIL)
    print("Test Case 5: Cyclic Causal Lattice (belief loop)")
    psi_sub = np.array([np.sqrt(0.9), np.sqrt(0.1)])
    conscious_outcome_idx = 0
    phi_n = 0.96
    causal_lattice_edges = [(0,1), (1,2), (2,0)]  # triangle cycle
    num_nodes = 3
    
    valid, results = validate_omega_invariants(
        psi_sub, conscious_outcome_idx, phi_n, causal_lattice_edges, num_nodes
    )
    print(f"Betti_1: {results['betti_1']} (==0? {results['topological_valid']})")
    print(f"OVERALL: {'PASS' if valid else 'FAIL'}\n")
    assert valid == False  # Betti_1 = 3 - 3 + 1 = 1 != 0
    
    # Test Case 6: Valid complex lattice (should PASS)
    print("Test Case 6: Valid tree-like lattice")
    psi_sub = np.array([np.sqrt(0.88), np.sqrt(0.06), np.sqrt(0.06)])  # COD=0.88 for idx0
    conscious_outcome_idx = 0
    phi_n = 0.97
    causal_lattice_edges = [(0,1), (0,2), (1,3), (2,4)]  # tree structure
    num_nodes = 5
    
    valid, results = validate_omega_invariants(
        psi_sub, conscious_outcome_idx, phi_n, causal_lattice_edges, num_nodes
    )
    print(f"COD: {results['COD']:.3f} (>=0.85? {results['COD_valid']})")
    print(f"H_collapse: {results['H_collapse']:.3f} (<0.3? {results['H_collapse_valid']})")
    print(f"Betti_1: {results['betti_1']} (==0? {results['topological_valid']})")
    print(f"OVERALL: {'PASS' if valid else 'FAIL'}\n")
    assert valid == True
    
    print("All tests completed.")

if __name__ == "__main__":
    test_validation()