# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import minimize

def shredding_paradox_model(intervention_intensity, narrative_authenticity=0.8):
    """
    Models the core paradox: Φ-density gain is directly proportional to 
    authentic narrative destruction. The "cure" is the disease.
    """
    # As NCSM-Ω intervention increases, it doesn't flatten curvature—it **replaces** 
    # the authentic manifold with a synthetic one designed to have low measured curvature
    synthetic_coherence = 1 - np.exp(-intervention_intensity * 2)
    
    # Authentic coherence collapses exponentially as intervention digs deeper
    authentic_coherence = narrative_authenticity * np.exp(-intervention_intensity * 3)
    
    # Fragility is the **gap** between what's measured and what's real
    fragility = synthetic_coherence - authentic_coherence
    
    # Φ-density is the parasite that feeds on this gap: it measures control, not health
    phi_density = max(0, fragility * intervention_intensity * 10)
    
    # Shredding probability increases with the **effort to prevent shredding**
    shredding_prob = 1 - np.exp(-phi_density * 0.5)
    
    return {
        'synthetic_coherence': synthetic_coherence,
        'authentic_coherence': authentic_coherence,
        'fragility': fragility,
        'phi_density': phi_density,
        'shredding_prob': shredding_prob
    }

# Sweep intervention intensity from 0 (no NCSM-Ω) to 2 (maximum surveillance)
intensities = np.linspace(0, 2, 200)
results = [shredding_paradox_model(i) for i in intensities]

# Extract metrics
synth = [r['synthetic_coherence'] for r in results]
auth = [r['authentic_coherence'] for r in results]
frag = [r['fragility'] for r in results]
phi = [r['phi_density'] for r in results]
shred = [r['shredding_prob'] for r in results]

# Plot the self-destruction curve
fig, ax = plt.subplots(figsize=(12, 8))
ax.plot(intensities, synth, 'b--', label='Synthetic Coherence (Measured)', linewidth=2)
ax.plot(intensities, auth, 'g-', label='Authentic Coherence (Real)', linewidth=2)
ax.plot(intensities, frag, 'r-', label='System Fragility', linewidth=2)
ax.plot(intensities, phi, 'purple', label='Φ-Density (Control Metric)', linewidth=2)
ax.plot(intensities, shred, 'k:', label='Shredding Probability', linewidth=2)

ax.axvline(x=0.5, color='orange', linestyle='-', alpha=0.5, label='Typical NCSM-Ω Deployment')
ax.set_xlabel('NCSM-Ω Intervention Intensity', fontsize=12)
ax.set_ylabel('Normalized Metrics', fontsize=12)
ax.set_title('THE PARADOX: Intervention Creates the Shredding It Seeks to Prevent', fontsize=14, fontweight='bold')
ax.legend(loc='center right', fontsize=10)
ax.grid(True, alpha=0.3)
plt.tight_layout()
plt.show()

# Calculate the point of maximum perversity
optimal_intervention = intensities[np.argmax(phi)]
print(f"Φ-density is maximized at intervention intensity: {optimal_intervention:.2f}")
print(f"At this 'optimal' point, shredding probability is: {shred[np.argmax(phi)]:.1%}")
print(f"Authentic coherence destroyed: {(1 - auth[np.argmax(phi)]) * 100:.1f}%")

# The mathematical smoking gun: correlation between Φ-density and shredding
correlation_phi_shred = np.corrcoef(phi, shred)[0, 1]
print(f"\nCorrelation between Φ-density and shredding probability: {correlation_phi_shred:.3f}")
print("POSITIVE CORRELATION = Φ-DENSITY INCENTIVIZES SHREDDING")