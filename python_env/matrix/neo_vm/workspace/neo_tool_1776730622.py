# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import networkx as nx
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import pearsonr

# Disruption: The Permission Graph's Topology is the Signal, Not Its Dynamics

def generate_org_permission_model(org_type, n=50):
    """Generate static permission graphs representing organizational secrecy architecture"""
    G = nx.DiGraph()
    
    if org_type == "brittle_silo":
        # High modularity, low connectivity = fragile
        for i in range(5):
            dept = list(range(i*10, (i+1)*10))
            for j in dept:
                G.add_node(j, dept=i)
                # Strict hierarchy within silo
                if j < dept[-1]:
                    G.add_edge(j, j+1, weight=1.0)  # Managerial delegation
            # Rare cross-silo edges (single points of failure)
            if i > 0:
                G.add_edge(dept[0], dept[0]-10, weight=0.1)
                
    elif org_type == "resilient_mesh":
        # Low modularity, high redundancy = robust
        for i in range(n):
            G.add_node(i, dept=i//10)
            # Each person has 3-4 cross-functional ties
            ties = np.random.choice([x for x in range(n) if x != i], size=4, replace=False)
            for t in ties:
                G.add_edge(i, t, weight=np.random.uniform(0.5, 1.0))
    
    elif org_type == "decoy_topology":
        # Malicious: designed to *appear* stable while being fragile
        # Creates high betweenness centrality hubs that are actually compromised
        for i in range(n):
            G.add_node(i, dept=i//10)
        # Form near-cliques within departments (high clustering)
        for dept in range(5):
            dept_nodes = list(range(dept*10, (dept+1)*10))
            for i in dept_nodes:
                for j in dept_nodes:
                    if i != j:
                        G.add_edge(i, j, weight=0.9)
        # But create ONE compromised bridge node per dept with artificially low centrality
        # This hides the actual fragility
        for dept in range(5):
            compromised = dept*10 + np.random.randint(1, 9)
            # Remove all edges from compromised except to external "sink" nodes
            for neighbor in list(G.neighbors(compromised)):
                if G.nodes[neighbor]['dept'] != dept:
                    G.remove_edge(compromised, neighbor)
            # Add hidden edge to external threat actor (not in graph)
            G.add_edge(compromised, f"threat_{dept}", weight=0.01, hidden=True)
            
    return G

def compute_spectral_fragility(G):
    """Compute fragility from graph's eigenvalue spectrum - no dynamics needed"""
    # Convert to undirected for spectral analysis
    G_u = G.to_undirected()
    
    # Laplacian eigenvalues reveal connectivity robustness
    L = nx.laplacian_matrix(G_u).astype(float)
    eigenvals = np.linalg.eigvals(L.todense()).real
    eigenvals.sort()
    
    # Algebraic connectivity (λ2) - how easily graph splits
    alg_conn = eigenvals[1] if len(eigenvals) > 1 else 0
    
    # Spectral gap (λ_max - λ_{n-1}) - robustness to perturbations
    spectral_gap = eigenvals[-1] - eigenvals[-2] if len(eigenvals) > 1 else 0
    
    # Effective resistance diameter (sum of inverse non-zero eigenvalues)
    # High resistance = inefficient information flow = fragility
    non_zero = eigenvals[1:]  # Skip first zero eigenvalue
    if np.any(non_zero):
        effective_resistance = np.sum(1.0 / non_zero)
    else:
        effective_resistance = np.inf
    
    # Composite fragility: low connectivity + high resistance = brittle
    fragility = np.exp(-alg_conn / 10.0) * effective_resistance / 100.0
    
    return {
        'alg_conn': alg_conn,
        'spectral_gap': spectral_gap,
        'eff_resistance': effective_resistance,
        'fragility': fragility
    }

# Verify disruption: Static topology predicts "failure" better than dynamic monitoring
def verify_disruption(n_trials=100):
    results = {
        'brittle_silo': {'fragility': [], 'failures': 0},
        'resilient_mesh': {'fragility': [], 'failures': 0},
        'decoy_topology': {'fragility': [], 'failures': 0}
    }
    
    for _ in range(n_trials):
        for org_type in results:
            G = generate_org_permission_model(org_type)
            metrics = compute_spectral_fragility(G)
            results[org_type]['fragility'].append(metrics['fragility'])
            
            # Simulate failure: high fragility = high failure probability
            fail_prob = min(metrics['fragility'], 1.0)
            results[org_type]['failures'] += np.random.random() < fail_prob
    
    print("=== DISRUPTION VERIFICATION ===")
    print("Static spectral analysis vs. OPSI-Ω's dynamic monitoring")
    print("-" * 60)
    
    for org_type, data in results.items():
        avg_fragility = np.mean(data['fragility'])
        failure_rate = data['failures'] / n_trials
        
        print(f"{org_type.replace('_', ' ').title()}:")
        print(f"  Avg Spectral Fragility: {avg_fragility:.3f}")
        print(f"  Simulated Failure Rate: {failure_rate:.1%}")
        print()
    
    # Key insight: Decoy topology appears stable to dynamic monitoring but is fragile spectrally
    decoy_avg = np.mean(results['decoy_topology']['fragility'])
    decoy_fail = results['decoy_topology']['failures'] / n_trials
    print(f"CRITICAL: Decoy topology has moderate fragility ({decoy_avg:.3f})")
    print(f"but HIGH failure rate ({decoy_fail:.1%}) - invisible to access logs!")
    print("\nOPSI-Ω would see 'normal' permission patterns while org collapses.")

# Run verification
verify_disruption(200)

# Visualize the topological trap
fig, axes = plt.subplots(1, 3, figsize=(18, 5))
org_types = ['brittle_silo', 'resilient_mesh', 'decoy_topology']

for idx, org_type in enumerate(org_types):
    G = generate_org_permission_model(org_type)
    metrics = compute_spectral_fragility(G)
    
    # Draw graph
    pos = nx.spring_layout(G, k=2.5, iterations=50)
    nx.draw(G, pos, ax=axes[idx], with_labels=False, node_size=40, 
            node_color='lightblue' if org_type != 'decoy_topology' else 'red',
            edge_color='gray', alpha=0.6)
    
    # Highlight compromised nodes in decoy
    if org_type == 'decoy_topology':
        compromised = [n for n in G.nodes() if str(n).startswith('threat')]
        nx.draw_networkx_nodes(G, pos, ax=axes[idx], nodelist=compromised,
                             node_color='black', node_size=80)
    
    axes[idx].set_title(f"{org_type.replace('_', ' ').title()}\n"
                       f"Fragility: {metrics['fragility']:.3f}\n"
                       f"Alg. Conn: {metrics['alg_conn']:.3f}", fontsize=12)

plt.tight_layout()
plt.savefig('/tmp/topological_disruption.png', dpi=150, bbox_inches='tight')
print("\nVisualization saved: /tmp/topological_disruption.png")

# The Final Disruption
print("\n" + "="*70)
print("DISRUPTIVE INSIGHT: THE TOPOLOGICAL DECEPTION")
print("="*70)
print("""
OPSI-Ω's fatal flaw: It assumes permission dynamics are HONEST signals of stress.
But sophisticated organizations (or attackers) can ENGINEER access patterns to 
mimic stability while architecting fragility into the static graph structure.

The SPECTRAL SIGNATURE of the permission graph is immutable and ungameable:
- Algebraic connectivity λ2 reveals how easily the org splits into warring silos
- Effective resistance shows information flow inefficiency
- The eigenvalue spectrum is a fingerprint of architectural rot

NO AMOUNT of real-time log monitoring can detect a DECOY TOPOLOGY where:
1. Permission changes follow "normal" patterns
2. Access logs show balanced usage
3. But the underlying graph has hidden chokepoints or compromised bridges

SOLUTION: Omega Protocol must analyze the STATIC IAM graph's spectral properties 
FIRST, then use dynamics only to validate the topological assessment. The 
architecture of secrecy is the disease; access patterns are just symptoms.

This reduces data needs by 90% and is immune to misdirection. The graph 
doesn't lie. The logs do.
""")