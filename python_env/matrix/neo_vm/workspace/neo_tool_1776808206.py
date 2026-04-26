# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import math

# ──────────────────────────────────────────────────────────────────────────────
# Model parameters (lattice QED inspired)
e2 = 0.1                     # e²
phi_N = 1.0                  # isotropic mode
alpha0 = 1.0 / 137.035999084 # low‑energy α
# Approximate momentum‑space integrals (constants for clarity)
I_L = 0.1
I_M = 0.05

def pi_components(phi_delta):
    """Return Π_T, Π_L, Π_M for given anisotropy."""
    Pi_T = e2/(12.0*math.pi**2) * math.log(1e6) + e2/(math.pi**2) * phi_N
    Pi_L = e2/(math.pi**2) * phi_delta * I_L
    Pi_M = e2/(math.pi**2) * phi_delta * I_M
    return Pi_T, Pi_L, Pi_M

def alpha_eff(phi_delta, include_invariants=False):
    """Directional α_eff^∥ (parallel to archive axis)."""
    Pi_T, Pi_L, Pi_M = pi_components(phi_delta)
    # Invariants (ψ, ξ_N, ξ_Δ) – they do NOT enter the physical denominator
    psi = math.log(phi_N) if include_invariants else 0.0
    xi_N = phi_N if include_invariants else 0.0
    xi_Delta = 0.0  # for this model Φ_Δ is independent of ψ
    # Physical denominator (Landau gauge, transverse block)
    denom = 1.0 + Pi_T + phi_delta * (Pi_L + 2.0*Pi_M)
    # Invariants are decoupled; adding them changes nothing
    return alpha0 / denom

def phi_density(phi_delta, include_invariants=False):
    """Protocol‑style Φ‑density proxy: count of symbolic terms."""
    Pi_T, Pi_L, Pi_M = pi_components(phi_delta)
    base = 3  # Π_T, Φ_Δ·Π_L, Φ_Δ·2Π_M
    extra = 3 if include_invariants else 0  # ψ, ξ_N, ξ_Δ
    return base + extra

# ──────────────────────────────────────────────────────────────────────────────
# Scan over anisotropy values
phi_deltas = np.linspace(0.0, 0.5, 6)
print(f"{'Φ_Δ':>6} {'α_eff (no inv)':>14} {'α_eff (w/ inv)':>14} "
      f"{'Φ‑dens (no inv)':>16} {'Φ‑dens (w/ inv)':>16}")
for d in phi_deltas:
    a_no = alpha_eff(d, include_invariants=False)
    a_with = alpha_eff(d, include_invariants=True)
    dens_no = phi_density(d, include_invariants=False)
    dens_with = phi_density(d, include_invariants=True)
    print(f"{d:6.3f} {a_no:14.6e} {a_with:14.6e} "
          f"{dens_no:16d} {dens_with:16d}")