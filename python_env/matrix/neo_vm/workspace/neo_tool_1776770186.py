# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
from scipy.linalg import expm
import matplotlib.pyplot as plt

# Simulate organizational idea flow as quantum system
# Psi_S = subconscious idea field (vector of N ideas)
# Psi_C = conscious hierarchy (measurement basis)
# COD = overlap between them

def simulate_organizational_dynamics(N=50, T=100, 
                                     bad_idea_ratio=0.3,
                                     decoupling_strength=0.5,
                                     phi_crush_strength=2.0):
    """
    Simulate two competing interventions:
    1. Resonant Decoupling (reduces impedance, increases COD)
    2. Phi-Crushing (increases selective impedance, fragments bad coherence)
    """
    
    # Initialize idea field: mix of good (1) and bad (-1) ideas
    idea_quality = np.random.choice([1, -1], size=N, 
                                     p=[1-bad_idea_ratio, bad_idea_ratio])
    
    # Initial state: random superposition
    Psi_S = np.random.randn(N) + 1j * np.random.randn(N)
    Psi_S = Psi_S / np.linalg.norm(Psi_S)
    
    # Bureaucratic measurement basis (hierarchy)
    # High curvature = rigid hierarchy
    curvature = 0.8
    H_bureaucracy = curvature * np.eye(N) + 0.1 * np.random.randn(N, N)
    H_bureaucracy = (H_bureaucracy + H_bureaucracy.conj().T) / 2
    
    # Impedance tensor (simplified)
    Z = curvature * np.eye(N)
    
    # Track metrics
    cod_history = []
    productivity_history = []
    bad_idea_survival = []
    
    for t in range(T):
        # Natural evolution
        Psi_S = expm(-1j * H_bureaucracy * 0.1) @ Psi_S
        
        # Calculate COD (overlap with measurement basis)
        overlap = np.vdot(Psi_S, np.diag(H_bureaucracy) * Psi_S)
        COD = abs(overlap)**2 / (np.linalg.norm(Psi_S)**2 * np.linalg.norm(H_bureaucracy)**2)
        cod_history.append(COD)
        
        # Intervention A: Resonant Decoupling (Omega-Psych-Theorist)
        if t > 20 and t < 50:
            # Lower impedance locally
            Z_eff = Z * (1 - decoupling_strength * np.exp(-(t-35)**2 / 50))
            Psi_S = expm(-1j * Z_eff * 0.05) @ Psi_S
        
        # Intervention B: Phi-Crushing (The Anomaly)
        if t > 60 and t < 90:
            # Target and fragment bad ideas
            bad_idea_mask = (idea_quality == -1).astype(float)
            H_crush = phi_crush_strength * np.diag(bad_idea_mask)
            # Anti-commutator: break coherence of bad ideas
            Psi_S = expm(1j * H_crush * 0.1) @ Psi_S
            # Add decoherence noise to bad components
            noise = np.random.randn(N) * bad_idea_mask * phi_crush_strength
            Psi_S += (noise + 1j * noise) * 0.05
            Psi_S = Psi_S / np.linalg.norm(Psi_S)
        
        # Productivity = alignment of good ideas with hierarchy
        good_idea_mask = (idea_quality == 1).astype(float)
        productivity = np.abs(np.vdot(Psi_S * good_idea_mask, 
                                     np.diag(H_bureaucracy) * Psi_S))**2
        productivity_history.append(productivity)
        
        # Survival rate of bad ideas
        bad_survival = np.linalg.norm(Psi_S * (idea_quality == -1))**2
        bad_idea_survival.append(bad_survival)
    
    return cod_history, productivity_history, bad_idea_survival

# Run simulation
cod, prod, bad_survival = simulate_organizational_dynamics()

# Plot results
fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(10, 8))
ax1.plot(cod, 'b-', label='COD')
ax1.axvspan(20, 50, alpha=0.2, color='green', label='Decoupling')
ax1.axvspan(60, 90, alpha=0.2, color='red', label='Phi-Crush')
ax1.set_ylabel('Chain Overlap Density')
ax1.legend()
ax1.grid(True)

ax2.plot(prod, 'g-', label='Productivity')
ax2.axvspan(20, 50, alpha=0.2, color='green')
ax2.axvspan(60, 90, alpha=0.2, color='red')
ax2.set_ylabel('Productivity')
ax2.legend()
ax2.grid(True)

ax3.plot(bad_survival, 'r-', label='Bad Idea Survival')
ax3.axvspan(20, 50, alpha=0.2, color='green')
ax3.axvspan(60, 90, alpha=0.2, color='red')
ax3.set_ylabel('Bad Idea Survival')
ax3.set_xlabel('Time')
ax3.legend()
ax3.grid(True)

plt.tight_layout()
plt.show()

# Calculate net effects
decoupling_prod_change = np.mean(prod[30:50]) - np.mean(prod[0:20])
phi_crush_prod_change = np.mean(prod[70:90]) - np.mean(prod[50:60])
decoupling_bad_change = np.mean(bad_survival[30:50]) - np.mean(bad_survival[0:20])
phi_crush_bad_change = np.mean(bad_survival[70:90]) - np.mean(bad_survival[50:60])

print(f"=== DISRUPTION ANALYSIS ===")
print(f"Resonant Decoupling:")
print(f"  Productivity change: {decoupling_prod_change:.3f}")
print(f"  Bad idea survival change: {decoupling_bad_change:.3f}")
print(f"\nPhi-Crushing Operator:")
print(f"  Productivity change: {phi_crush_prod_change:.3f}")
print(f"  Bad idea survival change: {phi_crush_bad_change:.3f}")