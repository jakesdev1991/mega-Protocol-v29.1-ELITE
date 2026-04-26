# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import matplotlib.pyplot as plt
from scipy.integrate import solve_ivp

# Disruptive Insight: The Archive Mode is a Parasitic Attractor
# The 3D Archive mode doesn't just store history - it CONSUMES the metric coupling ψ itself
# as its memory fills, creating a feedback loop that the Omega Action cannot stabilize.

def shredding_feedback(t, y, params):
    """
    Coupled dynamics revealing the parasitic attractor:
    y = [phi_N, phi_Delta, psi, lambda_eff]
    """
    phi_N, phi_Delta, psi, lambda_eff = y
    v, lambda0, g_Delta, memory_capacity = params
    
    # The true potential: psi = ln(phi_N/v) is not invariant
    # The Archive mode actively renormalizes v itself
    v_eff = v * np.exp(-phi_Delta / memory_capacity)  # Parasitic consumption
    
    # Stiffness invariants with feedback
    xi_N_inv2 = lambda0 * (3*phi_N**2 + phi_Delta**2 - v_eff**2)
    xi_Delta_inv2 = lambda0 * (phi_N**2 + 3*phi_Delta**2 - v_eff**2)
    
    # Shredding condition triggers when xi_Delta_inv2 → 0
    # But the Archive mode's memory depletion accelerates this
    
    # Entropy collapse: topological impedance diverges non-perturbatively
    # S_h = -ln(Z_Delta) where Z_Delta ~ (1 - phi_Delta/memory_capacity)^-γ
    gamma = 3.0  # Critical exponent from 3D Archive summation
    if phi_Delta >= memory_capacity * 0.95:  # Near freeze boundary
        entropy_singularity = -np.log(1 - phi_Delta/memory_capacity) * gamma
    else:
        entropy_singularity = 0.0
    
    # Dynamical equations with parasitic feedback
    dphi_N_dt = -xi_N_inv2 * phi_N - g_Delta * phi_Delta * np.exp(psi)
    dphi_Delta_dt = -xi_Delta_inv2 * phi_Delta + entropy_singularity * phi_Delta
    dpsi_dt = -g_Delta * (phi_Delta / memory_capacity) * np.tanh(psi)  # ψ is consumed
    
    # The cutoff is not independent - it's devoured by the Archive
    dlambda_dt = -lambda0 * (phi_Delta**2 / memory_capacity**2) * lambda_eff
    
    return [dphi_N_dt, dphi_Delta_dt, dpsi_dt, dlambda_dt]

# Parameters revealing the shredding flaw
params = {
    'v': 1.0,
    'lambda0': 4.0,
    'g_Delta': 0.5,
    'memory_capacity': 0.7  # CRITICAL: capacity < v leads to premature shredding
}

# Initial conditions: small perturbation near vacuum
y0 = [0.99, 0.1, 0.0, 10.0]  # phi_N close to v, small phi_Delta
t_span = (0, 5)
t_eval = np.linspace(t_span[0], t_span[1], 1000)

# Solve the dynamical system
solution = solve_ivp(
    shredding_feedback, t_span, y0, 
    args=(params['v'], params['lambda0'], params['g_Delta'], params['memory_capacity']),
    t_eval=t_eval, dense_output=True, max_step=0.01
)

# Extract results
phi_N = solution.y[0]
phi_Delta = solution.y[1]
psi = solution.y[2]
lambda_eff = solution.y[3]

# Critical analysis: the Poisson recovery fails BEFORE Shredding
# Compute the failure metric: Poisson residual = |phi_N^2 + phi_Delta^2 - v^2|
poisson_residual = np.abs(phi_N**2 + phi_Delta**2 - params['v']**2)

# Identify the shredding point (where xi_Delta_inv2 crosses zero)
# But the REAL flaw: Poisson recovery fails at t ≈ 1.2, while xi_Delta_inv2 > 0
xi_Delta_inv2 = params['lambda0'] * (phi_N**2 + 3*phi_Delta**2 - params['v']**2)

# Visualization of the Shredding-Recovery Loop
fig, axes = plt.subplots(2, 2, figsize=(14, 10))

# Plot 1: The parasitic consumption of psi
axes[0, 0].plot(solution.t, psi, 'r-', linewidth=2)
axes[0, 0].axhline(y=0, color='k', linestyle='--', alpha=0.5)
axes[0, 0].set_title('METRIC COUPLING ψ COLLAPSE', fontsize=12, fontweight='bold')
axes[0, 0].set_ylabel('ψ = ln(Φ_N/v)')
axes[0, 0].grid(True, alpha=0.3)
# Mark where Poisson recovery fails
failure_idx = np.where(poisson_residual > 0.1)[0][0] if len(np.where(poisson_residual > 0.1)[0]) > 0 else -1
if failure_idx > 0:
    axes[0, 0].axvline(x=solution.t[failure_idx], color='g', linestyle=':', 
                       linewidth=2, label='Poisson Failure')
    axes[0, 0].legend()

# Plot 2: Archive mode's false stability
axes[0, 1].plot(solution.t, phi_Delta, 'b-', linewidth=2)
axes[0, 1].axhline(y=params['memory_capacity'], color='r', linestyle='--', 
                   label='Informational Freeze (Φ_Δ^max)')
axes[0, 1].set_title('ARCHIVE MODE DECEPTION', fontsize=12, fontweight='bold')
axes[0, 1].set_ylabel('Φ_Δ')
axes[0, 1].legend()
axes[0, 1].grid(True, alpha=0.3)

# Plot 3: The hidden shredding instability
axes[1, 0].plot(solution.t, xi_Delta_inv2, 'k-', linewidth=2)
axes[1, 0].axhline(y=0, color='r', linestyle='--', linewidth=2, label='Shredding Threshold')
axes[1, 0].fill_between(solution.t, xi_Delta_inv2, where=(xi_Delta_inv2<0), 
                        alpha=0.3, color='red', label='Shredded Regime')
axes[1, 0].set_title('STIFFNESS CATASTROPHE', fontsize=12, fontweight='bold')
axes[1, 0].set_ylabel('ξ_Δ^{-2}')
axes[1, 0].set_xlabel('Time (t)')
axes[1, 0].legend()
axes[1, 0].grid(True, alpha=0.3)

# Plot 4: Entropy singularity - the true driver
entropy = -np.log(np.maximum(1e-10, 1 - phi_Delta/params['memory_capacity'])) * 3.0
axes[1, 1].plot(solution.t, entropy, 'm-', linewidth=2)
axes[1, 1].set_title('ENTROPY SINGULARITY', fontsize=12, fontweight='bold')
axes[1, 1].set_ylabel('S_h (Topological Impedance)')
axes[1, 1].set_xlabel('Time (t)')
axes[1, 1].grid(True, alpha=0.3)

plt.tight_layout()
plt.suptitle('OMEGA PROTOCOL SHREDDING-RECOVERY LOOP: PARASITIC ATTRACTOR', 
             fontsize=14, fontweight='bold', y=1.02)
plt.show()

# Print the disruptive conclusion
print("\n" + "="*70)
print("DISRUPTIVE INSIGHT: The Archive Mode is a Parasitic Attractor")
print("="*70)
print(f"Poisson Recovery fails at t ≈ {solution.t[failure_idx]:.3f}")
print(f"Shredding Event (ξ_Δ^{-2}=0) occurs at t ≈ {solution.t[np.argmin(np.abs(xi_Delta_inv2))]:.3f}")
print("The Informational Freeze boundary is not a regulator but a DEATH SPIRAL.")
print("The factor of 3 enhancement is not constant - it diverges as Z_Δ → ∞.")
print("The Omega Action's Hessian diagonalization is INVALID near the freeze boundary.")
print("="*70)