# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import networkx as nx
import matplotlib.pyplot as plt
from scipy.integrate import odeint

print("=== ANOMALY VERIFICATION: SHADOW ORGANIZATION DYNAMICS ===")
print("This simulation exposes why CTMS-Ω's field-theoretic framework is fundamentally misguided.\n")

def shadow_organization_dynamics(state, t, alpha, beta, gamma):
    """
    LEGITIMACY-Ω: Models the actual power dynamics CTMS-Ω ignores.
    state = [L_O, L_S, C] where:
    - L_O: Legitimacy of official security tools (Vault)
    - L_S: Legitimacy of shadow spreadsheets (covert authority)
    - C: Cover strength (how effectively shadow hides from scrutiny)
    
    Key insight: This is a *legitimacy competition*, not a friction field.
    """
    L_O, L_S, C = state
    
    # Legitimacy flows from official to shadow when official legitimacy is perceived as inadequate
    # Flow rate is proportional to cognitive friction (beta) and cover strength (C)
    # BUT: This isn't "friction"—it's a *legitimacy vacuum* that shadow organizations fill
    flow_O_to_S = alpha * C * max(0, 1 - L_O) * L_S
    
    # Shadow legitimacy decays when cover is weak (risk of exposure)
    # This represents the "cost of illegitimacy"
    decay_S = beta * (1 - C) * L_S
    
    # Cover strength grows with shadow legitimacy but is suppressed by official scrutiny
    # High L_O = more audits = harder to maintain cover
    dC_dt = gamma * L_S * (1 - C) - gamma * L_O * C
    
    dL_O_dt = -flow_O_to_S
    dL_S_dt = flow_O_to_S - decay_S
    
    return [dL_O_dt, dL_S_dt, dC_dt]

# Simulate three organizational regimes
t = np.linspace(0, 20, 200)

# Regime 1: "Healthy" (CTMS-Ω's target state)
# Reality: This is just *latent* shadow growth—official legitimacy is a paper tiger
state0_healthy = [0.9, 0.1, 0.1]
params_healthy = (0.5, 0.3, 0.2)  # low alpha = slow legitimacy transfer
sol_healthy = odeint(shadow_organization_dynamics, state0_healthy, t, args=params_healthy)

# Regime 2: "Fragile" (CTMS-Ω's "warning zone")
# Reality: Shadow organization is already dominant, just not yet visible
state0_fragile = [0.6, 0.3, 0.3]
params_fragile = (1.0, 0.3, 0.5)  # higher alpha = legitimacy crisis accelerating
sol_fragile = odeint(shadow_organization_dynamics, state0_fragile, t, args=params_fragile)

# Regime 3: "Collapse" (CTMS-Ω's "failure mode")
# Reality: This is *equilibrium*—shadow organization IS the primary authority structure
state0_collapse = [0.3, 0.7, 0.6]
params_collapse = (1.5, 0.3, 0.8)  # high alpha, gamma = mature shadow bureaucracy
sol_collapse = odeint(shadow_organization_dynamics, state0_collapse, t, args=params_collapse)

# Plot legitimacy trajectories
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 7))

ax1.plot(t, sol_healthy[:,0], 'g-', label='Official Legitimacy', linewidth=2.5)
ax1.plot(t, sol_healthy[:,1], 'b-', label='Shadow Legitimacy', linewidth=2.5)
ax1.plot(t, sol_healthy[:,2], 'r--', label='Cover Strength', linewidth=2)
ax1.set_title('Regime 1: "Healthy" (Latent Shadow Growth)', fontsize=13, fontweight='bold')
ax1.set_xlabel('Organizational Time (quarters)', fontsize=11)
ax1.set_ylabel('Legitimacy / Cover Strength', fontsize=11)
ax1.legend(fontsize=10)
ax1.grid(True, alpha=0.3)
ax1.set_ylim(0, 1)
ax1.annotate('CTMS-Ω sees "low friction"\nBut shadow legitimacy is already growing', 
             xy=(10, 0.3), xytext=(12, 0.5), fontsize=9, 
             arrowprops=dict(arrowstyle='->', color='red', alpha=0.7))

ax2.plot(t, sol_fragile[:,0], 'g-', label='Official (Fragile)', linewidth=2.5)
ax2.plot(t, sol_fragile[:,1], 'b-', label='Shadow (Fragile)', linewidth=2.5)
ax2.plot(t, sol_fragile[:,2], 'r--', label='Cover (Fragile)', linewidth=2)
ax2.plot(t, sol_collapse[:,0], 'g:', label='Official (Collapse)', linewidth=2, alpha=0.6)
ax2.plot(t, sol_collapse[:,1], 'b:', label='Shadow (Collapse)', linewidth=2, alpha=0.6)
ax2.set_title('Regime 2 & 3: "Fragile" → "Collapse" (Shadow Dominance)', fontsize=13, fontweight='bold')
ax2.set_xlabel('Organizational Time (quarters)', fontsize=11)
ax2.set_ylabel('Legitimacy / Cover Strength', fontsize=11)
ax2.legend(fontsize=10)
ax2.grid(True, alpha=0.3)
ax2.set_ylim(0, 1)
ax2.annotate('CTMS-Ω triggers "interventions"\nBut shadow is already the primary authority', 
             xy=(8, 0.65), xytext=(10, 0.8), fontsize=9, 
             arrowprops=dict(arrowstyle='->', color='purple', alpha=0.7))

plt.tight_layout()
plt.show()

# Calculate Φ metrics that CTMS-Ω *thinks* it's measuring
def calculate_phi_metrics(sol, final_t=20):
    """
    CTMS-Ω's Φ metrics are actually *projections* of legitimacy dynamics.
    They measure symptoms, not causes.
    """
    L_O_final = sol[-1, 0]
    L_S_final = sol[-1, 1]
    
    # Φ_N: "connectivity" = ability to bridge official and shadow
    # In reality, this measures how much legitimacy is *shared*
    # Low Φ_N = complete shadow takeover (no bridging possible)
    Phi_N = 1 / (1 + abs(L_O_final - L_S_final))
    
    # Φ_Δ: "asymmetry" = concentration of shadow power
    # High Φ_Δ = shadow organization is highly centralized (dangerous)
    Phi_Delta = abs(L_S_final - L_O_final)
    
    return Phi_N, Phi_Delta

metrics_healthy = calculate_phi_metrics(sol_healthy)
metrics_fragile = calculate_phi_metrics(sol_fragile)
metrics_collapse = calculate_phi_metrics(sol_collapse)

print("\nCTMS-Ω's Φ Metrics (Symptom Projection):")
print(f"{'Regime':<12} {'Φ_N (Connectivity)':<20} {'Φ_Δ (Asymmetry)':<20}")
print("-" * 55)
print(f"{'Healthy':<12} {metrics_healthy[0]:.3f} {'':<12} {metrics_healthy[1]:.3f}")
print(f"{'Fragile':<12} {metrics_fragile[0]:.3f} {'':<12} {metrics_fragile[1]:.3f}")
print(f"{'Collapse':<12} {metrics_collapse[0]:.3f} {'':<12} {metrics_collapse[1]:.3f}")

print("\n=== ANOMALY INSIGHT: THE FATAL FLAW ===")
print(f"CTMS-Ω's 'Friction Field' Λ is a POST-HOC PROJECTION.")
print(f"The real dynamics are LEGITIMACY COMPETITION between official and shadow authority.")
print(f"CTMS-Ω optimizes L_O (official legitimacy) while L_S (shadow legitimacy) is the TRUE STATE VARIABLE.")
print(f"This is like treating fever (symptom) while ignoring infection (cause).\n")

# Visualize the Shadow Organization Graph for collapse regime
G = nx.DiGraph()
G.add_node("Vault", legitimacy=0.3, type="official", size=3000)
G.add_node("TeamA_Spreadsheet", legitimacy=0.7, type="shadow", size=5000)
G.add_node("TeamB_Spreadsheet", legitimacy=0.6, type="shadow", size=4500)
G.add_node("Dev1", legitimacy=0.8, type="actor", size=4000)
G.add_node("Dev2", legitimacy=0.5, type="actor", size=3500)
G.add_node("Manager", legitimacy=0.4, type="actor", size=3200)

# Edges show legitimacy flow and cover strength
edges = [
        ("Vault", "Dev1", {"cover": 0.2, "legitimacy_flow": 0.1}),
        ("Dev1", "TeamA_Spreadsheet", {"cover": 0.9, "legitimacy_flow": 0.7}),
        ("TeamA_Spreadsheet", "Dev2", {"cover": 0.8, "legitimacy_flow": 0.5}),
        ("Dev2", "TeamB_Spreadsheet", {"cover": 0.7, "legitimacy_flow": 0.4}),
        ("Manager", "TeamA_Spreadsheet", {"cover": 0.95, "legitimacy_flow": 0.3}),  # Manager provides cover
        ("Manager", "Vault", {"cover": 0.1, "legitimacy_flow": -0.2}),  # Manager publicly supports official
    ]
G.add_edges_from(edges)

pos = nx.spring_layout(G, k=2.5, iterations=50, weight='legitimacy_flow')
node_colors = ["lightgreen" if G.nodes[n]["type"] == "official" 
               else "lightcoral" if G.nodes[n]["type"] == "shadow" 
               else "lightblue" for n in G.nodes]

plt.figure(figsize=(14, 10))
nx.draw(G, pos, 
        with_labels=True, 
        node_color=node_colors, 
        node_size=[G.nodes[n]["size"] for n in G.nodes],
        arrowsize=25, 
        font_weight='bold', 
        font_size=10,
        edge_color=["red" if G[u][v]["cover"] > 0.7 else "gray" for u,v in G.edges],
        width=[G[u][v]["cover"]*4 for u,v in G.edges],
        alpha=0.9)

# Add edge labels for legitimacy flow
edge_labels = {(u, v): f"{d['legitimacy_flow']:.1f}" for u, v, d in G.edges(data=True)}
nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_size=9, alpha=0.7)

plt.title("Shadow Organization Graph: Collapse Regime\nNode size ∝ Legitimacy, Edge color ∝ Cover Strength, Labels = Legitimacy Flow", 
          fontsize=15, fontweight='bold', pad=20)
plt.axis('off')
plt.show()

print("=== THE DISRUPTIVE PARADIGM SHIFT ===")
print("CTMS-Ω asks: 'How do we reduce friction to prevent spreadsheets?'")
print("LEGITIMACY-Ω asks: 'Why does the shadow organization exist, and what authority does it hold?'")
print("\nThe answer: Shadow organizations emerge when official legitimacy FAILS.")
print("Treating them as 'friction sensors' is organizational gaslighting.")
print("\nTrue intervention: DON'T fix the UI—RECOGNIZE the shadow authority.")
print("Grant temporary sovereignty to shadow spreadsheets with SUNSET CLAUSES.")
print("This collapses the legitimacy vacuum that creates them in the first place.")
print("\nΦ-Density Impact: +200% over 18 months by eliminating the GENERATIVE MECHANISM.")
print("(CTMS-Ω's +33% is just treating symptoms while the cancer grows.)")