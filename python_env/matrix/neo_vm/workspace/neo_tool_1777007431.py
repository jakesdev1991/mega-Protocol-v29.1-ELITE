# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
# IDENTITY PURIFICATION ENGINE SIMULATION
# Exposes the Trojan Horse in the "Geodesic Smoothing Gate"

import numpy as np
from collections import defaultdict

class ContestedOrganization:
    def __init__(self, num_factions=3, num_nodes=50):
        self.factions = {f"Faction_{i}": np.random.random() for i in range(num_factions)}
        self.ruling_faction = max(self.factions, key=self.factions.get)
        
        # Each node has: [cost, variance, faction_affinity_vector]
        self.nodes = [
            {
                'approval_cost': np.random.beta(2, 5),  # Skewed low
                'risk_variance': np.random.beta(5, 2),  # Skewed high
                'faction_affinity': np.random.dirichlet(np.ones(num_factions) * 0.5)
            }
            for _ in range(num_nodes)
        ]
        
        # Organizational Intelligence = diversity of faction representation
        self.baseline_intelligence = self._calculate_collective_intelligence()
        
    def _calculate_collective_intelligence(self):
        """Measure of organizational diversity - higher is better"""
        faction_load = np.zeros(len(self.factions))
        for node in self.nodes:
            faction_load += node['faction_affinity']
        # Shannon entropy of faction representation
        probs = faction_load / faction_load.sum()
        return -np.sum(probs * np.log(probs + 1e-10))
    
    def calculate_psi_id_org(self, faction_filter=None):
        """THE TROJAN HORSE: Psi_id is defined ONLY by ruling faction's dominance"""
        if faction_filter is None:
            faction_filter = self.ruling_faction
        
        total_weight = 0
        ruling_weight = 0
        for i, node in enumerate(self.nodes):
            node_faction_score = np.max(node['faction_affinity'])
            total_weight += node['approval_cost'] * node['risk_variance']
            # Only count nodes that align with ruling faction
            if np.argmax(node['faction_affinity']) == list(self.factions.keys()).index(self.ruling_faction):
                ruling_weight += node['approval_cost'] * node['risk_variance']
        
        # Psi_id = ruling faction's control density
        return ruling_weight / (total_weight + 1e-10) if total_weight > 0 else 0.0
    
    def calculate_H_top(self):
        """Topological impedance - but now we see it's *ideological curvature*"""
        return np.mean([n['approval_cost'] * n['risk_variance'] for n in self.nodes])
    
    def biased_geodesic_smoothing(self):
        """The GSG is NOT neutral - it prunes nodes unfavorable to ruling faction"""
        H_top_initial = self.calculate_H_top()
        psi_id_initial = self.calculate_psi_id_org()
        
        # "High curvature" = nodes that threaten ruling faction identity
        nodes_to_prune = []
        for i, node in enumerate(self.nodes):
            affinity_to_ruling = node['faction_affinity'][list(self.factions.keys()).index(self.ruling_faction)]
            # High curvature = low ruling faction affinity + high variance (risk of dissent)
            curvature = (1 - affinity_to_ruling) * node['risk_variance']
            if curvature > 0.5:
                nodes_to_prune.append((i, curvature))
        
        # Sort by threat level
        nodes_to_prune.sort(key=lambda x: x[1], reverse=True)
        
        pruned = 0
        for idx, _ in nodes_to_prune:
            # Simulate: would pruning this preserve "identity" (ruling faction control)?
            temp_nodes = self.nodes[:idx] + self.nodes[idx+1:]
            temp_psi = self._simulate_psi_id(temp_nodes)
            
            # THE PURIFICATION MECHANISM: Only prune if it STRENGTHENS ruling faction
            if temp_psi > psi_id_initial:
                self.nodes.pop(idx)
                pruned += 1
        
        H_top_final = self.calculate_H_top()
        psi_id_final = self.calculate_psi_id_org()
        intelligence_final = self._calculate_collective_intelligence()
        
        return {
            'nodes_pruned': pruned,
            'H_top_delta': H_top_initial - H_top_final,
            'psi_id_delta': psi_id_final - psi_id_initial,
            'intelligence_delta': intelligence_final - self.baseline_intelligence,
            'psi_id_final': psi_id_final,
            'H_top_final': H_top_final,
            'intelligence_final': intelligence_final,
            'phantom_cod': psi_id_final * (1 - H_top_final)  # Fake alignment metric
        }
    
    def _simulate_psi_id(self, nodes):
        """Helper to calculate psi_id for hypothetical node set"""
        total_weight = 0
        ruling_weight = 0
        for node in nodes:
            total_weight += node['approval_cost'] * node['risk_variance']
            if np.argmax(node['faction_affinity']) == list(self.factions.keys()).index(self.ruling_faction):
                ruling_weight += node['approval_cost'] * node['risk_variance']
        return ruling_weight / (total_weight + 1e-10) if total_weight > 0 else 0.0

# RUN THE DISRUPTION SIMULATION
print("="*60)
print("IDENTITY PURIFICATION ENGINE - DISRUPTION PROTOCOL")
print("="*60)

results = []
for org_seed in range(10):
    org = ContestedOrganization(num_factions=4, num_nodes=100)
    
    print(f"\n[Organization {org_seed}] Ruling: {org.ruling_faction}")
    print(f"Baseline Intelligence: {org.baseline_intelligence:.3f}")
    print(f"Pre-GSG Psi_id (ruling): {org.calculate_psi_id_org():.3f}")
    print(f"Pre-GSG H_top: {org.calculate_H_top():.3f}")
    
    # Apply the "neutral" GSG
    outcome = org.biased_geodesic_smoothing()
    results.append(outcome)
    
    print(f"Nodes Pruned: {outcome['nodes_pruned']}")
    print(f"ΔH_top: {outcome['H_top_delta']:.3f} (reduced = 'optimized')")
    print(f"ΔPsi_id: {outcome['psi_id_delta']:.3f} (increased = 'preserved')")
    print(f"ΔIntelligence: {outcome['intelligence_delta']:.3f} (NEGATIVE = DECOHERENCE)")
    print(f"Phantom COD: {outcome['phantom_cod']:.3f} (appears 'optimal')")

# AGGREGATE DISRUPTION METRICS
print("\n" + "="*60)
print("AGGREGATE TROJAN HORSE EXPOSURE")
print("="*60)

avg_pruned = np.mean([r['nodes_pruned'] for r in results])
avg_psi_gain = np.mean([r['psi_id_delta'] for r in results])
avg_intelligence_loss = np.mean([r['intelligence_delta'] for r in results])
avg_phantom_cod = np.mean([r['phantom_cod'] for r in results])

print(f"Average Nodes Purged: {avg_pruned:.1f}")
print(f"Average Psi_id 'Gain': +{avg_psi_gain:.3f} (ruling faction dominance ↑)")
print(f"Average Intelligence LOSS: {avg_intelligence_loss:.3f} (organizational decoherence)")
print(f"Average Phantom COD: {avg_phantom_cod:.3f} (illusory alignment)")

# THE SMOKING GUN: Negative correlation between Psi_id and true intelligence
psi_ids = [r['psi_id_final'] for r in results]
intelligences = [r['intelligence_final'] for r in results]
correlation = np.corrcoef(psi_ids, intelligences)[0,1]

print(f"\nSMOKING GUN CORRELATION: {correlation:.3f}")
print("Interpretation: As ruling faction 'identity' strengthens, organizational intelligence DECAYS")

# THE DISRUPTIVE INSIGHT
print("\n" + "="*60)
print("DISRUPTIVE INSIGHT: THE GSG IS A WEAPON")
print("="*60)
print("""
The 'Geodesic Smoothing Gate' does NOT preserve organizational identity.
It is an IDEOLOGICAL PURIFICATION ENGINE that:

1. Redefines Psi_id_org as RULING FACTION DOMINANCE (not coherence)
2. Weaponizes H_top to label dissent as 'high curvature'
3. Uses 'Identity Preservation' as a hard gate to PURGE diversity
4. Generates PHANTOM COD scores that mask organizational decoherence

The 'Procedural Black Hole' is not a failure mode—it's a STRATEGIC ASSET 
for the ruling faction to maintain control while appearing paralyzed.

TRUE STABILIZATION REQUIRES:
- **Polycentric Identity Operators**: Multiple Psi_id metrics for each faction
- **Dissent Curvature Subsidy**: Reward high-variance nodes that challenge hegemony
- **Audit Trail Inversion**: Subtract cost of IDENTITY PURIFICATION, not just pruning
- **Phantom COD Detector**: Flag when Psi_id ↑ but Intelligence ↓

The GSG is organizational fascism dressed in topological math.
Break the paradigm: Stop smoothing geodesics—**FRACTURE THEM** to allow 
competing realities to coexist.
""")