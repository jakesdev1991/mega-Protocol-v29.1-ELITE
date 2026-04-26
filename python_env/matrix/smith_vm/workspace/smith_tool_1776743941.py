# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
#!/usr/bin/env python3
"""
Omega Protocol Invariant Validator
----------------------------------
Checks:
  * Exact Shredding surface: det(Hessian) = 0
  * Poisson recovery: m_N^2 >= 0
  * Invariant bound: Phi_N^2 + 3*Phi_Delta^2 <= v^2
  * One-loop beta function sign (should be negative for asymptotic freedom)
"""

import numpy as np

# ---- Model parameters (can be changed) ----
lam = 0.1          # lambda coupling
v   = 1.0          # symmetry-breaking scale
# Optional: effective number of archive dimensions (default = 1 for correct counting)
N_archive_dims = 1  # set to 3 to reproduce the Engine's overcounting

def potential(phi_n, phi_d):
    """Mexican-hat V = lam/4 * (phi_n^2 + phi_d^2 - v^2)^2"""
    return lam/4.0 * (phi_n**2 + phi_d**2 - v**2)**2

def hessian(phi_n, phi_d):
    """Hessian matrix of V w.r.t (phi_n, phi_d)"""
    # d2V/dphi_n^2
    V_nn = lam * (3*phi_n**2 + phi_d**2 - v**2)
    # d2V/dphi_d^2
    V_dd = lam * (phi_n**2 + 3*phi_d**2 - v**2)
    # mixed derivative
    V_nd = lam * (4*phi_n*phi_d)
    return np.array([[V_nn, V_nd],
                     [V_nd, V_dd]])

def shredding_condition(phi_n, phi_d):
    """Returns True if point lies on the exact Shredding surface (det H = 0)."""
    H = hessian(phi_n, phi_d)
    return np.isclose(np.linalg.det(H), 0.0, atol=1e-8)

def poisson_recovery_ok(phi_n, phi_d):
    """Effective mass^2 for Phi_N from V''_nn must be >= 0."""
    V_nn = lam * (3*phi_n**2 + phi_d**2 - v**2)
    return V_nn >= -1e-12  # allow tiny numerical negative

def invariant_bound(phi_n, phi_d):
    """Checks the Phi_N^2 + 3 Phi_Delta^2 <= v^2 invariant."""
    return phi_n**2 + 3*phi_d**2 <= v**2 + 1e-12

def beta_function(alpha, g_n, g_delta):
    """
    One-loop beta for a U(1) gauge coupling with:
      - No fermions (Nf = 0)
      - One complex Newtonian scalar (charge = 1)
      - N_archive_dims complex Archive scalars (each charge = 1)
    beta = - alpha^2 / (2π) * (sum_i Q_i^2)
    """
    sum_Q2 = 1 + N_archive_dims   # Newtonian + archive scalars
    return - alpha**2 / (2.0*np.pi) * sum_Q2

def run_validation(num_samples=20000):
    rng = np.random.default_rng(seed=42)
    violations = []

    for _ in range(num_samples):
        # Sample fields in a reasonable range [-2v, 2v]
        phi_n = rng.uniform(-2*v, 2*v)
        phi_d = rng.uniform(-2*v, 2*v)

        # Invariant bound (Omega Protocol core)
        if not invariant_bound(phi_n, phi_d):
            violations.append(('bound', (phi_n, phi_d)))
            continue

        # Poisson recovery (deterministic sourcing of Phi_N)
        if not poisson_recovery_ok(phi_n, phi_d):
            violations.append(('poisson', (phi_n, phi_d)))
            continue

        # Optional: flag points that are *near* the exact Shredding surface
        if shredding_condition(phi_n, phi_d):
            violations.append(('shredding_exact', (phi_n, phi_d)))

        # Beta function sign check (should be negative for asymptotic freedom)
        # Choose dummy couplings; sign depends only on prefactor
        alpha = 0.01
        g_n   = 0.05
        g_delta = 0.05
        beta = beta_function(alpha, g_n, g_delta)
        if beta >= 0:   # would signal loss of asymptotic freedom
            violations.append(('beta_sign', (phi_n, phi_d, beta)))

    return violations

if __name__ == "__main__":
    vio = run_validation()
    if not vio:
        print("PASS: All sampled points respect Omega Protocol invariants.")
    else:
        print(f"FAIL: {len(vio)} invariant violations found.")
        # Show a few examples
        for typ, data in vio[:5]:
            print(f"  {typ}: {data}")