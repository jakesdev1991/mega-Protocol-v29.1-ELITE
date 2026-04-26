# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import math

# ------------------ SUPPLIED DATA ------------------
I0 = 1.0
phi_N = 0.78
phi_D = 0.35
psi = math.log(phi_N / I0)                     # ln(Phi_N/I0)
dot_phi_N = 2.1e3                              # s^-1
dot_phi_D = 8.7e3                              # s^-1
xi_inv2 = 4.2e6                                # s^-2
J_source = 1.5e12                              # s^-3
lam = 1.0e10                                   # s^-2 (assumed)
g_D = 0.1                                      # dimensionless

# ------------------ HELPERS ------------------
def shannon_entropy(p):
    return -sum(pi * math.log(pi) for pi in p if pi > 0)

# probabilities from two‑state model
p_N = phi_N / (phi_N + phi_D)
p_D = phi_D / (phi_N + phi_D)
S_h = shannon_entropy([p_N, p_D])

# derivatives of S_h w.r.t. phi_N (analytic for two‑state)
# dS/dphi_N = -ln(p_N/p_D)
dS_dphiN = -math.log(p_N / p_D)
# d2S/dphiN^2 = -(1/phi_N + 1/phi_D)
d2S_dphiN2 = -(1/phi_N + 1/phi_D)

# chain rule: dS/dpsi = (dS/dphiN)*(dphiN/dpsi) = dS_dphiN * phi_N
dS_dpsi = dS_dphiN * phi_N
# d2S/dpsi^2 = (d2S/dphiN^2)*phi_N^2 + (dS/dphiN)*phi_N
d2S_dpsi2 = d2S_dphiN2 * phi_N**2 + dS_dphiN * phi_N

# psi derivatives
dot_psi = dot_phi_N / phi_N
# approximate ddot_psi from stiffness time scale xi = 1/sqrt(xi_inv2)
xi = 1.0 / math.sqrt(xi_inv2)
ddot_psi = dot_psi / xi - dot_psi**2

# informational jerk dominant term: 2 * d2S/dpsi2 * dot_psi * ddot_psi
J_I_dom = 2.0 * d2S_dpsi2 * dot_psi * ddot_psi
J_I_total = J_I_dom + J_source

# fluctuation (20%)
sigma_J = 0.2 * abs(J_I_total)
sigma_J2 = sigma_J ** 2

# threshold Theta(psi)
# Phi_D^2 at shredding: (I0^2/3)*(1 - exp(2*psi))
PhiD2_shred = (I0**2 / 3.0) * (1.0 - math.exp(2.0 * psi))
V_shred = (lam / 4.0) * ((2.0/3.0) * I0**2 * (math.exp(2.0*psi) - 1.0))**2
Theta = V_shred * (1.0 + (3.0 * g_D**2) / (4.0 * math.pi) * math.exp(-2.0*psi))

# ------------------ OUTPUT ------------------
print(f"psi = {psi:.5f}")
print(f"S_h = {S_h:.5f} bits")
print(f"dS/dpsi = {dS_dpsi:.5f}")
print(f"d2S/dpsi2 = {d2S_dpsi2:.5f}")
print(f"dot_psi = {dot_psi:.3e} s^-1")
print(f"ddot_psi = {ddot_psi:.3e} s^-2")
print(f"J_I (dominant) = {J_I_dom:.3e} s^-3")
print(f"J_I (total)    = {J_I_total:.3e} s^-3")
print(f"sigma_J^2      = {sigma_J2:.3e} s^-6")
print(f"Theta(psi)     = {Theta:.3e} s^-6")
print(f"Stability? sigma_J^2 < Theta? {sigma_J2 < Theta}")