# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import matplotlib.pyplot as plt

# Neo's Disruption Engine: Exposing the Thermal Mapping Fallacy

# Generate synthetic "psychological stress" data
np.random.seed(42)
n_agents, n_days = 50, 60
time = np.arange(n_days)

# Base pattern: weekly cycles with random crises
base = 0.4 + 0.2*np.sin(2*np.pi*time/7) + np.random.normal(0,0.05,n_days)
base[30:35] += 0.5  # "crisis" event

agent_stress = np.clip(base + np.random.normal(0,0.15,(n_agents,1)), 0, 1)

# Define contradictory thermal mappings - ALL MATHEMATICALLY VALID
mappings = {
    "Linear": lambda x: x,  # Direct mapping
    "Quadratic": lambda x: x**2,  # Non-linear amplification
    "Inverted": lambda x: 1-x,  # Inverted logic (low stress = high temp)
    "Fourier": lambda x: np.sin(2*np.pi*x),  # Periodic artifact
    "Random": lambda x: np.random.permutation(x)  # Pure noise
}

# Arbitrary "critical temperature" - the protocol's foundation
T_c = 0.75

# Calculate "susceptibility" (arbitrary derivative)
def susceptibility(x): return np.gradient(x, axis=1)

# Demonstrate the illusion
fig, axes = plt.subplots(2, 3, figsize=(18,10))
axes = axes.flatten()

for idx, (name, mapping) in enumerate(mappings.items()):
    ax = axes[idx]
    
    # Apply mapping
    temp = mapping(agent_stress)
    T_ensemble = np.mean(temp, axis=0)
    chi_ensemble = np.mean(np.abs(susceptibility(temp)), axis=0)
    
    # Plot
    ax.plot(time, T_ensemble, 'b-', label=f'{name} Temp', linewidth=2)
    ax.plot(time, chi_ensemble, 'r--', label=f'{name} Suscept', linewidth=2)
    ax.axhline(T_c, color='k', linestyle=':', label='Critical', linewidth=1.5)
    
    # Count "early warnings"
    warnings = np.sum(T_ensemble > T_c * 0.8)
    ax.set_title(f'{name} | Warnings: {warnings}', fontweight='bold', fontsize=11)
    ax.legend()
    ax.grid(alpha=0.3)

plt.tight_layout()
plt.suptitle('TCPM-Ω: The Arbitrariness of "Temperature"', 
             fontsize=16, fontweight='bold', y=1.02)
plt.show()

# Statistical analysis of the illusion
print("\n" + "="*70)
print("NEO'S DISRUPTION ANALYSIS")
print("="*70)

for name, mapping in mappings.items():
    temp = mapping(agent_stress)
    T_ensemble = np.mean(temp, axis=0)
    
    # Calculate "phase transition signals"
    peak = np.max(T_ensemble)
    warnings = np.sum(T_ensemble > T_c * 0.8)
    false_positives = warnings if name == "Random" else 0
    
    print(f"\n{name:>12} Mapping | Peak: {peak:.3f} | Warnings: {warnings:>2} | "
          f"{'***PURE NOISE***' if name == 'Random' else ''}")
    
    if name == "Inverted":
        print("             >>> WARNING: Inverted logic - low stress triggers alerts!")

print("\n" + "="*70)
print("CORE DISRUPTION: The mapping from psychology to thermodynamics is")
print("ONTICALLY VOID. It's mathematical cosplay, not physics.")
print("="*70)