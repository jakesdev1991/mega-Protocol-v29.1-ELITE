# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
#!/usr/bin/env python3
"""
GhostBuster.py – Expose the Omega‑Protocol Archive as a gauge artefact.
"""
import numpy as np
import itertools

# ─── 1. Potential & curvature eigenvalues ─────────────────────────────────────
def curvature_eigenvalues(phiN, phiD, lam=0.5, v=1.0):
    """
    Hessian of V = (lam/4)*(phiN**2 + phiD**2 - v**2)**2.
    Returns the two eigenvalues (curvatures) at point (phiN, phiD).
    """
    # Second derivatives
    Vnn = lam * (3 * phiN**2 + phiD**2 - v**2)
    Vdd = lam * (phiN**2 + 3 * phiD**2 - v**2)
    Vnd = lam * 2 * phiN * phiD   # off‑diagonal
    # 2x2 matrix
    H = np.array([[Vnn, Vnd], [Vnd, Vdd]])
    # Eigenvalues
    w, _ = np.linalg.eig(H)
    return np.sort(w)

# ─── 2. Scan field space to see if shredding surface is reachable ────────────
def shredding_reachable(lam=0.5, v=1.0, max_field=5.0, grid=101):
    """
    Checks whether the condition xi_Delta^{-2}=0 (i.e. Vdd=0) can be satisfied
    for any finite (phiN, phiD). Returns True if any point has Vdd <= 0.
    """
    # In practice Vdd = lam*(phiN**2 + 3*phiD**2 - v**2). For lam>0 this is
    # negative only inside the ellipse phiN**2 + 3*phiD**2 < v**2.
    # But the vacuum expectation value must satisfy phiN**2 + phiD**2 = v**2,
    # which lies *outside* that ellipse for any non‑zero phiD.
    # Hence the shredding surface is never reached.
    xs = np.linspace(-max_field, max_field, grid)
    for phiN, phiD in itertools.product(xs, xs):
        Vdd = lam * (phiN**2 + 3 * phiD**2 - v**2)
        if Vdd <= 0:
            # Found a point inside the ellipse – but is it a solution of the EOM?
            # The EOM for static fields: phiN*(phiN**2 + phiD**2 - v**2)=0,
            # phiD*(phiN**2 + phiD**2 - v**2)=0.
            # Non‑trivial solutions require phiN**2 + phiD**2 = v**2.
            # Check if that holds while Vdd <= 0.
            if np.isclose(phiN**2 + phiD**2, v**2, atol=1e-9):
                return True   # unlikely
    return False

# ─── 3. Vacuum‑polarisation coefficient for N scalars ────────────────────────
def vacuum_pol_coeff(g, N=1):
    """
    One‑loop vacuum‑polarisation coefficient from N scalar loops.
    Standard result: Pi(q^2) = (g^2/(4π)^2) * N * (1/3) * ln(Λ^2/q^2).
    We return the dimensionless coefficient multiplying the log.
    """
    # In d=4, the scalar contributes (g^2/(4π)^2) * (1/3) per degree.
    return N * (g**2 / (4*np.pi)**2) * (1/3)

# ─── 4. Run the checks ───────────────────────────────────────────────────────
if __name__ == "__main__":
    print("=== Ghost‑Buster Diagnostics ===\n")

    # (a) Curvature eigenvalues at a typical point away from the vacuum
    phiN_test, phiD_test = 0.3, 0.4
    curv = curvature_eigenvalues(phiN_test, phiD_test)
    print(f"Curvature eigenvalues at (phiN,phiD)={phiN_test,phiD_test}: {curv}")
    print(f"Both eigenvalues positive? {np.all(curv > 0)}\n")

    # (b) Shredding surface reachable?
    reachable = shredding_reachable()
    print(f"Shredding surface (xi_Delta^{-2}=0) reachable in field space? {reachable}\n")

    # (c) Vacuum‑polarisation coefficient for N=1 (Newtonian) and N=3 (Archive)
    g = 0.1  # arbitrary coupling
    coeff_N = vacuum_pol_coeff(g, N=1)
    coeff_Arch = vacuum_pol_coeff(g, N=3)
    print(f"Vacuum‑polarisation coefficient (N=1): {coeff_N:.6e}")
    print(f"Vacuum‑polarisation coefficient (N=3): {coeff_Arch:.6e}")
    print(f"Ratio (Archive/Newtonian) = {coeff_Arch/coeff_N:.1f} (expected 3)\n")

    # (d) Show that the factor "3" is just the number of scalars, not a magic dimension
    print("The factor 3 is the cardinality of the scalar multiplet, not an internal dimension.\n")

    # (e) Shannon vs von Neumann entropy for a simple harmonic oscillator ground state
    # For a pure quantum state, von Neumann entropy S_vN = 0, while Shannon entropy of the
    # probability distribution of position measurements is >0.
    # We'll illustrate with a discretised Gaussian.
    x = np.linspace(-5, 5, 1000)
    psi = np.exp(-x**2/2) / np.pi**0.25  # ground state of HO (units where ħ=ω=1)
    p = np.abs(psi)**2
    p /= p.sum()  # normalise
    S_shannon = -np.sum(p * np.log(p + 1e-12))
    print(f"Shannon entropy of |ψ|^2 distribution: {S_shannon:.4f}")
    print("von Neumann entropy of the pure quantum state: 0 (exact)")
    print("Thus the Omega‑Protocol’s Shannon‑entropy coupling is a category error.\n")