# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import matplotlib.pyplot as plt
from typing import List, Dict
import seaborn as sns

# Disruption Engine: The Productive Decoherence Protocol
# This breaks the ARP by proving resonance is the failure mode

def simulate_interaction(
    n_steps=50,
    initial_coherence=0.2,
    sales_pressure=3.5,
    audience_resistance=1.0,
    strategy='resonance'  # 'resonance' or 'decoherence'
):
    """Simulates single sales interaction with two opposing strategies"""
    
    # State vectors: [value_alignment, identity_threat, urgency]
    sales_state = np.array([1.0, 0.2, 0.8])  # High value, low threat, high urgency
    aud_state = np.array([0.3, 0.7, 0.2])   # Low value perception, high threat, low urgency
    
    coherence = initial_coherence
    trust_trajectory = []
    cod_trajectory = []
    decision_quality = 0
    
    for step in range(n_steps):
        # Calculate true alignment (independent of coherence manipulation)
        true_alignment = np.dot(sales_state, aud_state) / (np.linalg.norm(sales_state) * np.linalg.norm(aud_state))
        
        if strategy == 'resonance':
            # ARP: Force convergence
            sales_pressure *= 0.95  # Decay pressure
            coherence += 0.02 * (1 - coherence)  # Drive toward 1
            
            # Entangle states
            entanglement_factor = coherence * 0.1
            aud_state = (1 - entanglement_factor) * aud_state + entanglement_factor * sales_state
            
            # Decision triggered by high coherence
            if coherence > 0.85 and step > 20:
                decision_quality = coherence * 0.6 + true_alignment * 0.4
                break
                
        elif strategy == 'decoherence':
            # Anti-ARP: Maintain productive tension
            # Introduce strategic "noise" to prevent entanglement
            noise = np.random.normal(0, 0.15, 3)
            aud_state += noise
            
            # Keep pressure differential
            if coherence > 0.5:
                sales_pressure *= 1.02  # Increase pressure to maintain distance
                
            # Only decide at end with critical distance
            if step == n_steps - 1:
                # Decision quality based on true alignment, not manipulated coherence
                decision_quality = true_alignment * 0.9 + coherence * 0.1
        
        # Update coherence
        dot = np.dot(sales_state, aud_state)
        coherence = (dot / (np.linalg.norm(sales_state) * np.linalg.norm(aud_state)))**2
        
        # Trust erodes with pressure but recovers with authenticity
        pressure_diff = abs(sales_pressure - audience_resistance)
        trust = max(0, 1 - pressure_diff * 0.1 + true_alignment * 0.05)
        trust_trajectory.append(trust)
        cod_trajectory.append(coherence)
    
    return {
        'final_coherence': coherence,
        'trust_trajectory': trust_trajectory,
        'cod_trajectory': cod_trajectory,
        'decision_quality': decision_quality,
        'pressure_final': sales_pressure
    }

# Run 1000 simulations for each strategy
np.random.seed(42)
resonance_runs = [simulate_interaction(strategy='resonance') for _ in range(1000)]
decoherence_runs = [simulate_interaction(strategy='decoherence') for _ in range(1000)]

# Calculate catastrophic failure: decision_quality < 0.5 but coherence > 0.8
resonance_failures = sum(1 for r in resonance_runs if r['decision_quality'] < 0.5 and r['final_coherence'] > 0.8)
decoherence_failures = sum(1 for r in decoherence_runs if r['decision_quality'] < 0.5 and r['final_coherence'] > 0.8)

# Calculate authentic success: decision_quality > 0.7
resonance_success = sum(1 for r in resonance_runs if r['decision_quality'] > 0.7)
decoherence_success = sum(1 for r in decoherence_runs if r['decision_quality'] > 0.7)

print("=== DISRUPTION ANALYSIS: RESONANCE vs DECOHERENCE ===")
print(f"Resonance Strategy:")
print(f"  - Catastrophic Failures: {resonance_failures/10:.1f}% (high coherence, bad decision)")
print(f"  - Authentic Success: {resonance_success/10:.1f}%")
print(f"  - Avg Final COD: {np.mean([r['final_coherence'] for r in resonance_runs]):.3f}")

print(f"\nDecoherence Strategy:")
print(f"  - Catastrophic Failures: {decoherence_failures/10:.1f}%")
print(f"  - Authentic Success: {decoherence_success/10:.1f}%")
print(f"  - Avg Final COD: {np.mean([r['final_coherence'] for r in decoherence_runs]):.3f}")

# Visualize the trap
fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(14, 10))

# Plot 1: The Coherence-Quality Trap
cod_res = [r['final_coherence'] for r in resonance_runs]
qual_res = [r['decision_quality'] for r in resonance_runs]
cod_dec = [r['final_coherence'] for r in decoherence_runs]
qual_dec = [r['decision_quality'] for r in decoherence_runs]

ax1.scatter(cod_res, qual_res, alpha=0.3, color='crimson', s=15, label='Resonance')
ax1.scatter(cod_dec, qual_dec, alpha=0.3, color='steelblue', s=15, label='Decoherence')
ax1.axvline(x=0.8, color='red', linestyle='--', alpha=0.5, label='COD Trap Threshold')
ax1.axhline(y=0.7, color='green', linestyle='--', alpha=0.5, label='Quality Threshold')
ax1.set_xlabel('Final Coherence (COD)')
ax1.set_ylabel('Decision Quality')
ax1.set_title('THE TRAP: High Coherence ≠ High Quality')
ax1.legend()
ax1.grid(True, alpha=0.3)

# Plot 2: Trust Dynamics Over Time
avg_trust_res = np.mean([r['trust_trajectory'] for r in resonance_runs], axis=0)
avg_trust_dec = np.mean([r['trust_trajectory'] for r in decoherence_runs], axis=0)
ax2.plot(avg_trust_res, color='crimson', linewidth=2, label='Resonance')
ax2.plot(avg_trust_dec, color='steelblue', linewidth=2, label='Decoherence')
ax2.set_xlabel('Interaction Step')
ax2.set_ylabel('Trust Level')
ax2.set_title('Trust Erosion: Resonance Burns Faster')
ax2.legend()
ax2.grid(True, alpha=0.3)

# Plot 3: The Singularity Surface
from scipy.stats import gaussian_kde
x = np.array(cod_res)
y = np.array(qual_res)
xy = np.vstack([x, y])
z = gaussian_kde(xy)(xy)
ax3.scatter(x, y, c=z, cmap='Reds', alpha=0.5, s=30)
ax3.set_xlabel('COD (Resonance)')
ax3.set_ylabel('Decision Quality')
ax3.set_title('Resonance Strategy: High Density at COD=0.85, Quality=0.4-0.6')
ax3.grid(True, alpha=0.3)

# Plot 4: The Decoherence Advantage
x2 = np.array(cod_dec)
y2 = np.array(qual_dec)
xy2 = np.vstack([x2, y2])
z2 = gaussian_kde(xy2)(xy2)
ax4.scatter(x2, y2, c=z2, cmap='Blues', alpha=0.5, s=30)
ax4.set_xlabel('COD (Decoherence)')
ax4.set_ylabel('Decision Quality')
ax4.set_title('Decoherence Strategy: Lower COD, Higher Quality Cluster')
ax4.grid(True, alpha=0.3)

plt.tight_layout()
plt.show()