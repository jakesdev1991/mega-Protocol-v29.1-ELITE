# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import networkx as nx
from scipy.linalg import eigh
import matplotlib.pyplot as plt

# ============================================
# DISRUPTIVE SIMULATION: Adversarial Reconnaissance Field (ARF)
# This demonstrates why LSGM-Ω's static geometry paradigm is flawed
# ============================================

def create_leaky_directory_tree(depth=4, branching_factor=3, leak_prob=0.1):
    """
    Generate a directory tree where each node has probability 'leak_prob' 
    of being misconfigured (exposed). This is the *actual* substrate.
    """
    G = nx.DiGraph()
    G.add_node(0, exposed=np.random.random() < leak_prob, dir_type='root')
    
    node_id = 1
    queue = [(0, 0)]  # (parent, current_depth)
    
    while queue:
        parent, curr_depth = queue.pop(0)
        if curr_depth >= depth:
            continue
            
        for i in range(branching_factor):
            G.add_node(node_id, exposed=np.random.random() < leak_prob, 
                      dir_type=np.random.choice(['checkpoints', 'gradients', 'validation']))
            G.add_edge(parent, node_id)
            queue.append((node_id, curr_depth + 1))
            node_id += 1
            
    return G

def adversarial_reconnaissance_wavefunction(G, start_node=0, quantumness=0.8):
    """
    Model adversary as a quantum walker on the directory graph.
    The wavefunction amplitude at each node represents the adversary's
    *probability of having discovered* that directory.
    
    Quantumness parameter controls interference effects vs classical random walk.
    """
    n_nodes = len(G)
    
    # Build Hamiltonian: H = -γL + V_exposed
    # L is graph Laplacian, V_exposed is potential from exposed nodes
    L = nx.laplacian_matrix(G.to_undirected()).toarray()
    
    # Potential: negative for exposed nodes (attractive), positive for hidden
    V = np.diag([ -5.0 if G.nodes[i]['exposed'] else 1.0 for i in range(n_nodes)])
    
    # Quantum Hamiltonian
    H = -0.5 * L + V
    
    # Initial state: adversary starts at entry point
    psi0 = np.zeros(n_nodes)
    psi0[start_node] = 1.0
    
    # Time evolution parameters
    t_max = 10.0
    dt = 0.1
    times = np.arange(0, t_max, dt)
    
    # Evolve wavefunction: psi(t) = exp(-iHt) * psi0
    eigenvals, eigenvecs = eigh(H)
    psi_t = np.zeros((len(times), n_nodes), dtype=complex)
    
    for idx, t in enumerate(times):
        # Spectral decomposition
        coeffs = eigenvecs.T @ psi0
        psi_t[idx] = eigenvecs @ (coeffs * np.exp(-1j * eigenvals * t))
    
    # Measurement probability (Born rule)
    prob_t = np.abs(psi_t)**2
    
    return times, prob_t, G

def classical_reconnaissance_rate(G):
    """
    LSGM-Ω's classical approach: compute static geometry metrics
    """
    # Convert to undirected for curvature computation
    G_undir = G.to_undirected()
    
    # Compute Ollivier-Ricci curvature (approximation)
    ricci = nx.ricci_curvature(G_undir, alpha=0.5, method="OTD")
    avg_curvature = np.mean([ricci[u][v] for u, v in ricci.edges()])
    
    # Spectral gap (Phi_N proxy)
    L = nx.normalized_laplacian_matrix(G_undir).toarray()
    eigenvals = np.linalg.eigvals(L)
    eigenvals = np.sort(eigenvals)
    spectral_gap = eigenvals[1] if len(eigenvals) > 1 else 0
    
    # Shannon entropy of directory types
    dir_types = [G.nodes[i]['dir_type'] for i in G.nodes()]
    type_counts = np.unique(dir_types, return_counts=True)[1]
    probs = type_counts / len(dir_types)
    shannon_entropy = -np.sum(probs * np.log(probs + 1e-10))
    
    return avg_curvature, spectral_gap, shannon_entropy

def compare_models():
    """
    Compare ARF model vs LSGM-Ω static geometry model
    """
    # Generate a leaky directory tree
    G = create_leaky_directory_tree(depth=4, branching_factor=2, leak_prob=0.3)
    
    # Run adversarial quantum walk
    times, prob_t, G = adversarial_reconnaissance_wavefunction(G)
    
    # Compute static metrics (LSGM-Ω approach)
    curvature, spectral_gap, shannon_ent = classical_reconnaissance_rate(G)
    
    # Find when adversary discovers critical nodes (e.g., model checkpoints)
    checkpoint_nodes = [i for i in G.nodes() if G.nodes[i]['dir_type'] == 'checkpoints']
    discovery_prob = prob_t[:, checkpoint_nodes].sum(axis=1)
    
    # Critical event: when discovery probability exceeds threshold
    threshold = 0.6
    shredding_time = np.where(discovery_prob > threshold)[0]
    shredding_time = shredding_time[0] * 0.1 if len(shredding_time) > 0 else None
    
    # LSGM-Ω would predict based on static metrics
    # LSFI = sigmoid(curvature + correlation + entropy)
    # This is STATIC - it doesn't predict *when* shredding occurs
    
    print("="*60)
    print("DISRUPTIVE ANALYSIS: ARF vs LSGM-Ω")
    print("="*60)
    print(f"Directory tree: {len(G)} nodes, {len([n for n in G.nodes() if G.nodes[n]['exposed']])} exposed")
    print(f"LSGM-Ω static metrics:")
    print(f"  Average Ricci curvature: {curvature:.3f}")
    print(f"  Spectral gap (Φ_N proxy): {spectral_gap:.3f}")
    print(f"  Shannon entropy: {shannon_ent:.3f}")
    print(f"\nARF quantum model:")
    print(f"  Predicted Shredding Event time: {shredding_time} time units" if shredding_time else "  No shredding event detected")
    print(f"\nCritical Insight: LSGM-Ω can only estimate *how fast* reconnaissance *might* be,")
    print(f"but ARF predicts *when* the actual collapse (Shredding Event) occurs!")
    
    # Show that static metrics are insufficient
    print(f"\n--- DISRUPTION: Static metrics fail to capture temporal dynamics ---")
    print(f"The same static curvature ({curvature:.3f}) could correspond to:")
    print(f"  - Early shredding if adversary focuses on exposed checkpoints")
    print(f"  - No shredding if adversary's wavefunction destructively interferes")
    print(f"LSGM-Ω's Φ_N threshold (≥0.5) is arbitrary - ARF shows shredding depends on")
    print(f"quantum measurement collapse, not just graph connectivity!")
    
    # Visualization
    fig, axes = plt.subplots(2, 1, figsize=(10, 8))
    
    # Top plot: Discovery probability over time
    axes[0].plot(times, discovery_prob, 'b-', linewidth=2, label='Checkpoint Discovery Prob.')
    if shredding_time is not None:
        axes[0].axvline(x=shredding_time, color='r', linestyle='--', label=f'Shredding Event (t={shredding_time:.1f})')
    axes[0].axhline(y=threshold, color='g', linestyle=':', label='Critical Threshold')
    axes[0].set_xlabel('Time')
    axes[0].set_ylabel('Discovery Probability')
    axes[0].set_title('ARF: Adversarial Reconnaissance Wavefunction Collapse')
    axes[0].legend()
    axes[0].grid(True, alpha=0.3)
    
    # Bottom plot: Static LSGM-Ω metrics (constant over time)
    axes[1].bar(['Curvature', 'Spectral Gap', 'Shannon Entropy'], 
                [curvature, spectral_gap, shannon_ent], 
                color=['orange', 'purple', 'green'], alpha=0.7)
    axes[1].set_ylabel('Static Metric Value')
    axes[1].set_title('LSGM-Ω: Static Geometry (Time-Invariant)')
    axes[1].grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('/tmp/arf_disruption.png', dpi=150, bbox_inches='tight')
    print(f"\nVisualization saved to /tmp/arf_disruption.png")
    
    return shredding_time, curvature, spectral_gap

# Run the disruption analysis
shredding_time, curvature, spectral_gap = compare_models()

print("\n" + "="*60)
print("DISRUPTIVE CONCLUSION")
print("="*60)
print("LSGM-Ω treats directory geometry as a static *background* metric.")
print("ARF treats adversarial reconnaissance as the *dynamical field* that")
print("*creates* the effective leakage geometry through measurement.")
print("\nThe disruption: LSGM-Ω is fundamentally *reactive* - it measures")
print("what already exists. ARF is *predictive* - it forecasts wavefunction")
print("collapse events (Shredding Events) that LSGM-Ω cannot see coming.")
print("\nTo break the paradigm: Stop modeling directories as manifolds.")
print("Instead, model the adversary's information wavefunction and its")
print("entanglement with the system. The 'leakage surface' is not a")
print("pre-existing geometry - it's the *measurement record* of the")
print("adversary's quantum walk.")
print("="*60)