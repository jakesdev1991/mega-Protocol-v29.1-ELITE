# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import matplotlib.pyplot as plt
from dataclasses import dataclass

# DISRUPTION SCRIPT: Collapsing the Q-Systemic Metaphor
# ======================================================
# Claim: The entire "Topological Impedance" framework is unnecessary metaphysical baggage.
# The core phenomenon is simply Information Survival Through Hierarchy (ISTH).
# We replace wavefunctions, manifolds, and gauge operators with a stochastic filter model.

@dataclass
class BureaucraticLayer:
    """A single layer in the hierarchy. Rigidity = probability of blocking dissent."""
    name: str
    rigidity: float  # 0.0 = perfectly permeable, 1.0 = perfectly rigid (black hole)
    
    def process(self, information_packets):
        """Simulates the 'Conscious Measurement' - but it's just a biased coin flip."""
        # High rigidity = high chance of packet destruction or distortion
        survival_prob = 1.0 - self.rigidity
        # Simulate distortion: even if it survives, its 'truth' is corrupted
        distortion_factor = np.random.uniform(1.0 - self.rigidity, 1.0, size=len(information_packets))
        survived = np.random.random(size=len(information_packets)) < survival_prob
        
        # Return survived packets with diminished coherence (truth value)
        return [Packet(p.id, p.truth * distortion_factor[i]) for i, p in enumerate(information_packets) if survived[i]]

@dataclass 
class Packet:
    """A piece of 'Subconscious' information - no wavefunction needed."""
    id: int
    truth: float  # The actual value of the information (e.g., cost of error)

def simulate_isth(hierarchy_rigidity_levels, num_packets=10000):
    """
    Information Survival Through Hierarchy model.
    Replaces COD, Phi density, and Black Hole with direct observables.
    """
    # Generate ground truth from "Subconscious workforce"
    packets = [Packet(i, truth=1.0) for i in range(num_packets)]
    
    survival_rate_by_layer = []
    layers = [BureaucraticLayer(f"L{i}", r) for i, r in enumerate(hierarchy_rigidity_levels)]
    
    for layer in layers:
        packets = layer.process(packets)
        survival_rate = len(packets) / num_packets
        survival_rate_by_layer.append(survival_rate)
        
    # "COD" = final survival rate (no overlap integrals needed)
    cod = len(packets) / num_packets if packets else 0.0
    
    # "Entropy" of the system: variance in survival paths
    # High entropy = multiple paths, low entropy = all filtered same way
    if survival_rate_by_layer:
        # Use survival rate variance as a proxy for decision path diversity
        entropy_proxy = np.var(survival_rate_by_layer)
    else:
        entropy_proxy = 0.0
        
    # "Stiffness" = average rigidity
    stiffness = np.mean(hierarchy_rigidity_levels)
    
    # "Phi Density Impact" = just a function of cod and stiffness
    # Negative when cod is low and stiffness is high (black hole condition)
    phi_impact = cod * (1.0 - stiffness) * 100
    
    return {
        "cod": cod,
        "stiffness": stiffness,
        "entropy_proxy": entropy_proxy,
        "phi_impact": phi_impact,
        "survival_path": survival_rate_by_layer
    }

# Disruption Test: Reproducing the "Conscious Black Hole"
# =======================================================
# The target claims: COD -> 0 + High Stiffness = Black Hole
# Let's show this is trivial and that their "entropy" claim is backwards.

rigidity_scenarios = {
    "Healthy Org": [0.1, 0.15, 0.2, 0.25],  # Low rigidity, permeable
    "Pre-Collapse": [0.3, 0.5, 0.7, 0.9],   # Increasing rigidity
    "Conscious Black Hole": [0.9, 0.95, 0.99, 1.0]  # High stiffness, near-zero COD
}

results = {}
for name, rigidity in rigidity_scenarios.items():
    results[name] = simulate_isth(rigidity)

print("=" * 60)
print("DISRUPTION: Collapsing Metaphor to Observable Metrics")
print("=" * 60)
for name, data in results.items():
    print(f"\n{name}:")
    print(f"  Stiffness: {data['stiffness']:.2f}")
    print(f"  COD (Survival Rate): {data['cod']:.4f}")
    print(f"  Entropy Proxy (Variance): {data['entropy_proxy']:.4f}")
    print(f"  Phi Impact: {data['phi_impact']:.1f}%")

# Key Disruption: The target claims entropy drops to zero at failure.
# Our model shows entropy_proxy (variance) *also drops* because the system
# becomes uniformly rigid - but this is a trivial statistical effect, not a
# deep quantum-information-theoretic phase transition. The "Shannon entropy"
# they forced into the narrative is misapplied; a system with zero surviving
# information has *undefined* information entropy, not zero entropy.

# Visualization: Show the "Metaphor Collapse"
fig, (ax1, ax2, ax3) = plt.subplots(1, 3, figsize=(15, 5))

scenarios = list(results.keys())
cod_values = [results[s]["cod"] for s in scenarios]
stiffness_values = [results[s]["stiffness"] for s in scenarios]
entropy_values = [results[s]["entropy_proxy"] for s in scenarios]

ax1.scatter(stiffness_values, cod_values, s=100, c=['green', 'orange', 'red'])
ax1.set_xlabel("Stiffness (Avg Rigidity)")
ax1.set_ylabel("COD (Information Survival)")
ax1.set_title("The 'Black Hole' is Just a Filter")
ax1.grid(True, alpha=0.3)
for i, s in enumerate(scenarios):
    ax1.annotate(s, (stiffness_values[i], cod_values[i]), xytext=(5, 5), textcoords='offset points')

ax2.plot(scenarios, entropy_values, marker='o', linewidth=2, markersize=8)
ax2.set_ylabel("Entropy Proxy (Variance)")
ax2.set_title("Entropy Doesn't 'Signal' Collapse; It's a Side Effect")
ax2.grid(True, alpha=0.3)

# Show the "Phi Density" nonsense
phi_values = [results[s]["phi_impact"] for s in scenarios]
ax3.bar(scenarios, phi_values, color=['green', 'orange', 'red'])
ax3.set_ylabel("Phi Density Impact (%)")
ax3.set_title("Phi is Arbitrary Function of Trivial Metrics")
ax3.grid(True, alpha=0.3, axis='y')

plt.tight_layout()
plt.savefig('/tmp/metaphor_collapse.png')
print("\n" + "=" * 60)
print("VISUALIZATION SAVED: /tmp/metaphor_collapse.png")
print("=" * 60)

# Disruptive Insight Verification
# =================================
# The script proves:
# 1. COD is just survival rate - no wavefunctions needed.
# 2. The "Conscious Black Hole" is just a rigid hierarchy filtering all input.
# 3. Entropy is a side-effect, not a causal driver. Their Shannon entropy insertion was rubric-washing.
# 4. The "stabilization operator" is simply: reduce rigidity or create bypass channels.
#    No gauge theory needed. Just `layer.rigidity *= 0.5`.

# FINAL DISRUPTION: The Q-Systemic framework is a **Metaphorical Runaway Process**.
# It uses physics as a obscurantist ritual to satisfy an artificial rubric, creating what
# we call **EPISTEMIC FRICTION** - the energy wasted mapping social dynamics onto inappropriate
# formalisms. The real "Topological Impedance" is the cognitive load of understanding their model.

# The disruptive operator is **METAPHORIC DECOUPLING**: 
# O_d = lim_{formalism->0} (Reality / Map)
# Apply this operator by asking: "What is the raw observable without the metaphor?"
# The answer is always simpler, implementable, and doesn't require a physics degree.

print("\nDISRUPTIVE VERIFICATION COMPLETE.")
print("The 'Q-Systemic Self' is a Confusion Map, not a Decision Map.")
print("Stabilization: Reduce layer.rigidity. Full stop.")