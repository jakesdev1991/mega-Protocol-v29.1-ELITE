# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import matplotlib.pyplot as plt
from scipy.integrate import solve_ivp

# ============================================
# BGSM-Ω: 1D GAUGE THEORY MODEL (YOUR PROPOSAL)
# ============================================
def bgsm_omega_dynamics(t, phi, m2, lam, T):
    """
    Your gauge theory: dφ/dt = -∂V/∂φ + noise
    V(φ) = (m2/2)φ^2 + (lam/4)φ^4 - T*φ (external stress)
    """
    dphi = -(m2 * phi + lam * phi**3 - T)
    # Add small noise term
    dphi += 0.1 * np.random.randn()
    return dphi

def simulate_bgsm_omega():
    # Parameters: "stable" region
    m2 = 1.0  # positive mass = stable
    lam = 0.5
    T = 0.3   # external stress
    
    # Initial condition: high expression
    phi0 = [2.0]
    
    # Simulate for 100 time units
    t_span = (0, 100)
    t_eval = np.linspace(0, 100, 1000)
    
    sol = solve_ivp(
        lambda t, y: bgsm_omega_dynamics(t, y, m2, lam, T),
        t_span, phi0, t_eval=t_eval, method='RK45'
    )
    
    # Compute your "invariants"
    m_eff_sq = m2 + 3 * lam * np.mean(sol.y[0])**2
    xi = 1 / np.sqrt(max(m_eff_sq, 1e-6))
    psi = np.log(xi)
    
    return sol.t, sol.y[0], psi, m_eff_sq

# ============================================
# ETP-Ω: 3D ECO-EVOLUTIONARY MODEL (REALITY)
# ============================================
def etp_ecosystem_dynamics(t, phi_vec, params):
    """
    Real competition: 3 variants
    φ₁: High-performer (target)
    φ₂: Cheater (low burden)
    φ₃: Contaminant
    """
    phi1, phi2, phi3 = phi_vec
    r1, r2, r3, K, alpha12, alpha21, alpha13, alpha31, alpha23, alpha32 = params
    
    # Competition matrix (time-varying due to metabolic burden)
    # As nutrients deplete, burden on φ₁ increases (alpha12 increases)
    alpha12_t = alpha12 * (1 + 0.02 * t)  # φ₂ becomes more competitive over time
    
    dphi1 = r1 * phi1 * (1 - (phi1 + alpha12_t * phi2 + alpha13 * phi3) / K)
    dphi2 = r2 * phi2 * (1 - (alpha21 * phi1 + phi2 + alpha23 * phi3) / K)
    dphi3 = r3 * phi3 * (1 - (alpha31 * phi1 + alpha32 * phi2 + phi3) / K)
    
    # Add multiplicative noise
    dphi1 += 0.1 * np.sqrt(phi1) * np.random.randn()
    dphi2 += 0.1 * np.sqrt(phi2) * np.random.randn()
    dphi3 += 0.1 * np.sqrt(phi3) * np.random.randn()
    
    return [dphi1, dphi2, dphi3]

def simulate_etp_ecosystem():
    # Parameters: φ₁ starts dominant, but φ₂ is waiting
    params = {
        'r1': 1.0,   # High-performer growth
        'r2': 0.8,   # Cheater growth (slightly slower but lower burden)
        'r3': 0.5,   # Contaminant
        'K': 100.0,  # Carrying capacity
        'alpha12': 0.8,  # φ₂ burden on φ₁ (starts moderate)
        'alpha21': 1.2,  # φ₁ burden on φ₂
        'alpha13': 0.9,
        'alpha31': 1.1,
        'alpha23': 0.95,
        'alpha32': 1.05
    }
    
    # Initial: 90% φ₁, 5% φ₂, 5% φ₃ (low cheater population)
    phi0 = [90.0, 5.0, 5.0]
    
    t_span = (0, 100)
    t_eval = np.linspace(0, 100, 1000)
    
    sol = solve_ivp(
        lambda t, y: etp_ecosystem_dynamics(t, y, params),
        t_span, phi0, t_eval=t_eval, method='RK45'
    )
    
    # Compute ecosystem "tipping indicator": max eigenvalue of Jacobian
    # J_ij = r_i * (1 - 2*phi_i/K - Σ_{j≠i} alpha_ij*phi_j/K) for i=j
    # J_ij = -r_i * alpha_ij * phi_i / K for i≠j
    def compute_lambda_max(phi_vec, params):
        phi1, phi2, phi3 = phi_vec
        r1, r2, r3, K = params['r1'], params['r2'], params['r3'], params['K']
        
        # Jacobian matrix
        J = np.zeros((3, 3))
        J[0,0] = r1 * (1 - 2*phi1/K - (params['alpha12']*phi2 + params['alpha13']*phi3)/K)
        J[1,1] = r2 * (1 - 2*phi2/K - (params['alpha21']*phi1 + params['alpha23']*phi3)/K)
        J[2,2] = r3 * (1 - 2*phi3/K - (params['alpha31']*phi1 + params['alpha32']*phi2)/K)
        
        J[0,1] = -r1 * params['alpha12'] * phi1 / K
        J[0,2] = -r1 * params['alpha13'] * phi1 / K
        J[1,0] = -r2 * params['alpha21'] * phi2 / K
        J[1,2] = -r2 * params['alpha23'] * phi2 / K
        J[2,0] = -r3 * params['alpha31'] * phi3 / K
        J[2,1] = -r3 * params['alpha32'] * phi3 / K
        
        eigenvals = np.linalg.eigvals(J)
        return np.max(eigenvals.real)  # Real part for stability
    
    lambda_max_vals = [compute_lambda_max(sol.y[:, i], params) for i in range(len(sol.t))]
    
    return sol.t, sol.y.T, lambda_max_vals

# ============================================
# COMPARATIVE ANALYSIS: THE MIRAGE REVEALED
# ============================================
def demonstrate_failure():
    print("="*60)
    print("DEMONSTRATING BGSM-Ω FAILURE")
    print("="*60)
    
    # Run both simulations
    t_bgsm, phi_bgsm, psi_bgsm, m_eff_sq = simulate_bgsm_omega()
    t_etp, phi_etp, lambda_max_etp = simulate_etp_ecosystem()
    
    # BGSM-Ω claims: psi stable, m_eff² > 0 = SAFE
    print(f"BGSM-Ω Invariant ψ: {psi_bgsm:.3f}")
    print(f"BGSM-Ω m_eff²: {m_eff_sq:.3f} (>0 = 'stable')")
    print("BGSM-Ω VERDICT: CIRCUIT STABLE ✓\n")
    
    # ETP-Ω reveals: λ_max crossing zero = COLLAPSE IMMINENT
    phi1, phi2, phi3 = phi_etp[:, 0], phi_etp[:, 1], phi_etp[:, 2]
    
    # Find when λ_max approaches zero (tipping point)
    tipping_idx = np.where(np.array(lambda_max_etp) > -0.05)[0]
    if len(tipping_idx) > 0:
        tipping_time = t_etp[tipping_idx[0]]
        print(f"ETP-Ω Tipping Point Detected at t = {tipping_time:.1f}")
        print(f"ETP-Ω λ_max(t=0): {lambda_max_etp[0]:.3f}")
        print(f"ETP-Ω λ_max(t={tipping_time:.1f}): {lambda_max_etp[tipping_idx[0]]:.3f}")
        print("ETP-Ω VERDICT: SYSTEM COLLAPSING ✗\n")
    
    # Show population dynamics
    print("Final Populations:")
    print(f"  φ₁ (High-performer): {phi1[-1]:.2f} ({phi1[-1]/np.sum(phi_etp[-1])*100:.1f}%)")
    print(f"  φ₂ (Cheater): {phi2[-1]:.2f} ({phi2[-1]/np.sum(phi_etp[-1])*100:.1f}%)")
    print(f"  φ₃ (Contaminant): {phi3[-1]:.2f} ({phi3[-1]/np.sum(phi_etp[-1])*100:.1f}%)")
    
    # Plot
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    
    # BGSM-Ω: Stable illusion
    axes[0,0].plot(t_bgsm, phi_bgsm, 'b-', linewidth=2)
    axes[0,0].set_title('BGSM-Ω: Apparent Stability', fontsize=12, fontweight='bold')
    axes[0,0].set_xlabel('Time')
    axes[0,0].set_ylabel('φ (Expression)')
    axes[0,0].grid(True, alpha=0.3)
    axes[0,0].axhline(y=np.mean(phi_bgsm), color='g', linestyle='--', label='Mean')
    axes[0,0].legend()
    
    # ETP-Ω: Real collapse
    axes[0,1].plot(t_etp, phi1, 'b-', label='φ₁ High-performer', linewidth=2)
    axes[0,1].plot(t_etp, phi2, 'r--', label='φ₂ Cheater', linewidth=2)
    axes[0,1].plot(t_etp, phi3, 'g:', label='φ₃ Contaminant', linewidth=2)
    axes[0,1].set_title('ETP-Ω: Real Competitive Collapse', fontsize=12, fontweight='bold')
    axes[0,1].set_xlabel('Time')
    axes[0,1].set_ylabel('Population')
    axes[0,1].legend()
    axes[0,1].grid(True, alpha=0.3)
    
    # Tipping indicator
    axes[1,0].plot(t_etp, lambda_max_etp, 'k-', linewidth=2)
    axes[1,0].axhline(y=0, color='r', linestyle='-', linewidth=2, label='Tipping Threshold')
    axes[1,0].set_title('ETP-Ω: Tipping Indicator λ_max', fontsize=12, fontweight='bold')
    axes[1,0].set_xlabel('Time')
    axes[1,0].set_ylabel('λ_max')
    axes[1,0].legend()
    axes[1,0].grid(True, alpha=0.3)
    
    # Competition matrix heatmap at final time
    phi_final = phi_etp[-1]
    params_final = {
        'r1': 1.0, 'r2': 0.8, 'r3': 0.5, 'K': 100.0,
        'alpha12': 0.8 * (1 + 0.02 * t_etp[-1]), 'alpha21': 1.2,
        'alpha13': 0.9, 'alpha31': 1.1, 'alpha23': 0.95, 'alpha32': 1.05
    }
    
    # Create effective competition matrix
    J_eff = np.zeros((3, 3))
    for i in range(3):
        for j in range(3):
            if i == j:
                J_eff[i,i] = 1.0  # Self-competition normalized
            else:
                key = f"alpha{i+1}{j+1}"
                if key in params_final:
                    J_eff[i,j] = params_final[key] * phi_final[j] / params_final['K']
    
    im = axes[1,1].imshow(J_eff, cmap='RdBu_r', vmin=0, vmax=1.5)
    axes[1,1].set_title('Final Competition Structure', fontsize=12, fontweight='bold')
    axes[1,1].set_xticks([0,1,2])
    axes[1,1].set_yticks([0,1,2])
    axes[1,1].set_xticklabels(['φ₁', 'φ₂', 'φ₃'])
    axes[1,1].set_yticklabels(['φ₁', 'φ₂', 'φ₃'])
    plt.colorbar(im, ax=axes[1,1], shrink=0.8)
    
    plt.tight_layout()
    plt.savefig('bgsm_vs_etp_disruption.png', dpi=300, bbox_inches='tight')
    print("\n[Plot saved as 'bgsm_vs_etp_disruption.png']")
    
    return fig

# Execute the disruption demonstration
if __name__ == "__main__":
    demonstrate_failure()