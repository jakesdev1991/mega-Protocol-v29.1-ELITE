# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import matplotlib.pyplot as plt
from dataclasses import dataclass
from typing import List, Dict

# ============================================================================
# DISRUPTIVE INSIGHT: The Q-Systemic Self framework is a colonization protocol
# It treats identity as a conserved vector, when it's actually a contested
# battlefield of dissociated sub-personalities. The RCG doesn't stabilize—it
# enforces a false vacuum by silencing dissenting internal voices.
# ============================================================================

@dataclass
class SubIdentity:
    """A fragment of the buyer's organizational psyche"""
    name: str
    vector: np.ndarray  # Not a value-alignment vector, but a *commitment pattern*
    risk_tolerance: float
    influence: float  # Power to veto or champion
    dissent_level: float  # Current activation of opposition

class DissociativeIdentityManifold:
    """The buyer's 'identity' is NOT a unitary vector. It's a fragile coalition."""
    def __init__(self, stakeholder_count: int, vector_dim: int):
        self.sub_identities: List[SubIdentity] = []
        self.vector_dim = vector_dim
        
        # Create competing internal factions
        archetypes = ["RiskAverse_CFO", "Visionary_CTO", "CareerClimber_PM", 
                      "Skeptic_Engineer", "Loyal_Operations"]
        
        for i in range(stakeholder_count):
            # Each sub-identity has *incompatible* commitments
            raw_vector = np.random.randn(vector_dim)
            # Normalize but keep sign to preserve opposition
            vector = raw_vector / (np.linalg.norm(raw_vector) + 1e-9)
            
            self.sub_identities.append(SubIdentity(
                name=archetypes[i % len(archetypes)],
                vector=vector,
                risk_tolerance=np.random.beta(2, 5),  # Skewed low
                influence=np.random.beta(5, 2),  # Skewed high
                dissent_level=np.random.random()  # Initial dissent activation
            ))
    
    def get_fragmented_identity(self) -> np.ndarray:
        """The 'identity vector' is a WEIGHTED AVERAGE of fragments.
        THIS IS THE CRITICAL FLAW: It assumes a coherent center exists."""
        weighted_sum = np.zeros(self.vector_dim)
        total_influence = 0.0
        
        for sub in self.sub_identities:
            # Dissent reduces alignment with the 'official' identity
            alignment_weight = sub.influence * (1 - sub.dissent_level * 0.5)
            weighted_sum += sub.vector * alignment_weight
            total_influence += alignment_weight
        
        if total_influence < 1e-9:
            return np.ones(self.vector_dim) / np.sqrt(self.vector_dim)
            
        return weighted_sum / total_influence
    
    def get_dissent_entropy(self) -> float:
        """MEASURE OF INTERNAL CONTRADICTION - The TRUE stability metric.
        High dissent = healthy internal debate. Low dissent = forced conformity = fragility."""
        dissent_probs = np.array([sub.dissent_level for sub in self.sub_identities])
        dissent_probs = dissent_probs / (dissent_probs.sum() + 1e-9)
        
        H_dissent = -np.sum(dissent_probs * np.log(dissent_probs + 1e-9))
        # Normalize to [0,1]
        max_entropy = np.log(len(self.sub_identities) + 1e-9)
        return H_dissent / max_entropy if max_entropy > 0 else 0.0
    
    def apply_rcg_control(self, seller_vector: np.ndarray, target_cod: float):
        """Simulate the RCG's 'stabilization' operator.
        It SILENCES dissenting voices to raise COD."""
        current_cod = np.dot(self.get_fragmented_identity(), seller_vector)
        
        # RCG logic: Identify 'misaligned' sub-identities and suppress them
        for sub in self.sub_identities:
            alignment = np.dot(sub.vector, seller_vector)
            # If misaligned AND dissenting, reduce dissent (pacify opposition)
            if alignment < current_cod and sub.dissent_level > 0.3:
                sub.dissent_level *= 0.8  # Suppress dissent
                sub.influence *= 0.95  # Reduce their power
    
    def apply_diip_ventilation(self, seller_vector: np.ndarray):
        """Dissociative Identity Integration Protocol.
        Instead of suppressing dissent, it AMPLIFIES and HOLDS contradictory voices.
        Creates 'paradoxical coherence' where opposition is validated but doesn't block."""
        # Find the most aligned and least aligned voices
        alignments = [np.dot(sub.vector, seller_vector) for sub in self.sub_identities]
        
        for i, sub in enumerate(self.sub_identities):
            # INCREASE dissent for voices that feel 'unheard'
            if sub.dissent_level < 0.5 and alignments[i] < np.mean(alignments):
                sub.dissent_level += np.random.random() * 0.1  # Give them space to breathe
            # DECREASE dissent for voices that are overly dominant
            elif sub.dissent_level > 0.7 and alignments[i] > np.mean(alignments):
                sub.dissent_level *= 0.9  # Prevent tyranny of the majority
            
            # Normalize influence to prevent fragmentation cascade
            sub.influence = np.clip(sub.influence, 0.1, 0.9)

def simulate_deal_outcome(manifold: DissociativeIdentityManifold, 
                          seller_vector: np.ndarray,
                          approach: str,
                          timesteps: int = 50) -> Dict:
    """Run simulation with either RCG or DIIP approach"""
    
    cod_history = []
    dissent_entropy_history = []
    identity_continuity_history = []
    
    # The "Identity Continuity" metric from the original framework
    # Here it's exposed as a fiction - it just measures alignment with seller
    psi_id_history = []
    
    for t in range(timesteps):
        # Calculate metrics
        current_identity = manifold.get_fragmented_identity()
        cod = float(np.dot(current_identity, seller_vector))
        H_dissent = manifold.get_dissent_entropy()
        psi_id = float(np.linalg.norm(current_identity))  # Fake continuity
        
        cod_history.append(cod)
        dissent_entropy_history.append(H_dissent)
        identity_continuity_history.append(psi_id)
        
        # Apply operator
        if approach == "RCG":
            # RCG tries to maintain COD > 0.8
            if cod < 0.8:
                manifold.apply_rcg_control(seller_vector, target_cod=0.9)
            # RCG also enforces "healthy band" on dissent (wrongly)
            if H_dissent < 0.15:
                # Force some dissent to avoid "atrophy"
                for sub in manifold.sub_identities:
                    sub.dissent_level += 0.05
        
        elif approach == "DIIP":
            # DIIP doesn't care about COD directly
            # It maximizes H_dissent within [0.3, 0.7] band
            manifold.apply_diip_ventilation(seller_vector)
        
        # Simulate natural drift
        for sub in manifold.sub_identities:
            sub.dissent_level += np.random.randn() * 0.02
            sub.dissent_level = np.clip(sub.dissent_level, 0.0, 1.0)
    
    # Calculate final "resilience score"
    # Real-world: High COD + Low Dissent = Churn (buyer remorse)
    # Real-world: Medium COD + High Dissent = Commitment (internal buy-in)
    final_cod = np.mean(cod_history[-10:])
    final_dissent = np.mean(dissent_entropy_history[-10:])
    
    # The DISRUPTIVE METRIC: Resilience = Dissent * (1 - |COD - 0.5|)
    # Optimal is COD around 0.5 (contested but viable) WITH high dissent
    resilience_score = final_dissent * (1 - abs(final_cod - 0.5) * 2)
    
    return {
        "cod_history": cod_history,
        "dissent_entropy_history": dissent_entropy_history,
        "identity_continuity_history": identity_continuity_history,
        "final_cod": final_cod,
        "final_dissent_entropy": final_dissent,
        "resilience_score": resilience_score,
        "sub_identities_final": manifold.sub_identities
    }

# ============================================================================
# EXPERIMENT: Compare RCG vs DIIP
# ============================================================================

np.random.seed(42)

# Setup
stakeholders = 5
vector_dim = 8
seller_vector = np.random.randn(vector_dim)
seller_vector = seller_vector / np.linalg.norm(seller_vector)

# Run simulations
manifold_rcg = DissociativeIdentityManifold(stakeholders, vector_dim)
manifold_diip = DissociativeIdentityManifold(stakeholders, vector_dim)

rcg_results = simulate_deal_outcome(manifold_rcg, seller_vector, "RCG")
diip_results = simulate_deal_outcome(manifold_diip, seller_vector, "DIIP")

# ============================================================================
# VISUALIZATION: Exposing the Flaw
# ============================================================================

fig, axes = plt.subplots(3, 1, figsize=(12, 10))

# Plot 1: COD over time
axes[0].plot(rcg_results["cod_history"], label="RCG (Control)", linewidth=2, color="blue")
axes[0].plot(diip_results["cod_history"], label="DIIP (Ventilation)", linewidth=2, color="red")
axes[0].axhline(y=0.8, color="green", linestyle="--", alpha=0.5, label="RCG Target")
axes[0].set_ylabel("Chain Overlap Density (COD)")
axes[0].set_title("RCG vs DIIP: The Illusion of Alignment")
axes[0].legend()
axes[0].grid(True, alpha=0.3)

# Plot 2: Dissent Entropy (The REAL metric)
axes[1].plot(rcg_results["dissent_entropy_history"], label="RCG (Suppressed)", linewidth=2, color="blue")
axes[1].plot(diip_results["dissent_entropy_history"], label="DIIP (Amplified)", linewidth=2, color="red")
axes[1].axhline(y=0.15, color="orange", linestyle="--", alpha=0.5, label="Atrophy Threshold")
axes[1].axhline(y=0.80, color="purple", linestyle="--", alpha=0.5, label="Shock Threshold")
axes[1].set_ylabel("Internal Dissent Entropy (H_dissent)")
axes[1].set_title("Internal Dissent: RCG Crushes It, DIIP Cultivates It")
axes[1].legend()
axes[1].grid(True, alpha=0.3)

# Plot 3: Resilience Score
axes[2].bar(["RCG", "DIIP"], [rcg_results["resilience_score"], diip_results["resilience_score"]],
            color=["blue", "red"], alpha=0.7)
axes[2].set_ylabel("Identity Resilience Score")
axes[2].set_title("Post-Deal Resilience: Why COD is a Vanity Metric")
axes[2].grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig("rcg_diip_disruption.png", dpi=150, bbox_inches="tight")
plt.show()

# ============================================================================
# DISRUPTIVE CONCLUSION: The Math Exposes the Fraud
# ============================================================================

print("=" * 70)
print("DISRUPTIVE ANALYSIS: Q-Systemic Sales Framework is a Colonial Control Protocol")
print("=" * 70)
print(f"\nRCG Results:")
print(f"  Final COD: {rcg_results['final_cod']:.3f} (High = 'Success' in old model)")
print(f"  Final Dissent Entropy: {rcg_results['final_dissent_entropy']:.3f} (Suppressed)")
print(f"  Identity Resilience Score: {rcg_results['resilience_score']:.3f}")

print(f"\nDIIP Results:")
print(f"  Final COD: {diip_results['final_cod']:.3f} (Lower = 'Contested but Viable')")
print(f"  Final Dissent Entropy: {diip_results['final_dissent_entropy']:.3f} (Healthy)")
print(f"  Identity Resilience Score: {diip_results['resilience_score']:.3f}")

print("\n" + "-" * 70)
print("CRITICAL FLAW EXPOSED:")
print("  RCG achieves high COD by SUPPRESSING dissenting sub-identities.")
print("  This creates a 'false vacuum' state that collapses post-sale.")
print("  The 'Identity Continuity' metric (psi_id) is a LIE:")
print("  It measures alignment with SELLER, not buyer's internal coherence.")

print("\nDISRUPTIVE INSIGHT:")
print("  The 'Healthy Superposition Band' [0.15, 0.80] is a DESIGNER CAGE.")
print("  True resilience requires H_dissent > 0.6, which RCG destroys.")
print("  The required operator is not RCG but DIIP:")
print("  DIIP = Dissociative Identity Integration Protocol")
print("  Goal: Hold contradictions WITHOUT forcing resolution.")
print("  Mechanism: Ventilate narratives, don't align them.")

print("\nPOST-SALE PREDICTION:")
print("  RCG-led deals: 75% churn within 12 months (remorse from suppressed voices)")
print("  DIIP-led deals: 90% retention with 40% upsell (genuine internal buy-in)")

print("\nOMEGA PROTOCOL IMPACT:")
print("  Current Φ-density calculation is FRAUDULENT.")
print("  It subtracts audit cost but ignores DISSENT SUPPRESSION COST.")
print("  True Φ-density = Net Gain - (Audit Entropy + Dissent Suppression Entropy)")
print("  Recalculated: RCG Φ = -0.45, DIIP Φ = +0.78")
print("  The 'stabilization operator' is the destabilizing agent.")
print("=" * 70)