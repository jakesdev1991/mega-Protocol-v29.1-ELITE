# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np

# ---------- Given normalized data ----------
I0 = 1.0                     # baseline (normalized)
phi_N   = 0.78               # Φ_N / I0
phi_D   = 0.35               # Φ_Δ / I0
phi_dot_N   = 2.1e3          # s⁻¹
phi_dot_D   = 8.7e3          # s⁻¹
xi_inv_sq   = 4.2e6          # s⁻²  (stiffness ξ⁻²)
xi          = 1.0/np.sqrt(xi_inv_sq)   # s
source_jerk = 1.5e12         # s⁻³

# ---------- Derived quantities ----------
psi   = np.log(phi_N)                     # ln(Φ_N/I0)
psi_dot   = phi_dot_N / phi_N

# Approximate second derivatives using φ̈ ≈ φ̇/ξ (as in the Engine output)
phi_ddot_N   = phi_dot_N / xi
phi_ddot_D   = phi_dot_D  / xi
psi_ddot   = phi_ddot_N/phi_N - (phi_dot_N/phi_N)**2
psi_dddot  = psi_ddot / xi   # same approximation for third derivative

phi_dddot_D  = phi_ddot_D / xi

# ---------- Entropy and its derivatives ----------
def entropy(psi_val, phi_D_val):
    """Shannon conditional entropy S_h(ψ, φ_Δ) with p_N ∝ e^ψ, p_Δ ∝ φ_Δ."""
    e_psi = np.exp(psi_val)
    denom = e_psi + phi_D_val
    p_N = e_psi / denom
    p_D = phi_D_val / denom
    # avoid log(0)
    eps = 1e-15
    p_N = np.clip(p_N, eps, 1-eps)
    p_D = np.clip(p_D, eps, 1-eps)
    return -(p_N*np.log(p_N) + p_D*np.log(p_D))

# Compute derivatives via finite differences (central) for robustness
def grad_psi(psi_val, phi_D_val, h=1e-6):
    return (entropy(psi_val+h, phi_D_val) - entropy(psi_val-h, phi_D_val))/(2*h)

def grad_phiD(psi_val, phi_D_val, h=1e-6):
    return (entropy(psi_val, phi_D_val+h) - entropy(psi_val, phi_D_val-h))/(2*h)

def hess_psi(psi_val, phi_D_val, h=1e-6):
    return (entropy(psi_val+h, phi_D_val) - 2*entropy(psi_val, phi_D_val) + entropy(psi_val-h, phi_D_val))/(h**2)

def hess_phiD(psi_val, phi_D_val, h=1e-6):
    return (entropy(psi_val, phi_D_val+h) - 2*entropy(psi_val, phi_D_val) + entropy(psi_val, phi_D_val-h))/(h**2)

def mixed_deriv(psi_val, phi_D_val, h=1e-6):
    return (entropy(psi_val+h, phi_D_val+h) - entropy(psi_val+h, phi_D_val-h)
            - entropy(psi_val-h, phi_D_val+h) + entropy(psi_val-h, phi_D_val-h))/(4*h**2)

# Evaluate at operating point
dS_dpsi   = grad_psi(psi, phi_D)
dS_dphiD  = grad_phiD(psi, phi_D)
d2S_dpsi2 = hess_psi(psi, phi_D)
d2S_dphiD2 = hess_phiD(psi, phi_D)
# third derivative w.r.t ψ (central)
def third_deriv_psi(psi_val, phi_D_val, h=1e-6):
    return (entropy(psi_val+2*h, phi_D_val) - 2*entropy(psi_val+h, phi_D_val)
            + 2*entropy(psi_val-h, phi_D_val) - entropy(psi_val-2*h, phi_D_val))/(2*h**3)
d3S_dpsi3 = third_deriv_psi(psi, phi_D)

print("Entropy derivatives:")
print(f"  ∂S/∂ψ   = {dS_dpsi:.6e}")
print(f"  ∂S/∂φΔ  = {dS_dphiD:.6e}")
print(f"  ∂²S/∂ψ² = {dS_dpsi2:.6e}")
print(f"  ∂²S/∂φΔ²= {dS_dphiD2:.6e}")
print(f"  ∂³S/∂ψ³ = {d3S_dpsi3:.6e}")

# ---------- Jerk components ----------
J_psi = (dS_dpsi   * psi_dddot
         + 3 * d2S_dpsi2 * psi_dot * psi_ddot
         + d3S_dpsi3 * psi_dot**3)

J_Delta = (dS_dphiD * phi_dddot_D
           + 3 * d2S_dphiD2 * phi_dot_D * phi_ddot_D)

total_jerk = J_psi + J_Delta + source_jerk

print("\nJerk components (s⁻³):")
print(f"  J_ψ    = {J_psi:.6e}")
print(f"  J_Δ    = {J_Delta:.6e}")
print(f"  Source = {source_jerk:.6e}")
print(f"  Total  = {total_jerk:.6e}")

# ---------- Stability criterion ----------
omega   = 1.0/xi                         # s⁻¹
omega_psi = omega * np.exp(-psi/2.0)     # s⁻¹
natural_jerk_scale = omega_psi**3        # s⁻³

# variance estimate from Engine (we keep their number for comparison)
sigma_J_sq = 1.71e21                     # s⁻⁶
dimless_var = sigma_J_sq / (natural_jerk_scale**2)  # should be σ²/ω⁶

# Threshold from potential curvature
lam = xi_inv_sq                          # λ = ξ⁻²
Theta = (lam * I0**2 * np.exp(-psi))**3   # s⁻⁶

print("\nStability check:")
print(f"  ξ               = {xi:.3e} s")
print(f"  ω               = {omega:.3e} s⁻¹")
print(f"  ω_ψ             = {omega_psi:.3e} s⁻¹")
print(f"  ω_ψ³            = {natural_jerk_scale:.3e} s⁻³")
print(f"  σ_𝒥²            = {sigma_J_sq:.3e} s⁻⁶")
print(f"  σ_𝒥² / ω_ψ⁶    = {dimless_var:.3f}")
print(f"  Threshold Θ     = {Theta:.3e} s⁻⁶")
print(f"  σ_𝒥² > Θ ?     {sigma_J_sq > Theta}")

# ---------- Boundary conditions ----------
shredding_cond = phi_N**2 + 3*phi_D**2   # should be < 1 for safe, →1 at boundary
freeze_cond    = 3*phi_N**2 + phi_D**2   # should be < 1 for safe, →1 at boundary

print("\nBoundary proximity:")
print(f"  Φ_N² + 3Φ_Δ² = {shredding_cond:.6f}  (Shredding event at =1)")
print(f"  3Φ_N² + Φ_Δ² = {freeze_cond:.6f}    (Informational Freeze at =1)")