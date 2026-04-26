# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np

# ── Parameters (in arbitrary units, the ratio matters) ──
g_N       = 0.2                # Yukawa coupling of Φ_N
g_Delta   = 0.6                # Yukawa coupling of Φ_Δ
Lambda    = 1.0e4              # UV cutoff
pi        = np.pi

# ── One‑loop quadratic divergences (mass corrections) ──
delta_m_N_sq    = (g_N**2   / (16*pi**2)) * Lambda**2
delta_m_Delta_sq = (g_Delta**2 / (16*pi**2)) * Lambda**2

# ── Off‑diagonal mixing term from the fermion bubble ──
mixing_coeff = (g_N * g_Delta / (16*pi**2)) * Lambda**2

print(f"Δm_N²            = {delta_m_N_sq:.3e}")
print(f"Δm_Δ²            = {delta_m_Delta_sq:.3e}")
print(f"Φ_N–Φ_Δ mixing   = {mixing_coeff:.3e}")
print(f"Mixing / Δm_N²   = {mixing_coeff / delta_m_N_sq:.3f}")
print(f"Mixing / Δm_Δ²   = {mixing_coeff / delta_m_Delta_sq:.3f}")

# ── Landau pole for g_Delta (β(g)=g³/(16π²)) ──
mu0      = 1.0
b0       = 1/(16*pi**2)
Lambda_LP = mu0 * np.exp(1/(2*b0*g_Delta**2))
print(f"\nLandau pole scale Λ_LP = {Lambda_LP:.3e}")

# ── Lattice cutoff as a function of Φ_N (a = ξ₀ e^{-ψ}, ψ = ln(Φ_N/I₀)) ──
xi0 = 1.0
I0  = 1.0

def lattice_cutoff(Phi_N):
    psi = np.log(Phi_N / I0)
    a   = xi0 * np.exp(-psi)          # a = ξ₀ e^{-ψ}
    return np.pi / a                  # Λ_lat = π / a

for Phi_N in [0.5, 2.0, 10.0]:
    Λ_lat = lattice_cutoff(Phi_N)
    print(f"Φ_N = {Phi_N:4.1f} → lattice cutoff Λ_lat = {Λ_lat:.3f}")

# ── Comparison: if the Landau pole lies below the lattice cutoff, perturbation
#    theory dies before the regulator is reached ──
Phi_test = 10.0
Λ_lat_test = lattice_cutoff(Phi_test)
if Lambda_LP < Λ_lat_test:
    print(f"\nPremature Shredding: Λ_LP ({Lambda_LP:.3e}) < Λ_lat ({Λ_lat_test:.3e})")
else:
    print(f"\nNo immediate conflict: Λ_LP ({Lambda_LP:.3e}) > Λ_lat ({Λ_lat_test:.3e})")

# ── Entanglement entropy growth due to mixing (illustrative) ──
# Treat the two‑scalar subsystem as a bipartite pure state; the entropy
# scales with the mixing coefficient relative to the mass gap.
entropy_estimate = np.log(1 + mixing_coeff / (delta_m_N_sq + 1e-30))
print(f"\nEntanglement entropy estimate (mixing) = {entropy_estimate:.3f} (arbitrary units)")