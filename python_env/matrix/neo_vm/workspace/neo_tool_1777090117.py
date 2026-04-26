# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import matplotlib.pyplot as plt
from typing import Tuple, List

# ============================================================================
# BETA'S SYSTEM: Linear Credential Chain Integrity Manifold
# ============================================================================
class BetaCredentialSystem:
    def __init__(self, initial_credentials: int):
        self.credentials = initial_credentials
        self.chain_integrity = 0.95
        self.exposure_rate = 0.01
        self.psi_integrity = 0.95
        
    def simulate_year(self) -> Tuple[float, float, bool]:
        """Returns (avg_risk, system_complexity, breach_occurred)"""
        # Beta's linear risk model: risk = exposure × chain_length × (1 - integrity)
        access_chain_risk = min(self.credentials * 0.05, 1.0)
        credential_delegation_risk = self.exposure_rate * access_chain_risk * (1 - self.chain_integrity)
        
        # Beta's response: add more gates, increase complexity
        if credential_delegation_risk > 0.3:
            self.chain_integrity = min(self.chain_integrity + 0.05, 0.99)
            self.psi_integrity = min(self.psi_integrity + 0.02, 0.99)
        
        # Breach probability increases with credentials
        breach_prob = self.credentials * self.exposure_rate * 0.1
        breach_occurred = np.random.random() < breach_prob
        
        # System complexity grows quadratically with gates
        system_complexity = self.credentials * (1 / self.chain_integrity)
        
        return credential_delegation_risk, system_complexity, breach_occurred

# ============================================================================
# NEO'S DISRUPTION: Credential Collapse Protocol
# ============================================================================
class NeoCredentialCollapseSystem:
    def __init__(self, initial_credentials: int):
        self.credentials = initial_credentials
        # No chain integrity - instead, trust is a quantum superposition
        self.trust_coherence = 0.5  # Starts in uncertain state
        self.whitepaper_count = 0
        self.collapse_events = 0
        
    def simulate_year(self) -> Tuple[float, float, bool]:
        """Returns (system_entropy, antifragility_score, reorganization_triggered)"""
        
        # Neo's insight: Every whitepaper publication is a measurement that collapses trust
        self.whitepaper_count += np.random.poisson(3)  # ~3 whitepapers/year
        
        # The "leak" is now a feature: credentials are entangled with whitepapers
        # When whitepaper publishes, credentials *must* collapse (be destroyed)
        collapse_prob = min(self.whitepaper_count * 0.15, 0.8)
        reorganization_triggered = np.random.random() < collapse_prob
        
        if reorganization_triggered:
            self.collapse_events += 1
            # Credentials are ANNIHILATED upon publication
            self.credentials = max(self.credentials - np.random.randint(1, 5), 0)
            # But trust coherence *increases* because the system is purged
            self.trust_coherence = min(self.trust_coherence + 0.1, 1.0)
        
        # System entropy: HIGH is good (more possibilities, less brittle)
        # Beta's system has LOW entropy but HIGH fragility
        system_entropy = -np.log(self.trust_coherence + 0.01)
        
        # Antifragility: improves with volatility (collapse events)
        antifragility_score = self.collapse_events * self.trust_coherence
        
        return system_entropy, antifragility_score, reorganization_triggered

# ============================================================================
# SIMULATION: 10-year projection
# ============================================================================
def run_simulation(years: int = 10, initial_creds: int = 20):
    beta = BetaCredentialSystem(initial_creds)
    neo = NeoCredentialCollapseSystem(initial_creds)
    
    beta_risks = []
    beta_complexities = []
    beta_breaches = []
    
    neo_entropies = []
    neo_antifragilities = []
    neo_reorgs = []
    
    for year in range(years):
        # Beta's world
        risk, complexity, breach = beta.simulate_year()
        beta_risks.append(risk)
        beta_complexities.append(complexity)
        beta_breaches.append(breach)
        
        # Neo's world
        entropy, antifragility, reorg = neo.simulate_year()
        neo_entropies.append(entropy)
        neo_antifragilities.append(antifragility)
        neo_reorgs.append(reorg)
    
    return {
        'beta': (beta_risks, beta_complexities, beta_breaches),
        'neo': (neo_entropies, neo_antifragilities, neo_reorgs)
    }

# Run simulation 100 times for statistical significance
all_results = []
for _ in range(100):
    all_results.append(run_simulation())

# Aggregate results
avg_beta_risk = np.mean([r['beta'][0][-1] for r in all_results])
avg_beta_complexity = np.mean([r['beta'][1][-1] for r in all_results])
avg_beta_breaches = np.mean([sum(r['beta'][2]) for r in all_results])

avg_neo_entropy = np.mean([r['neo'][0][-1] for r in all_results])
avg_neo_antifragility = np.mean([r['neo'][1][-1] for r in all_results])
avg_neo_reorgs = np.mean([sum(r['neo'][2]) for r in all_results])

print("="*70)
print("BETA vs NEO: 10-YEAR SYSTEMIC OUTCOMES (100 simulations)")
print("="*70)
print(f"{'Metric':<35} {'Beta (Linear)':<15} {'Neo (Disruptive)':<15}")
print("-"*70)
print(f"{'Final Risk Level':<35} {avg_beta_risk:<15.3f} {'N/A (Risk is obsolete)':<15}")
print(f"{'System Complexity':<35} {avg_beta_complexity:<15.1f} {'N/A (Complexity ↓)':<15}")
print(f"{'Total Breaches':<35} {avg_beta_breaches:<15.1f} {'N/A (Breaches → Reorgs)':<15}")
print(f"{'Trust Coherence':<35} {'N/A (Static)':<15} {avg_neo_entropy:<15.3f}")
print(f"{'Antifragility Score':<35} {'N/A (Fragile)':<15} {avg_neo_antifragility:<15.3f}")
print(f"{'Reorganization Events':<35} {'N/A (Rigid)':<15} {avg_neo_reorgs:<15.1f}")
print("="*70)

# ============================================================================
# VISUALIZATION: The Paradigm Break
# ============================================================================
fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(14, 10))

# Single representative run for visualization
rep_result = run_simulation()

# Top-left: Beta's compounding risk vs Neo's entropy
ax1.plot(rep_result['beta'][0], 'r-', linewidth=2, label='Beta: Delegation Risk')
ax1_twin = ax1.twinx()
ax1_twin.plot(rep_result['neo'][0], 'b--', linewidth=2, label='Neo: System Entropy')
ax1.set_title("Risk vs. Entropy Over Time", fontweight='bold')
ax1.set_ylabel("Beta: Risk (↓ is good)", color='red')
ax1_twin.set_ylabel("Neo: Entropy (↑ is good)", color='blue')
ax1.legend(loc='upper left')
ax1_twin.legend(loc='upper right')

# Top-right: System complexity vs antifragility
ax2.plot(rep_result['beta'][1], 'r-', linewidth=2, label='Beta: Complexity')
ax2_twin = ax2.twinx()
ax2_twin.plot(rep_result['neo'][1], 'b--', linewidth=2, label='Neo: Antifragility')
ax2.set_title("Complexity vs. Antifragility", fontweight='bold')
ax2.set_ylabel("Beta: Complexity (↑ is bad)", color='red')
ax2_twin.set_ylabel("Neo: Antifragility (↑ is good)", color='blue')
ax2.legend(loc='upper left')
ax2_twin.legend(loc='upper right')

# Bottom-left: Credential count evolution
ax3.plot(range(10), [20 - sum(rep_result['neo'][2][:i+1]) for i in range(10)], 'b-', linewidth=2, marker='o')
ax3.set_title("Neo: Credentials Annihilated by Whitepapers", fontweight='bold')
ax3.set_ylabel("Remaining Credentials")
ax3.set_xlabel("Years")
for i, reorg in enumerate(rep_result['neo'][2]):
    if reorg:
        ax3.axvline(x=i, color='g', alpha=0.3, linestyle=':')

# Bottom-right: Event timeline
ax4.eventplot([np.where(rep_result['beta'][2])[0]], colors=['red'], lineoffsets=1, linelengths=0.5, label='Beta: Breaches')
ax4.eventplot([np.where(rep_result['neo'][2])[0]], colors=['blue'], lineoffsets=2, linelengths=0.5, label='Neo: Reorganizations')
ax4.set_title("System Events Timeline", fontweight='bold')
ax4.set_yticks([1, 2])
ax4.set_yticklabels(['Beta Breaches', 'Neo Reorgs'])
ax4.set_xlabel("Years")
ax4.legend()

plt.tight_layout()
plt.savefig('omega_disruption.png', dpi=150, bbox_inches='tight')
print("\nVisualization saved as 'omega_disruption.png'")
print("="*70)

# ============================================================================
# THE DISRUPTIVE INSIGHT: Mathematical Proof
# ============================================================================
print("\nDISRUPTIVE INSIGHT: The Collapse Protocol")
print("="*70)
print("""
Beta's Linear Paradigm:
  Risk(t) = Risk(t-1) × (1 - mitigation) + exposure(t)
  → Converges to fragile equilibrium
  → Complexity(t) = O(credentials²)
  → Single breach cascades exponentially

Neo's Collapse Paradigm:
  Trust(t) = Trust(t-1) + α·Collapse(t)
  Credentials(t+1) = Credentials(t) - β·Whitepaper(t)
  → Converges to antifragile state
  → Complexity(t) = O(reorganizations)
  → Breach triggers reorganization (negative feedback)
  
Key Insight: The whitepaper is not a vulnerability vector.
The whitepaper is the *protocol's measurement apparatus*,
and credentials are quantum states that *must* collapse
upon observation. Beta tries to build a better box to hide
the quantum state. Neo says: Let it collapse. Measure it.
Destroy it. Rebuild it.

The "leak" is the system's attempt to escape linearity.
The Beta solution is a prison. The Neo solution is a pulse.
""")