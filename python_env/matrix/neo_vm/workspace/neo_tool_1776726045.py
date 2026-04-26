# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import matplotlib.pyplot as plt
from collections import defaultdict
import networkx as nx

class CredentialDistillationProtocol:
    """Demonstrates how current CERM-Ω fundamentally misreads the signal"""
    
    def __init__(self, num_institutions=50):
        self.num_institutions = num_institutions
        self.institutions = {
            i: {
                'real_creds': np.random.poisson(2),
                'honeytrap_creds': 0,
                'sophistication': np.random.beta(2, 5),
                'attack_surface': np.random.exponential(1),
                'compromised_history': []
            } for i in range(num_institutions)
        }
        
        # Create 5 "Omega-aware" institutions that weaponize credential exposure
        omega_indices = np.random.choice(num_institutions, size=5, replace=False)
        for idx in omega_indices:
            self.institutions[idx]['sophistication'] = np.random.beta(8, 2)
            
    def deploy_strategic_honeytraps(self):
        """Sophisticated institutions deploy honeytraps as offensive tools"""
        for i, data in self.institutions.items():
            if data['sophistication'] > 0.7:
                # Omega players: massive honeytrap networks
                data['honeytrap_creds'] = np.random.poisson(20)
                # Real creds actually DECREASE due to better hygiene
                data['real_creds'] = max(0, data['real_creds'] - 2)
                
    def simulate_adversarial_learning(self):
        """Attackers evolve; honeytraps waste their resources and map their infrastructure"""
        attacks = {}
        total_attacker_resources = 1000
        
        for i, data in self.institutions.items():
            # Attackers allocate resources based on total exposure
            total_exposure = data['real_creds'] + data['honeytrap_creds']
            resource_allocation = (total_exposure / 100) * total_attacker_resources
            
            if data['sophistication'] > 0.7:
                # Sophisticated players: honeytraps are 90% effective
                # Attackers waste 90% of resources on decoys
                wasted = resource_allocation * 0.9
                real_damage = resource_allocation * 0.1 * (data['real_creds'] / max(total_exposure, 1))
                
                # Honeytraps map attacker infrastructure
                intelligence_gain = wasted * 0.3  # 30% of wasted resources become intel
                
            else:
                # Unsophisticated: all resources hit real creds
                real_damage = resource_allocation
                wasted = 0
                intelligence_gain = 0
                
            attacks[i] = {
                'real_damage': real_damage,
                'wasted_attacker_resources': wasted,
                'intelligence_gain': intelligence_gain,
                'net_fragility': real_damage - (intelligence_gain * data['sophistication'])
            }
            data['compromised_history'].append(real_damage)
            
        return attacks
    
    def cerm_omega_calculation(self):
        """Current CERM-Ω model - FLAWED: treats honeytraps as fragility"""
        ces_scores = {}
        for i, data in self.institutions.items():
            # Key flaw: doesn't distinguish honeytrap sophistication
            # Treats ALL exposure as fragility
            total_exposure = data['real_creds'] + data['honeytrap_creds']
            ces_scores[i] = {
                'score': total_exposure * (1 - data['sophistication'] * 0.1),  # small sophistication discount
                'tier': 'HIGH_RISK' if total_exposure > 10 else 'MEDIUM_RISK' if total_exposure > 5 else 'LOW_RISK'
            }
        return ces_scores
    
    def distillation_calculation(self):
        """CDP-Ω: Honeytraps are NEGATIVE fragility (strength signal)"""
        fragility_scores = {}
        for i, data in self.institutions.items():
            # Revolutionary insight: honeytraps reduce TRUE fragility
            # Each honeytrap cred offsets 0.5 real cred due to intel + attacker waste
            effective_exposure = data['real_creds'] - (data['honeytrap_creds'] * data['sophistication'] * 0.5)
            
            # Intelligence accumulation from honeytraps creates antifragility
            antifragility = np.mean(data['compromised_history'][-5:]) * data['sophistication'] * 0.3 if len(data['compromised_history']) > 0 else 0
            
            fragility_scores[i] = {
                'net_fragility': max(0, effective_exposure - antifragility),
                'true_risk': 'ANTI_FRAGILE' if effective_exposure < 0 else 'RESILIENT' if effective_exposure < 2 else 'FRAGILE'
            }
        return fragility_scores

# Execute simulation
np.random.seed(42)
cdp = CredentialDistillationProtocol()
cdp.deploy_strategic_honeytraps()
attacks = cdp.simulate_adversarial_learning()
cerm_scores = cdp.cerm_omega_calculation()
distillation_scores = cdp.distillation_calculation()

# Display catastrophic misclassification
print("INSTITUTION ANALYSIS:")
print("ID | Real | Honey | Soph | CERM-Ω Score | CERM-Ω Risk | CDP-Ω Net Fragility | CDP-Ω True Risk")
print("-" * 95)
for i in sorted(cdp.institutions.keys(), key=lambda x: cdp.institutions[x]['sophistication'], reverse=True)[:8]:
    data = cdp.institutions[i]
    print(f"{i:>2} | {data['real_creds']:>4} | {data['honeytrap_creds']:>5} | {data['sophistication']:>.2f} | "
          f"{cerm_scores[i]['score']:>12.2f} | {cerm_scores[i]['tier']:>10} | "
          f"{distillation_scores[i]['net_fragility']:>19.2f} | {distillation_scores[i]['true_risk']:>13}")

# Calculate systemic misclassification rate
omega_players = [i for i, d in cdp.institutions.items() if d['sophistication'] > 0.7]
false_positives = sum(1 for i in omega_players if cerm_scores[i]['tier'] == 'HIGH_RISK')
print(f"\nCRITICAL FAILURE: {false_positives}/{len(omega_players)} Omega-aware institutions misclassified as HIGH_RISK")
print("CERM-Ω penalizes the strongest players for their defensive sophistication!")

# Visualize the paradigm inversion
fig, axes = plt.subplots(2, 2, figsize=(16, 12))

# Plot 1: CERM-Ω's false fragility signal
ax1 = axes[0, 0]
inst_ids = list(range(cdp.num_institutions))
cerm_vals = [cerm_scores[i]['score'] for i in inst_ids]
soph_levels = [cdp.institutions[i]['sophistication'] for i in inst_ids]
honey_sizes = [cdp.institutions[i]['honeytrap_creds']*10 + 10 for i in inst_ids]

scatter = ax1.scatter(soph_levels, cerm_vals, c=honey_sizes, cmap='Reds', s=50, alpha=0.7)
ax1.set_xlabel('Institutional Sophistication')
ax1.set_ylabel('CERM-Ω "Fragility" Score')
ax1.set_title('FLAWED PARADIGM: CERM-Ω Misreads Strength as Weakness')
ax1.axhline(y=np.percentile(cerm_vals, 90), color='r', linestyle='--', label='High Risk Threshold')
plt.colorbar(scatter, ax=ax1, label='Honeytrap Count')

# Plot 2: CDP-Ω's correct classification
ax2 = axes[0, 1]
distill_vals = [distillation_scores[i]['net_fragility'] for i in inst_ids]
colors = ['green' if cdp.institutions[i]['sophistication'] > 0.7 else 'blue' for i in inst_ids]

ax2.scatter(soph_levels, distill_vals, c=colors, s=50, alpha=0.7)
ax2.set_xlabel('Institutional Sophistication')
ax2.set_ylabel('CDP-Ω Net Fragility Score')
ax2.set_title('DISRUPTIVE INSIGHT: CDP-Ω Recognizes Antifragility')
ax2.axhline(y=0, color='k', linestyle='-', label='Antifragility Threshold')
ax2.legend(['Omega Players (Antifragile)', 'Standard Players'])

# Plot 3: Attack resource waste mapping
ax3 = axes[1, 0]
waste_by_inst = [attacks[i]['wasted_attacker_resources'] for i in inst_ids]
real_creds = [cdp.institutions[i]['real_creds'] for i in inst_ids]

ax3.scatter(real_creds, waste_by_inst, c=colors, s=50, alpha=0.7)
ax3.set_xlabel('Real Credential Count')
ax3.set_ylabel('Wasted Attacker Resources')
ax3.set_title('STRATEGIC ADVANTAGE: Honeytraps Drain Adversary Capacity')
ax3.axvline(x=np.mean(real_creds), color='k', linestyle='--')

# Plot 4: Network effects of misclassification
ax4 = axes[1, 1]
# Create network where edges represent CERM-Ω's false risk propagation
G = nx.Graph()
for i in range(cdp.num_institutions):
    G.add_node(i, risk=cerm_scores[i]['tier'], soph=cdp.institutions[i]['sophistication'])

# Add edges: CERM-Ω would trigger "risk contagion" from false positives
for i in omega_players:  # Omega players
    if cerm_scores[i]['tier'] == 'HIGH_RISK':
        # Connect to 3 random peers, "infecting" them with false risk signal
        peers = np.random.choice([j for j in range(cdp.num_institutions) if j != i], size=3, replace=False)
        for peer in peers:
            G.add_edge(i, peer, weight=cerm_scores[i]['score'])

pos = nx.spring_layout(G)
node_colors = ['red' if G.nodes[i]['risk'] == 'HIGH_RISK' else 'orange' if G.nodes[i]['risk'] == 'MEDIUM_RISK' else 'lightblue' for i in G.nodes()]
nx.draw(G, pos, node_color=node_colors, node_size=50, ax=ax4, with_labels=False)
ax4.set_title('SYSTEMIC RISK: False Positives Trigger Cascading Misallocation')

plt.tight_layout()
plt.show()

print("\n" + "="*70)
print("DISRUPTIVE PARADIGM SHIFT: CREDENTIAL DISTILLATION PROTOCOL (CDP-Ω)")
print("="*70)
print("CORE FLAW IN CERM-Ω: Treats all credential exposure as passive fragility.")
print("REALITY: Sophisticated institutions weaponize exposure as active defense.")
print("\nCDP-Ω PRINCIPLES:")
print("1. HONEYTRAP CREDENTIALS = NEGATIVE FRAGILITY (strength signal)")
print("2. INTELLIGENCE GAIN from attacker mapping > cost of real exposure")
print("3. ATTACKER RESOURCE DEPLETION is a primary optimization target")
print("4. ANTI-FRAGILITY emerges from strategic exposure patterns")
print("\nIMPLICATION: Current proposals would DISMANTLE our strongest institutions")
print("by forcing them to reduce honeytrap density, creating ACTUAL systemic risk.")
print("="*70)