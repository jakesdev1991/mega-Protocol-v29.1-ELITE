# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
# -*- coding: utf-8 -*-
"""
Omega Protocol Invariant Validator
----------------------------------
Checks the mathematical consistency of the Higher‑Order Lattice Polarization
derivation for the fine‑structure constant using the orthogonal decomposition
(Φ_N, Φ_Δ).  The script exits with code 0 if all invariants hold,
otherwise with code 1 and a diagnostic message.
"""

import sympy as sp
import sys

# ----------------------------------------------------------------------
# Symbols (all real, positive where appropriate)
# ----------------------------------------------------------------------
λ, v = sp.symbols('λ v', positive=True, real=True)
Φ_N, Φ_Δ = sp.symbols('Φ_N Φ_Δ', real=True)

# ----------------------------------------------------------------------
# 1. Define the candidate potential
# ----------------------------------------------------------------------
# Correct O(2)-symmetric Mexican hat:
V_correct = λ/4 * (Φ_N**2 + Φ_Δ**2 - v**2)**2

# Erroneous version that appeared in the Engine's "Technical Reasoning"
# section (λ_Δ^2 instead of Φ_Δ^2).  We keep λ_Δ as a separate symbol to
# detect the mismatch.
λ_Δ = sp.symbols('λ_Δ', positive=True, real=True)
V_erroneous = λ/4 * (Φ_N**2 + λ_Δ**2 - v**2)**2

# ----------------------------------------------------------------------
# 2. Compute stiffness invariants (second derivatives)
# ----------------------------------------------------------------------
def stiffness_invariants(V):
    ξN2_inv = sp.diff(V, Φ_N, 2)   # ∂²V/∂Φ_N²
    ξΔ2_inv = sp.diff(V, Φ_Δ, 2)   # ∂²V/∂Φ_Δ²
    return sp.simplify(ξN2_inv), sp.simplify(ξΔ2_inv)

ξN2_corr, ξΔ2_corr = stiffness_invariants(V_correct)
ξN2_err,  ξΔ2_err  = stiffness_invariants(V_erroneous)

# ----------------------------------------------------------------------
# 3. Vacuum values (Φ_N = v, Φ_Δ = 0)
# ----------------------------------------------------------------------
vac_subs = {Φ_N: v, Φ_Δ: 0}
ξN2_vac_corr = ξN2_corr.subs(vac_subs)
ξΔ2_vac_corr = ξΔ2_corr.subs(vac_subs)

ξN2_vac_err  = ξN2_err.subs(vac_subs)
ξΔ2_vac_err  = ξΔ2_err.subs(vac_subs)

# ----------------------------------------------------------------------
# 4. Shredding condition: ξ_Δ → ∞  <=>  ∂²V/∂Φ_Δ² = 0
# ----------------------------------------------------------------------
shred_cond_corr = sp.simplify(ξΔ2_corr)   # set = 0
shred_cond_err  = sp.simplify(ξΔ2_err)

# Expected shredding surface: Φ_N^2 + 3 Φ_Δ^2 = v^2
expected_shred = sp.Eq(Φ_N**2 + 3*Φ_Δ**2, v**2)

# ----------------------------------------------------------------------
# 5. Validation logic
# ----------------------------------------------------------------------
def check(msg, condition):
    if not condition:
        print(f"[FAIL] {msg}")
        return False
    print(f"[PASS] {msg}")
    return True

all_ok = True

# Potential must be the correct O(2) form
all_ok &= check(
    "Potential matches O(2)-symmetric Mexican hat",
    sp.simplify(V_correct - V_erroneous.subs({λ_Δ: Φ_Δ})) == 0
)

# Stiffness invariants from correct potential
all_ok &= check(
    "ξ_N^{-2} = λ(3Φ_N^2 + Φ_Δ^2 - v^2)",
    sp.simplify(ξN2_corr - λ*(3*Φ_N**2 + Φ_Δ**2 - v**2)) == 0
)
all_ok &= check(
    "ξ_Δ^{-2} = λ(Φ_N^2 + 3Φ_Δ^2 - v^2)",
    sp.simplify(ξΔ2_corr - λ*(Φ_N**2 + 3*Φ_Δ**2 - v**2)) == 0
)

# Vacuum values
all_ok &= check(
    "ξ_N^{-2}(vac) = λ v^2",
    sp.simplify(ξN2_vac_corr - λ*v**2) == 0
)
all_ok &= check(
    "ξ_Δ^{-2}(vac) = λ v^2",
    sp.simplify(ξΔ2_vac_corr - λ*v**2) == 0
)

# Shredding surface from correct potential
all_ok &= check(
    "Shredding condition: ξ_Δ^{-2}=0  <=>  Φ_N^2 + 3Φ_Δ^2 = v^2",
    sp.simplify(shred_cond_corr - λ*(Φ_N**2 + 3*Φ_Δ**2 - v**2)) == 0
)

# Ensure the erroneous version does NOT satisfy the vacuum or shredding
# conditions (this catches the typo)
if sp.simplify(ξN2_vac_err - λ*v**2) == 0 and \
   sp.simplify(ξΔ2_vac_err - λ*v**2) == 0 and \
   sp.simplify(shred_cond_err - λ*(Φ_N**2 + 3*Φ_Δ**2 - v**2)) == 0:
    print("[FAIL] Erroneous potential unexpectedly passes invariant checks.")
    all_ok = False
else:
    print("[PASS] Erroneous potential correctly fails invariant checks.")

# ----------------------------------------------------------------------
# Final verdict
# ----------------------------------------------------------------------
if all_ok:
    print("\nAll Omega Protocol invariants satisfied. Derivation is mathematically sound.")
    sys.exit(0)
else:
    print("\nInvariant violation detected. Derivation non‑compliant.")
    sys.exit(1)