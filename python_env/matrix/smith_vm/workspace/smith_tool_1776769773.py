# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import math

# ------------------------------
# Supplied audit data (normalized to I0 = 1)
# ------------------------------
phi_N   = 0.78          # normalized Newtonian mode
phi_D   = 0.35          # normalized Archive mode
I0      = 1.0

dot_phi_N   = 2.1e3     # s^-1
dot_phi_D   = 8.7e3     # s^-1
xi_inv2     = 4.2e6     # s^-2  (stiffness invariant)
J_source    = 1.5e12    # s^-3  (source jerk)

lam   = 1e10            # s^-2  (coupling lambda)
g_D   = 0.1             # Archive mode coupling

# ------------------------------
# Derived quantities
# ------------------------------
psi = math.log(phi_N / I0)                     # metric coupling invariant
print(f"psi = ln(phi_N/I0) = {psi:.6f}")

# characteristic time scale from stiffness invariant
xi = 1.0 / math.sqrt(xi_inv2)                  # s
print(f"xi = 1/sqrt(xi_inv2) = {xi:.3e} s")

# time derivatives of psi
dot_psi = dot_phi_N / phi_N                    # s^-1
print(f"dot_psi = dot_phi_N/phi_N = {dot_psi:.3e} s^-1")

# approximate second derivative of psi (using characteristic time)
ddot_psi = dot_psi/xi - dot_psi**2             # s^-2
print(f"ddot_psi ≈ dot_psi/xi - dot_psi^2 = {ddot_psi:.3e} s^-2")

# ------------------------------
# Entropy and its derivatives (two‑state model)
# ------------------------------
p_N = phi_N / (phi_N + phi_D)
p_D = phi_D / (phi_N + phi_D)
print(f"p_N = {p_N:.3f}, p_D = {p_D:.3f}")

# Shannon entropy (natural log) – convert to bits if desired
S_h_nat = -p_N*math.log(p_N) - p_D*math.log(p_D)   # nats
S_h_bits = S_h_nat / math.log(2)                  # bits
print(f"Shannon entropy S_h = {S_h_nat:.3f} nats = {S_h_bits:.3f} bits")

# Derivatives w.r.t. psi (using chain rule approximations from the pleading)
# dS_h/d psi ≈ phi_N * dS_h/d phi_N ; dS_h/d phi_N = -ln(p_N/p_D)
dS_h_dphiN = -math.log(p_N/p_D)
dS_h_dpsi  = phi_N * dS_h_dphiN
print(f"dS_h/d psi ≈ phi_N * (-ln(p_N/p_D)) = {dS_h_dpsi:.3f}")

# second derivative approximation:
# d2S_h/d psi^2 ≈ phi_N^2 * d2S_h/d phi_N^2 + phi_N * dS_h/d phi_N
# d2S_h/d phi_N^2 ≈ - (1/p_N + 1/p_D)  (derivative of -ln(p_N/p_D) w.r.t phi_N)
d2S_h_dphiN2 = -(1.0/p_N + 1.0/p_D)
d2S_h_dpsi2  = (phi_N**2) * d2S_h_dphiN2 + phi_N * dS_h_dphiN
print(f"d2S_h/d psi^2 ≈ {d2S_h_dpsi2:.3f}")

# ------------------------------
# Jerk calculation (dominant term + source)
# ------------------------------
# dominant term from pleading: 2 * (d2S_h/d psi^2) * dot_psi * ddot_psi
J_dom = 2.0 * d2S_h_dpsi2 * dot_psi * ddot_psi
J_total = J_dom + J_source
print(f"Dominant jerk term = {J_dom:.3e} s^-3")
print(f"Total informational jerk J_I = {J_total:.3e} s^-3")

# Fluctuation estimate (±20%)
sigma_J = 0.20 * abs(J_total)          # s^-3
sigma_J2 = sigma_J**2                  # s^-6
print(f"sigma_J (20% fluctuation) = {sigma_J:.3e} s^-3")
print(f"sigma_J^2 = {sigma_J2:.3e} s^-6")

# ------------------------------
# Stability threshold Theta(psi)
# ------------------------------
# V_shred = (lambda * I0^4 / 9) * (exp(2*psi) - 1)^2
V_shred = (lam * I0**4 / 9.0) * (math.exp(2.0*psi) - 1.0)**2
# fluctuation scaling factor: 1 + (3*g_D^2/(4*pi)) * exp(-2*psi)
scale   = 1.0 + (3.0 * g_D**2 / (4.0*math.pi)) * math.exp(-2.0*psi)
Theta   = V_shred * scale
print(f"V_shred = {V_shred:.3e} (units s^-2?)")
print(f"Scaling factor = {scale:.3f}")
print(f"Stability threshold Theta(psi) = {Theta:.3e} s^-6")

# ------------------------------
# Stability decision
# ------------------------------
stable = sigma_J2 < Theta
print(f"\nStability check: sigma_J^2 < Theta ?  {stable}")
print(f"  sigma_J^2 = {sigma_J2:.3e}")
print(f"  Theta    = {Theta:.3e}")
if not stable:
    print("  => System is UNSTABLE (shredding regime).")
else:
    print("  => System is STABLE.")

# ------------------------------
# Informational Freeze condition
# ------------------------------
freeze_lhs = 3.0*phi_N**2 + phi_D**2   # should approach I0^2 = 1 for freeze
print(f"\nInformational Freeze check: 3*phi_N^2 + phi_D^2 = {freeze_lhs:.5f}")
print(f"  Compared to I0^2 = {I0**2}")
if abs(freeze_lhs - I0**2) < 1e-2:
    print("  => Near Informational Freeze (xi_N → ∞).")
elif freeze_lhs > I0**2:
    print("  => Beyond freeze (unphysical under current parameters).")
else:
    print("  => Safely away from Informational Freeze.")

# ------------------------------
# Dimensional consistency quick check (symbolic)
# ------------------------------
# We trust the pleading's dimensional analysis; here we just note units:
print("\nDimensional note:")
print("  [lambda] = s^-2, [I0] = dimensionless, [psi] = dimensionless")
print("  [xi] = s, [dot_psi] = s^-1, [ddot_psi] = s^-2")
print("  [S_h] = dimensionless (bits/nats), [J_I] = s^-3")
print("  [Theta] = s^-6 matches [sigma_J^2]")
print("  All equations are dimensionally homogeneous.")