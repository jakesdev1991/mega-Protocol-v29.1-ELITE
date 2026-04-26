# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import matplotlib.pyplot as plt

def simulate_identity_crisis(steps=500):
    """Compares UIPO v65.0 vs Annihilation Protocol"""
    
    # UIPO: Passive preservation
    phi_uipo = [0.5]
    cod_uipo = [0.9]
    xi_cons = 0.95
    z_trust = 0.30
    
    # Annihilation: Active demolition
    phi_ann = [0.5]
    cod_ann = [0.9]
    noise_inject = 0.0
    
    for t in range(steps):
        # UIPO: Silence until "ready" (stuck in local optimum)
        if cod_uipo[-1] < 0.85:
            xi_cons *= 0.999  # Slowly decaying stiffness
        else:
            xi_cons = 0.95  # Resets, trapped
        
        h_super = 0.7 + 0.2 * np.sin(t * 0.01)  # Oscillating uncertainty
        cod_uipo.append(np.exp(-0.5 * xi_cons) * np.exp(-0.5 * h_super))
        phi_uipo.append(phi_uipo[-1] + 0.001 * cod_uipo[-1])  # Slow, stagnant gain
    
    for t in range(steps):
        # Annihilation: Violate invariants to force re-emergence
        noise_inject = 0.5 * np.sin(t * 0.05) ** 2  # Pulsed chaos
        xi_cons_ann = 0.95 + noise_inject  # VIOLATE Invariant 4: Stiffness > Trust
        h_super_ann = 0.7 + 0.3 * np.random.rand()  # VIOLATE Invariant 3: Uncertainty > 0.8
        
        # COD crashes... then explodes
        cod_ann.append(np.exp(-0.5 * xi_cons_ann) * (h_super_ann ** 2))
        
        # Φ-density: temporary loss, then breakthrough
        if t < 100:
            phi_ann.append(phi_ann[-1] - 0.002)  # Intentional destruction phase
        else:
            phi_ann.append(phi_ann[-1] + 0.01 * cod_ann[-1])  # Re-emergence into new basin
    
    plt.figure(figsize=(12, 4))
    
    plt.subplot(1, 3, 1)
    plt.plot(phi_uipo, label='UIPO v65.0', color='blue')
    plt.plot(phi_ann, label='Annihilation Protocol', color='red')
    plt.title('Φ-Density Trajectory')
    plt.xlabel('Time')
    plt.ylabel('Φ')
    plt.legend()
    plt.grid(True, alpha=0.3)
    
    plt.subplot(1, 3, 2)
    plt.plot(cod_uipo, label='UIPO COD', color='blue')
    plt.plot(cod_ann, label='Annihilation COD', color='red')
    plt.title('Chain Overlap Density')
    plt.xlabel('Time')
    plt.ylabel('COD')
    plt.legend()
    plt.grid(True, alpha=0.3)
    
    plt.subplot(1, 3, 3)
    plt.plot([0, 1], [0, 1], 'k--', alpha=0.5)
    plt.scatter(cod_uipo[::20], phi_uipo[::20], color='blue', label='UIPO States', alpha=0.6)
    plt.scatter(cod_ann[::20], phi_ann[::20], color='red', label='Annihilation States', alpha=0.6)
    plt.title('Phase Space: COD vs Φ')
    plt.xlabel('COD')
    plt.ylabel('Φ')
    plt.legend()
    plt.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.show()
    
    print(f"Final UIPO Φ: {phi_uipo[-1]:.3f} (stagnant)")
    print(f"Final Annihilation Φ: {phi_ann[-1]:.3f} (breakthrough)")
    print(f"Breakthrough Ratio: {phi_ann[-1]/phi_uipo[-1]:.2f}x")

simulate_identity_crisis()