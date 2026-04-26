# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
# -*- coding: utf-8 -*-
"""
Validate the internal consistency of the invariant ψ
    ψ = ln[1 + (α₀/π) Π_Δ(0)]
derived from the mass‑shift definition:
    m_eff² = m₀² + δm_Δ²,
    ψ = ln(m_eff² / m₀²)
with the UV scale m₀² = π / a².
"""

import sympy as sp

# Symbols (all positive, real)
α0, π, ΠΔ0, a = sp.symbols('α0 π ΠΔ0 a', positive=True)

# Original definitions from the Engine's pleading
m0_sq   = π / a**2                                 # UV scale
δmΔ_sq_orig = (α0 / a**2) * ΠΔ0                    # original mass‑shift
ψ_orig  = sp.log(1 + (α0 / π) * ΠΔ0)               # target invariant
ψ_from_orig = sp.log(1 + δmΔ_sq_orig / m0_sq)      # ψ computed from definitions

# Repaired (erroneous) definition of δm_Δ²
δmΔ_sq_rep = (α0 / π) * ΠΔ0                        # <-- incorrect substitution
ψ_from_rep = sp.log(1 + δmΔ_sq_rep / m0_sq)       # ψ using the repaired term

# Simplify differences
diff_orig = sp.simplify(ψ_orig - ψ_from_orig)
diff_rep  = sp.simplify(ψ_orig - ψ_from_rep)

print("Difference (original definition):", diff_orig)   # should be 0
print("Difference (repaired definition):", diff_rep)   # non‑zero → inconsistency

# Optional: show the explicit forms
print("\nTarget ψ:", ψ_orig)
print("ψ from original def:", ψ_from_orig)
print("ψ from repaired def :", ψ_from_rep)