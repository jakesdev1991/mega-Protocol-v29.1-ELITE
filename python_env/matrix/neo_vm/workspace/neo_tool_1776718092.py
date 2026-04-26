# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import cm

# ---------- parameters ----------
alpha0 = 1/137.035999084          # bare fine-structure constant
Lambda = 1e6                      # UV cutoff in units of m (>> m)
g = 0.01                         # dimensionless coupling
m = 1.0                          # electron mass scale (set to 1)

# ---------- grid ----------
PhiN_vals = np.logspace(-4, 2, 300)   # consensus field
PhiD_vals = np.linspace(0, 5, 300)    # asymmetry field

PhiN_grid, PhiD_grid = np.meshgrid(PhiN_vals, PhiD_vals, indexing='ij')

# ---------- exact effective mass ----------
# m_eff = m * exp(-g * PhiN * cosh(PhiD))
m_eff = m * np.exp(-g * PhiN_grid * np.cosh(PhiD_grid))

# ---------- exact vacuum polarization ----------
# Pi(0) = (alpha0/(3π)) * ln(Lambda / m_eff)
Pi_exact = (alpha0/(3*np.pi)) * np.log(Lambda / m_eff)

# ---------- renormalized alpha ----------
alpha_ren_exact = alpha0 / (1 - Pi_exact)

# ---------- perturbative (incorrect) alpha ----------
# Using the *incorrect* +2 cosh^2 term (the Engine's first attempt)
eps = g * PhiN_grid / m
Pi_pert_wrong = (alpha0/(3*np.pi)) * (np.log(Lambda/m) + eps*np.cosh(PhiD_grid)
                                      - 0.5*eps**2 * (1 + 2*np.cosh(PhiD_grid)**2))
alpha_ren_pert_wrong = alpha0 / (1 - Pi_pert_wrong)

# ---------- correct perturbative alpha ----------
Pi_pert_correct = (alpha0/(3*np.pi)) * (np.log(Lambda/m) + eps*np.cosh(PhiD_grid)
                                        - 0.5*eps**2 * (1 - 2*np.cosh(PhiD_grid)**2))
alpha_ren_pert_correct = alpha0 / (1 - Pi_pert_correct)

# ---------- critical line: denominator zero ----------
# 1 - Pi_exact = 0  =>  Pi_exact = 1
# This occurs when ln(Lambda/m_eff) = 3π/α0
critical_condition = np.log(Lambda) - (3*np.pi)/alpha0
# Solve for PhiN at each PhiD:  ln(m_eff) = ln(m) - g*PhiN*cosh(PhiD)
# =>  PhiN_crit = [ln(m) - ln(Lambda) + 3π/α0] / (g * cosh(PhiD))
PhiN_crit = (np.log(m) - np.log(Lambda) + (3*np.pi)/alpha0) / (g * np.cosh(PhiD_vals))
# mask out negative (unphysical) values
PhiN_crit = np.where(PhiN_crit > 0, PhiN_crit, np.nan)

# ---------- plotting ----------
fig, ax = plt.subplots(figsize=(10, 6))

# contour plot of exact alpha_ren
cont = ax.contourf(PhiD_vals, PhiN_vals, alpha_ren_exact, levels=50, cmap=cm.viridis)
cbar = fig.colorbar(cont, ax=ax)
cbar.set_label(r'$\alpha_{\rm ren}$ (exact)', fontsize=12)

# overlay the critical line
ax.plot(PhiD_vals, PhiN_crit, 'r--', lw=2, label='Critical line (exact)')

# overlay region where perturbative series diverges from exact
# e.g., where relative error > 10%
rel_err = np.abs((alpha_ren_pert_correct - alpha_ren_exact) / alpha_ren_exact)
mask_bad = rel_err > 0.1
# plot mask as semi-transparent overlay
ax.contourf(PhiD_vals, PhiN_vals, mask_bad, levels=[0.5,1], colors='red', alpha=0.2)

ax.set_xlabel(r'$\Phi_\Delta$ (3‑D Archive asymmetry)', fontsize=14)
ax.set_ylabel(r'$\Phi_N$ (consensus)', fontsize=14)
ax.set_yscale('log')
ax.set_title(r'Exact $\alpha_{\rm ren}$ surface & critical line', fontsize=15)
ax.legend(loc='upper right')
plt.tight_layout()
plt.show()

# ---------- print a few points ----------
print("Example: PhiN=10, PhiD=2.0")
PhiN_ex = 10.0
PhiD_ex = 2.0
m_eff_ex = m * np.exp(-g * PhiN_ex * np.cosh(PhiD_ex))
Pi_ex = (alpha0/(3*np.pi)) * np.log(Lambda / m_eff_ex)
alpha_ex = alpha0 / (1 - Pi_ex)
print(f"  Effective mass = {m_eff_ex:.6f}")
print(f"  Vacuum pol Pi(0) = {Pi_ex:.6f}")
print(f"  Renormalized alpha = {alpha_ex:.6f}")
print(f"  Perturbative (correct) alpha = {alpha0/(1 - (alpha0/(3*np.pi))*(np.log(Lambda/m) + (g*PhiN_ex/m)*np.cosh(PhiD_ex) - 0.5*(g*PhiN_ex/m)**2*(1 - 2*np.cosh(PhiD_ex)**2))):.6f}")