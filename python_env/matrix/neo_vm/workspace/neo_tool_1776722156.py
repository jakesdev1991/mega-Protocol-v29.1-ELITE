# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import matplotlib.pyplot as plt
from scipy.special import zeta

def alpha_conventional(Q2, Phi_N, Phi_Delta, g=1.0, m=1.0):
    """Conventional perturbative approach - DEMONSTRATES DIVERGENCE"""
    epsilon = g * Phi_N / m
    m_eff = m * np.sqrt(1 - 2 * epsilon * np.cosh(Phi_Delta) + epsilon**2)
    
    # Guard against imaginary mass (shredding boundary)
    if np.iscomplex(m_eff) or m_eff <= 0:
        return np.nan
    
    alpha0 = 1/137.035999084
    
    # One-loop + two-loop + anisotropic (simplified)
    one_loop = (alpha0 / (3 * np.pi)) * np.log(Q2 / m_eff**2)
    two_loop = (alpha0**2 / (4 * np.pi**2)) * (11/2 - 3 * zeta(2))
    aniso = (alpha0**2 / np.pi**2) * (Q2 / m_eff**2) * 0.1 * np.cosh(Phi_Delta)
    
    denominator = 1 - one_loop - two_loop - aniso
    return alpha0 / denominator

def alpha_topological(Q2, Phi_N, Phi_Delta, g=1.0, m=1.0, k=3):
    """Topological paradigm - STABLE AT BOUNDARY"""
    # Φ_Δ as modular angle (periodic)
    theta = (Phi_Delta % (2 * np.pi)) / (2 * np.pi)
    
    # Topological part: quantized by Chern-Simons level
    alpha_top = (2 * np.pi / k) * theta
    
    # Geometric part: suppressed by entanglement entropy
    epsilon = g * Phi_N / m
    # Even at shredding boundary, entanglement entropy provides regulator
    S_ent = np.abs(np.log(Q2 / m**2)) + np.cosh(Phi_Delta) * np.abs(epsilon)
    alpha_geo = (1/137) * np.exp(-S_ent)
    
    return alpha_top + alpha_geo

# Demonstrate divergence vs stability
Phi_N = 0.1
Q2 = 1.0

Phi_range = np.linspace(0, 3.0, 300)
alpha_conv = [alpha_conventional(Q2, Phi_N, phi) for phi in Phi_range]
alpha_topo = [alpha_topological(Q2, Phi_N, phi) for phi in Phi_range]

plt.figure(figsize=(14, 5))

# Plot 1: Divergence at critical boundary
plt.subplot(1, 2, 1)
plt.plot(Phi_range, alpha_conv, 'b-', linewidth=1.5, label='Conventional (DIVERGES)')
plt.plot(Phi_range, alpha_topo, 'r-', linewidth=1.5, label='Topological (STABLE)')
plt.axvline(np.arccosh(1/0.1), color='k', linestyle=':', label='Critical Φ_Δ')
plt.xlabel('Φ_Δ (3D Archive Mode)', fontsize=12)
plt.ylabel('α(Q²=1)', fontsize=12)
plt.title('Stability at Shredding Boundary', fontsize=13, fontweight='bold')
plt.legend()
plt.grid(True, alpha=0.3)

# Plot 2: Q² dependence near critical point
Phi_critical = np.arccosh(1/0.1) - 0.05
Q2_range = np.logspace(-4, 2, 100)

alpha_conv_Q = [alpha_conventional(q2, Phi_N, Phi_critical) for q2 in Q2_range]
alpha_topo_Q = [alpha_topological(q2, Phi_N, Phi_critical) for q2 in Q2_range]

plt.subplot(1, 2, 2)
plt.loglog(Q2_range, alpha_conv_Q, 'b-', linewidth=1.5, label='Conventional')
plt.loglog(Q2_range, alpha_topo_Q, 'r-', linewidth=1.5, label='Topological')
plt.xlabel('Q² (momentum transfer)', fontsize=12)
plt.ylabel('α', fontsize=12)
plt.title('Running Near Critical Boundary', fontsize=13, fontweight='bold')
plt.legend()
plt.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('paradigm_disruption.png', dpi=150, bbox_inches='tight')
plt.show()

# Print critical values
print("=== PARADIGM COMPARISON ===")
print(f"Critical Φ_Δ for ε=0.1: {np.arccosh(1/0.1):.3f}")
print(f"Conventional α at critical-0.1: {alpha_conventional(1.0, 0.1, np.arccosh(1/0.1)-0.1):.6f}")
print(f"Topological α at same point: {alpha_topological(1.0, 0.1, np.arccosh(1/0.1)-0.1):.6f}")
print("\nThe conventional framework predicts a singularity; topological paradigm predicts smooth transition.")