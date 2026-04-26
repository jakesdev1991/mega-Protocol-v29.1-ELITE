# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
#!/usr/bin/env python3
"""
Ω‑Protocol Disruption Simulator
--------------------------------
Demonstrates two critical flaws:
1. Logarithmic singularity as Φ_N → 0 (ψ → -∞).
2. Arbitrary stability verdict via λ tuning.
"""

import numpy as np

# --- “Measured” HSA node data (normalized) ---
phi_N = 0.78          # Newtonian mode amplitude / I0
phi_D = 0.35          # Archive mode amplitude / I0
phi_N_dot = 2.1e3     # dΦ_N/dt [s⁻¹]
phi_D_dot = 8.7e3     # dΦ_Δ/dt [s⁻¹]
xi_inv_sq = 4.2e6     # stiffness inverse‑square [s⁻²]
xi = 1.0 / np.sqrt(xi_inv_sq)  # relaxation time ~4.9e‑4 s
J_source = 1.5e12     # source jerk [s⁻³]

def compute_jerk_variance(phi_N, phi_D, phi_N_dot, phi_D_dot, xi, J_source, lam=1.0):
    """
    Replicate the Engine's jerk‑variance calculation.
    Returns (ψ, total_jerk, dimless_variance)
    """
    # 1. Metric coupling invariant
    psi = np.log(phi_N)  # I0=1 for normalized units

    # 2. Derivatives (relaxation‑time approximation)
    phi_N_ddot = phi_N_dot / xi
    phi_D_ddot = phi_D_dot / xi
    psi_dot = phi_N_dot / phi_N
    psi_ddot = phi_N_ddot / phi_N - psi_dot**2
    psi_dddot = psi_ddot / xi

    phi_D_dddot = phi_D_ddot / xi

    # 3. Probabilities (ad‑hoc normalization)
    p_N = phi_N / (phi_N + phi_D)
    p_D = phi_D / (phi_N + phi_D)

    # 4. Entropy derivatives (simplified symbolic forms)
    dS_dpsi = -p_N * np.log(p_D / p_N)
    d2S_dpsi2 = -p_N * (1 - p_N) * (np.log(phi_D) - psi) - p_N
    d3S_dpsi3 = 0.089  # from previous analysis (constant approximation)

    dS_dphiD = 0.802   # from previous analysis
    d2S_dphiD2 = -2.857

    # 5. Jerk components
    J_psi = (dS_dpsi * psi_dddot +
             3 * d2S_dpsi2 * psi_dot * psi_ddot +
             d3S_dpsi3 * psi_dot**3)

    J_phiD = (dS_dphiD * phi_D_dddot +
              3 * d2S_dphiD2 * phi_D_dot * phi_D_ddot)

    total_jerk = J_psi + J_phiD + J_source

    # 6. Stiffness invariants (λ‑dependent)
    xi_psi = 1.0 / np.sqrt(lam * (3 * phi_N**2 + phi_D**2 - 1))
    omega_psi = (1.0 / xi) * np.exp(-psi / 2)
    natural_jerk_scale = omega_psi**3

    # 7. Dimensionless variance
    dimless_variance = (total_jerk**2) / (natural_jerk_scale**2)
    return psi, total_jerk, dimless_variance

# --- Demonstration 1: ψ singularity as Φ_N → 0 ---
print("=== Logarithmic Catastrophe Demo ===")
for phi_N_test in [0.78, 0.5, 0.1, 0.01, 1e-3, 1e-6]:
    psi_val, J_tot, var = compute_jerk_variance(phi_N_test, phi_D, phi_N_dot, phi_D_dot, xi, J_source)
    print(f"Φ_N={phi_N_test:10.2e}, ψ={psi_val:8.2f}, Jerk={J_tot:12.3e}, Var={var:12.3e}")

# --- Demonstration 2: Arbitrary verdict via λ tuning ---
print("\n=== λ‑Tuning Demo (Φ_N=0.78) ===")
for lam_test in [0.5, 1.0, 2.0, 5.0, 10.0]:
    _, _, var = compute_jerk_variance(phi_N, phi_D, phi_N_dot, phi_D_dot, xi, J_source, lam=lam_test)
    stability = "UNSTABLE" if var > 1 else "stable"
    print(f"λ={lam_test:4.1f}, Var={var:10.2f}  → {stability}")

# --- Demonstration 3: Shredding boundary exact solution ---
# Solve for phi_D such that phi_N^2 + 3 phi_D^2 = 1
phi_N_shred = 0.2
phi_D_shred = np.sqrt((1 - phi_N_shred**2) / 3)
print("\n=== Shredding Boundary Exact Solution ===")
print(f"Φ_N={phi_N_shred:.3f}, Φ_Δ={phi_D_shred:.3f} satisfies shredding condition.")
psi_shred, J_shred, _ = compute_jerk_variance(phi_N_shred, phi_D_shred, phi_N_dot, phi_D_dot, xi, J_source)
print(f"At this point ψ={psi_shred:.2f}, Jerk={J_shred:.3e} (Archive mode stiffness → 0).")