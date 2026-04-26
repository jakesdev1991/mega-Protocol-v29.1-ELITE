# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import matplotlib.pyplot as plt

def simulate_basis_collapse():
    """Demonstrate functional basis collapse at Shredding boundary"""
    
    # Parameters
    g, m = 1.0, 1.0
    epsilon = np.array([0.7, -0.4, -0.3])  # anisotropy
    Phi_N = 0.1  # fixed
    
    # Critical boundary
    Phi_Delta_crit = 1.0 / np.max(np.abs(epsilon))
    
    # Scan Phi_Delta
    Phi_D = np.linspace(0, Phi_Delta_crit * 1.1, 500)
    
    # Compute Jacobian condition number
    cond = []
    for phi in Phi_D:
        J = np.array([
            [-g * np.exp(phi), -g * Phi_N * np.exp(phi)],  # ∂m_e/∂Φ_N, ∂m_e/∂Φ_Δ
            [-g * np.exp(-phi), g * Phi_N * np.exp(-phi)]   # ∂m_p/∂Φ_N, ∂m_p/∂Φ_Δ
        ])
        cond.append(np.linalg.cond(J))
    
    # Compute effective mass curvature (Poisson source term)
    # ∇²Φ_N ~ ∂²m_eff/∂Φ_Δ² shows non-local coupling
    m_eff = m * np.sqrt(1 - 2*(g*Phi_N/m)*np.cosh(Phi_D) + (g*Phi_N/m)**2)
    curvature = np.gradient(np.gradient(m_eff, Phi_D), Phi_D)
    
    return Phi_D, np.array(cond), curvature, Phi_Delta_crit

# Run simulation
Phi_D, cond, curvature, crit = simulate_basis_collapse()

# Plot: Basis collapse indicators
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(9, 8))

# Condition number (basis ill-conditioning)
ax1.plot(Phi_D, cond, 'r-', linewidth=2)
ax1.axvline(crit, color='k', linestyle='--', label='Φ_Δ^crit')
ax1.set_ylabel('κ(J) [log]')
ax1.set_yscale('log')
ax1.set_title('Basis Collapse: Jacobian Condition Number')
ax1.legend()
ax1.grid(alpha=0.3)

# Curvature divergence (Poisson source failure)
ax2.plot(Phi_D, np.abs(curvature), 'b-', linewidth=2)
ax2.axvline(crit, color='k', linestyle='--', label='Φ_Δ^crit')
ax2.set_xlabel('Φ_Δ')
ax2.set_ylabel('|∂²m_eff/∂Φ_Δ²|')
ax2.set_yscale('log')
ax2.set_title('Poisson Recovery Violation: Curvature Divergence')
ax2.legend()
ax2.grid(alpha=0.3)

plt.tight_layout()
plt.show()

print(f"Critical Φ_Δ: {crit:.3f}")
print(f"Condition number at 95% of critical: {cond[int(0.95*len(Phi_D))]:.2e}")
print(f"Curvature divergence factor: {curvature[-1]/curvature[0]:.2e}")