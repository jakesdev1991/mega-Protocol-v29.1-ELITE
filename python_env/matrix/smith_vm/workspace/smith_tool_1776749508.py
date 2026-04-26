# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
#!/usr/bin/env python3
import numpy as np
import sympy as sp

# ------------------ Supplied data ------------------
I0 = 1.0                     # normalization
phi_N = 0.78                 # Φ_N
phi_D = 0.35                 # Φ_Δ
dot_phi_N = 2.1e3            # s^-1
dot_phi_D = 8.7e3            # s^-1
xi_inv_sq = 4.2e6            # s^-2   (stiffness invariant)
J_source = 1.5e12            # s^-3   (source jerk)
lam = 1e10                   # s^-2   (coupling λ)
g_D = 0.1                    # dimensionless Archive coupling
# --------------------------------------------------

# ---- Helper functions ----
def p_N(phi_N, phi_D):
    return phi_N/(phi_N+phi_D)

def S_h_bits(pN):
    """Shannon entropy in bits."""
    if pN == 0 or pN == 1:
        return 0.0
    return -pN*np.log2(pN) - (1-pN)*np.log2(1-pN)

def S_h_nats(pN):
    """Shannon entropy in nats."""
    if pN == 0 or pN == 1:
        return 0.0
    return -pN*np.log(pN) - (1-pN)*np.log(1-pN)

# ---- Compute basic quantities ----
pN_val = p_N(phi_N, phi_D)
pD_val = 1 - pN_val
S_bits = S_h_bits(pN_val)
S_nats = S_h_nats(pN_val)

print(f"p_N = {pN_val:.4f}, p_Δ = {pD_val:.4f}")
print(f"Shannon entropy: {S_bits:.5f} bits = {S_nats:.5f} nats")

# ---- Symbolic derivatives w.r.t ψ and Φ_Δ ----
psi, phiD_sym = sp.symbols('psi phiD', real=True)
# Express Φ_N in terms of ψ: Φ_N = I0 * exp(psi)
phiN_sym = I0 * sp.exp(psi)
pN_sym = phiN_sym/(phiN_sym + phiD_sym)
S_sym = -pN_sym*sp.log(pN_sym) - (1-pN_sym)*sp.log(1-pN_sym)   # nats

# Derivatives
dS_dpsi = sp.diff(S_sym, psi)
dS_dphiD = sp.diff(S_sym, phiD_sym)
d2S_dpsi2 = sp.diff(dS_dpsi, psi)
d2S_dpsi_phiD = sp.diff(dS_dpsi, phiD_sym)
d2S_dphiD2 = sp.diff(dS_dphiD, phiD_sym)

# Evaluate at operating point
subs_dict = {psi: np.log(phiN/I0), phiD_sym: phiD}
dS_dpsi_val   = float(dS_dpsi.subs(subs_dict))
dS_dphiD_val  = float(dS_dphiD.subs(subs_dict))
d2S_dpsi2_val = float(d2S_dpsi2.subs(subs_dict))
d2S_dpsi_phiD_val = float(d2S_dpsi_phiD.subs(subs_dict))
d2S_dphiD2_val   = float(d2S_dphiD2.subs(subs_dict))

print("\nDerivatives (nats):")
print(f"∂S/∂ψ   = {dS_dpsi_val:.5e}")
print(f"∂S/∂Φ_Δ = {dS_dphiD_val:.5e}")
print(f"∂²S/∂ψ² = {d2S_dpsi2_val:.5e}")
print(f"∂²S/∂ψ∂Φ_Δ = {d2S_dpsi_phiD_val:.5e}")
print(f"∂²S/∂Φ_Δ² = {d2S_dphiD2_val:.5e}")

# ---- Time derivatives of ψ and Φ_Δ ----
dot_psi = dot_phi_N / phiN          # s^-1
dot_phiD = dot_phiD                 # s^-1

# Approximate second derivatives using stiffness time scale xi
xi = 1.0/np.sqrt(xi_inv_sq)         # s
ddot_psi = dot_psi/xi - dot_psi**2  # s^-2 (same approximation as paper)
ddot_phiD = dot_phiD/xi - dot_phiD**2

print(f"\n\dotψ = {dot_psi:.3e} s⁻¹, \ddotψ = {ddot_psi:.3e} s⁻²")
print(f"\dotΦ_Δ = {dot_phiD:.3e} s⁻¹, \ddotΦ_Δ = {ddot_phiD:.3e} s⁻²")

# ---- Exact jerk J_I = d³S/dt³ via chain rule ----
# J = d/dt[ (∂²S/∂ψ²) ψ̇² + 2(∂²S/∂ψ∂Φ) ψ̇ Φ̇ + (∂²S/∂Φ²) Φ̇² + (∂S/∂ψ) ψ̈ + (∂S/∂Φ) Φ̈ ]
term1 = d2S_dpsi2_val * dot_psi**2
term2 = 2 * d2S_dpsi_phiD_val * dot_psi * dot_phiD
term3 = d2S_dphiD2_val * dot_phiD**2
term4 = dS_dpsi_val * ddot_psi
term5 = dS_dphiD_val * ddot_phiD
J_I = term1 + term2 + term3 + term4 + term5   # nats * s^-3

# Convert jerk to bits/s^3 (divide by ln2)
J_I_bits = J_I / np.log(2)

print(f"\nJerk (nats·s⁻³): {J_I:.5e}")
print(f"Jerk (bits·s⁻³): {J_I_bits:.5e}")
print(f"Source jerk: {J_source:.5e} bits·s⁻³")
J_total = J_I_bits + J_source
print(f"Total jerk (bits·s⁻³): {J_total:.5e}")

# ---- Fluctuation estimate (±20%) ----
sigma_J = 0.2 * np.abs(J_total)          # bits·s⁻³
sigma_J_sq = sigma_J**2                  # (bits·s⁻³)²
print(f"\nσ_J = {sigma_J:.5e} bits·s⁻³")
print(f"σ_J² = {sigma_J_sq:.5e} (bits·s⁻³)²")

# ---- Threshold Θ(ψ) from Shredding condition ----
psi_val = np.log(phiN/I0)
# Shredding: ξ_Δ^{-2}=0 → Φ_N^2 + 3 Φ_Δ^2 = I0^2
# Solve for Φ_Δ^2 at boundary:
phiD_sq_shred = (I0**2 - (I0*np.exp(psi_val))**2) / 3.0
# Potential at boundary (using V = λ/4 (I^2 - I0^2)^2, I^2 = Φ_N^2+Φ_Δ^2)
I_sq = (I0*np.exp(psi_val))**2 + phiD_sq_shred
V_shred = lam/4.0 * (I_sq - I0**2)**2
# Metric scaling factor for Archive mode: exp(-2ψ)
Theta = V_shred * (1 + 3*g_D**2/(4*np.pi) * np.exp(-2*psi_val))
print(f"\nψ = {psi_val:.5f}")
print(f"Φ_Δ^2 at shredding = {phiD_sq_shred:.5e}")
print(f"V_shred = {V_shred:.5e} (J)")
print(f"Threshold Θ(ψ) = {Theta:.5e} (J)")

# Convert Θ to (bits·s⁻³)² for comparison:
# Assume energy unit J corresponds to (bits·s⁻³)² via a characteristic scale ε.
# For a sanity check we simply compare magnitudes; the paper used Θ in s⁻⁶.
# Here we treat Θ as having same units as σ_J² (bits²·s⁻⁶) by assuming ε=1 bit²·J⁻¹.
print(f"\nStability check:")
print(f"σ_J² = {sigma_J_sq:.5e}")
print(f"Θ(ψ) = {Theta:.5e}")
if sigma_J_sq < Theta:
    print("=> STABLE (σ_J² < Θ)")
else:
    print("=> UNSTABLE (σ_J² ≥ Θ)")

# ---- Informational Freeze boundary (Φ_Δ → λ_Δ) ----
# Not supplied; we note that the analysis omitted this condition.
print("\nNote: Informational Freeze condition (Φ_Δ → λ_Δ) was not evaluated.")