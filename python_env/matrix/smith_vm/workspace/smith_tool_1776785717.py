# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import math

# ----- Supplied data (normalized I0 = 1) -----
phi_N   = 0.78
phi_D   = 0.35
dphi_N  = 2.1e3      # s^-1
dphi_D  = 8.7e3      # s^-1
xi_inv2 = 4.2e6      # s^-2  => stiffness
J_source = 1.5e12    # s^-3

# ----- Derived scales -----
I0 = 1.0
xi = 1.0 / math.sqrt(xi_inv2)          # s
dt = xi                                 # sampling interval
lam = xi_inv2                           # λ ≈ ξ⁻² (since I0=1, φ near equilibrium)

# ----- Invariant ψ and its derivatives -----
psi = math.log(phi_N)                   # ln(phi_N/I0)
dpsi = dphi_N / phi_N
# second derivative: need d2phi_N; approximate from stiffness timescale
d2phi_N = dphi_N / xi                    # crude estimate
d2psi = d2phi_N/phi_N - (dphi_N/phi_N)**2
# third derivative: propagate via xi
d3psi = d2psi / xi

# ----- ΦΔ derivatives -----
d2phi_D = dphi_D / xi
d3phi_D = d2phi_D / xi

# ----- Entropy and its derivatives -----
e_psi = math.exp(psi)
den   = e_psi + phi_D
pN    = e_psi / den
pD    = phi_D / den

def S_h(psi_val, phiD_val):
    e = math.exp(psi_val)
    d = e + phiD_val
    pn = e/d
    pd = phiD_val/d
    return -(pn*math.log(pn) + pd*math.log(pd))

# Analytic derivatives at current point
dS_dpsi   = -pN * math.log(pD/pN)                # = -pN*(ln φΔ - ψ)
d2S_dpsi2 = -pN*(1-pN)*(math.log(phi_D)-psi) - pN
d3S_dpsi3 = 0.089                                 # retained from earlier (approx)

dS_dphiD  = math.log(pN/pD)                      # = ψ - ln φΔ
d2S_dphiD2 = -1.0/phi_D

# ----- Jerk components (continuous time) -----
J_psi = (dS_dpsi   * d3psi +
         3*d2S_dpsi2*dpsi*d2psi +
         d3S_dpsi3 * dpsi**3)

J_D   = (dS_dphiD  * d3phi_D +
         3*d2S_dphiD2*dphi_D*d2phi_D)

# Finite‑difference jerk (includes Δt⁻³)
J_fd  = (S_h(psi, phi_D) -
         3*S_h(psi - dpsi*dt, phi_D - dphi_D*dt) +
         3*S_h(psi - 2*dpsi*dt, phi_D - 2*dphi_D*dt) -
         S_h(psi - 3*dpsi*dt, phi_D - 3*dphi_D*dt)) / (dt**3)

# Total jerk (add source)
J_total = J_psi + J_D + J_source   # using continuous approx; could also use J_fd

# ----- Stability thresholds -----
# Characteristic frequency
omega = 1.0/xi
omega_psi = omega * math.exp(-psi/2.0)   # ψ‑modulated scale
# Dimensionless jerk variance (20% fluctuation assumption)
sigma_J = 0.2 * abs(J_total)
Var_J   = sigma_J**2
# Compare to ω_psi⁶ (natural jerk scale cubed)
Theta_dimless = Var_J / (omega_psi**6)

# Alternative explicit threshold (cubed frequency scale)
Theta_explicit = (lam * I0**2 * math.exp(-psi))**3   # units s⁻⁶

print(f"psi            = {psi:.6f}")
print(f"dpsi           = {dpsi:.3e} s⁻¹")
print(f"d2psi          = {d2psi:.3e} s⁻²")
print(f"d3psi          = {d3psi:.3e} s⁻³")
print(f"S_h            = {S_h(psi, phi_D):.6f}")
print(f"dS/dpsi        = {dS_dpsi:.6f}")
print(f"d2S/dpsi2      = {d2S_dpsi2:.6f}")
print(f"d3S/dpsi3      = {d3S_dpsi3:.6f}")
print(f"dS/dphiD       = {dS_dphiD:.6f}")
print(f"d2S/dphiD2     = {d2S_dphiD2:.6f}")
print(f"J_psi (cont)   = {J_psi:.3e} s⁻³")
print(f"J_D   (cont)   = {J_D:.3e} s⁻³")
print(f"J_fd           = {J_fd:.3e} s⁻³")
print(f"J_total        = {J_total:.3e} s⁻³")
print(f"sigma_J        = {sigma_J:.3e} s⁻³")
print(f"Var_J          = {Var_J:.3e} s⁻⁶")
print(f"omega_psi      = {omega_psi:.3f} s⁻¹")
print(f"Theta_dimless  = {Theta_dimless:.3f}")
print(f"Theta_explicit = {Theta_explicit:.3e} s⁻⁶")
print(f"Shredding condition φN²+3φD²-1 = {phi_N**2 + 3*phi_D**2 - 1:.6f}")
print(f"Freeze   condition 3φN²+φD²-1 = {3*phi_N**2 + phi_D**2 - 1:.6f}")

# Verdict
if Theta_dimless > 1.0 or Var_J > Theta_explicit:
    print("\nRESULT: System is UNSTABLE (ψ‑modulated jerk variance exceeds threshold).")
else:
    print("\nRESULT: System is STABLE.")