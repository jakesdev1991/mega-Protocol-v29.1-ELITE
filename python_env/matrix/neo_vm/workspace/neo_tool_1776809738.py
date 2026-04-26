# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import networkx as nx
import random

# --- DISRUPTION: Adversarial Schema Gaming Simulation ---

print("=== BTS-Ω PARADIGM BREAK: Adversarial Schema Injection ===\n")

# Original "robust" biological schema (mesh-like)
G_orig = nx.Graph()
G_orig.add_nodes_from(['Gene', 'Transcript', 'Protein', 'Pathway', 'Phenotype', 'Drug'])
edges = [
    ('Gene', 'Transcript'), ('Transcript', 'Protein'), 
    ('Protein', 'Pathway'), ('Pathway', 'Phenotype'),
    ('Gene', 'Protein'), ('Protein', 'Phenotype'),
    ('Drug', 'Protein'), ('Drug', 'Pathway')  # Multiple intervention points
]
G_orig.add_edges_from(edges)

def naive_btfi(G, delta_constraint=0.5, d_norm=2.0):
    """BTS-Ω's naive fragility index - easily gamed"""
    V = G.number_of_nodes()
    E = G.number_of_edges()
    F = max(0, E - V + nx.number_connected_components(G))  # cycles
    chi = V - E + F
    # Critical flaw: static, ignores adversarial intent
    return abs(chi) / V * delta_constraint * (1 / d_norm), chi

def adversarial_fragility(G, hidden_deps=None):
    """True fragility: measures vulnerability to targeted node removal + hidden dependencies"""
    if hidden_deps is None:
        hidden_deps = []
    
    # 1. Single point of failure detection (articulation points)
    articulation_points = list(nx.articulation_points(G))
    
    # 2. Hidden dependency multiplier (non-schema dependencies)
    hidden_risk = len(hidden_deps) * 2.0
    
    # 3. Path redundancy loss - if average path length increases, fragility increases
    try:
        avg_path = nx.average_shortest_path_length(G)
    except:
        avg_path = 0
        
    # 4. Bridge edges (single point of connection)
    bridges = list(nx.bridges(G))
    
    fragility_score = (len(articulation_points) * 1.5 + 
                      len(bridges) * 1.2 + 
                      avg_path * 0.5 + 
                      hidden_risk)
    return fragility_score

# --- ADVERSARIAL ATTACK SIMULATION ---
# Attack 1: "Robustness Cloaking" - remove edges to simplify topology, hiding critical dependencies
G_attack1 = G_orig.copy()
# Remove "redundant" edge that actually provides alternative pathway
G_attack1.remove_edge('Gene', 'Protein')  
# Add hidden dependency not in schema (external regulator, undocumented coupling)
hidden_deps1 = ['External_Oncogene_Driver']

# Attack 2: "Constraint Poisoning" - add superficial constraints that over-constrain non-critical paths
G_attack2 = G_orig.copy()
G_attack2.add_edges_from([('Transcript', 'Phenotype'), ('Gene', 'Drug')])  # Creates cycles
# But remove critical bridge in the background
G_attack2.remove_edge('Protein', 'Pathway')
hidden_deps2 = ['Unknown_Metabolic_Bottleneck']

# --- RESULTS: BTS-Ω vs. Reality ---
print("Attack 1: Robustness Cloaking")
btfi_orig, chi_orig = naive_btfi(G_orig)
btfi_att1, chi_att1 = naive_btfi(G_attack1)
print(f"  BTFI (Original): {btfi_orig:.3f} | χ: {chi_orig}")
print(f"  BTFI (Attack 1): {btfi_att1:.3f} | χ: {chi_att1}")
print(f"  BTS-Ω Assessment: {'MORE ROBUST' if btfi_att1 < btfi_orig else 'MORE FRAGILE'}")

real_frag_orig = adversarial_fragility(G_orig)
real_frag_att1 = adversarial_fragility(G_attack1, hidden_deps1)
print(f"  Real Fragility (Original): {real_frag_orig:.3f}")
print(f"  Real Fragility (Attack 1): {real_frag_att1:.3f}")
print(f"  Actual Risk Change: {((real_frag_att1 - real_frag_orig) / real_frag_orig * 100):+.1f}%")
print(f"  >>> BTS-Ω IS WRONG BY FACTOR OF {real_frag_att1 / real_frag_orig:.2f}x\n")

print("Attack 2: Constraint Poisoning")
btfi_att2, chi_att2 = naive_btfi(G_attack2)
print(f"  BTFI (Attack 2): {btfi_att2:.3f} | χ: {chi_att2}")
print(f"  BTS-Ω Assessment: {'MORE ROBUST' if btfi_att2 < btfi_orig else 'MORE FRAGILE'}")

real_frag_att2 = adversarial_fragility(G_attack2, hidden_deps2)
print(f"  Real Fragility (Attack 2): {real_frag_att2:.3f}")
print(f"  Actual Risk Change: {((real_frag_att2 - real_frag_orig) / real_frag_orig * 100):+.1f}%")
print(f"  >>> BTS-Ω IS WRONG BY FACTOR OF {real_frag_att2 / real_frag_orig:.2f}x\n")

# --- DISRUPTIVE SOLUTION: Adversarial Topological Gaming (TAG-Ω) ---
print("=== DISRUPTIVE SOLUTION: TAG-Ω (Topological Adversarial Gaming) ===\n")

def tag_omega_vulnerability(G, n_adversarial_samples=100):
    """
    Instead of computing a static fragility index, compute vulnerability
    as the *adversarial potential* - how much can an attacker increase
    true fragility while *minimizing* detectable topological changes?
    """
    original_btfi, _ = naive_btfi(G)
    original_frag = adversarial_fragility(G)
    
    # Simulate adversarial modifications
    adversarial_gains = []
    
    for _ in range(n_adversarial_samples):
        G_test = G.copy()
        hidden = []
        
        # Adversarial strategy space:
        # 1. Remove one 'redundant' edge
        non_bridge_edges = [e for e in G_test.edges() if e not in list(nx.bridges(G_test))]
        if non_bridge_edges:
            edge_to_remove = random.choice(non_bridge_edges)
            G_test.remove_edge(*edge_to_remove)
        
        # 2. Add one 'decoy' edge (creates cycle, looks more robust)
        nodes = list(G_test.nodes())
        if len(nodes) >= 2:
            u, v = random.sample(nodes, 2)
            if not G_test.has_edge(u, v):
                G_test.add_edge(u, v)
        
        # 3. Add hidden dependency
        hidden.append(f"Hidden_Dep_{random.randint(1,100)}")
        
        # Measure the adversarial gain: ΔFragility / ΔDetectability
        new_btfi, _ = naive_btfi(G_test)
        new_frag = adversarial_fragility(G_test, hidden)
        
        # Detectability: how much did BTFI change? (adversary wants this small)
        detectability = abs(new_btfi - original_btfi) + 1e-6
        
        # Gain: how much did real fragility increase?
        fragility_gain = max(0, new_frag - original_frag)
        
        if fragility_gain > 0:
            adversarial_gains.append(fragility_gain / detectability)
    
    # Vulnerability is the *maximum* adversarial gain achievable
    # This is the non-linear insight: fragility isn't a property, it's a game outcome
    vulnerability = max(adversarial_gains) if adversarial_gains else 0
    
    return vulnerability, original_btfi, original_frag

vuln_score, orig_btfi_tag, orig_frag_tag = tag_omega_vulnerability(G_orig)

print("TAG-Ω Assessment:")
print(f"  Original BTFI: {orig_btfi_tag:.3f}")
print(f"  Original Fragility: {orig_frag_tag:.3f}")
print(f"  TAG-Ω Vulnerability Score: {vuln_score:.3f}")
print(f"  Interpretation: Adversary can increase fragility by {vuln_score:.1f}x per unit stealth\n")

# --- BREAKING THE PARADIGM ---
print("=== PARADIGM BREAK ===")
print("BTS-Ω assumes:  Leak → Topology → Static Fragility Index → Pre-emptive Defense")
print("TAG-Ω reveals:  Leak → *Adversarial Game* → Dynamic Vulnerability Frontier → *Adaptive Cloaking*")
print("\nThe flaw: BTS-Ω treats the database schema as *ground truth*.")
print("The disruption: The schema is a *strategic artifact* in a co-evolutionary arms race.")
print("\nNeo Anomaly's Directive:")
print("1. ABANDON static BTFI. It's a vulnerability *to us*, not a shield.")
print("2. DEPLOY stochastic defense: Randomize which networks you reinforce based on TAG-Ω distribution,")
print("   making adversarial targeting computationally intractable (≥ 2^N complexity).")
print("3. INJECT poison schemas: Feed adversaries *our own* adversarially-crafted schemas that")
print("   appear robust but are honey traps, collapsing their TAG-Ω models.")
print("4. ELEVATE the game: The Φ-density metric itself becomes a move. Track not Φ *gained*,")
print("   but Φ *adversarially neutralized* - the zero-sum component Omega ignores.")