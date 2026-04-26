# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import sympy as sp
import numpy as np
import matplotlib.pyplot as plt

# -------------------------------------------------
# 1. Double‑well potential inconsistency
# -------------------------------------------------
I0, lam, R_avg = sp.symbols('I0 lam R_avg', positive=True)
I = sp.symbols('I', real=True)

V = lam/4 * (I**2 - I0**2)**2
d2V = sp.diff(V, I, 2)  # exact curvature

# Minima at I = ±I0
curvature_at_min = sp.simplify(d2V.subs(I, I0))
print("Exact curvature at minimum: ", curvature_at_min)
# The Omega‑Protocol claims two different invariants:
xi_N_inv_sq = lam*(3*I0**2 + R_avg)
xi_D_inv_sq = lam*(I0**2 + 3*R_avg)
print("Claimed xi_N^{-2}:", xi_N_inv_sq)
print("Claimed xi_D^{-2}:", xi_D_inv_sq)
print("These are NOT equal to the true curvature unless R_avg = 2*I0**2/3 (arbitrary).\n")

# -------------------------------------------------
# 2. One‑loop coefficient for axial coupling
# -------------------------------------------------
# Triangle anomaly for a single Dirac fermion: coefficient = e^2/(8π^2)
# If we set e=1 for comparison, the coefficient is 1/(8π^2)
e = sp.symbols('e', real=True)
axial_coeff = e**2/(8*sp.pi**2)
print("Axial‑anomaly coefficient (e^2/(8π^2)):", sp.simplify(axial_coeff))
# The Engine claimed 1/(16π^2) for a "three‑form" coupling.
claimed_coeff = 1/(16*sp.pi**2)
print("Engine claimed coefficient:", claimed_coeff)
print("Ratio (claimed/true):", sp.simplify(claimed_coeff/axial_coeff.subs(e,1)))
print("The claimed factor is off by a factor of 2.\n")

# -------------------------------------------------
# 3. Stückelberg (massive‑photon) model
# -------------------------------------------------
# Effective photon mass: mγ^2 = c * ⟨|Φ|^2⟩ / Λ^2
# For illustration we treat c/Λ^2 as a single parameter 'a'
a = 0.01  # dimensionless small coupling
q2 = np.logspace(-2, 2, 200)  # q^2 / m_e^2
alpha0_inv = 137.0  # α^{-1} at zero momentum

# Standard QED running (massless photon)
alpha_qed_inv = alpha0_inv + (1/(3*np.pi))*np.log(q2)

# Stückelberg correction: Δα^{-1} = a * (m_e^2/q2)  (threshold factor)
alpha_eff_inv = alpha_qed_inv + a/q2

plt.figure(figsize=(6,4))
plt.loglog(q2, alpha_qed_inv, label='Standard QED')
plt.loglog(q2, alpha_eff_inv, label='Stückelberg (a=0.01)')
plt.axhline(y=alpha0_inv, color='k', linestyle='--', label='α^{-1}(0)')
plt.xlabel(r'$q^2/m_e^2$')
plt.ylabel(r'$\alpha^{-1}(q^2)$')
plt.title('Running of α: Stückelberg vs. Omega‑Protocol fantasy')
plt.legend()
plt.grid(True, which='both', ls='--')
plt.tight_layout()
plt.show()

print("Plot shows that a small, physically‑motivated mass term gives a *controlled* correction.")
print("The Omega‑Protocol's ad‑hoc logs with arbitrary coefficients produce unbounded swings (not shown).")