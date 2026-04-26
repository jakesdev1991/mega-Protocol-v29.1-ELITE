# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import random

# ──────────── Simulation Parameters (dimensionless) ────────────
I0 = 1.0
lambda_ = 1e10  # not used directly; we work with derived scales
g_delta = 0.1
alpha = 0.5      # cross‑coupling strength via ψ
gamma_N = 2.1e3  # effective damping of Newtonian mode
gamma_D = 8.7e3  # effective damping of Archive mode
beta = 1e6       # coupling extracted from hardware telemetry
kappa = 1e4      # relaxation rate of ψ
dt = 1e-6        # 1 µs time step
T = 0.01         # 10 ms simulation window
steps = int(T / dt)

# ──────────── Initialize State ────────────
Phi_N = 0.78
Phi_D = 0.35
psi = np.log(Phi_N / I0)

# ──────────── Noise Model (simulates HSA counter sampling noise) ────────────
def sample_noise():
    return np.random.normal(0, 0.02)  # 2% relative noise

# ──────────── Entropy Estimator (two‑state histogram) ────────────
def compute_entropy(N, D):
    total = N + D
    if total <= 0:
        return 0.0
    pN = N / total
    pD = D / total
    # guard against log(0)
    if pN <= 0 or pD <= 0:
        return 0.0
    return -(pN * np.log(pN) + pD * np.log(pD))

# ──────────── Jerk via Finite Differences ────────────
def jerk_from_entropy(S_hist):
    # S_hist is a list of recent entropy values [S[t], S[t-1], S[t-2], S[t-3]]
    if len(S_hist) < 4:
        return 0.0
    return S_hist[0] - 3 * S_hist[1] + 3 * S_hist[2] - S_hist[3]

# ──────────── Storage for analysis ────────────
entropy_history = []
jerk_values = []

# ──────────── Time‑marching (Euler) ────────────
for i in range(steps):
    # ────── Compute ψ‑modulated coupling ──────
    # The coupling term appears in the dynamics of both modes
    coupling_N = beta * psi * Phi_D
    coupling_D = beta * psi * Phi_N

    # ────── ODEs (overdamped limit for simplicity) ──────
    dPhi_N = (-gamma_N * Phi_N + coupling_N) * dt + sample_noise()
    dPhi_D = (-gamma_D * Phi_D + coupling_D) * dt + sample_noise()
    dpsi = (-kappa * psi + (Phi_N - I0) / Phi_N) * dt  # relaxation + drive from mode mismatch

    Phi_N += dPhi_N
    Phi_D += dPhi_D
    psi += dpsi

    # ────── Entropy & Jerk ──────
    S = compute_entropy(Phi_N, Phi_D)
    entropy_history.append(S)
    if len(entropy_history) >= 4:
        J = jerk_from_entropy(entropy_history[-4:])
        jerk_values.append(J)

# ──────────── Compute “variance” of jerk (as in SERC) ────────────
jerk_array = np.array(jerk_values)
sigma_J2 = np.var(jerk_array) if jerk_array.size else 0.0

# ──────────── Compute SERC threshold Θ ────────────
Theta = (lambda_ * I0**2) / (4 * np.pi) * (1 + (3 * g_delta**2) / (4 * np.pi))

# ──────────── Print results ────────────
print(f"Simulated jerk variance σ²_J : {sigma_J2:.6e}")
print(f"SERC threshold Θ             : {Theta:.6e}")
print(f"σ²_J >> Θ ? {sigma_J2 > Theta}  (SERC would declare UNSTABLE)")

# ──────────── Now repeat *without* ψ coupling (β=0) ────────────
beta = 0.0
Phi_N = 0.78
Phi_D = 0.35
psi = np.log(Phi_N / I0)
entropy_history.clear()
jerk_values.clear()

for i in range(steps):
    # No coupling
    dPhi_N = (-gamma_N * Phi_N) * dt + sample_noise()
    dPhi_D = (-gamma_D * Phi_D) * dt + sample_noise()
    dpsi = (-kappa * psi + (Phi_N - I0) / Phi_N) * dt

    Phi_N += dPhi_N
    Phi_D += dPhi_D
    psi += dpsi

    S = compute_entropy(Phi_N, Phi_D)
    entropy_history.append(S)
    if len(entropy_history) >= 4:
        J = jerk_from_entropy(entropy_history[-4:])
        jerk_values.append(J)

sigma_J2_no_psi = np.var(np.array(jerk_values)) if jerk_values else 0.0
print("\n--- Without ψ coupling (β=0) ---")
print(f"Jerk variance σ²_J : {sigma_J2_no_psi:.6e}")
print(f"σ²_J >> Θ ? {sigma_J2_no_psi > Theta}")

# ──────────── Demonstrate eigenvalue crossing near Shredding ────────────
def eigenvalues_of_linearised(psi_val, Phi_N_val, Phi_D_val):
    # Jacobian matrix from the linearised system above
    J = np.array([[-gamma_N, beta*psi_val, beta*Phi_D_val],
                  [beta*psi_val, -gamma_D, beta*Phi_N_val],
                  [1.0/Phi_N_val, 0.0, -kappa]])
    return np.linalg.eigvals(J)

# Example near the Shredding condition (Phi_N^2 + 3Phi_D^2 ≈ I0^2)
Phi_N_shred = np.sqrt(I0**2 - 3 * 0.35**2)
psi_shred = np.log(Phi_N_shred / I0)
eig = eigenvalues_of_linearised(psi_shred, Phi_N_shred, 0.35)
print("\n--- Eigenvalues near Shredding (ψ-coupling ON) ---")
print(eig)
print(f"Max real part = {np.max(eig.real):.2e} (instability if >0)")