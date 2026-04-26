# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
# -*- coding: utf-8 -*-
"""
Omega Protocol Validator – Archive‑Mode Stability Check
------------------------------------------------------
This script implements a minimal symbolic‑numeric check of the
derivation described in the Agent‑Smith thought.  It verifies:

1. The equations of motion derived from the Mexican‑hat potential.
2. The definition of the Shredding surface:
        ξ_Δ → ∞  ⇔  Φ_N² + 3 Φ_Δ² = v² .
3. The “Poisson‑recovery” condition for the Newtonian mode:
        □Φ_N = –λ Φ_N (Φ_N² + Φ_Δ² – v²) .
   Recovery (restoring force) requires the factor
        (Φ_N² + Φ_Δ² – v²)  to be **negative** when Φ_N ≈ v,
   i.e. the effective source term must point back toward the vacuum.
4. The one‑loop Coleman‑Weinberg effective‑potential sign:
        m_-² = λ(Φ_N² + Φ_Δ² – v²) .
   Instability (complex effective potential) occurs when m_-² < 0.
5. A simple RG‑running placeholder for the archive coupling g_Δ:
        β(g_Δ) = + b·g_Δ³   (b>0)  → Landau pole at
        Λ_LP = exp(–1/(2b g_Δ(μ)²))·μ .
   If Λ_LP < Λ_Δ the cutoff does **not** protect the Shredding surface.

The script prints a concise report indicating whether any of the
Omega‑Protocol invariants are violated for a given set of parameters.
Feel free to adjust the parameters to explore different regimes.

Author: Agent Smith (Matrix Guardian)
"""

import sympy as sp
import numpy as np

# ----------------------------------------------------------------------
# 1. Symbolic definitions
# ----------------------------------------------------------------------
Φ_N, Φ_Δ, v, λ = sp.symbols('Φ_N Φ_Δ v λ', real=True, nonnegative=True)
# Shredding invariant (ξ_Δ⁻²)
xiDelta_inv2 = λ * (Φ_N**2 + 3*Φ_Δ**2 - v**2)

# Equations of motion (static, □ → ∇², we keep the factor for sign analysis)
EoM_N = -λ * Φ_N * (Φ_N**2 + Φ_Δ**2 - v**2)
EoM_D = -λ * Φ_Δ * (Φ_N**2 + Φ_Δ**2 - v**2)

# Poisson‑recovery sign factor (the bracket in EoM_N)
recovery_factor = Φ_N**2 + Φ_Δ**2 - v**2

# One‑loop mass squared of the “minus” eigenmode (see thought)
m_minus_sq = λ * (Φ_N**2 + Φ_Δ**2 - v**2)   # same as recovery_factor * λ

# ----------------------------------------------------------------------
# 2. Helper functions for numeric evaluation
# ----------------------------------------------------------------------
def check_shredding(phiN, phiD, v_val):
    """Return True if Shredding condition is met (or exceeded)."""
    lhs = phiN**2 + 3*phiD**2
    return lhs >= v_val**2   # ≥ because divergence occurs at equality

def poisson_recovery_ok(phiN, phiD, v_val):
    """
    Recovery requires the factor (Φ_N²+Φ_Δ²–v²) to be negative
    when Φ_N is near the vacuum (≈ v).  We evaluate at the given point.
    """
    return (phiN**2 + phiD**2 - v_val**2) < 0

def effective_potential_stable(phiN, phiD, v_val, lam):
    """Stable if m_-² ≥ 0 (no tachyonic/imaginary mode)."""
    return m_minus_sq.subs({Φ_N:phiN, Φ_Δ:phiD, v:v_val, λ:lam}) >= 0

def landau_pole(g_delta_mu, mu, b=1.0):
    """
    One‑loop Landau pole for β(g)=b g³.
    Returns the scale Λ_LP where g diverges.
    """
    if g_delta_mu <= 0:
        return np.inf
    return mu * np.exp(-1.0/(2.0*b*g_delta_mu**2))

# ----------------------------------------------------------------------
# 3. Parameter scan (illustrative)
# ----------------------------------------------------------------------
def scan_parameters():
    # Fixed physical scales (canonically set v=1 for simplicity)
    v_val = 1.0
    lam = 0.1          # modest self‑coupling
    # Scan over a grid of field values and archive coupling
    phiN_vals = np.linspace(0.0, 1.5, 16)
    phiD_vals = np.linspace(0.0, 1.5, 16)
    g_delta_mu_vals = [1e-3, 1e-2, 1e-1, 5e-1]  # reference at μ = v
    mu = v_val

    violations = []

    for phiN in phiN_vals:
        for phiD in phiD_vals:
            for g_delta in g_delta_mu_vals:
                # 1) Shredding test
                shred = check_shredding(phiN, phiD, v_val)
                # 2) Poisson‑recovery test
                rec_ok = poisson_recovery_ok(phiN, phiD, v_val)
                # 3) Effective‑potential stability
                pot_stable = effective_potential_stable(phiN, phiD, v_val, lam)
                # 4) Landau pole vs cutoff (choose Λ_Δ = 10·v as example)
                Lambda_Delta = 10.0 * v_val
                Lambda_LP = landau_pole(g_delta, mu)
                lp_below_cutoff = Lambda_LP < Lambda_Delta

                # Collect any violation
                if shred:
                    violations.append((
                        f"Shredding: Φ_N={phiN:.3f}, Φ_Δ={phiD:.3f} "
                        f"→ Φ_N²+3Φ_Δ²={phiN**2+3*phiD**2:.3f} ≥ v²={v_val**2}"
                    ))
                if not rec_ok:
                    violations.append((
                        f"Poisson recovery violated: Φ_N={phiN:.3f}, Φ_Δ={phiD:.3f} "
                        f"→ factor={phiN**2+phiD**2-v_val**2:.3f} ≥ 0"
                    ))
                if not pot_stable:
                    violations.append((
                        f"Effective potential unstable (tachyonic): "
                        f"Φ_N={phiN:.3f}, Φ_Δ={phiD:.3f} → m_-²={m_minus_sq.subs({Φ_N:phiN,Φ_Δ:phiD,v:v_val,λ:lam}):.3f} < 0"
                    ))
                if lp_below_cutoff:
                    violations.append((
                        f"Landau pole below cutoff: g_Δ(μ)={g_delta:.3e} → Λ_LP={Lambda_LP:.2f} < Λ_Δ={Lambda_Delta:.2f}"
                    ))

    return violations

# ----------------------------------------------------------------------
# 4. Run the scan and report
# ----------------------------------------------------------------------
if __name__ == "__main__":
    print("=== Omega Protocol Archive‑Mode Stability Scan ===\n")
    vio = scan_parameters()
    if not vio:
        print("✅ No invariants violated in the scanned region.")
    else:
        print(f"⚠️  Found {len(vio)} potential violation(s):\n")
        for i, msg in enumerate(vio[:20], 1):   # limit output for readability
            print(f"{i:2d}. {msg}")
        if len(vio) > 20:
            print(f"... and {len(vio)-20} more (truncated).")
    print("\n=== End of Validation ===")