# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import math

# supplied normalized modes (I0 = 1)
phi_n = 0.78
phi_d = 0.35
I0 = 1.0

# psi = ln(phi_n / I0)
psi = math.log(phi_n / I0)
print(f"psi = {psi:.6f}")

# shannon entropy from two state model
p_n = phi_n / (phi_n + phi_d)
p_d = 1.0 - p_n
S_h = -(p_n * math.log(p_n) if p_n > 0 else 0.0) - (p_d * math.log(p_d) if p_d > 0 else 0.0)
print(f"Shannon entropy S_h = {S_h:.6f} bits")

# derivatives of S_h w.r.t phi_n and phi_d (analytic for two state)
# dS_h/dphi_n = -log(p_n) - 1 + (phi_n/(phi_n+phi_d)) * (log(p_n) - log(p_d))
# simpler: dS_h/dphi_n = -log(p_n) + log(p_d) * (phi_d/(phi_n+phi_d))
# we compute numerically via finite difference for clarity
eps = 1e-6
def entropy(phi_n_var, phi_d_var):
    pn = phi_n_var / (phi_n_var + phi_d_var)
    pd = 1.0 - pn
    return -(pn * math.log(pn) if pn>0 else 0.0) - (pd * math.log(pd) if pd>0 else 0.0)
dS_dphi_n = (entropy(phi_n+eps, phi_d) - entropy(phi_n-eps, phi_d)) / (2*eps)
dS_dphi_d = (entropy(phi_n, phi_d+eps) - entropy(phi_n, phi_d-eps)) / (2*eps)
print(f"dS_h/dphi_n = {dS_dphi_n:.6f}")
print(f"dS_h/dphi_d = {dS_dphi_d:.6f}")

# dpsi/dt = (dphi_n/dt)/phi_n
dot_phi_n = 2.1e3
dot_phi_d = 8.7e3
dot_psi = dot_phi_n / phi_n
print(f"dot_psi = {dot_psi:.6f} s^-1")

# second derivative of psi using characteristic time xi from stiffness invariant
# xi^-2 = 4.2e6 s^-2 (given)
xi_inv_sq = 4.2e6
xi = 1.0 / math.sqrt(xi_inv_sq)
# approximate ddot_psi = dot_psi/xi - dot_psi^2 (as in engine)
ddot_psi = dot_psi/xi - dot_psi**2
print(f"xi = {xi:.6e} s")
print(f"ddot_psi = {ddot_psi:.6e} s^-2")

# second and third derivatives of S_h w.r.t psi (chain rule)
# dS_h/dpsi = (dS_h/dphi_n) * (dphi_n/dpsi) = (dS_h/dphi_n) * phi_n
dS_dpsi = dS_dphi_n * phi_n
# d2S_h/dpsi^2 = (d2S_h/dphi_n^2) * phi_n^2 + (dS_h/dphi_n) * phi_n
# compute d2S_h/dphi_n^2 via finite difference
def dS_dphi_n_val(phi_n_var):
    return (entropy(phi_n_var+eps, phi_d) - entropy(phi_n_var-eps, phi_d)) / (2*eps)
d2S_dphi_n2 = (dS_dphi_n_val(phi_n+eps) - dS_dphi_n_val(phi_n-eps)) / (2*eps)
d2S_dpsi2 = d2S_dphi_n2 * phi_n**2 + dS_dphi_n * phi_n
print(f"dS_h/dpsi = {dS_dpsi:.6f}")
print(f"d2S_h/dpsi^2 = {d2S_dpsi2:.6f}")

# dominant jerk term: d/dt[ d2S_h/dpsi^2 * dot_psi^2 ] ≈ 2 * d2S_h/dpsi^2 * dot_psi * ddot_psi
J_jerk = 2.0 * d2S_dpsi2 * dot_psi * ddot_psi
print(f"informational jerk from entropy term = {J_jerk:.6e} s^-3")

# source jerk contribution
J_source = 1.5e12
J_total = J_jerk + J_source
print(f"total informational jerk J_I = {J_total:.6e} s^-3")

# assume 20% fluctuation
sigma_J = 0.2 * abs(J_total)
sigma_J_sq = sigma_J**2
print(f"sigma_J = {sigma_J:.6e} s^-3")
print(f"sigma_J^2 = {sigma_J_sq:.6e} s^-6")

# threshold calculation
lam = 1e10  # s^-2
g_delta = 0.1
# theta(psi) = (lam * I0^4 / 9) * (exp(2*psi)-1)^2 * (1 + (3*g_delta^2/(4*pi))*exp(-2*psi))
theta = (lam * I0**4 / 9.0) * (math.exp(2*psi)-1.0)**2 * (1.0 + (3.0*g_delta**2/(4.0*math.pi))*math.exp(-2*psi))
print(f"threshold theta(psi) = {theta:.6e} s^-6")

# stability condition
stable = sigma_J_sq < theta
print(f"stability condition sigma_J^2 < theta ? {stable}")
if not stable:
    print("system is unstable according to the psi‑dependent threshold")
else:
    print("system is stable")