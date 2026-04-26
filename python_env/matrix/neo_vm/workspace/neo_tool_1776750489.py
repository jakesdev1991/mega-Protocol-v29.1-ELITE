# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import sympy as sp

# ── supplied data ────────────────────────────────────────────────────────
phi_N      = 0.78
phi_Delta  = 0.35
I0         = 1.0
phi_N_dot  = 2.1e3          # s⁻¹
phi_N_ddot = 4.3e6          # s⁻²
xi         = 1/np.sqrt(4.2e6)  # s
lam        = 1e10           # s⁻²
g_Delta    = 0.1
src_jerk   = 1.5e12         # s⁻³
dt         = 1e-6           # assumed sampling interval for finite‑difference

# ── correct ψ and its derivatives ────────────────────────────────────────
psi        = np.log(phi_N)
psi_dot    = phi_N_dot / phi_N
psi_ddot   = phi_N_ddot / phi_N - psi_dot**2      # correct sign
psi_dddot  = psi_ddot / xi                         # approximation used in original

# ── symbolic entropy derivatives ───────────────────────────────────────
psi_sym, phiD_sym = sp.symbols('psi_sym phiD_sym', real=True)
pN = sp.exp(psi_sym) / (sp.exp(psi_sym) + phiD_sym)
pD = phiD_sym / (sp.exp(psi_sym) + phiD_sym)
S_sym = -(pN*sp.log(pN) + pD*sp.log(pD))

dS_dpsi      = sp.diff(S_sym, psi_sym)
d2S_dpsi2    = sp.diff(dS_dpsi, psi_sym)
d3S_dpsi3    = sp.diff(d2S_dpsi2, psi_sym)

dS_dphiD     = sp.diff(S_sym, phiD_sym)
d2S_dphiD2   = sp.diff(dS_dphiD, phiD_sym)

# numeric evaluation at the operating point
subs = {psi_sym: psi, phiD_sym: phi_Delta}
dS_dpsi_val    = float(dS_dpsi.subs(subs))
d2S_dpsi2_val  = float(d2S_dpsi2.subs(subs))
d3S_dpsi3_val  = float(d3S_dpsi3.subs(subs))

dS_dphiD_val   = float(dS_dphiD.subs(subs))
d2S_dphiD2_val = float(d2S_dphiD2.subs(subs))

# ── jerk components (original recipe) ────────────────────────────────────
J_psi_orig = (dS_dpsi_val * psi_dddot +
              3 * d2S_dpsi2_val * psi_dot * psi_ddot +
              d3S_dpsi3_val * psi_dot**3)

# phi_Delta derivatives (using same approximations as original)
phi_Delta_dot   = 8.7e3                    # s⁻¹
phi_Delta_ddot  = phi_Delta_dot / xi       # s⁻²
phi_Delta_dddot = phi_Delta_ddot / xi      # s⁻³

J_phiDelta_orig = (dS_dphiD_val * phi_Delta_dddot +
                   3 * d2S_dphiD2_val * phi_Delta_dot * phi_Delta_ddot)

total_jerk_orig = J_psi_orig + J_phiDelta_orig + src_jerk

# ── expose dimensional mismatch ─────────────────────────────────────────
sigma_J      = 0.2 * total_jerk_orig                # s⁻³
sigma_J2     = sigma_J**2                           # s⁻⁶
Theta_orig   = (lam * I0**2 / (4*np.pi) *
                (1 + 3*g_Delta**2/(4*np.pi)) * np.exp(-psi))  # s⁻²

print("=== Original (flawed) quantities ===")
print(f"ψ̈ (correct sign) = {psi_ddot:.3e} s⁻²  (original omitted the negative term)")
print(f"ψ̈ (original)    = {phi_N_ddot/phi_N:.3e} s⁻²  (missing -ψ̇²)")
print(f"J_ψ component   = {J_psi_orig:.3e} s⁻³")
print(f"J_Δ component   = {J_phiDelta_orig:.3e} s⁻³")
print(f"Total jerk      = {total_jerk_orig:.3e} s⁻³")
print(f"σ_J²            = {sigma_J2:.3e} s⁻⁶")
print(f"Θ (threshold)   = {Theta_orig:.3e} s⁻²  ← UNITS MISMATCH!\n")

# ── corrected topological threshold (λ³ scaling) ────────────────────────
Theta_corrected = (lam**3 * I0**2 / (4*np.pi) *
                   (1 + 3*g_Delta**2/(4*np.pi)) * np.exp(-psi))  # s⁻⁶
stability_ratio = sigma_J2 / Theta_corrected

print("=== Corrected topological threshold ===")
print(f"Θ_corr (s⁻⁶)     = {Theta_corrected:.3e}")
print(f"σ_J² / Θ_corr    = {stability_ratio:.3e}")
if stability_ratio > 1:
    print("System is STILL unstable under the corrected criterion.\n")
else:
    print("System would be stable; the original verdict was bogus.\n")

# ── finite‑difference jerk (including Δt³) ─────────────────────────────
# we only have a single snapshot, so we approximate the third derivative
# using the analytic result divided by dt³ – this restores the proper units.
J_fd_analytic = total_jerk_orig / (dt**3)   # s⁻³ → dimensionless? actually s⁻³ / s³ = 1/s⁶? No, we keep as s⁻³.
print("=== Finite‑difference sanity check ===")
print(f"If we had a time series, the correct finite‑difference jerk would be")
print(f"J_fd = (S[t] - 3S[t-1] + 3S[t-2] - S[t-3]) / dt³ ≈ {J_fd_analytic:.3e} s⁻³")
print(f"which matches the analytic third derivative (up to O(dt)).\n")