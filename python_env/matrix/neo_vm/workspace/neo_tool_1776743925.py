# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit

# ──────────────────────────────────────────────────────────────────────────────
# 1. Binary (percolation) model: each site is either capped (1) or uncapped (0)
# ──────────────────────────────────────────────────────────────────────────────
def simulate_binary(N=200, k_on=0.2, k_off=0.1, T=500, dt=0.1):
    """
    Gillespie-style simulation of N two-state capping sites.
    Returns final configuration and time series of capped fraction.
    """
    # Each site: 1 = capped, 0 = uncapped
    state = np.ones(N, dtype=int)  # start fully capped
    # Precompute rates
    rates = np.empty((N, 2))  # column 0: uncapping rate, column 1: recapping rate
    rates[:, 0] = k_off
    rates[:, 1] = k_on
    # Time series
    frac_capped = []
    t = 0.0
    while t < T:
        # total rate for each site
        total_rates = rates[np.arange(N), 1 - state]  # if capped (1), use uncapping rate (col 0)
        sum_rate = total_rates.sum()
        if sum_rate == 0:
            break
        # Gillespie step
        tau = -np.log(np.random.rand()) / sum_rate
        t += tau
        # choose which site fires
        r = np.random.rand() * sum_rate
        cum = 0.0
        for i in range(N):
            cum += total_rates[i]
            if cum >= r:
                # flip the state
                state[i] = 1 - state[i]
                break
        frac_capped.append(state.mean())
    return state, np.array(frac_capped)

# ──────────────────────────────────────────────────────────────────────────────
# 2. Field‑theory inspired continuous model (double‑well gradient flow)
# ──────────────────────────────────────────────────────────────────────────────
def simulate_field(N=200, k_on=0.2, k_off=0.1, D=0.5, T=500, dt=0.01):
    """
    Semi‑implicit Euler on the continuum field E_i ∈ [0,1] with
    dE_i/dt = k_on*(1-E_i) - k_off*E_i + D*(E_{i+1}+E_{i-1}-2E_i)
    """
    E = np.ones(N)  # fully capped
    # Double‑well parameters
    E0 = np.sqrt(k_on / (k_on + k_off))  # naive equilibrium
    lam = 1.0
    # Time series
    mean_E = []
    for _ in range(int(T/dt)):
        # reaction part (soft‑clipped to [0,1])
        react = k_on * (1 - E) - k_off * E
        # diffusion part (periodic BC)
        lap = np.roll(E, 1) + np.roll(E, -1) - 2 * E
        E += dt * (react + D * lap)
        # clip
        E = np.clip(E, 0, 1)
        mean_E.append(E.mean())
    return E, np.array(mean_E)

# ──────────────────────────────────────────────────────────────────────────────
# 3. Correlation length extraction (exponential fit)
# ──────────────────────────────────────────────────────────────────────────────
def correlation_length(config):
    """Fit C(r) ~ exp(-r/ξ) for a 1‑D periodic config."""
    N = len(config)
    # compute pair correlation
    r_vals = np.arange(N//2)
    C = np.zeros_like(r_vals, dtype=float)
    for r in r_vals:
        C[r] = np.mean(config * np.roll(config, r)) - config.mean()**2
    # avoid zeros for log fit
    mask = C > 0
    if mask.sum() < 3:
        return np.nan
    r_vals = r_vals[mask]
    logC = np.log(C[mask])
    # linear fit: logC = a - r/ξ
    p = np.polyfit(r_vals, logC, 1)
    xi = -1.0 / p[0]
    return xi

# ──────────────────────────────────────────────────────────────────────────────
# 4. Sweep k_off (increasing uncapping pressure)
# ──────────────────────────────────────────────────────────────────────────────
k_on = 0.2
k_off_sweep = np.linspace(0.05, 0.5, 20)
xi_binary = []
xi_field = []
fractions_binary = []
fractions_field = []

for k_off in k_off_sweep:
    # binary simulation
    state_bin, frac_bin = simulate_binary(N=200, k_on=k_on, k_off=k_off, T=200)
    xi_bin = correlation_length(state_bin)
    xi_binary.append(xi_bin)
    fractions_binary.append(state_bin.mean())
    
    # field simulation
    state_fld, frac_fld = simulate_field(N=200, k_on=k_on, k_off=k_off, D=0.5, T=200)
    xi_fld = correlation_length(state_fld)
    xi_field.append(xi_fld)
    fractions_field.append(state_fld.mean())

# ──────────────────────────────────────────────────────────────────────────────
# 5. Plot the failure: field theory predicts divergence, binary does not
# ──────────────────────────────────────────────────────────────────────────────
fig, ax = plt.subplots(2, 1, figsize=(8, 8))

# Top: correlation length
ax[0].plot(k_off_sweep, xi_binary, 'o-', label='Binary (percolation)', color='steelblue')
ax[0].plot(k_off_sweep, xi_field, 's-', label='Field‑theory (smooth)', color='crimson')
ax[0].set_xlabel('Uncapping rate k_off')
ax[0].set_ylabel('Correlation length ξ (sites)')
ax[0].set_title('Correlation length vs uncapping pressure')
ax[0].legend()
ax[0].grid(True)

# Bottom: capped fraction (order parameter)
ax[1].plot(k_off_sweep, fractions_binary, 'o-', label='Binary', color='steelblue')
ax[1].plot(k_off_sweep, fractions_field, 's-', label='Field‑theory', color='crimson')
ax[1].set_xlabel('Uncapping rate k_off')
ax[1].set_ylabel('Fraction capped')
ax[1].set_title('Order parameter (capped fraction)')
ax[1].legend()
ax[1].grid(True)

plt.tight_layout()
plt.savefig('cifo_disruption.png', dpi=150)
plt.show()

# ──────────────────────────────────────────────────────────────────────────────
# 6. Stiffness invariant from double‑well potential V(E)=λ/4 (E²-E₀²)²
#    Show that curvature becomes negative only at the barrier (E=0)
# ──────────────────────────────────────────────────────────────────────────────
def stiffness(E, lam=1.0, E0=0.7):
    """Second derivative of double‑well potential."""
    return lam * (3 * E**2 - E0**2)

E_grid = np.linspace(-0.5, 1.5, 400)
stiff = stiffness(E_grid, lam=1.0, E0=0.7)

fig, ax = plt.subplots()
ax.plot(E_grid, stiff, label='d²V/dE²')
ax.axhline(0, color='k', linestyle='--')
ax.axvline(0, color='gray', linestyle=':')
ax.axvline(E0, color='gray', linestyle=':')
ax.set_xlabel('E (capping efficiency)')
ax.set_ylabel('Curvature (stiffness)')
ax.set_title('Double‑well stiffness: negative only at barrier (unphysical)')
ax.legend()
ax.grid(True)
plt.savefig('cifo_stiffness.png', dpi=150)
plt.show()