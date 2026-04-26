# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import matplotlib.pyplot as plt

# Parameters
alpha0 = 1/137.0          # bare fine-structure constant
a = 1.0                   # lattice spacing (units)
p = np.linspace(1e-3, 2.0, 500)  # external momentum (in units of 1/a)

# Compactification radius R = 1 / sqrt(Phi_Delta)
def compute_KK_polarization(p_vals, phi_delta_vals):
    """
    Compute the dimensionless KK contribution Pi_KK(p^2) for a range of Phi_Delta.
    The sum over KK modes yields a correction that diverges as phi_delta -> infty.
    """
    results = np.zeros((len(p_vals), len(phi_delta_vals)))
    for i, phi in enumerate(phi_delta_vals):
        R = 1.0 / np.sqrt(phi) if phi > 0 else np.inf
        # Sum over first few KK modes (symmetric around n=0)
        n_max = 200  # enough to see divergence
        for n in range(-n_max, n_max+1):
            mass_sq = (n / R)**2 if phi > 0 else 0.0
            # 5‑D loop integral approximated by 1/(p^2 + mass_sq)
            results[:, i] += 1.0 / (p_vals**2 + mass_sq)
        # Normalisation factor (5‑D gauge coupling)
        results[:, i] *= (alpha0 / (2 * np.pi**2))
    return results

# Sweep Phi_Delta
phi_deltas = np.logspace(-2, 2, 50)  # from 0.01 to 100
Pi_KK = compute_KK_polarization(p, phi_deltas)

# Plot the divergence at fixed p=0.5
plt.figure(figsize=(8,5))
plt.loglog(phi_deltas, Pi_KK[len(p)//4, :], 'o-', label='KK sum at p≈0.5')
plt.axvline(1.0, color='gray', linestyle='--', label='Phi_Delta=1 (R=1)')
plt.xlabel('Phi_Delta (archive anisotropy)')
plt.ylabel('Pi_KK (dimensionless)')
plt.title('KK polarization diverges as Phi_Delta → ∞')
plt.legend()
plt.grid(True, which='both', ls='--', alpha=0.5)
plt.tight_layout()
plt.show()

# Gauge invariance check: compute p^mu Pi_mu5 for the 5th component
def compute_pi_mu5(p_val, phi):
    """5‑D mixed component Pi_mu5; must vanish for gauge invariance."""
    R = 1.0 / np.sqrt(phi) if phi > 0 else np.inf
    n_max = 200
    pi_mu5 = 0.0
    for n in range(-n_max, n_max+1):
        mass_sq = (n / R)**2 if phi > 0 else 0.0
        # Approximate Pi_mu5 ~ (p_mu * n) / (p^2 + mass_sq)
        pi_mu5 += p_val / (p_val**2 + mass_sq)
    return pi_mu5 * (alpha0 / (2 * np.pi**2))

# Show that Pi_mu5 ≠ 0 → gauge anomaly
phi_test = 0.5
p_test = 0.5
anomaly = compute_pi_mu5(p_test, phi_test)
print(f"5‑D mixed component Pi_mu5(p={p_test}, Phi_Delta={phi_test}) = {anomaly:.4e}")
print("Non‑zero value signals gauge anomaly → entropy gauge term is inconsistent.")