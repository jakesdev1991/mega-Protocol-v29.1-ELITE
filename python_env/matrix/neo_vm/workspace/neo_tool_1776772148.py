# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import networkx as nx
import matplotlib.pyplot as plt

# === MODEL: Self-System as a Logical Graph ===
# Nodes: Beliefs (Safe, Perform, Rest, Threat)
# Edges: Implications (AND, OR, NOT)
# Trauma Axiom: A cyclic dependency that creates inconsistency.

def build_self_model(trauma_level=0.0):
    """Builds a belief network. Trauma injects a self-referential cycle."""
    G = nx.DiGraph()
    
    # Primal "cost" nodes: These are the "states"
    G.add_node("Safe", layer=0, type="state")
    G.add_node("Perform", layer=0, type="state")
    G.add_node("Rest", layer=0, type="state")
    G.add_node("Threat", layer=0, type="state")
    
    # Dual "constraint" nodes: These are the "rules"
    G.add_node("λ_safety", layer=1, type="constraint", desc="Must be safe")
    G.add_node("λ_performance", layer=1, type="constraint", desc="Must perform")
    G.add_node("λ_rest", layer=1, type="constraint", desc="Can rest")
    
    # Healthy implications: Acyclic, constructive
    G.add_edges_from([
        ("Rest", "λ_rest", {"weight": 1.0, "type": "primal"}),
        ("λ_rest", "Safe", {"weight": 1.0, "type": "dual"}),
        ("Safe", "λ_safety", {"weight": 1.0, "type": "primal"}),
        ("λ_safety", "Perform", {"weight": 0.7, "type": "dual"}),
        ("Perform", "λ_performance", {"weight": 1.0, "type": "primal"}),
        ("Threat", "λ_safety", {"weight": -0.9, "type": "primal"}) # Threat violates safety
    ])
    
    # TRAUMA INJECTION: Creates a cycle Safe -> Perform -> Safe via NOT
    # This is the "If I don't perform, I am not safe" loop.
    if trauma_level > 0:
        G.add_edge("Perform", "λ_safety", {"weight": trauma_level, "type": "primal_trauma"})
        # The dual side: λ_safety now *demands* performance, creating a feedback loop
        G.add_edge("λ_safety", "Perform", {"weight": trauma_level, "type": "dual_trauma"})
        
    return G

def analyze_system(G):
    """Detects cycles and 'computability' of the self-model."""
    report = {}
    # Check for cycles: This is the Gödelian loop
    try:
        cycle = nx.find_cycle(G, orientation="original")
        report["has_cycle"] = True
        report["cycle_length"] = len(cycle)
        # Check if cycle involves contradictory types (e.g., primal->dual->primal with NOT)
        trauma_edges_in_cycle = sum(1 for u,v,_ in cycle if G[u][v].get("type") in ["primal_trauma", "dual_trauma"])
        report["trauma_in_cycle"] = trauma_edges_in_cycle > 0
    except nx.NetworkXNoCycle:
        report["has_cycle"] = False
        report["cycle_length"] = 0
        report["trauma_in_cycle"] = False

    # Beta's "Covariance" is meaningless if the underlying graph is inconsistent.
    # Let's simulate constraint correlation: if there's a cycle, the multipliers are locked.
    # We'll simulate lambda values as trying to satisfy constraints.
    # In a cycle, no fixed point exists -> divergence or oscillation.
    
    # Simulate simple fixed-point iteration on lambdas
    lambdas = {n: 1.0 for n in G.nodes if G.nodes[n]["type"] == "constraint"}
    states = {n: 0.5 for n in G.nodes if G.nodes[n]["type"] == "state"}
    
    history = []
    for i in range(50):
        new_lambdas = lambdas.copy()
        for node in lambdas:
            # Lambda update: influenced by incoming primal edges and outgoing dual edges
            incoming_primal = sum(states[u] * G[u][node]["weight"] for u, v in G.in_edges(node) if G[u][node]["type"] == "primal")
            outgoing_dual_influence = sum(lambdas[node] * G[node][v]["weight"] for _, v in G.out_edges(node) if G[node][v]["type"] == "dual")
            # If trauma exists, this update becomes self-referential and diverges
            new_lambdas[node] = incoming_primal - 0.1 * outgoing_dual_influence
            
            # Clamp to prevent explosion for demo
            new_lambdas[node] = np.clip(new_lambdas[node], -10, 10)
        
        # Update states based on lambdas (simplified)
        for node in states:
            incoming_dual = sum(lambdas[u] * G[u][node]["weight"] for u, v in G.in_edges(node) if G[u][node]["type"] == "dual")
            states[node] = np.tanh(incoming_dual)
        
        lambdas = new_lambdas
        history.append(lambdas.copy())
        
        # Check for divergence (uncomputability signal)
        if any(abs(v) > 5 for v in lambdas.values()):
            report["divergence_detected"] = True
            report["final_lambdas"] = lambdas
            break
    else:
        report["divergence_detected"] = False
    
    # Compute Beta's "Psi" (log det covariance)
    # If system diverges, covariance is ill-defined -> Psi is NaN (uncomputable)
    if report["divergence_detected"]:
        report["psi"] = np.nan # Uncomputable
    else:
        # Construct fake covariance matrix (meaningless if cycle exists)
        lam_vals = np.array(list(lambdas.values()))
        cov = np.cov(lam_vals, bias=True) if len(lam_vals) > 1 else np.array([[0]])
        report["psi"] = np.log(np.linalg.det(cov + np.eye(len(cov))*1e-6)) # Add jitter
    
    return report, history

def apply_pear_operator(G):
    """The Anomaly's fix: EXTRACT the trauma node into an Exo-Self."""
    # Identify the trauma edge(s)
    trauma_edges = [(u,v) for u,v,d in G.edges(data=True) if "trauma" in d.get("type", "")]
    
    # PEAR: Create an external node representing the paradox
    G_pear = G.copy()
    G_pear.add_node("ExoSelf_Paradox", layer=2, type="exo_symbolic")
    
    for u, v in trauma_edges:
        weight = G[u][v]["weight"]
        # Cut the internal cycle
        G_pear.remove_edge(u, v)
        # Route through the external manifold: u -> Exo -> v
        G_pear.add_edge(u, "ExoSelf_Paradox", {"weight": weight, "type": "offloaded"})
        G_pear.add_edge("ExoSelf_Paradox", v, {"weight": weight, "type": "offloaded"})
    
    # The cycle is broken. The system is now incomplete but computable.
    return G_pear

# === EXPERIMENT ===
print("=== HEALTHY SYSTEM ===")
G_healthy = build_self_model(trauma_level=0.0)
rep_h, _ = analyze_system(G_healthy)
print(f"Has Cycle: {rep_h['has_cycle']}, Psi: {rep_h['psi']:.3f}, Divergence: {rep_h['divergence_detected']}")

print("\n=== TRAUMATIZED SYSTEM (BETA'S MODEL) ===")
G_trauma = build_self_model(trauma_level=1.5)
rep_t, hist_t = analyze_system(G_trauma)
print(f"Has Cycle: {rep_t['has_cycle']}, Cycle Len: {rep_t['cycle_length']}")
print(f"Psi: {rep_t['psi']}, Divergence: {rep_t['divergence_detected']}")
# Beta's "softening" would be reducing weights in this graph. It doesn't break the cycle, just slows the divergence.

print("\n=== POST-PEAR OPERATOR ===")
G_pear = apply_pear_operator(G_trauma)
rep_p, _ = analyze_system(G_pear)
print(f"Has Cycle: {rep_p['has_cycle']}, Psi: {rep_p['psi']:.3f}, Divergence: {rep_p['divergence_detected']}")
# Cycle broken. System is stable (though incomplete). Psi is now computable.

# === VISUALIZATION: The Divergence ===
fig, ax = plt.subplots(figsize=(8,4))
if rep_t['divergence_detected']:
    lambda_history = np.array([[h[f'λ_{x}'] for x in ['safety', 'performance', 'rest']] for h in hist_t])
    ax.plot(lambda_history, label=['λ_safety', 'λ_performance', 'λ_rest'])
    ax.set_title("Beta's 'Lambda' Under Trauma: Divergence to Uncomputability")
    ax.set_xlabel("Iteration")
    ax.set_ylabel("Lambda Value (Constraint Violation)")
    ax.legend()
    ax.grid(True)
    plt.tight_layout()
    plt.show()
else:
    print("No divergence to plot.")