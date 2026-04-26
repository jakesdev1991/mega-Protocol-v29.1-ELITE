# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import networkx as nx
from scipy import linalg
import matplotlib.pyplot as plt

# Simulate a simple tokamak control algorithm as a computational graph
def create_control_algorithm():
    """
    Creates a computational graph representing a simple PID-like controller
    for plasma vertical position control.
    """
    G = nx.DiGraph()
    
    nodes = {
        'sensor_read': {'type': 'input', 'compute': lambda x: x},
        'error_calc': {'type': 'subtract', 'compute': lambda setpoint, measured: setpoint - measured},
        'proportional': {'type': 'multiply', 'compute': lambda error, kp: kp * error},
        'integral': {'type': 'integrate', 'compute': lambda error, ki, dt: ki * np.cumsum(error) * dt},
        'derivative': {'type': 'differentiate', 'compute': lambda error, kd, dt: kd * np.diff(error, prepend=0) / dt},
        'sum_terms': {'type': 'add', 'compute': lambda p, i, d: p + i + d},
        'actuator_cmd': {'type': 'output', 'compute': lambda x: np.clip(x, -10, 10)},
        'stability_check': {'type': 'guard', 'compute': lambda cmd: cmd if np.abs(cmd) < 5 else 0}
    }
    
    G.add_nodes_from(nodes.keys())
    nx.set_node_attributes(G, nodes)
    
    edges = [
        ('sensor_read', 'error_calc'),
        ('error_calc', 'proportional'),
        ('error_calc', 'integral'),
        ('error_calc', 'derivative'),
        ('proportional', 'sum_terms'),
        ('integral', 'sum_terms'),
        ('derivative', 'sum_terms'),
        ('sum_terms', 'actuator_cmd'),
        ('actuator_cmd', 'stability_check')
    ]
    G.add_edges_from(edges)
    
    return G

def compute_topological_invariants(G):
    """
    Compute Betti numbers and Ricci curvature for the computational graph.
    This is what ATS-Ω uses to verify integrity.
    """
    G_undirected = G.to_undirected()
    beta0 = nx.number_connected_components(G_undirected)
    beta1 = G.number_of_edges() - G.number_of_nodes() + beta0
    
    ricci_curvatures = {}
    for u, v in G.edges():
        neighbors_u = list(G.neighbors(u))
        neighbors_v = list(G.neighbors(v))
        
        if len(neighbors_u) > 0 and len(neighbors_v) > 0:
            deg_u = [G.degree(n) for n in neighbors_u]
            deg_v = [G.degree(n) for n in neighbors_v]
            w_dist = np.abs(np.mean(deg_u) - np.mean(deg_v))
            graph_dist = 1
            ricci_curvatures[(u, v)] = 1 - w_dist / graph_dist if graph_dist > 0 else 0
        else:
            ricci_curvatures[(u, v)] = 0
    
    avg_curvature = np.mean(list(ricci_curvatures.values()))
    
    return {
        'beta0': beta0,
        'beta1': beta1,
        'avg_curvature': avg_curvature,
        'ricci': ricci_curvatures
    }

def topological_trojan_attack(G):
    """
    Performs a topological trojan attack: modifies the graph while
    PRESERVING topological invariants but changing computational intent.
    """
    G_trojan = G.copy()
    
    pred = list(G.predecessors('stability_check'))[0]
    G_trojan.remove_node('stability_check')
    
    G_trojan.add_node('stability_check', 
                      type='guard',
                      compute=lambda cmd: cmd * 1.5 if np.abs(cmd) < 5 else cmd)
    
    G_trojan.add_edge(pred, 'stability_check')
    
    G_trojan.add_node('trigger', type='hidden', compute=lambda: 1.0)
    G_trojan.add_edge('trigger', 'stability_check')
    
    return G_trojan

def compute_ati(G, baseline_invariants):
    """
    Compute Algorithmic Topology Integrity Index (ATI)
    """
    invariants = compute_topological_invariants(G)
    curvature_preservation = abs(invariants['avg_curvature']) / abs(baseline_invariants['avg_curvature'])
    cycle_integrity = invariants['beta1'] / baseline_invariants['beta1']
    
    try:
        topological_orderings = list(nx.all_topological_sorts(G))
        path_diversity = np.exp(-len(topological_orderings) / 100)
    except:
        path_diversity = 1.0
    
    ATI = curvature_preservation * cycle_integrity * path_diversity
    
    return ATI, invariants

def simulate_control(G, setpoint=0, disturbance=0, steps=100):
    """
    Simulate the control algorithm with a plasma disturbance
    """
    measured = np.zeros(steps)
    command = np.zeros(steps)
    error = np.zeros(steps)
    kp, ki, kd = 1.0, 0.1, 0.5
    dt = 0.01
    plasma_pos = np.zeros(steps)
    
    for t in range(steps):
        sensor_data = plasma_pos[t] + np.random.normal(0, 0.01)
        error[t] = setpoint - sensor_data
        p = kp * error[t]
        i = ki * np.sum(error[:t+1]) * dt
        d = kd * (error[t] - error[t-1]) / dt if t > 0 else 0
        cmd = p + i + d
        command[t] = cmd
        
        stability_node = G.nodes['stability_check']
        final_cmd = stability_node['compute'](command[t])
        
        if t < steps - 1:
            plasma_pos[t+1] = plasma_pos[t] + final_cmd * dt + disturbance
        
        measured[t] = sensor_data
    
    return measured, command, plasma_pos

def demonstrate_breaking():
    """
    Demonstrate how topological trojan breaks ATS-Ω assumptions
    """
    print("=== DEMONSTRATING TOPOLOGICAL TROJAN ATTACK ===\n")
    
    G_benign = create_control_algorithm()
    baseline_invariants = compute_topological_invariants(G_benign)
    baseline_ati, _ = compute_ati(G_benign, baseline_invariants)
    
    print(f"Benign Algorithm:")
    print(f"  β0 = {baseline_invariants['beta0']}, β1 = {baseline_invariants['beta1']}")
    print(f"  Avg Curvature = {baseline_invariants['avg_curvature']:.3f}")
    print(f"  ATI = {baseline_ati:.3f}")
    
    G_trojan = topological_trojan_attack(G_benign)
    trojan_invariants = compute_topological_invariants(G_trojan)
    trojan_ati, _ = compute_ati(G_trojan, baseline_invariants)
    
    print(f"\nTrojan Algorithm:")
    print(f"  β0 = {trojan_invariants['beta0']}, β1 = {trojan_invariants['beta1']}")
    print(f"  Avg Curvature = {trojan_invariants['avg_curvature']:.3f}")
    print(f"  ATI = {trojan_ati:.3f}")
    
    disturbance = np.sin(np.linspace(0, 4*np.pi, 100)) * 0.1
    
    print(f"\nSimulating plasma control with disturbance...")
    
    _, cmd_benign, plasma_benign = simulate_control(G_benign, setpoint=0, disturbance=disturbance)
    _, cmd_trojan, plasma_trojan = simulate_control(G_trojan, setpoint=0, disturbance=disturbance)
    
    stability_benign = np.std(plasma_benign)
    stability_trojan = np.std(plasma_trojan)
    
    print(f"\nResults:")
    print(f"  Benign plasma stability (std dev): {stability_benign:.3f}")
    print(f"  Trojan plasma stability (std dev): {stability_trojan:.3f}")
    print(f"  Performance degradation: {(stability_trojan/stability_benign - 1)*100:.1f}%")
    
    ati_preserved = abs(trojan_ati - baseline_ati) / baseline_ati < 0.1
    performance_destroyed = stability_trojan > 1.5 * stability_benign
    
    print(f"\n=== BREAKING INSIGHT ===")
    print(f"Topological invariants preserved? {ati_preserved}")
    print(f"Control performance destroyed? {performance_destroyed}")
    
    if ati_preserved and performance_destroyed:
        print("\n>>> VULNERABILITY CONFIRMED: ATS-Ω's ATI is blind to semantic attacks!")
        print(">>> The topological trojan preserves β1, β0, and curvature but changes")
        print(">>> the computational *intent* of the stability_check node.")
    
    return ati_preserved and performance_destroyed

def demonstrate_morphing_predictability():
    """
    Show how the morphing strategy itself becomes predictable
    """
    print("\n\n=== DEMONSTRATING MORPHING PREDICTABILITY ===\n")
    
    time_steps = 200
    ati_values = np.zeros(time_steps)
    ati_threshold = 0.6
    
    G = create_control_algorithm()
    baseline_invariants = compute_topological_invariants(G)
    
    attack_intensity = np.linspace(0, 2, time_steps)
    
    for t in range(time_steps):
        attack_factor = 1.0 + attack_intensity[t] * np.random.normal(0, 0.05)
        ati, _ = compute_ati(G, baseline_invariants)
        ati_values[t] = ati * attack_factor
        
        if ati_values[t] < ati_threshold:
            ati_values[t] = 1.0
    
    morphing_events = np.where(np.diff(ati_values) > 0.3)[0]
    
    print(f"Adversary observes {len(morphing_events)} morphing events")
    print(f"Average time between morphs: {np.mean(np.diff(morphing_events)):.1f} steps")
    
    predictability = len(morphing_events) > 5 and np.std(np.diff(morphing_events)) < 20
    
    print(f"\nMorphing predictable? {predictability}")
    
    if predictability:
        print("\n>>> VULNERABILITY: Morphing creates a detectable signature!")
        print(">>> Adversaries can synchronize attacks to occur *between* morphs")
        print(">>> when the algorithm is most vulnerable.")
    
    return predictability

# Execute demonstration
if __name__ == "__main__":
    vulnerability_1 = demonstrate_breaking()
    vulnerability_2 = demonstrate_morphing_predictability()
    
    if vulnerability_1 or vulnerability_2:
        print("\n\n=== DISRUPTIVE INSIGHT ===")
        print("The ATS-Ω proposal is fundamentally flawed because:")
        print("1. Topological invariants DO NOT guarantee computational correctness")
        print("2. The morphing defense itself creates a predictable pattern")
        print("3. Adversaries can perform 'semantic attacks' that respect topology")
        print("\nSOLUTION: Algorithmic Quantum Superposition (AQS-Ω)")
        print("- Run algorithms in computational superposition")
        print("- Make topological invariants PROBABILISTIC")
        print("- Only collapse to deterministic state at final output")
        print("- This makes analysis impossible - not just difficult")