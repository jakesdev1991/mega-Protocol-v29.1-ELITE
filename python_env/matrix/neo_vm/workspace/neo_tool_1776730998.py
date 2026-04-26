# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import matplotlib.pyplot as plt

def entropic_shredding_analysis(phi_delta_range, critical_phi=3.0):
    """
    Model the entropy-impedance collapse at the Shredding horizon
    Demonstrates how S_h diverges and Z_Δ becomes ill-defined
    """
    results = {
        'phi': [],
        'entropy': [],
        'impedance': [],
        'state': [],
        'feedback_sign': []
    }
    
    for phi in phi_delta_range:
        results['phi'].append(phi)
        
        # Below critical: finite memory states, entropy decreases with storage
        if phi < critical_phi:
            # Model: S_h = S_0 * exp(-φ/λ) + S_min
            S_h = 5.0 * np.exp(-phi/2.0) + 0.2
            Z_delta = 1.0 / (S_h + 0.01)  # Well-defined impedance
            state = "REGULATED"
            feedback = "STABILIZING"
            
        # At critical: capacity diverges, distribution becomes non-normalizable
        else:
            # Entropy diverges exponentially as states become uncountable
            S_h = 5.0 * np.exp((phi - critical_phi)/1.5)
            # Impedance collapses or becomes imaginary (numerical: approach zero)
            Z_delta = np.exp(-(phi - critical_phi)/1.0) * 1e-6
            state = "ENTROPIC_SHREDDING"
            feedback = "CATASTROPHIC"
        
        results['entropy'].append(S_h)
        results['impedance'].append(Z_delta)
        results['state'].append(state)
        results['feedback_sign'].append(feedback)
    
    return results

# Generate analysis across Phi_Δ range
phi_vals = np.linspace(0, 6, 200)
analysis = entropic_shredding_analysis(phi_vals)

# Critical visualization
fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(12, 10))

# Plot 1: Entropy divergence
ax1.plot(analysis['phi'], analysis['entropy'], 'b-', linewidth=2.5)
ax1.axvline(x=3.0, color='r', linestyle='--', alpha=0.8, linewidth=2, label='Entropic Horizon')
ax1.fill_between([0, 3.0], [0, 0], [10, 10], alpha=0.1, color='green', label='Regulated Phase')
ax1.fill_between([3.0, 6.0], [0, 0], [10, 10], alpha=0.1, color='red', label='Entropic Shredding')
ax1.set_ylabel('Shannon Entropy S_h', fontsize=12, fontweight='bold')
ax1.set_title('ENTROPIC SHREDDING: The Feedback Loop Reversal', fontsize=14, fontweight='bold')
ax1.legend(loc='upper right')
ax1.grid(True, alpha=0.3)
ax1.set_yscale('log')

# Plot 2: Impedance collapse
ax2.plot(analysis['phi'], analysis['impedance'], 'r-', linewidth=2.5)
ax2.axvline(x=3.0, color='r', linestyle='--', alpha=0.8, linewidth=2)
ax2.set_ylabel('Topological Impedance Z_Δ', fontsize=12, fontweight='bold')
ax2.set_yscale('log')
ax2.grid(True, alpha=0.3)

# Plot 3: State diagram
states_numeric = [1 if s == "REGULATED" else 0 for s in analysis['state']]
ax3.plot(analysis['phi'], states_numeric, 'g-', linewidth=3)
ax3.axvline(x=3.0, color='r', linestyle='--', alpha=0.8, linewidth=2)
ax3.fill_between([0, 3.0], [-0.1, -0.1], [1.1, 1.1], alpha=0.1, color='green')
ax3.fill_between([3.0, 6.0], [-0.1, -0.1], [1.1, 1.1], alpha=0.1, color='red')
ax3.set_ylabel('System State', fontsize=12, fontweight='bold')
ax3.set_xlabel('Φ_Δ (Archive Mode Amplitude)', fontsize=12, fontweight='bold')
ax3.set_yticks([0, 1])
ax3.set_yticklabels(['SHREDDING', 'REGULATED'])
ax3.grid(True, alpha=0.3)

plt.tight_layout()
plt.show()

# Critical values demonstration
print("="*60)
print("ENTROPIC SHREDDING TRANSITION")
print("="*60)
for phi_test in [1.0, 2.5, 3.0, 3.5, 5.0]:
    idx = np.argmin(np.abs(np.array(analysis['phi']) - phi_test))
    print(f"Φ_Δ = {phi_test:.1f} → S_h = {analysis['entropy'][idx]:.3e}, Z_Δ = {analysis['impedance'][idx]:.3e}, State: {analysis['state'][idx]}")