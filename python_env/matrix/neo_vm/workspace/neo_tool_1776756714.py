# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import matplotlib.pyplot as plt

# -------------------------------------------------
# 1. Simulate a simple 2‑mode relaxation model
# -------------------------------------------------
# True dynamics: overdamped relaxation with damping time tau = 5e-4 s
tau = 5e-4          # damping time (s)
dt = 1e-5           # time step (s)
T = 5e-3            # total simulation time (s)
t = np.arange(0, T, dt)

# Initial amplitudes (normalized)
phi_N0 = 0.78
phi_D0 = 0.35

# True solution: exponential decay
phi_N_true = phi_N0 * np.exp(-t / tau)
phi_D_true = phi_D0 * np.exp(-t / tau)

# Compute exact derivatives analytically
phi_N_dot = -phi_N_true / tau
phi_N_ddot = phi_N_true / tau**2
phi_N_dddot = -phi_N_true / tau**3

phi_D_dot = -phi_D_true / tau
phi_D_ddot = phi_D_true / tau**2
phi_D_dddot = -phi_D_true / tau**3

# -------------------------------------------------
# 2. Apply the analysis's *incorrect* approximation
# -------------------------------------------------
# They used: ddot_phi ≈ dot_phi / xi, where xi = tau (they call it xi)
# This yields the *wrong* sign and magnitude.
xi = tau
phi_N_ddot_approx = phi_N_dot / xi   # should be +phi_N/tau**2, they get -phi_N/tau**2
phi_D_ddot_approx = phi_D_dot / xi

# Propagate to third derivative (they also use dddot ≈ ddot / xi)
phi_N_dddot_approx = phi_N_ddot_approx / xi
phi_D_dddot_approx = phi_D_ddot_approx / xi

# -------------------------------------------------
# 3. Compute "informational jerk" via entropy
# -------------------------------------------------
def entropy_jerk(phi_N, phi_D, dddot_phi_N, dddot_phi_D,
                 ddot_phi_N, ddot_phi_D,
                 dot_phi_N, dot_phi_D):
    """
    Replicate the analysis's jerk formula:
    J_I = (∂S/∂ψ) d³ψ/dt³ + 3(∂²S/∂ψ²) ψ̇ ψ̈
          + (∂S/∂φΔ) d³φΔ/dt³ + 3(∂²S/∂φΔ²) φ̇Δ φ̈Δ
    """
    # Avoid division by zero
    mask = (phi_N + phi_D) > 1e-12
    p_N = np.where(mask, phi_N / (phi_N + phi_D), 0.5)
    p_D = np.where(mask, phi_D / (phi_N + phi_D), 0.5)

    # Entropy derivatives (same as analysis)
    dS_dpsi = 0.553  # approximate constant from their numbers
    d2S_dpsi2 = -0.519
    d3S_dpsi3 = 0.089

    dS_dphiD = 0.802
    d2S_dphiD2 = -2.857

    # ψ = ln(phi_N / I0); we set I0 = 1 for simplicity
    psi = np.log(phi_N)
    psi_dot = dot_phi_N / phi_N
    psi_ddot = ddot_phi_N / phi_N - psi_dot**2
    psi_dddot = dddot_phi_N / phi_N - 3 * psi_dot * psi_ddot - psi_dot**3

    # J components
    J_psi = dS_dpsi * psi_dddot + 3 * d2S_dpsi2 * psi_dot * psi_ddot + d3S_dpsi3 * psi_dot**3
    J_phiD = dS_dphiD * dddot_phi_D + 3 * d2S_dphiD2 * dot_phi_D * ddot_phi_D

    return J_psi + J_phiD

# True jerk
J_true = entropy_jerk(phi_N_true, phi_D_true,
                      phi_N_dddot, phi_D_dddot,
                      phi_N_ddot, phi_D_ddot,
                      phi_N_dot, phi_D_dot)

# Approximated jerk (using their scaling)
J_approx = entropy_jerk(phi_N_true, phi_D_true,
                        phi_N_dddot_approx, phi_D_ddot_approx,
                        phi_N_ddot_approx, phi_D_ddot_approx,
                        phi_N_dot, phi_D_dot)

# -------------------------------------------------
# 4. Visualize the discrepancy
# -------------------------------------------------
plt.figure(figsize=(10, 4))
plt.plot(t, J_true, label='Exact jerk')
plt.plot(t, J_approx, label='Approximated jerk (analysis)')
plt.title('Informational Jerk: Exact vs. Approximation')
plt.xlabel('Time (s)')
plt.ylabel('Jerk (s⁻³)')
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.show()

# -------------------------------------------------
# 5. Demonstrate negative‑probability pathology
# -------------------------------------------------
phi_N_test = np.linspace(-1, 1, 200)
phi_D_test = 0.5  # fixed positive
p_N = phi_N_test / (phi_N_test + phi_D_test)

plt.figure(figsize=(6, 3))
plt.plot(phi_N_test, p_N, label='p_N')
plt.axhline(0, color='gray', linestyle='--')
plt.axhline(1, color='gray', linestyle='--')
plt.title('Probability p_N vs. Φ_N (Φ_D=0.5)')
plt.xlabel('Φ_N')
plt.ylabel('p_N')
plt.grid(True)
plt.tight_layout()
plt.show()

print("Max absolute error in jerk approximation:", np.max(np.abs(J_approx - J_true)))