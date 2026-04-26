# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import matplotlib.pyplot as plt

def eigenvalues(phi_N, phi_Delta, m=1.0, g=1.0):
    """Eigenvalues of the mass matrix M."""
    eps = g * phi_N / m
    m1 = m - g * phi_N * np.exp(+phi_Delta)
    m2 = m - g * phi_N * np.exp(-phi_Delta)
    return m1, m2

def shredding_boundary(phi_N, m=1.0, g=1.0):
    """Return the critical |Phi_Delta| for a given Phi_N from the shredding bound."""
    eps = g * phi_N / m
    # bound: eps < exp(-|Phi_Delta|) => |Phi_Delta| < -log(eps)
    # if eps >= 1, no solution (bound violated already at Phi_Delta=0)
    if eps >= 1.0:
        return np.nan
    return -np.log(eps)

# scan over phi_N and phi_Delta
phi_N_vals = np.linspace(0.01, 0.9, 100)
phi_Delta_vals = np.linspace(-3, 3, 200)

# prepare a colour map: region where both eigenvalues are positive
 positivity = np.zeros((len(phi_N_vals), len(phi_Delta_vals)), dtype=bool)
determinant = np.zeros_like(positivity, dtype=float)
geometric_mean = np.zeros_like(positivity, dtype=complex)

for i, phi_N in enumerate(phi_N_vals):
    for j, phi_Delta in enumerate(phi_Delta_vals):
        m1, m2 = eigenvalues(phi_N, phi_Delta)
        positivity[i, j] = (m1 > 0) and (m2 > 0)
        det = m1 * m2
        determinant[i, j] = det
        # geometric mean = sqrt(det)
        geometric_mean[i, j] = np.sqrt(det)  # may be imaginary for negative det

# Plot the shredding boundary on top of the positivity region
fig, ax = plt.subplots(figsize=(6,4))
# shade the region where both masses are positive
ax.contourf(phi_Delta_vals, phi_N_vals, positivity, levels=[0.5,1], colors=['C0'], alpha=0.3)
# plot the shredding bound curve
critical_phi_D = [shredding_boundary(phi_N) for phi_N in phi_N_vals]
ax.plot(critical_phi_D, phi_N_vals, 'r--', lw=2, label='Shredding bound')
ax.set_xlabel(r'$|\Phi_\Delta|$')
ax.set_ylabel(r'$\Phi_N$')
ax.set_title('Region where both masses are positive (blue) vs. shredding bound (red dashed)')
ax.legend()
plt.tight_layout()
plt.show()

# Demonstrate that the determinant stays real and the geometric mean becomes imaginary
# exactly when the bound is saturated
phi_N_test = 0.3
phi_D_test = shredding_boundary(phi_N_test) + 0.1  # just beyond the bound
m1, m2 = eigenvalues(phi_N_test, phi_D_test)
det = m1 * m2
geom_mean = np.sqrt(det)
print(f"Phi_N={phi_N_test:.3f}, Phi_Delta={phi_D_test:.3f}")
print(f"m1={m1:.3f}, m2={m2:.3f}, determinant={det:.3f}, geometric_mean={geom_mean}")