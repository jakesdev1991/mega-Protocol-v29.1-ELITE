# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import matplotlib.pyplot as plt
from scipy.integrate import solve_ivp

# ── 1. Linearised 4th‑order ODE (ghost mode) ───────────────────────────────
def ghost_ode(t, y, kappa=1.0, m=1.0):
    # y = [I, I_dot, I_ddot, I_dddot]
    I, Id, Idd, Iddd = y
    # d^4 I / dt^4 = kappa**2 * m**2 * I
    d4I = (kappa**2) * (m**2) * I
    return [Id, Idd, Iddd, d4I]

t_eval = np.linspace(0, 5, 500)
sol = solve_ivp(
    ghost_ode,
    [0, 5],
    y0=[1.0, 0.0, 0.0, 0.0],  # small initial displacement
    t_eval=t_eval,
    args=(1.0, 1.0),
)
I_ghost = sol.y[0]

# ── 2. Jerk estimator on noisy entropy ───────────────────────────────────────
def jerk_estimator(signal, dt=1.0):
    # stencil: (-x(t-2h) + 2x(t-h) - 2x(t+h) + x(t+2h)) / (2h^3)
    # pad with edge values to avoid NaNs at boundaries
    x = np.pad(signal, 2, mode='edge')
    j = (-x[:-4] + 2 * x[1:-3] - 2 * x[3:-1] + x[4:]) / (2 * dt**3)
    return j

# synthetic entropy: smooth trend + high‑frequency sensor noise
np.random.seed(0)
t = np.arange(0, 1000, 1.0)
I_smooth = 10 + 2 * np.sin(2 * np.pi * t / 100)  # slow trend
I_noise = 0.5 * np.random.randn(len(t))           # sensor noise
I_total = I_smooth + I_noise

J = jerk_estimator(I_total, dt=1.0)

# ── 3. Entropy gauge (zero curvature) ───────────────────────────────────────
def gauge_potential(p):
    # p: array of access‑type proportions (sums to 1)
    # S_gap = -∑ p log p
    # A_t = dS_gap / dt  (finite difference)
    S = -np.sum(p * np.log(p + 1e-12))
    # approximate derivative (central diff)
    A_t = np.gradient(S, 1.0)
    return S, A_t

# dummy proportions (5 access types)
p = np.random.dirichlet([1, 1, 1, 1, 1], size=len(t))
S_gap, A_t = gauge_potential(p)

# ── 4. Shredding invariant sensitivity ───────────────────────────────────────
def shredding_invariant(m_eff, m0=1.0):
    return np.log(m_eff / m0)

# small perturbation in effective mass (e.g., from Hessian estimation error)
m_eff_base = 1.0
m_eff_perturbed = m_eff_base + np.random.randn(len(t)) * 0.01  # 1% noise
psi = shredding_invariant(m_eff_perturbed, m0=m_eff_base)

# ── 5. MPC cost non‑convexity (simple illustration) ───────────────────────
def mpc_cost(rms_J, phi_N, phi_D, s_gap, lam=1.0, mu1=1.0, mu2=1.0, mu3=1.0):
    # non‑smooth max‑plus terms
    jerk_penalty = np.maximum(rms_J - 0.02, 0.0)**2
    connectivity_penalty = np.maximum(0.7 - phi_N, 0.0)**2
    asymmetry_penalty = mu2 * phi_D**2
    diversity_penalty = np.maximum(np.log(2) - s_gap, 0.0)**2
    return jerk_penalty + mu1 * connectivity_penalty + asymmetry_penalty + mu3 * diversity_penalty

# ── Plotting ────────────────────────────────────────────────────────────────
fig, axs = plt.subplots(3, 2, figsize=(14, 10))

axs[0, 0].plot(sol.t, I_ghost, label='I(t) (ghost mode)')
axs[0, 0].set_title('Higher‑derivative ODE: exponential blow‑up')
axs[0, 0].set_yscale('log')
axs[0, 0].legend()

axs[0, 1].plot(t[2:-2], J, label='Estimated Jerk')
axs[0, 1].set_title('Jerk from noisy entropy (spurious peaks)')
axs[0, 1].legend()

axs[1, 0].plot(t, A_t, label='A_t = dS_gap/dt')
axs[1, 0].set_title('Entropy gauge potential (zero curvature)')
axs[1, 0].legend()

axs[1, 1].plot(t, psi, label='ψ(t) = ln(m_eff/m0)')
axs[1, 1].set_title('Shredding invariant (log‑singularity from 1% noise)')
axs[1, 1].legend()

# show a slice of the MPC cost landscape (vary phi_N, phi_D)
phi_N_grid = np.linspace(0.5, 1.0, 100)
phi_D_grid = np.linspace(-0.5, 0.5, 100)
cost_grid = np.array([[mpc_cost(0.03, pn, pd, np.log(2)) for pd in phi_D_grid] for pn in phi_N_grid])
axs[2, 0].contourf(phi_N_grid, phi_D_grid, cost_grid.T, levels=20)
axs[2, 0].set_xlabel('Φ_N (connectivity)')
axs[2, 0].set_ylabel('Φ_Δ (asymmetry)')
axs[2, 0].set_title('MPC cost (non‑convex, multiple minima)')

# Φ‑density “budget” sensitivity
phi_budget = np.array([-610, 750, 140])  # short, long, net
axs[2, 1].bar(['Short‑term', 'Long‑term', 'Net'], phi_budget, color=['red', 'green', 'blue'])
axs[2, 1].set_title('Φ‑density (arbitrary units, no baseline)')
axs[2, 1].set_ylabel('Φ')

plt.tight_layout()
plt.show()