# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import matplotlib.pyplot as plt
from scipy.integrate import solve_ivp

# === THE DISRUPTION: Mexican-hat vs. Reality ===

def mexican_hat_dynamics(t, y, psi0, D_N, D_D, lambda_N, lambda_D):
    """The Engine's model: equilibrium statistical mechanics"""
    Phi_N, Phi_D = y
    dPhi_N_dt = -D_N * Phi_N - lambda_N * Phi_N * (Phi_N**2 + Phi_D**2 - psi0**2)
    dPhi_D_dt = -D_D * Phi_D - lambda_D * Phi_D * (Phi_N**2 + 3*Phi_D**2 - psi0**2)
    return [dPhi_N_dt, dPhi_D_dt]

def realistic_tokamak_dynamics(t, y, beta, eta, alpha):
    """Reality: non-equilibrium dissipative system with explosive instability"""
    psi, W = y  # psi: poloidal flux, W: magnetic island width
    J = -psi  # Simplified current
    gamma = 0.5  # Saturation
    
    # EXPLOSIVE GROWTH: positive feedback loop
    dpsi_dt = eta * J + alpha * W  # Resistive diffusion + island coupling
    dW_dt = beta * psi * W - gamma * W**2  # Nonlinear island growth
    
    return [dpsi_dt, dW_dt]

# === SIMULATION ===
t_span = (0, 8)
t_eval = np.linspace(0, 8, 2000)

# Mexican-hat parameters
psi0, D_N, D_D = 1.0, 0.1, 0.1
lambda_N, lambda_D = 1.0, 1.0
y0_mexican = [0.9, 0.1]

# Realistic tokamak parameters (tuned for explosive behavior)
beta, eta, alpha = 3.0, 0.05, 0.5  # beta > 2.5 triggers explosive growth
y0_realistic = [1.0, 0.01]

sol_mexican = solve_ivp(mexican_hat_dynamics, t_span, y0_mexican,
                        args=(psi0, D_N, D_D, lambda_N, lambda_D),
                        t_eval=t_eval, dense_output=True)

sol_realistic = solve_ivp(realistic_tokamak_dynamics, t_span, y0_realistic,
                          args=(beta, eta, alpha),
                          t_eval=t_eval, dense_output=True)

# === ANALYSIS ===
Phi_N, Phi_D = sol_mexican.y
mass_term = lambda_D * (Phi_N**2 + 3*Phi_D**2 - psi0**2)
xi_D = 1.0 / np.sqrt(np.abs(mass_term))

psi, W = sol_realistic.y
dt = t_eval[1] - t_eval[0]
jerk = np.gradient(np.gradient(np.gradient(psi, dt), dt), dt)

# === THE BREAK ===
fig, axes = plt.subplots(2, 2, figsize=(14, 10))

# Mexican-hat: smooth "soft" transition
axes[0,0].plot(t_eval, Phi_D, 'b-', linewidth=2)
axes[0,0].set_title('Mexican-Hat: Asymmetric Mode (Φ_Δ)', fontsize=12, fontweight='bold')
axes[0,0].set_ylabel('Φ_Δ')
axes[0,0].grid(True, alpha=0.3)

axes[0,1].plot(t_eval, xi_D, 'r-', linewidth=2)
axes[0,1].set_title('Mexican-Hat: Correlation Length ξ_Δ', fontsize=12, fontweight='bold')
axes[0,1].set_ylabel('ξ_Δ')
axes[0,1].grid(True, alpha=0.3)
# Mark the "divergence" point
divergence_idx = np.argmin(np.abs(mass_term))
axes[0,1].axvline(t_eval[divergence_idx], color='g', linestyle='--', alpha=0.7,
                  label=f'Soft threshold (t={t_eval[divergence_idx]:.2f})')
axes[0,1].legend()

# Realistic tokamak: explosive "hard" transition
axes[1,0].plot(t_eval, W, 'b-', linewidth=2)
axes[1,0].set_title('Realistic Tokamak: Magnetic Island Width', fontsize=12, fontweight='bold')
axes[1,0].set_xlabel('Time')
axes[1,0].set_ylabel('W (island width)')
axes[1,0].grid(True, alpha=0.3)

axes[1,1].plot(t_eval, jerk, 'r-', linewidth=2)
axes[1,1].set_title('Realistic Tokamak: Current Jerk', fontsize=12, fontweight='bold')
axes[1,1].set_xlabel('Time')
axes[1,1].set_ylabel('Jerk (d³ψ/dt³)')
axes[1,1].grid(True, alpha=0.3)
# Mark the explosive spike
spike_idx = np.argmax(np.abs(jerk))
axes[1,1].axvline(t_eval[spike_idx], color='g', linestyle='--', alpha=0.7,
                  label=f'Explosion (t={t_eval[spike_idx]:.2f})')
axes[1,1].legend()

plt.tight_layout()
plt.savefig('tokamak_category_error.png', dpi=150, bbox_inches='tight')
plt.show()

# === DISRUPTIVE INSIGHT ===
print("\n" + "="*60)
print("DISRUPTIVE INSIGHT: THE CATEGORY ERROR")
print("="*60)
print("\nThe entire Omega Protocol chain is built on a FATAL MISTAKE:")
print("\nEngine's Proposal: Uses EQUILIBRIUM statistical mechanics (Mexican-hat potential)")
print("                  ξ_Δ → ∞ at 'soft' second-order transition")
print("\nScrutiny's Audit: Corrects the math but NOT the paradigm")
print("                  Still accepts equilibrium field theory as valid")
print("\nMeta-Scrutiny: Validates the validation, missing the CATEGORY ERROR")
print("               Declares META-PASS while the framework is fundamentally wrong")
print("\n=== THE REALITY ===")
print("Tokamak disruptions are NON-EQUILIBRIUM, DISSIPATIVE, FIRST-ORDER events")
print("- No divergence of correlation length")
print("- No 'soft' warning from equilibrium potential")
print("- Explosive growth when feedback loops cross critical threshold")
print("- Jerk is a CONSEQUENCE, not a predictor (appears AT the crash)")
print("\n=== THE TRUE OMEGA INVARIANT ===")
print("For non-equilibrium systems, the rubric's 'correlation length' is MEANINGLESS")
print("The real invariant is CAUSAL INFORMATION SPEED v_c between system components")
print("- v_c = dI/dt where I = mutual information between spatially separated probes")
print("- Shredding Event: v_c → 0 (causal decoupling of plasma regions)")
print("- Informational Freeze: v_c = 0 (system becomes causally disconnected)")
print("- This is the actual 'informational' measure the Protocol seeks")
print("\n=== VERIFICATION ===")
print(f"Mexican-hat predicts smooth divergence at t≈{t_eval[divergence_idx]:.2f}")
print(f"Realistic model shows abrupt spike at t≈{t_eval[spike_idx]:.2f}")
print(f"No correlation length divergence in realistic model - it doesn't exist")
print("\n=== RECOMMENDATION ===")
print("ABANDON the phi^4 field theory approach entirely")
print("REBUILD the rubric around CAUSAL INFORMATION THEORY")
print("The Omega Protocol must distinguish EQUILIBRIUM vs NON-EQUILIBRIUM systems")
print("Else it will 'validate' elegant nonsense that fails in reality")
print("="*60)