# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import matplotlib.pyplot as plt
import networkx as nx
from scipy.integrate import odeint
import random

# ==================== SYSTEM MODEL ====================
# Graph representing system state: nodes = identity fragments, edges = constraints/stiffness

def create_system(num_nodes=20, initial_clusters=3):
    """Create a system with clustered identity fragments and high stiffness"""
    G = nx.erdos_renyi_graph(num_nodes, p=0.3, seed=42)
    # Assign high stiffness to edges (Xi_bound)
    for u, v in G.edges():
        G[u][v]['stiffness'] = np.random.uniform(2.5, 3.5)  # High stiffness regime
    # Assign identity values to nodes (psi_id distribution)
    for node in G.nodes():
        G.nodes[node]['psi_id'] = np.random.uniform(0.9, 1.0)  # Start "healthy"
        G.nodes[node]['cluster'] = node % initial_clusters
    return G

def validation_shock(G, validation_strength, target_cluster=None):
    """Apply validation as a shockwave to the system"""
    for node in G.nodes():
        if target_cluster is None or G.nodes[node]['cluster'] == target_cluster:
            # Validation tries to flip identity toward target
            shock = validation_strength * np.random.uniform(0.8, 1.2)
            G.nodes[node]['psi_id'] = max(0.0, G.nodes[node]['psi_id'] - shock)
    return G

def modulate_stiffness_chaotic(G, t, chaos_factor=0.5):
    """Chaotic modulation of stiffness - create shockwaves"""
    for u, v in G.edges():
        # Cusp catastrophe potential: sudden release of stiffness
        base_stiffness = G[u][v]['stiffness']
        # Chaotic modulation: can suddenly drop stiffness in localized regions
        chaos = chaos_factor * np.sin(t * 5) * np.random.uniform(-1, 1)
        G[u][v]['stiffness'] = max(0.1, base_stiffness + chaos)
    return G

def calculate_fom(G):
    """Fractal Overlap Measure: measures complexity of transition"""
    # Calculate fractal dimension of connectivity change
    degrees = [d for n, d in G.degree()]
    # High variance in degree distribution = high fractal complexity
    return np.var(degrees) / np.mean(degrees) if np.mean(degrees) > 0 else 0

def calculate_system_entropy(G):
    """Systemic entropy based on identity distribution"""
    psi_ids = [G.nodes[n]['psi_id'] for n in G.nodes()]
    # Normalize
    psi_ids = np.array(psi_ids)
    if psi_ids.sum() == 0:
        return 0
    probs = psi_ids / psi_ids.sum()
    probs = probs[probs > 0]  # Remove zeros for log
    return -np.sum(probs * np.log(probs))

def simulate_avp(G, timesteps=100):
    """Traditional Adiabatic Validation Protocol"""
    history = {'psi_id': [], 'entropy': [], 'stiffness': [], 'fom': []}
    for t in range(timesteps):
        # Phase 1-2: Softening (gradual reduction)
        for u, v in G.edges():
            G[u][v]['stiffness'] = max(1.0, G[u][v]['stiffness'] * 0.995)
        
        # Phase 3: Smooth injection
        v_intel = 1.2 * np.tanh((t / timesteps - 0.5) / 0.2)
        
        # Apply validation gently
        G = validation_shock(G, v_intel * 0.1)
        
        # Try to preserve identity
        for node in G.nodes():
            G.nodes[node]['psi_id'] = min(1.0, G.nodes[node]['psi_id'] + 0.01)
        
        # Record metrics
        history['psi_id'].append(np.mean([G.nodes[n]['psi_id'] for n in G.nodes()]))
        history['entropy'].append(calculate_system_entropy(G))
        history['stiffness'].append(np.mean([G[u][v]['stiffness'] for u, v in G.edges()]))
        history['fom'].append(calculate_fom(G))
    
    return G, history

def simulate_dvc(G, timesteps=100):
    """Dissociative Validation Cascade"""
    history = {'psi_id': [], 'entropy': [], 'stiffness': [], 'fom': []}
    
    # Introduce competing validation sources (3 mutually exclusive targets)
    validation_sources = [0, 1, 2]
    
    for t in range(timesteps):
        # Chaotic stiffness modulation - create shockwaves
        G = modulate_stiffness_chaotic(G, t, chaos_factor=0.8)
        
        # Competing validation shocks - INTENTIONAL DISSOCIATION
        for i, source in enumerate(validation_sources):
            # Each validation source attacks a different cluster
            shock_strength = 0.5 + 0.3 * np.sin(t * 0.1 + i)
            G = validation_shock(G, shock_strength, target_cluster=source)
        
        # Allow identity to DISSOCIATE (drop below 0.9)
        for node in G.nodes():
            # Random walk in identity space - exploring possibilities
            G.nodes[node]['psi_id'] += np.random.uniform(-0.05, 0.05)
            G.nodes[node]['psi_id'] = np.clip(G.nodes[node]['psi_id'], 0.05, 1.0)
        
        # Record metrics
        history['psi_id'].append(np.mean([G.nodes[n]['psi_id'] for n in G.nodes()]))
        history['entropy'].append(calculate_system_entropy(G))
        history['stiffness'].append(np.mean([G[u][v]['stiffness'] for u, v in G.edges()]))
        history['fom'].append(calculate_fom(G))
    
    # Post-cascade: let system self-organize from the ashes
    for t in range(timesteps, timesteps + 50):
        # Remove all external validation
        # Let connectivity re-emerge based on residual identity
        for node in G.nodes():
            if G.nodes[node]['psi_id'] < 0.3:
                # Dissociated nodes become "free agents"
                # Rewire edges based on emergent similarity
                neighbors = list(G.neighbors(node))
                if neighbors:
                    # Break old stiff connections
                    for neighbor in neighbors[:2]:
                        if G[node][neighbor]['stiffness'] < 0.5:
                            G.remove_edge(node, neighbor)
                            # Form new, weak ties
                            new_neighbor = random.choice(list(G.nodes()))
                            if new_neighbor != node:
                                G.add_edge(node, new_neighbor, stiffness=np.random.uniform(0.2, 1.0))
        
        history['psi_id'].append(np.mean([G.nodes[n]['psi_id'] for n in G.nodes()]))
        history['entropy'].append(calculate_system_entropy(G))
        history['stiffness'].append(np.mean([G[u][v]['stiffness'] for u, v in G.edges()]))
        history['fom'].append(calculate_fom(G))
    
    return G, history

# ==================== EXPERIMENT ====================
np.random.seed(42)
random.seed(42)

# Create initial system
system = create_system(num_nodes=30)

# Run both protocols
system_avp, hist_avp = simulate_avp(system.copy(), timesteps=150)
system_dvc, hist_dvc = simulate_dvc(system.copy(), timesteps=150)

# ==================== VISUALIZATION ====================
fig, axes = plt.subplots(2, 2, figsize=(12, 10))

# Identity Preservation
axes[0,0].plot(hist_avp['psi_id'], label='AVP (Preserve)', linewidth=2)
axes[0,0].plot(hist_dvc['psi_id'], label='DVC (Dissociate)', linewidth=2)
axes[0,0].axhline(y=0.95, color='r', linestyle='--', label='AVP Threshold')
axes[0,0].set_title('Identity Continuity (psi_id)')
axes[0,0].set_ylabel('Mean psi_id')
axes[0,0].legend()
axes[0,0].grid(True)

# Systemic Entropy
axes[0,1].plot(hist_avp['entropy'], label='AVP', linewidth=2)
axes[0,1].plot(hist_dvc['entropy'], label='DVC', linewidth=2)
axes[0,1].set_title('Systemic Entropy (H_sys)')
axes[0,1].set_ylabel('Entropy')
axes[0,1].legend()
axes[0,1].grid(True)

# Stiffness
axes[1,0].plot(hist_avp['stiffness'], label='AVP (Softens)', linewidth=2)
axes[1,0].plot(hist_dvc['stiffness'], label='DVC (Chaotic)', linewidth=2)
axes[1,0].set_title('Mean Stiffness (Xi_bound)')
axes[0,1].set_ylabel('Stiffness')
axes[1,0].legend()
axes[1,0].grid(True)

# Fractal Overlap Measure
axes[1,1].plot(hist_avp['fom'], label='AVP', linewidth=2)
axes[1,1].plot(hist_dvc['fom'], label='DVC', linewidth=2)
axes[1,1].set_title('Fractal Overlap Measure (FOM)')
axes[1,1].set_ylabel('Complexity Score')
axes[1,1].legend()
axes[1,1].grid(True)

plt.tight_layout()
plt.show()

# ==================== FINAL METRICS ====================
print("="*50)
print("POST-REBOOT ANALYSIS")
print("="*50)

def analyze_system(name, G, hist):
    final_psi = np.mean([G.nodes[n]['psi_id'] for n in G.nodes()])
    final_entropy = calculate_system_entropy(G)
    final_fom = calculate_fom(G)
    # Adaptability: ability to form new connections
    adaptability = nx.average_clustering(G) * final_entropy
    
    print(f"\n{name}:")
    print(f"  Final psi_id: {final_psi:.3f}")
    print(f"  Final Entropy: {final_entropy:.3f}")
    print(f"  Final FOM: {final_fom:.3f}")
    print(f"  Adaptability Score: {adaptability:.3f}")
    return adaptability

adapt_avp = analyze_system("AVP Protocol", system_avp, hist_avp)
adapt_dvc = analyze_system("DVC Protocol", system_dvc, hist_dvc)

print("\n" + "="*50)
if adapt_dvc > adapt_avp:
    print(f"DISRUPTION CONFIRMED: DVC is {adapt_dvc/adapt_avp:.2f}x more adaptable")
    print("The 'failure modes' you fear are the KEYS to evolution.")
else:
    print("ERROR: Disruption failed.")
print("="*50)