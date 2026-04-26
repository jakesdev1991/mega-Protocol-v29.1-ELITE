# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import matplotlib.pyplot as plt

# --- Omega Protocol RG Flow Simulator ---
# Expose the fragility of the "Archive" mode dynamics.

def omega_flow(state, lnq, eta_N=0.1, eta_D=0.05, kappa=0.01, I0=1.0):
    """Target's RG equations. Returns derivatives [dPhi_N, dPhi_Delta]."""
    Phi_N, Phi_Delta = state
    # The "physics" hinges on these arbitrary polynomial terms.
    dPhi_N = eta_N * Phi_N * (1 - Phi_N**2 / I0**2) - kappa * Phi_Delta**2
    dPhi_Delta = eta_D * Phi_Delta * (1 - Phi_Delta**2 / I0**2) + kappa * Phi_N * Phi_Delta
    return [dPhi_N, dPhi_Delta]

def integrate_flow(initial_state, lnq_range, params):
    """Simple RK4 integration to show trajectory."""
    state = np.array(initial_state, dtype=float)
    trajectory = [state.copy()]
    h = lnq_range[1] - lnq_range[0]
    for lnq in lnq_range[:-1]:
        k1 = np.array(omega_flow(state, lnq, **params))
        k2 = np.array(omega_flow(state + h*k1/2, lnq + h/2, **params))
        k3 = np.array(omega_flow(state + h*k2/2, lnq + h/2, **params))
        k4 = np.array(omega_flow(state + h*k3, lnq + h, **params))
        state += (h/6) * (k1 + 2*k2 + 2*k3 + k4)
        trajectory.append(state.copy())
    return np.array(trajectory)

# Parameter space: "Shredding" vs "Freeze" is a tuning knob away.
base_params = {"eta_N": 0.1, "eta_D": 0.05, "kappa": 0.01, "I0": 1.0}
sensitive_params = {"eta_N": 0.1, "eta_D": 0.05, "kappa": 0.15, "I0": 1.0} # Slight tweak

lnq = np.linspace(0, 10, 500)
initial = [0.2, 0.1] # "Small fluctuations"

traj_base = integrate_flow(initial, lnq, base_params)
traj_sens = integrate_flow(initial, lnq, sensitive_params)

# --- Visualization of Theoretical Collapse ---
fig, axs = plt.subplots(2, 2, figsize=(12, 8))
fig.suptitle("Archive Mode Instability: A House of Cards", fontsize=16, fontweight='bold')

# Plot 1: Amplitude Death
axs[0, 0].plot(lnq, traj_base[:, 0], 'b-', label='Φ_N (Base)')
axs[0, 0].plot(lnq, traj_base[:, 1], 'r-', label='Φ_Δ (Base)')
axs[0, 0].plot(lnq, traj_sens[:, 0], 'b--', label='Φ_N (Tuned)')
axs[0, 0].plot(lnq, traj_sens[:, 1], 'r--', label='Φ_Δ (Tuned)')
axs[0, 0].set_title("Mode Evolution: Tuning κ → Shredding/Freeze")
axs[0, 0].set_xlabel("ln(q)")
axs[0, 0].set_ylabel("Amplitude")
axs[0, 0].legend()
axs[0, 0].grid(True, alpha=0.3)

# Plot 2: The "Physical" Ratio Explodes
ratio_base = traj_base[:, 1] / np.maximum(traj_base[:, 0], 1e-6)
ratio_sens = traj_sens[:, 1] / np.maximum(traj_sens[:, 0], 1e-6)
axs[0, 1].plot(lnq, ratio_base, 'g-', label='κ=0.01')
axs[0, 1].plot(lnq, ratio_sens, 'm-', label='κ=0.15')
axs[0, 1].set_title("Φ_Δ/Φ_N Ratio: Non-Predictive Chaos")
axs[0, 1].set_xlabel("ln(q)")
axs[0, 1].set_ylabel("Ratio (Controls α_fs Correction)")
axs[0, 1].legend()
axs[0, 1].grid(True, alpha=0.3)
axs[0, 1].set_yscale('symlog', linthresh=1e-3)

# Plot 3: ψ-Arbitrariness on α_fs Running
alpha0 = 1/137.036
ln_qsq = lnq
alpha_standard = alpha0 / (1 - (alpha0/(3*np.pi)) * ln_qsq)

# Omega "correction" is just a linear shift in slope.
psi_values = [-0.5, 0.0, 0.5]
for psi in psi_values:
    Pi_omega = (alpha0/(3*np.pi)) * ln_qsq + (alpha0/(2*np.pi)) * psi * ln_qsq
    alpha_omega = alpha0 / (1 - alpha0 * Pi_omega)
    axs[1, 0].plot(lnq, alpha_omega, label=f'ψ={psi}')
axs[1, 0].plot(lnq, alpha_standard, 'k--', lw=2, label='Standard QED')
axs[1, 0].set_title("α_fs Running: ψ is a Free Parameter, Not a Prediction")
axs[1, 0].set_xlabel("ln(q²/me²)")
axs[1, 0].set_ylabel("α_fs(q²)")
axs[1, 0].legend()
axs[1, 0].grid(True, alpha=0.3)

# Plot 4: Phase Space Trajectory ( reveals fixed point illusion)
axs[1, 1].plot(traj_base[:, 0], traj_base[:, 1], 'b-', label='Base Flow')
axs[1, 1].plot(traj_sens[:, 0], traj_sens[:, 1], 'r-', label='Tuned Flow')
axs[1, 1].scatter(initial[0], initial[1], s=100, c='black', marker='x', label='Initial State')
axs[1, 1].set_title("Phase Space: Flow to Nowhere (No Universal Attractor)")
axs[1, 1].set_xlabel("Φ_N")
axs[1, 1].set_ylabel("Φ_Δ")
axs[1, 1].legend()
axs[1, 1].grid(True, alpha=0.3)

plt.tight_layout()
plt.show()

# --- Anomaly Summary Printout ---
print("="*60)
print("OMEGA PROTOCOL DECONSTRUCTION RESULTS:")
print("="*60)
print(f"Base κ=0.01: Final Ratio Φ_Δ/Φ_N = {ratio_base[-1]:.3e}")
print(f"Tuned κ=0.15: Final Ratio Φ_Δ/Φ_N = {ratio_sens[-1]:.3e}")
print(f"Ratio Volatility: {np.abs(ratio_sens[-1] - ratio_base[-1]):.3e} (Non-Physical!)")
print("\nConclusion: The 'Archive' is a purely numerical artifact.")
print("Its 'predictions' are arbitrary functions of unobservable internal parameters.")
print("Shredding Event = Numerical Divergence. Informational Freeze = Trivial Fixed Point.")
print("="*60)