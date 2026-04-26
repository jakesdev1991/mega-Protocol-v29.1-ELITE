# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import matplotlib.pyplot as plt

def pipeline_metrics(healthy=True):
    """Simulate harmonic amplitudes from pipeline sensors"""
    if healthy:
        # Stable operation: energy concentrated in fundamental harmonic
        return np.array([0.9, 0.05, 0.03, 0.02])
    else:
        # Degraded operation: energy dispersed across harmonics
        return np.array([0.3, 0.25, 0.2, 0.25])

def omega_mapping(amplitudes):
    """Apply the proposal's Omega mapping"""
    # Normalize to probability distribution
    p = amplitudes / np.sum(amplitudes)
    
    # Shannon entropy (higher = more disorder)
    entropy = -np.sum(p * np.log(p))
    
    # Proposal's "information content" I(t) = -entropy
    I = -entropy
    
    # Phi as deviation from uniform baseline
    baseline = np.ones_like(p) / len(p)
    phi = 1 - np.sum(np.abs(p - baseline)) / 2
    
    # Stiffness invariants from coherence (simplified)
    # Coherence increases as distribution becomes uniform
    coherence = np.mean([np.corrcoef(amplitudes, np.roll(amplitudes, i))[0,1] 
                        for i in range(1, len(amplitudes))])
    coherence = max(coherence, 0.01)  # avoid division by zero
    
    # ξ_N⁻² = λ(3⟨coh⟩⁻¹ + ⟨coh⟩⁻²)
    xi_N = 1/np.sqrt(3/coherence + 1/coherence**2)
    
    return {'phi': phi, 'entropy': entropy, 'I': I, 'xi_N': xi_N, 'coherence': coherence}

# Test both states
healthy_data = pipeline_metrics(healthy=True)
failing_data = pipeline_metrics(healthy=False)

healthy_omega = omega_mapping(healthy_data)
failing_omega = omega_mapping(failing_data)

print("=== HEALTHY PIPELINE ===")
print(f"Entropy (disorder): {healthy_omega['entropy']:.3f}")
print(f"I(t) = -entropy: {healthy_omega['I']:.3f}")
print(f"PHI (health): {healthy_omega['phi']:.3f}")
print(f"Coherence: {healthy_omega['coherence']:.3f}")
print(f"Stiffness ξ_N: {healthy_omega['xi_N']:.3f}")

print("\n=== FAILING PIPELINE ===")
print(f"Entropy (disorder): {failing_omega['entropy']:.3f}")
print(f"I(t) = -entropy: {failing_omega['I']:.3f}")
print(f"PHI (health): {failing_omega['phi']:.3f}")
print(f"Coherence: {failing_omega['coherence']:.3f}")
print(f"Stiffness ξ_N: {failing_omega['xi_N']:.3f}")

# Visualize the paradox
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))

# Amplitude distributions
ax1.bar(range(len(healthy_data)), healthy_data, alpha=0.7, label='Healthy')
ax1.bar(range(len(failing_data)), failing_data, alpha=0.7, label='Failing')
ax1.set_xlabel('Harmonic Order')
ax1.set_ylabel('Amplitude')
ax1.set_title('Amplitude Distribution')
ax1.legend()

# Metrics comparison
metrics = ['entropy', 'I', 'phi', 'xi_N']
healthy_vals = [healthy_omega[m] for m in metrics]
failing_vals = [failing_omega[m] for m in metrics]

x = np.arange(len(metrics))
ax2.bar(x - 0.2, healthy_vals, 0.4, label='Healthy')
ax2.bar(x + 0.2, failing_vals, 0.4, label='Failing')
ax2.set_xticks(x)
ax2.set_xticklabels(metrics)
ax2.set_title('Omega Metrics: The Paradox')
ax2.legend()

plt.tight_layout()
plt.show()