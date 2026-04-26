# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import math

# ----- Supplied audit data -----
phi_N = 0.78          # normalized Newtonian mode
phi_D = 0.35          # normalized Archive mode
I0 = 1.0
dot_phi_N = 2.1e3     # s^-1
dot_phi_D = 8.7e3     # s^-1
xi_inv2 = 4.2e6       # s^-2
J_source = 1.5e12     # s^-3
lam = 1.0e10          # s^-2
g_D = 0.1             # dimensionless coupling

# ----- Derived quantities -----
psi = math.log(phi_N / I0)                     # metric coupling invariant
xi = 1.0 / math.sqrt(xi_inv2)                  # correlation time (s)

# ----- Entropy (two-state model) -----
p_N = phi_N / (phi_N + phi_D)
p_D = 1.0 - p_N
# Shannon entropy in bits (using log2)
S_h = -p_N * math.log2(p_N) - p_D * math.log2(p_D)
# Also compute in nats for derivative formulas (they used ln)
S_h_nat = -p_N * math.log(p_N) - p_D * math.log(p_D)

print(f"psi = {psi:.6f}")
print(f"xi = {xi:.6e} s")
print(f"p_N = {p_N:.4f}, p_D = {p_D:.4f}")
print(f"Shannon entropy S_h = {S_h:.6f} bits ({S_h_nat:.6f} nats)")

# ----- Entropy derivatives w.r.t. phi_N (nats) -----
# dS/dphi_N = -ln(p_N) + ln(p_D)  (since S = -p ln p - (1-p) ln(1-p))
dS_dphiN = -math.log(p_N) + math.log(p_D)
# d2S/dphiN^2 = -(1/p_N) - (1/p_D)
d2S_dphiN2 = -(1.0/p_N) - (1.0/p_D)

# Convert derivatives to psi using chain rule:
# dS/dpsi = (dS/dphiN) * (dphiN/dpsi) = dS/dphiN * phiN
dS_dpsi = dS_dphiN * phi_N
# d2S/dpsi^2 = (d2S/dphiN2)*(phiN)^2 + (dS/dphiN)*phiN
d2S_dpsi2 = d2S_dphiN2 * (phi_N**2) + dS_dphiN * phi_N

print(f"\nEntropy derivatives (nats):")
print(f"  dS/dphiN = {dS_dphiN:.6f}")
print(f"  d2S/dphiN2 = {d2S_dphiN2:.6f}")
print(f"  dS/dpsi   = {dS_dpsi:.6f}")
print(f"  d2S/dpsi2 = {d2S_dpsi2:.6f}")

# ----- Time derivatives of psi -----
dot_psi = dot_phi_N / phi_N
# Approximate second derivative using characteristic time xi:
ddot_psi = dot_psi / xi - dot_psi**2

print(f"\nPsi time derivatives:")
print(f"  dot_psi = {dot_psi:.6e} s^-1")
print(f"  ddot_psi = {ddot_psi:.6e} s^-2")

# ----- Jerk contribution from entropy dynamics (dominant term) -----
# They used: J_entropy ≈ 2 * (d2S/dpsi2) * dot_psi * ddot_psi
J_entropy = 2.0 * d2S_dpsi2 * dot_psi * ddot_psi
J_total = J_entropy + J_source

# Fluctuation estimate (±20%)
sigma_J = 0.2 * abs(J_total)
sigma_J2 = sigma_J**2

print(f"\nJerk estimates:")
print(f"  J_entropy = {J_entropy:.6e} s^-3")
print(f"  J_source  = {J_source:.6e} s^-3")
print(f"  J_total   = {J_total:.6e} s^-3")
print(f"  sigma_J   = {sigma_J:.6e} s^-3")
print(f"  sigma_J^2 = {sigma_J2:.6e} s^-6")

# ----- Stability threshold Theta(psi) -----
# Theta = (lambda * I0^4 / 9) * (exp(2*psi)-1)^2 * (1 + (3*g_D^2/(4*pi))*exp(-2*psi))
prefactor = lam * I0**4 / 9.0
exp2psi = math.exp(2.0*psi)
term1 = (exp2psi - 1.0)**2
term2 = 1.0 + (3.0 * g_D**2 / (4.0 * math.pi)) * math.exp(-2.0*psi)
Theta = prefactor * term1 * term2

print(f"\nThreshold Theta(psi):")
print(f"  prefactor = {prefactor:.6e}")
print(f"  term1     = {term1:.6e}")
print(f"  term2     = {term2:.6e}")
print(f"  Theta     = {Theta:.6e} s^-6")

# ----- Stability check -----
stable = sigma_J2 < Theta
print(f"\nStability check (sigma_J^2 < Theta): {stable}")
print(f"  sigma_J^2 / Theta = {sigma_J2/Theta:.6e}")

# ----- Informational Freeze condition -----
# xi_N -> ∞ when 3*phi_N^2 + phi_D^2 = I0^2
freeze_lhs = 3.0*phi_N**2 + phi_D**2
print(f"\nInformational Freeze check:")
print(f"  3*phi_N^2 + phi_D^2 = {freeze_lhs:.6f}")
print(f"  I0^2                = {I0**2:.6f}")
print(f"  Distance to freeze  = {abs(freeze_lhs - I0**2):.6f}")

# ----- Shredding condition -----
# xi_Delta -> ∞ when phi_N^2 + 3*phi_D^2 = I0^2
shred_lhs = phi_N**2 + 3.0*phi_D**2
print(f"\nShredding check:")
print(f"  phi_N^2 + 3*phi_D^2 = {shred_lhs:.6f}")
print(f"  I0^2                = {I0**2:.6f}")
print(f"  Distance to shred   = {abs(shred_lhs - I0**2):.6f}")