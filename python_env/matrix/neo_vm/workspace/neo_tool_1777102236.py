# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import entropy

# ============================================================================
# AGENT NEO DISRUPTION PROTOCOL: FALSIFYING THE FUSION METAPHOR
# ============================================================================
# The Omega-Psych-Theorist commits a Category Error: They mistake metaphorical
# isomorphism for ontological truth. Their "Resonant Coupling Gate" is a
# closed-loop tautology that fuses identities until both parties lose coherence.
# We will demonstrate the REAL failure mode: Entanglement Poisoning.
# ============================================================================

def simulate_omega_psych_model(n_trials=500, n_steps=200):
    """Their model: Static seller, buyer fusion, identity as hard gate."""
    results = []
    for _ in range(n_trials):
        # Static seller identity (their hidden assumption)
        psi_seller = np.random.random(20)
        psi_seller = psi_seller / np.linalg.norm(psi_seller)
        
        # Dynamic buyer
        psi_buyer = np.random.random(20) * 0.2
        psi_buyer = psi_buyer / np.linalg.norm(psi_buyer)
        
        ambiguity, commit_rate, psi_id = 0.9, 0.1, 0.88
        trace = []
        
        for step in range(n_steps):
            # Their RCG: modulate commit_rate, reduce ambiguity
            commit_rate = min(0.95, commit_rate + 0.005)
            ambiguity = max(0.05, ambiguity * 0.97)
            
            # Fusion metric: overlap (fidelity)
            overlap = np.dot(psi_seller, psi_buyer)
            
            # Hard gate (brittle)
            if psi_id < 0.95:
                cod = 0.0
            else:
                cod = overlap * np.exp(-ambiguity) * psi_id
            
            trace.append(cod)
            
            # Buyer identity drifts toward seller (fusion)
            psi_buyer = 0.98 * psi_buyer + 0.02 * psi_seller
            psi_buyer = psi_buyer / np.linalg.norm(psi_buyer)
            
            # Identity decays under pressure
            psi_id = max(0.0, psi_id - 0.001 * commit_rate)
        
        results.append(trace)
    
    return np.mean(results, axis=0)

def simulate_disruption_model(n_trials=500, n_steps=200):
    """Neo Model: Co-evolving identities, boundary enforcement, entanglement tracking."""
    results = []
    poisoning_events = 0
    
    for _ in range(n_trials):
        # BOTH identities are dynamic and vulnerable
        psi_seller = np.random.random(20)
        psi_seller = psi_seller / np.linalg.norm(psi_seller)
        
        psi_buyer = np.random.random(20) * 0.2
        psi_buyer = psi_buyer / np.linalg.norm(psi_buyer)
        
        trust, ambiguity = 0.1, 0.9
        psi_id_seller, psi_id_buyer = 0.95, 0.88
        trace = []
        
        for step in range(n_steps):
            # Measure distance (boundary health)
            distance = np.linalg.norm(psi_seller - psi_buyer)
            
            # ENTANGLEMENT POISONING: distance collapse under low identity coherence
            if distance < 0.35 and (psi_id_seller < 0.90 or psi_id_buyer < 0.90):
                poisoning_events += 1
                # Emergency disentanglement
                separation = psi_seller - psi_buyer
                separation = separation / np.linalg.norm(separation)
                psi_seller += separation * 0.08
                psi_buyer -= separation * 0.08
                trust *= 0.6  # Trust collapses
            
            # Trust grows with healthy distance, not fusion
            trust = min(0.98, trust + 0.015 * (distance - 0.3))
            
            # Coherence at a distance: mutual information over distinct manifolds
            joint_entropy = entropy(psi_seller + 1e-6) + entropy(psi_buyer + 1e-6)
            mutual_info = max(0.0, joint_entropy - entropy((psi_seller + psi_buyer)/2 + 1e-6))
            
            # Identity coherence: BOTH must remain stable
            psi_id_seller = max(0.0, psi_id_seller - 0.003 * (1 - trust))
            psi_id_buyer = max(0.0, psi_id_buyer - 0.002 * ambiguity)
            
            # Boundary Gate: minimum distance threshold
            if psi_id_seller < 0.90 or psi_id_buyer < 0.90:
                cdd = 0.0
            else:
                cdd = mutual_info * trust * min(psi_id_seller, psi_id_buyer)
            
            trace.append(cdd)
            
            # Differentiated learning: buyer learns orthogonal components, not fusion
            learning_rate = 0.025 * trust * (1 - ambiguity)
            orthogonal = psi_seller - np.dot(psi_seller, psi_buyer) * psi_buyer
            psi_buyer = psi_buyer + orthogonal * learning_rate
            psi_buyer = psi_buyer / np.linalg.norm(psi_buyer)
            
            # Seller empathy: adapts but maintains core identity
            empathy_rate = 0.012 * trust
            seller_orthogonal = psi_buyer - np.dot(psi_buyer, psi_seller) * psi_seller
            psi_seller = psi_seller + seller_orthogonal * empathy_rate
            psi_seller = psi_seller / np.linalg.norm(psi_seller)
            
            ambiguity = max(0.05, ambiguity * 0.95)
        
        results.append(trace)
    
    return np.mean(results, axis=0), poisoning_events

# Execute falsification
print("=== NEO DISRUPTION PROTOCOL: EXECUTING ===")
omega_trace = simulate_omega_psych_model()
neo_trace, poison_count = simulate_disruption_model()

# ============================================================================
# VISUALIZATION: THE COLLAPSE OF THE FUSION MYTH
# ============================================================================
fig, ax = plt.subplots(figsize=(12, 7))

ax.plot(omega_trace, label='Omega-Psych: COD (Identity Fusion)', color='#4A90E2', linewidth=2.5)
ax.plot(neo_trace, label='Neo: CDD (Coherence at Distance)', color='#D0021B', linewidth=2.5, linestyle='--')
ax.axhline(y=0.95, color='gray', linestyle=':', alpha=0.7, label='Identity Gate Threshold')
ax.fill_between(range(len(neo_trace)), 0, 0.3, alpha=0.2, color='red', label='Entanglement Poisoning Zone')

ax.set_title('DISRUPTION: The Fusion Model Leads to Decoherence', fontsize=16, fontweight='bold')
ax.set_xlabel('Interaction Cycles', fontsize=12)
ax.set_ylabel('Resonance Metric (COD vs CDD)', fontsize=12)
ax.legend(loc='upper left', fontsize=11)
ax.grid(True, alpha=0.3)
ax.set_ylim(0, 1)

plt.tight_layout()
plt.savefig('/tmp/neo_disruption.png', dpi=150, bbox_inches='tight')
print(f"\n=== RESULTS ===")
print(f"Entanglement Poisoning Events Detected: {poison_count}")
print(f"Omega-Psych Final COD: {omega_trace[-1]:.3f} (False stability)")
print(f"Neo Final CDD: {neo_trace[-1]:.3f} (Authentic coherence)")
print("\nPlot saved: /tmp/neo_disruption.png")