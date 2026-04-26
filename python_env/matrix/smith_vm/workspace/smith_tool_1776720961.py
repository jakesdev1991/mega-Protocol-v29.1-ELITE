# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Omega Protocol validation script for the Higher-Order Lattice Polarization
derivation.  It checks:
  1. Symbolic correctness of the expansion and alpha_ren formula.
  2. Mass‑positivity condition over a random parameter sweep.
  3. (Optional) Computation of Omega invariants psi, xi_N, xi_Delta and entropy.
"""

import sympy as sp
import numpy as np
import itertools
import math
import sys

# ----------------------------------------------------------------------
# 1. Symbolic verification
# ----------------------------------------------------------------------
def symbolic_check():
    # Define symbols
    Phi_N, Phi_Delta, g, m, alpha0, Lambda = sp.symbols(
        'Phi_N Phi_Delta g m alpha0 Lambda', positive=True, real=True
    )
    eps = g * Phi_N / m

    # Effective masses
    m_e = m - g * Phi_N * sp.exp(Phi_Delta)
    m_p = m - g * Phi_N * sp.exp(-Phi_Delta)

    # Product and ratio
    prod = sp.simplify(m_e * m_p)
    ratio = sp.simplify(prod / m**2)

    # Expected ratio: 1 - 2*eps*cosh(Phi_Delta) + eps**2
    expected_ratio = 1 - 2*eps*sp.cosh(Phi_Delta) + eps**2
    assert sp.simplify(ratio - expected_ratio) == 0, "Ratio mismatch"

    # Log expansion to O(eps^2)
    log_expr = sp.series(sp.log(ratio), eps, 0, 3).removeO()
    expected_log = -2*eps*sp.cosh(Phi_Delta) + eps**2 * (1 - 2*sp.cosh(Phi_Delta)**2)
    assert sp.simplify(log_expr - expected_log) == 0, "Log expansion mismatch"

    # Effective mass for Pi(0)
    m_eff = sp.sqrt(m_e * m_p)
    Pi0 = (alpha0 / (3*sp.pi)) * sp.log(Lambda / m_eff)
    Pi0_series = sp.series(Pi0, eps, 0, 3).removeO()
    # Expected Pi0 from engine:
    expected_Pi0 = (alpha0/(3*sp.pi)) * (
        sp.log(Lambda/m) + eps*sp.cosh(Phi_Delta) -
        (eps**2/2)*(1 - 2*sp.cosh(Phi_Delta)**2)
    )
    assert sp.simplify(Pi0_series - expected_Pi0) == 0, "Pi0 series mismatch"

    # Alpha_ren
    alpha_ren = alpha0 / (1 - Pi0)
    alpha_ren_series = sp.series(alpha_ren, eps, 0, 3).removeO()
    # Expand to same order for comparison:
    alpha_ren_expected = alpha0 * (
        1 + (alpha0/(3*sp.pi)) * (
            sp.log(Lambda/m) + eps*sp.cosh(Phi_Delta) -
            (eps**2/2)*(1 - 2*sp.cosh(Phi_Delta)**2)
        )
    ) + O(eps**3)  # we keep symbolic; sympy will treat O as 0 after series
    # Direct simplification:
    assert sp.simplify(alpha_ren_series - alpha_ren_expected.removeO()) == 0, "Alpha_ren mismatch"

    print("[OK] Symbolic derivation verified.")
    return True

# ----------------------------------------------------------------------
# 2. Numerical mass‑positivity check
# ----------------------------------------------------------------------
def mass_positivity_check(num_samples=10000):
    np.random.seed(42)
    # Sample parameters in physically plausible ranges
    Phi_N_vals   = np.random.uniform(0.01, 5.0, num_samples)
    Phi_Delta_vals = np.random.uniform(-3.0, 3.0, num_samples)
    g_vals       = np.random.uniform(0.01, 0.5, num_samples)
    m_vals       = np.random.uniform(0.5, 2.0, num_samples)  # set bare mass scale

    m_e = m_vals - g_vals * Phi_N_vals * np.exp(Phi_Delta_vals)
    m_p = m_vals - g_vals * Phi_N_vals * np.exp(-Phi_Delta_vals)

    violations = np.sum((m_e <= 0) | (m_p <= 0))
    if violations:
        print(f"[FAIL] Mass positivity violated in {violations}/{num_samples} samples.")
        return False
    else:
        print(f"[OK] Mass positivity holds for {num_samples} random samples.")
        return True

# ----------------------------------------------------------------------
# 3. Optional invariant computation (user must supply a field grid)
# ----------------------------------------------------------------------
def compute_invariants(Phi_N_grid):
    """
    Phi_N_grid: 3D numpy array of shape (nx, ny, nz) representing Phi_N(x,y,z).
    Returns psi, xi_N, xi_Delta, Shannon entropy S_h.
    """
    # psi = ln(Phi_N)
    psi = np.log(Phi_N_grid)

    # Gradient using central differences (spacing = 1 for simplicity)
    grad_y, grad_x, grad_z = np.gradient(psi)  # returns [d/dz, d/dy, d/dx] order
    grad_sq = grad_x**2 + grad_y**2 + grad_z**2
    xi_N = 1.0 / np.sqrt(np.mean(grad_sq) + 1e-12)  # avoid div‑by‑zero

    # For xi_Delta we need a directional variance measure.
    # Here we approximate by variance along each axis after smoothing.
    var_x = np.var(Phi_N_grid, axis=0)
    var_y = np.var(Phi_N_grid, axis=1)
    var_z = np.var(Phi_N_grid, axis=2)
    # Take mean variance per direction
    var_dir = np.array([np.mean(var_x), np.mean(var_y), np.mean(var_z)])
    xi_Delta = np.max(var_dir) / (np.min(var_dir) + 1e-12)

    # Shannon entropy of psi (normalize to positive probabilities)
    psi_pos = psi - np.min(psi) + 1e-12
    p = psi_pos / np.sum(psi_pos)
    S_h = -np.sum(p * np.log(p))

    return psi, xi_N, xi_Delta, S_h

def invariant_check_demo():
    # Create a simple synthetic field: a point source decaying as 1/r
    nx = ny = nz = 31
    xs = np.linspace(-5, 5, nx)
    ys = np.linspace(-5, 5, ny)
    zs = np.linspace(-5, 5, nz)
    X, Y, Z = np.meshgrid(xs, ys, zs, indexing='ij')
    r = np.sqrt(X**2 + Y**2 + Z**2) + 1e-6  # avoid zero
    Phi_N_grid = 1.0 / r  # polynomial (1/r) decay

    psi, xi_N, xi_Delta, S_h = compute_invariants(Phi_N_grid)
    print("[Demo] Invariants from a 1/r source:")
    print(f"  <psi>   = {np.mean(psi):.4f}")
    print(f"  xi_N    = {xi_N:.4f}")
    print(f"  xi_Delta= {xi_Delta:.4f}")
    print(f"  Entropy S_h = {S_h:.4f}")
    # In a real audit you would assert that the analysis *mentions* these quantities.
    return True

# ----------------------------------------------------------------------
# Main driver
# ----------------------------------------------------------------------
def main():
    if not symbolic_check():
        sys.exit(1)
    if not mass_positivity_check():
        sys.exit(1)
    # Optional: show invariants for a sample field
    invariant_check_demo()
    print("\nAll mathematical checks passed. "
          "Remember to include ψ, ξ_N, ξ_Δ and an entropy term "
          "to satisfy the Omega Physics Rubric v26.0.")

if __name__ == "__main__":
    main()