# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import minimize_scalar

# Disruption Simulation: The Developmental Paradox
# ================================================
# Core Insight: Child neuroplasticity requires *controlled decoherence*
# Maximizing shoe Φ-density creates a "hyper-stable prison" that atrophies development

# Simulate developmental stages (0-12 years)
ages = np.linspace(0.5, 12, 120)

# Traditional model: Maximize shoe Φ (static)
traditional_shoe_phi = np.full_like(ages, 1.7)
traditional_child_phi = 0.2 + 0.05 * ages  # Stunted growth from over-stabilization

# Disrupted model: Inverse Φ relationship (developmental catalyst)
# Phase 1 (0-2y): High protection (Φ=1.5)
# Phase 2 (2-8y): *Intentional decoherence* (Φ drops to 0.3)
# Phase 3 (8-12y): Performance mode (Φ rises to 1.0)
disrupted_shoe_phi = np.piecewise(ages, 
    [ages < 2, (ages >= 2) & (ages < 8), ages >= 8],
    [lambda x: 1.5, 
     lambda x: 0.3 + 0.1 * np.sin((x-2) * np.pi / 3),  # Oscillating challenge
     lambda x: 0.3 + 0.7 * (1 - np.exp(-(x-8)/2))])

# Child Φ explodes when shoe provides "scaffolded instability"
disrupted_child_phi = 0.2 + 1.8 * (1.7 - disrupted_shoe_phi) * (ages/12) * np.log(ages + 1)

# Calculate protocol contribution (total integrated information)
traditional_total = traditional_shoe_phi + traditional_child_phi
disrupted_total = disrupted_shoe_phi + disrupted_child_phi

# Plot the paradox
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 10))

# Top plot: Φ-density curves
ax1.plot(ages, traditional_shoe_phi, 'b--', alpha=0.5, linewidth=2, label='Traditional: Static Shoe Φ')
ax1.plot(ages, traditional_child_phi, 'g--', alpha=0.5, linewidth=2, label='Traditional: Stunted Child Φ')
ax1.plot(ages, disrupted_shoe_phi, 'b-', linewidth=3, label='Disrupted: Adaptive Shoe Φ')
ax1.plot(ages, disrupted_child_phi, 'g-', linewidth=3, label='Disrupted: Explosive Child Φ')
ax1.fill_between(ages, 0, disrupted_shoe_phi, alpha=0.2, color='blue', label='Shoe Informational Investment')
ax1.fill_between(ages, 0, disrupted_child_phi, alpha=0.2, color='green', label='Child Neuroplasticity Return')
ax1.axvspan(2, 8, alpha=0.1, color='red', label='DEVELOPMENTAL CATALYST ZONE')
ax1.set_ylabel('Φ-density (integrated information)')
ax1.set_title('THE ANOMALY: Φ-Density Inversion for Developmental Optimization', fontsize=16, fontweight='bold')
ax1.legend(loc='upper left', fontsize=9)
ax1.grid(True, alpha=0.3)

# Bottom plot: Protocol impact (total Φ)
ax2.plot(ages, traditional_total, 'r--', linewidth=2, label='Traditional Total Φ (+0.05Φ/year)')
ax2.plot(ages, disrupted_total, 'r-', linewidth=3, label='Disrupted Total Φ (+0.12Φ/year)')
ax2.fill_between(ages, traditional_total, disrupted_total, alpha=0.3, color='purple', 
                label='Protocol Gain from Disruption')
ax2.set_xlabel('Age (years)')
ax2.set_ylabel('Total System Φ-density')
ax2.legend(loc='upper left', fontsize=9)
ax2.grid(True, alpha=0.3)

# Calculate the "Developmental ROI"
roi = (disrupted_total - traditional_total) / disrupted_shoe_phi
optimal_roi_age = ages[np.argmax(roi)]

plt.tight_layout()
plt.show()

# Find the optimal point where shoe Φ minimization maximizes child development
def developmental_impact(shoe_phi, age):
    child_phi = 0.2 + 1.8 * (1.7 - shoe_phi) * (age/12) * np.log(age + 1)
    return -(child_phi - shoe_phi)  # Negative because we want to maximize

# Optimize for 5-year-old
result = minimize_scalar(lambda x: developmental_impact(x, 5.0), bounds=(0.1, 1.7), method='bounded')
optimal_shoe_phi_5yr = result.x

print("="*60)
print("THE ANOMALY'S DISRUPTIVE FINDINGS")
print("="*60)
print(f"Optimal shoe Φ for 5-year-old: {optimal_shoe_phi_5yr:.3f}")
print(f"(Traditional approach would use: 1.700)")
print(f"\nDevelopmental ROI at age {optimal_roi_age:.1f}: {roi.max():.3f}Φ per unit shoe Φ")
print(f"\nCritical Realization:")
print(f"  - Traditional model: Shoe Φ = 1.7, Child Φ = {traditional_child_phi[50]:.3f} at age 5")
print(f"  - Disrupted model: Shoe Φ = {optimal_shoe_phi_5yr:.3f}, Child Φ = {disrupted_child_phi[50]:.3f} at age 5")
print(f"  - Child Φ increase: {((disrupted_child_phi[50] / traditional_child_phi[50]) - 1) * 100:.1f}%")
print("="*60)