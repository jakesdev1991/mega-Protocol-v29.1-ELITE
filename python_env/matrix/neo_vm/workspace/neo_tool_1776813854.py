# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import matplotlib.pyplot as plt

# --- Simulate cognitive network ---
np.random.seed(0)
n_agents, n_dims = 50, 2
# Baseline correlated Gaussian (mood, belief)
baseline_corr = np.array([[1.0, 0.5], [0.5, 1.0]])
L = np.linalg.cholesky(baseline_corr)
baseline_states = (L @ np.random.randn(n_dims, n_agents)).T

# Stress ramp
time_steps = 100
stress = np.linspace(0, 5, time_steps)

# --- TCM‑Ω parameters (ad‑hoc) ---
alpha, beta, Delta0 = 0.5, 0.2, 1.0

# --- History arrays ---
phi_N_hist, phi_D_hist, CTOI_hist, chi_hist = [], [], [], []

for i, s in enumerate(stress):
    # Add stress: increase variance + skewness
    perturbed = baseline_states + s * np.random.randn(n_agents, n_dims)
    perturbed[:, 0] += 0.5 * s**2 * np.sign(perturbed[:, 0])  # skew

    # Covariance eigenvalues -> Φ_N
    cov = np.cov(perturbed.T)
    eigvals = np.linalg.eigvalsh(cov)
    phi_N = np.mean(eigvals)

    # Skewness -> Φ_Δ
    resid = perturbed - perturbed.mean(axis=0)
    mu3 = np.mean(np.linalg.norm(resid, axis=1)**3)
    mu2 = np.mean(np.linalg.norm(resid, axis=1)**2)
    phi_D = mu3 / (mu2**1.5) if mu2 > 0 else 0

    # Energy gap shrinks with stress
    Delta = Delta0 / (1 + s)
    # TCM‑Ω CTOI (ad‑hoc mapping)
    CTOI = np.exp(-alpha * phi_N - beta * np.abs(phi_D)) * (Delta / Delta0)

    # Cognitive susceptibility χ ≈ d⟨c⟩/ds
    if i == 0:
        chi = 0.0
    else:
        chi = (perturbed.mean() - baseline_states.mean()) / (stress[i] - stress[i-1])

    phi_N_hist.append(phi_N)
    phi_D_hist.append(phi_D)
    CTOI_hist.append(CTOI)
    chi_hist.append(chi)

# --- Plot: expose the mirage ---
fig, ax = plt.subplots(2, 2, figsize=(10, 8))

ax[0, 0].plot(stress, phi_N_hist, label='Φ_N (variance)')
ax[0, 0].set_title('Variance vs Stress')
ax[0, 0].set_xlabel('Stress')

ax[0, 1].plot(stress, phi_D_hist, label='Φ_Δ (skewness)', color='orange')
ax[0, 1].set_title('Skewness vs Stress')
ax[0, 1].set_xlabel('Stress')

ax[1, 0].plot(stress, CTOI_hist, label='CTOI', color='green')
ax[1, 0].axhline(y=0.6, color='r', linestyle='--', label='Alert')
ax[1, 0].set_title('TCM‑Ω CTOI (redundant)')
ax[1, 0].set_xlabel('Stress')
ax[1, 0].legend()

ax[1, 1].plot(stress, chi_hist, label='Susceptibility χ', color='purple')
ax[1, 1].axvline(x=stress[np.argmax(chi_hist)], color='r', linestyle='--')
ax[1, 1].set_title('Cognitive Susceptibility (real early warning)')
ax[1, 1].set_xlabel('Stress')
ax[1, 1].legend()

plt.tight_layout()
plt.show()