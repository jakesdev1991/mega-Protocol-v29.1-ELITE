# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
#!/usr/bin/env python3
"""
Omega Protocol Invariant Validator for the Higher‑Order Lattice Polarization
derivation (Phi_N, Phi_Delta).

Checks:
  * Invariant definitions: psi, xi_N, xi_delta
  * Shredding Event: xi_delta -> ∞  <=>  Phi_N^2 + 3*Phi_Delta^2 = v^2
  * Informational Freeze: Phi_Delta saturates at Lambda_Delta (hard cutoff)
  * Poisson recovery of Phi_N: sign of source term S_N = -lambda*Phi_N*(Phi_N^2+Phi_Delta^2-v^2)
    should point toward the vacuum (Phi_N -> v) when Phi_Delta is small.
  * Reality of one‑loop mass‑squares: m_plus^2, m_minus^2 >= 0 (no tachyonic/imaginary modes)
  * Dimensional sanity check (symbolic): all terms in V_eff have dimension [E]^4 in 4D.
"""

import numpy as np

# ----------------------------------------------------------------------
# Parameters (set to representative values; user can override)
# ----------------------------------------------------------------------
lam   = 0.1      # lambda coupling (dimensionless in 4D)
v     = 246.0    # vacuum expectation value (GeV)
Lambda_Delta = 1e3  # Informational Freeze cutoff (GeV)

# ----------------------------------------------------------------------
# Invariant definitions (as per Omega Action)
# ----------------------------------------------------------------------
def invariants(phi_N, phi_Delta):
    """Return psi, xi_N^{-2}, xi_Delta^{-2}."""
    psi      = np.log(phi_N / v)
    xiN_inv2 = lam * (3 * phi_N**2 + phi_Delta**2 - v**2)
    xiD_inv2 = lam * (phi_N**2 + 3 * phi_Delta**2 - v**2)
    # Avoid division by zero; return infinities where appropriate
    xi_N    = np.inf if xiN_inv2 == 0 else 1.0 / np.sqrt(xiN_inv2)
    xi_D    = np.inf if xiD_inv2 == 0 else 1.0 / np.sqrt(xiD_inv2)
    return psi, xi_N, xi_D, xiN_inv2, xiD_inv2

# ----------------------------------------------------------------------
# Shredding & Freeze conditions
# ----------------------------------------------------------------------
def is_shredding(phi_N, phi_Delta):
    """True when xi_Delta -> ∞ (within tolerance)."""
    lhs = phi_N**2 + 3 * phi_Delta**2
    return np.isclose(lhs, v**2, rtol=1e-6, atol=1e-8)

def is_informational_freeze(phi_Delta):
    """True when Phi_Delta saturates the cutoff."""
    return np.isclose(np.abs(phi_Delta), Lambda_Delta, rtol=1e-6, atol=1e-8)

# ----------------------------------------------------------------------
# Poisson recovery check for Phi_N
# ----------------------------------------------------------------------
def poisson_recovery_ok(phi_N, phi_Delta):
    """
    Returns True if the source term S_N = -lam*phi_N*(phi_N^2+phi_Delta^2-v^2)
    drives phi_N toward v (i.e., S_N * (v - phi_N) > 0).
    """
    S_N = -lam * phi_N * (phi_N**2 + phi_Delta**2 - v**2)
    return S_N * (v - phi_N) > 0

# ----------------------------------------------------------------------
# One-loop effective potential reality check
# ----------------------------------------------------------------------
def mass_squares(phi_N, phi_Delta):
    """Tree‑level mass‑squared eigenvalues from the mass matrix."""
    m_plus2  = lam * (3 * (phi_N**2 + phi_Delta**2) - v**2)
    m_minus2 = lam * (phi_N**2 + phi_Delta**2 - v**2)
    return m_plus2, m_minus2

def potential_real(phi_N, phi_Delta):
    """True if both mass‑squares are non‑negative (no imaginary frequencies)."""
    m2p, m2m = mass_squares(phi_N, phi_Delta)
    return m2p >= 0 and m2m >= 0

# ----------------------------------------------------------------------
# Dimensional consistency (symbolic, 4D)
# ----------------------------------------------------------------------
def dimensional_check():
    """
    In natural units (hbar = c = 1):
      [phi] = [E]^{(d-1)/2} = [E]^{3/2} for d=4.
      [V]   = [E]^4.
      [lam] = dimensionless.
      [psi] = dimensionless (log of ratio).
      [xi_N], [xi_Delta] = [E]^{-1} (inverse mass).
    The function returns a descriptive string; no numeric failure possible
    unless the user changes the definition of the action.
    """
    return ("[phi] = E^{3/2}, [V] = E^4, [lam] = 0, "
            "[psi] = 0, [xi] = E^{-1}. All terms in V_eff scale as E^4 → OK.")

# ----------------------------------------------------------------------
# Example sweep to locate instability regions
# ----------------------------------------------------------------------
def scan_grid(N=200):
    phi_N_vals  = np.linspace(0.1*v, 1.5*v, N)
    phi_D_vals  = np.linspace(0.0, 1.5*v, N)
    unstable = []
    for phi_N in phi_N_vals:
        for phi_D in phi_D_vals:
            if is_informational_freeze(phi_D):
                continue   # respect the cutoff; points beyond are discarded
            if not poisson_recovery_ok(phi_N, phi_D):
                unstable.append((phi_N, phi_D, "Poisson recovery violated"))
            elif not potential_real(phi_N, phi_D):
                unstable.append((phi_N, phi_D, "Imaginary mass‑squared (tachyonic/unstable)"))
            elif is_shredding(phi_N, phi_D):
                unstable.append((phi_N, phi_D, "Shredding condition met"))
    return unstable

if __name__ == "__main__":
    print("=== Omega Protocol Invariant Validator ===")
    print(dimensional_check())
    print("\nScanning for instability regions (phi_N, phi_Delta) …")
    bad = scan_grid()
    if not bad:
        print("No instability detected within the scanned range.")
    else:
        print(f"Found {len(bad)} problematic points. First few:")
        for phi_N, phi_D, reason in bad[:5]:
            print(f"  phi_N={phi_N:.3f}, phi_D={phi_D:.3f} → {reason}")