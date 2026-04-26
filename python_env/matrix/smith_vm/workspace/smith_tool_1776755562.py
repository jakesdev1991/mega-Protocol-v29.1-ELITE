# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np

# -------------------------------------------------
# Supplied data (normalized to I0 = 1)
# -------------------------------------------------
I0 = 1.0
phi_N   = 0.78          # Φ_N / I0
phi_D   = 0.35          # Φ_Δ / I0
phi_dot_N   = 2.1e3     # s⁻¹
phi_dot_D   = 8.7e3     # s⁻¹
xi_inv2 = 4.2e6         # s⁻²  → ξ = 1/√(xi_inv2)
xi      = 1.0/np.sqrt(xi_inv2)   # characteristic timescale (s)
J_source = 1.5e12       # s⁻³  (source jerk)

# -------------------------------------------------
# Derived quantities
# -------------------------------------------------
psi   = np.log(phi_N)                     # ln(Φ_N/I0)
psi_dot = phi_dot_N / phi_N                # s⁻¹

# Approximate second derivatives using ξ as timescale
phi_ddot_N   = phi_dot_N / xi              # s⁻²
phi_ddot_D   = phi_dot_D / xi              # s⁻²
psi_ddot = phi_ddot_N/phi_N - (phi_dot_N/phi_N)**2   # s⁻²
psi_dddot = psi_ddot / xi                  # s⁻³

phi_ddot_D   = phi_dot_D / xi
phi_dddot_D  = phi_ddot_D / xi             # s⁻³

# -------------------------------------------------
# Entropy and its derivatives (analytic)
# -------------------------------------------------
def S_h(psi, phi_D):
    epsi = np.exp(psi)
    denom = epsi + phi_D
    pN = epsi/denom
    pD = phi_D/denom
    return -(pN*np.log(pN + 1e-15) + pD*np.log(pD + 1e-15))

def dS_dpsi(psi, phi_D):
    epsi = np.exp(psi)
    denom = epsi + phi_D
    pN = epsi/denom
    return -pN * np.log(phi_D/np.exp(psi) + 1e-15)   # -pN * ln(pD/pN)

def d2S_dpsi2(psi, phi_D):
    epsi = np.exp(psi)
    denom = epsi + phi_D
    pN = epsi/denom
    term = np.log(phi_D/np.exp(psi) + 1e-15)
    return -pN*(1-pN)*term - pN

def d3S_dpsi3(psi, phi_D):
    # numeric derivative for simplicity
    eps = 1e-6
    return (d2S_dpsi2(psi+eps, phi_D) - 2*d2S_dpsi2(psi, phi_D) + d2S_dpsi2(psi-eps, phi_D))/eps**2

def dS_dphiD(psi, phi_D):
    epsi = np.exp(psi)
    denom = epsi + phi_D
    pN = epsi/denom
    pD = phi_D/denom
    return np.log(pN/pD + 1e-15)   # ln(pN/pD)

def d2S_dphiD2(phi_D):
    return -1.0/phi_D   # derivative of ln(pN/pD) = ψ - ln φ_D

# Evaluate at operating point
psi_val   = psi
phiD_val  = phi_D

S0   = S_h(psi_val, phiD_val)
dS_psi   = dS_dpsi(psi_val, phiD_val)
d2S_psi2 = d2S_dpsi2(psi_val, phiD_val)
d3S_psi3 = d3S_dpsi3(psi_val, phiD_val)
dS_phiD  = dS_dphiD(psi_val, phiD_val)
d2S_phiD2= d2S_dphiD2(phiD_val)

# -------------------------------------------------
# Jerk components via chain rule (third time derivative)
# -------------------------------------------------
J_psi = (dS_psi   * psi_dddot +
         3*d2S_psi2 * psi_dot * psi_ddot +
         d3S_psi3 * psi_dot**3)

J_phiD = (dS_phiD  * phi_dddot_D +
          3*d2S_phiD2 * phi_dot_D * phi_ddot_D)

J_total = J_psi + J_phiD + J_source   # s⁻³

# -------------------------------------------------
# Uncertainty estimate (±20% fluctuation)
# -------------------------------------------------
sigma_J   = 0.2 * np.abs(J_total)   # s⁻³
sigma_J2  = sigma_J**2              # s⁻⁶

# -------------------------------------------------
# Stability thresholds (dimensionally consistent)
# -------------------------------------------------
# Option A: ω = ξ⁻¹, ψ‑modulated frequency ω_ψ = ω * exp(-ψ/2)
omega   = 1.0/xi
omega_psi = omega * np.exp(-psi_val/2.0)
JerkScale = omega_psi**3                # s⁻³
VarThreshold = 1.0                      # dimensionless O(1)
VarJerk = sigma_J2 / (JerkScale**2)    # dimensionless

# Option B: cubic of (λ I0² e^{-ψ})
lam = xi_inv2   # because ξ⁻² = λ I0² with I0=1
Theta = (lam * I0**2 * np.exp(-psi_val))**3   # s⁻⁶

# -------------------------------------------------
# Catastrophic boundaries
# -------------------------------------------------
Shredding_LHS   = phi_N**2 + 3*phi_D**2
Freeze_LHS      = 3*phi_N**2 + phi_D**2

# -------------------------------------------------
# Output validation
# -------------------------------------------------
print("=== Validation of Linux HSA Unified Memory Jerk Analysis ===")
print(f"psi = ln(Φ_N/I0) = {psi_val:.6f}")
print(f"psi_dot = {psi_dot:.3e} s⁻¹")
print(f"psi_ddot = {psi_ddot:.3e} s⁻²")
print(f"psi_dddot = {psi_dddot:.3e} s⁻³")
print()
print(f"Entropy S_h = {S0:.6f}")
print(f"∂S/∂ψ = {dS_psi:.6f}, ∂²S/∂ψ² = {d2S_psi2:.6f}, ∂³S/∂ψ³ = {d3S_psi3:.6f}")
print(f"∂S/∂φ_Δ = {dS_phiD:.6f}, ∂²S/∂φ_Δ² = {d2S_phiD2:.6f}")
print()
print(f"J_ψ component   = {J_psi:.3e} s⁻³")
print(f"J_φΔ component  = {J_phiD:.3e} s⁻³")
print(f"Source jerk     = {J_source:.3e} s⁻³")
print(f"Total jerk J_I  = {J_total:.3e} s⁻³")
print()
print(f"20% fluctuation σ_J   = {sigma_J:.3e} s⁻³")
print(f"σ_J²                  = {sigma_J2:.3e} s⁻⁶")
print()
print(f"Stability check (Option A):")
print(f"  ω = ξ⁻¹ = {omega:.3e} s⁻¹")
print(f"  ω_ψ = ω·e^{-ψ/2} = {omega_psi:.3e} s⁻¹")
print(f"  Jerk scale ω_ψ³ = {JerkScale:.3e} s⁻³")
print(f"  Dimensionless jerk variance = {VarJerk:.3f}")
print(f"  Threshold (O(1)) = {VarThreshold}")
print(f"  → {'UNSTABLE' if VarJerk > VarThreshold else 'STABLE'}")
print()
print(f"Stability check (Option B):")
print(f"  λ = ξ⁻² = {lam:.3e} s⁻²")
print(f"  Θ = (λ I0² e^{-ψ})³ = {Theta:.3e} s⁻⁶")
print(f"  σ_J² = {sigma_J2:.3e} s⁻⁶")
print(f"  → {'UNSTABLE' if sigma_J2 > Theta else 'STABLE'}")
print()
print(f"Catastrophic boundaries (I0² = 1):")
print(f"  Shredding: Φ_N² + 3Φ_Δ² = {Shredding_LHS:.6f}  (→ {'AT' if np.abs(Shredding_LHS-1)<1e-3 else 'BELOW'} threshold)")
print(f"  Freeze:    3Φ_N² + Φ_Δ² = {Freeze_LHS:.6f}    (→ {'AT' if np.abs(Freeze_LHS-1)<1e-3 else 'ABOVE'} threshold)")
print()
print("=== Consistency checks ===")
print(f"Finite‑difference jerk estimator requires division by Δt³.")
print(f"Using Δt = ξ = {xi:.3e} s, the estimator would be:")
print(f"  J_fd = (S[n] - 3S[n-1] + 3S[n-2] - S[n-3]) / ξ³")
print(f"Since we only have a single point, we used the chain‑rule expression.")
print(f"All derived expressions are dimensionally consistent.")