# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import math

# Supplied audit data
phi_N = 0.78          # normalized Newtonian mode (I0 = 1)
phi_D = 0.35          # normalized Archive mode
I0 = 1.0

# Derived quantities
psi = math.log(phi_N / I0)                     # metric coupling invariant
print(f"psi = ln(phi_N/I0) = {psi:.6f}")

# Time derivatives (s^-1)
phi_N_dot = 2.1e3
phi_D_dot = 8.7e3
psi_dot = phi_N_dot / phi_N                    # dpsi/dt = phi_N_dot/phi_N
print(f"psi_dot = {psi_dot:.3e} s^-1")

# Stiffness invariant (s^-2)
xi_inv_sq = 4.2e6
xi = 1.0 / math.sqrt(xi_inv_sq)
print(f"xi = 1/sqrt(xi^-2) = {xi:.3e} s")

# Approximate second derivative of psi using characteristic time scale
psi_ddot = psi_dot / xi - psi_dot**2
print(f"psi_ddot ≈ psi_dot/xi - psi_dot^2 = {psi_ddot:.3e} s^-2")

# Source jerk (s^-3)
J_source = 1.5e12
print(f"J_source = {J_source:.3e} s^-3")

# Two-state entropy model
p_N = phi_N / (phi_N + phi_D)
p_D = phi_D / (phi_N + phi_D)
S_h = -p_N * math.log(p_N) - p_D * math.log(p_D)   # in nats; convert to bits if needed
S_h_bits = S_h / math.log(2)
print(f"p_N = {p_N:.3f}, p_D = {p_D:.3f}")
print(f"Shannon entropy S_h = {S_h:.3f} nats = {S_h_bits:.3f} bits")

# Entropy derivatives w.r.t. psi (approximate from two-state model)
# dS_h/dphi_N = -ln(p_N/p_D)
dS_h_dphiN = -math.log(p_N / p_D)
dS_h_dpsi = phi_N * dS_h_dphiN                     # chain rule: dS_h/dpsi = (dS_h/dphi_N)*(dphi_N/dpsi) ; dphi_N/dpsi = phi_N
# second derivative: d2S_h/dphiN^2 = -1/(p_N) - 1/(p_D) (derived from derivative of -ln(p_N/p_D))
d2S_h_dphiN2 = -(1.0/p_N + 1.0/p_D)
d2S_h_dpsi2 = (phi_N**2) * d2S_h_dphiN2 + phi_N * dS_h_dphiN   # includes term from derivative of phi_N factor
print(f"dS_h/dpsi ≈ {dS_h_dpsi:.6f}")
print(f"d2S_h/dpsi2 ≈ {d2S_h_dpsi2:.6f}")

# Dominant jerk term from psi contribution: 2 * (d2S_h/dpsi2) * psi_dot * psi_ddot
J_psi = 2.0 * d2S_h_dpsi2 * psi_dot * psi_ddot
print(f"J_psi (dominant psi term) = {J_psi:.3e} s^-3")

# Total jerk (psi term + source)
J_total = J_psi + J_source
print(f"Total informational jerk J_I ≈ {J_total:.3e} s^-3")

# Fluctuation assumption (±20%)
sigma_J = 0.2 * abs(J_total)
sigma_J_sq = sigma_J**2
print(f"sigma_J (20% fluctuation) = {sigma_J:.3e} s^-3")
print(f"sigma_J^2 = {sigma_J_sq:.3e} s^-6")

# Threshold calculation
lam = 1.0e10          # s^-2
g_D = 0.1
# Shredding boundary potential factor
V_shred_factor = (math.exp(2*psi) - 1.0)**2
Theta = (lam * I0**4 / 9.0) * V_shred_factor * (1.0 + (3.0 * g_D**2) / (4.0 * math.pi) * math.exp(-2.0*psi))
print(f"Threshold Theta(psi) = {Theta:.3e} s^-6")

# Stability check
stable = sigma_J_sq < Theta
print(f"Stability condition sigma_J^2 < Theta ? {stable}")
if not stable:
    print("Result: System is unstable (shredding imminent).")
else:
    print("Result: System is stable.")

# Informational Freeze check: 3*phi_N^2 + phi_D^2 vs I0^2
freeze_lhs = 3.0 * phi_N**2 + phi_D**2
print(f"Informational Freeze LHS 3*phi_N^2 + phi_D^2 = {freeze_lhs:.6f}")
print(f"I0^2 = {I0**2:.6f}")
if freeze_lhs >= I0**2:
    print("System is at or beyond the Informational Freeze boundary.")
else:
    print("System is away from the Informational Freeze boundary.")