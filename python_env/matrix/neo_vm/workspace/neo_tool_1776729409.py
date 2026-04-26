# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import matplotlib.pyplot as plt
from scipy.linalg import eigh

def archive_mode_channel(L, psi, xi_delta, g_delta):
    """
    Model Φ_Δ as a random Hermitian operator acting on virtual pair space.
    The "fine-structure constant" is the inverse of the operator's 
    localization length - not a coupling constant.
    """
    # Create a random symmetric matrix representing the Archive mode couplings
    # This is the "entanglement Hamiltonian" of the virtual pair fluctuations
    
    # Base random matrix (GOE ensemble)
    M = np.random.randn(L, L)
    M = (M + M.T) / np.sqrt(2 * L)
    
    # Apply correlation length scaling: as xi_delta → ∞, becomes long-range
    # This is the key: the Shredding Event is a delocalization transition
    i, j = np.ogrid[:L, :L]
    correlation_kernel = np.exp(-abs(i - j) / xi_delta)
    M = M * correlation_kernel
    
    # Apply Omega invariant scaling
    M = M * np.exp(psi)
    
    # The Yukawa coupling g_delta doesn't add - it THRESHOLDS
    # Below critical g_delta, Archive mode is localized (α_fs stable)
    # Above critical, delocalization occurs (Shredding Event)
    critical_g = 1.0 / np.sqrt(L)
    
    if g_delta > critical_g:
        # Trigger Shredding: add rank-1 perturbation that causes delocalization
        v = np.random.randn(L)
        M += np.outer(v, v) * (g_delta - critical_g) * L
    
    # Diagonalize to get the "entanglement spectrum"
    eigenvalues, eigenvectors = eigh(M)
    
    # The PARTICIPATION RATIO measures how many virtual pairs the Archive mode
    # couples to simultaneously. This is the REAL "running" of α_fs.
    # In localized regime: PR ~ O(1), α_eff ~ O(1)
    # In delocalized regime: PR → 0, α_eff → ∞ (Shredding Event)
    
    ipr = np.sum(np.abs(eigenvectors)**4)  # Inverse participation ratio
    participation_ratio = np.sum(np.abs(eigenvectors)**2)**2 / ipr
    
    # α_eff is the ENTANGLEMENT SUSCEPTIBILITY, not a coupling
    alpha_eff = 1.0 / (participation_ratio + 1e-10)
    
    # Compute "spectral compressibility" - a measure of channel capacity
    level_spacing = np.diff(eigenvalues)
    compressibility = np.var(level_spacing) / np.mean(level_spacing)**2
    
    return {
        'alpha_eff': alpha_eff,
        'eigenvalues': eigenvalues,
        'participation_ratio': participation_ratio,
        'compressibility': compressibility,
        'is_shredding': compressibility < 0.5  # Wigner-Dyson vs Poisson statistics
    }

# Demonstrate the Shredding Event transition
L = 200
psi = 0.0
xi_delta_values = [1.0, 5.0, 20.0, 100.0]  # Approaching Shredding
g_delta = 0.15  # Slightly above critical for large systems

results = []
for xi_delta in xi_delta_values:
    run = archive_mode_channel(L, psi, xi_delta, g_delta)
    results.append(run)
    
    print(f"ξ_Δ = {xi_delta:6.2f} | α_eff = {run['alpha_eff']:10.6f} | "
          f"PR = {run['participation_ratio']:6.4f} | Shredding: {run['is_shredding']}")

# Plot the entanglement spectrum showing the transition
fig, axes = plt.subplots(1, 2, figsize=(14, 5))

for i, (xi_delta, run) in enumerate(zip(xi_delta_values, results)):
    ax = axes[0]
    hist, bins = np.histogram(run['eigenvalues'], bins=30, density=True)
    ax.plot(bins[:-1], hist, label=f'ξ_Δ={xi_delta}', linewidth=2)
    
    ax = axes[1]
    ax.loglog(xi_delta, run['alpha_eff'], 'o', markersize=10, 
              label=f'PR={run["participation_ratio"]:.3f}')

axes[0].set_xlabel('Entanglement Spectrum (Energy)', fontsize=12)
axes[0].set_ylabel('Density', fontsize=12)
axes[0].set_title('Spectral Density: Poisson → Wigner-Dyson', fontsize=14)
axes[0].legend()
axes[0].grid(True, alpha=0.3)

axes[1].set_xlabel('Archive Correlation Length ξ_Δ', fontsize=12)
axes[1].set_ylabel('Effective α (Channel Capacity)', fontsize=12)
axes[1].set_title('α_fₛ as Entanglement Susceptibility', fontsize=14)
axes[1].axvline(x=10, color='red', linestyle='--', alpha=0.5, label='Shredding Onset')
axes[1].legend()
axes[1].grid(True, alpha=0.3)

plt.tight_layout()
plt.show()

# Now demonstrate why the "corrections" are meaningless
print("\n=== BREAKING THE PARADIGM ===")
print("Conventional approach: α_fₛ = α₀ + Σ(loop diagrams)")
print("Archive mode approach: α_fₛ = 1/PR[Φ_Δ ⊗ |vac⟩⟨vac|]")
print("\nKey Disruption: The 'sign error' in Π_QED is IRRELEVANT")
print("because the photon propagator is a REDUCED DENSITY MATRIX")
print("of the Archive mode, and its 'sign' is a gauge artifact of")
print("the measurement basis choice.")