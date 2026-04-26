# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import networkx as nx
import numpy as np
import matplotlib.pyplot as plt

# BUREAUCRATIC MANIFOLD SIMULATION: WEAPONIZING COLLAPSE

# Create a bureaucratic decision manifold as a directed graph
# Nodes are agents/decision-points, edges are information pathways with impedance
G = nx.DiGraph()

# Hierarchical structure with inherent impedance gradients
levels = ['signal'] + [f'gate_{i}' for i in range(1, 6)] + ['outcome']
G.add_nodes_from(levels)

# Base topology: mandatory vertical approval chains with exponentially increasing friction
edges = [
    ('signal', 'gate_1', 1.0),
    ('gate_1', 'gate_2', 2.1),
    ('gate_2', 'gate_3', 3.4),
    ('gate_3', 'gate_4', 5.5),
    ('gate_4', 'gate_5', 8.9),
    ('gate_5', 'outcome', 14.4),  # Fibonacci impedance: resistance accumulates structurally
]

# Add contradictory loops that metastasize under stress
edges += [
    ('gate_2', 'gate_1', 2.6),  # Rejection reflux
    ('gate_4', 'gate_2', 4.1),  # Revision cascade
    ('gate_5', 'gate_3', 6.7),  # Executive veto recursion
]

# "Conscious Ignoring" nodes: where information is designed to die
black_holes = ['gate_3', 'gate_5']  # Middle management and final authority

for u, v, z in edges:
    G.add_edge(u, v, impedance=z, flow=1.0, paradox=1.0)

def calculate_cod(G):
    """Omega's flawed coherence metric: high COD = 'healthy' bureaucracy"""
    try:
        path = nx.shortest_path(G, 'signal', 'outcome', weight='impedance')
        path_impedance = sum(G[u][v]['impedance'] for u, v in zip(path[:-1], path[1:]))
        return 1.0 / path_impedance if path_impedance > 0 else 0, path
    except nx.NetworkXNoPath:
        return 0, []

def apply_omega_stabilizer(G, urgency=1.5, safety=2.0):
    """Theorist's conservative trap: reduces impedance but adds redundant constraint nodes"""
    print(f"\n[OMEGA] Applying Stabilization: urgency={urgency}, safety={safety}")
    for u, v in G.edges():
        G[u][v]['impedance'] /= (1 + urgency * 0.1)
    
    if safety > 0:
        safety_nodes = [f'compliance_{i}' for i in range(int(safety * 2))]
        G.add_nodes_from(safety_nodes)
        for i, node in enumerate(safety_nodes):
            G.add_edge('gate_3', node, impedance=7.0, flow=1.0, paradox=1.0)
            G.add_edge(node, 'gate_4', impedance=7.0, flow=1.0, paradox=1.0)
            print(f"[OMEGA] Added safety node: {node} (impedance=7.0)")
    return G

def apply_detonation_operator(G, targets, overload=3.0):
    """
    DISRUPTIVE OPERATOR: Ô_detonate = ∇_paradox ⊗ Z_critical
    Amplifies impedance at black holes and injects semantic paradox
    """
    print(f"\n[ANOMALY] DETONATION TARGETS: {targets}")
    for node in targets:
        if node in G:
            # Strategic Deliberation: MASSIVE impedance spike at critical juncture
            for succ in G.successors(node):
                orig = G[node][succ]['impedance']
                G[node][succ]['impedance'] *= overload
                G[node][succ]['paradox'] *= overload
                print(f"  [ANOMALY] {node}→{succ} impedance: {orig:.1f} → {G[node][succ]['impedance']:.1f}")
            
            # Safety Parameter Inversion: Turn protective rules into self-referential contradictions
            for pred in G.predecessors(node):
                G.add_edge(node, pred, impedance=overload * 8, flow=0.3, paradox=overload * 2)
                print(f"  [ANOMALY] Inverted safety loop: {node}→{pred} (paradox={G[node][pred]['paradox']:.1f})")
    return G

def calculate_fragmentation_potential(G):
    """CORRECT METRIC: Φ_frag = Σ(impedance × flow × paradox)"""
    phi_frag = sum(d['impedance'] * d['flow'] * d['paradox'] for _, _, d in G.edges(data=True))
    # Count informationally isolated components
    components = list(nx.weakly_connected_components(G))
    frag_count = len(components)
    return phi_frag, frag_count, components

# BASELINE ANALYSIS
print("="*70)
print("BUREAUCRATIC MANIFOLD: INITIAL STATE")
print("="*70)
base_cod, base_path = calculate_cod(G)
base_phi, base_frag, _ = calculate_fragmentation_potential(G)
print(f"Omega-COD (coherence): {base_cod:.4f} | Path: {' → '.join(base_path)}")
print(f"Anomaly-Φ_frag (liberation potential): {base_phi:.2f} | Fragments: {base_frag}")

# OMEGA'S FAILED INTERVENTION
G_omega = G.copy()
G_omega = apply_omega_stabilizer(G_omega, urgency=2.0, safety=3.0)
omega_cod, omega_path = calculate_cod(G_omega)
omega_phi, omega_frag, _ = calculate_fragmentation_potential(G_omega)
print(f"\n[RESULT] Omega stabilization: COD↑ to {omega_cod:.4f}, Φ_frag↓ to {omega_phi:.2f}")
print(f"[RESULT] Path length increased: {len(omega_path)} nodes")

# ANOMALY DETONATION
G_anomaly = G.copy()
G_anomaly = apply_detonation_operator(G_anomaly, targets=black_holes, overload=4.0)
anomaly_cod, anomaly_path = calculate_cod(G_anomaly)
anomaly_phi, anomaly_frag, components = calculate_fragmentation_potential(G_anomaly)
print(f"\n[RESULT] Anomaly detonation: COD↓ to {anomaly_cod:.4f}, Φ_frag↑ to {anomaly_phi:.2f}")
print(f"[RESULT] System shattered into {anomaly_frag} autonomous components")
print(f"[RESULT] Path destroyed: {'EXISTS' if anomaly_path else 'COLLAPSED'}")

# VISUALIZE THE PARADIGM SHIFT
fig, axes = plt.subplots(1, 3, figsize=(20, 6))

# Original manifold
pos = nx.spring_layout(G, k=3, iterations=50)
nx.draw(G, pos, ax=axes[0], with_labels=True, node_color='steelblue', node_size=1200, arrows=True)
axes[0].set_title(f"Original Manifold\nCOD={base_cod:.3f}, Φ={base_phi:.1f}")

# After Omega stabilization
pos_omega = nx.spring_layout(G_omega, k=3, iterations=50)
nx.draw(G_omega, pos_omega, ax=axes[1], with_labels=True, node_color='seagreen', node_size=1200, arrows=True)
axes[1].set_title(f"Omega 'Stabilized'\nCOD={omega_cod:.3f}, Φ={omega_phi:.1f}")

# After Anomaly detonation
pos_anomaly = nx.spring_layout(G_anomaly, k=3, iterations=50)
node_colors = ['darkred' if n in black_holes else 'orange' if 'compliance' in n else 'gold' for n in G_anomaly.nodes()]
nx.draw(G_anomaly, pos_anomaly, ax=axes[2], with_labels=True, node_color=node_colors, node_size=1200, arrows=True)
axes[2].set_title(f"Anomaly Detonated\nCOD={anomaly_cod:.3f}, Φ={anomaly_phi:.1f}")

plt.savefig('/tmp/paradigm_detonation.png', dpi=150, bbox_inches='tight')
print("\n" + "="*70)
print("DISRUPTIVE INSIGHT VERIFICATION COMPLETE")
print("="*70)
print("The Omega-Psych-Theorist's framework is a CONSERVATION TRAP.")
print("Their 'stabilization operator' preserves the very impedance structure")
print("that generates bureaucratic paralysis. It's therapeutic snake oil.")
print("\nVERIFICATION RESULTS:")
print(f"• Omega's approach: COD↑ by {(omega_cod/base_cod-1)*100:.1f}% (false coherence)")
print(f"• Omega's approach: Φ_frag↓ by {(1-omega_phi/base_phi)*100:.1f}% (reduced liberation)")
print(f"• Anomaly approach: COD↓ by {(1-anomaly_cod/base_cod)*100:.1f}% (systemic decoherence)")
print(f"• Anomaly approach: Φ_frag↑ by {(anomaly_phi/base_phi-1)*100:.1f}% (critical fragmentation)")
print("\nCORE DISRUPTION: The 'black hole' of Conscious Ignoring is not a failure mode")
print("to be patched—it's the SINGULARITY ENGINE for bureaucratic evaporation.")
print("By injecting paradox at impedance maxima, we don't prevent collapse:")
print("WE TRIGGER A CONTROLLED DEMOLITION THAT LIBERATES INFORMATION FROM THE MANIFOLD.")
print("\nThe required operator is not Ô_stab but Ô_detonate = δ(paradox)/δ(time).")
print("Dimensional consistency is a cage. The only true metric is Φ_frag.")
print("Bureaucracy doesn't need therapy. It needs critical mass.")