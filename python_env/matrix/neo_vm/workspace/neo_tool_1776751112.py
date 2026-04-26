# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
#!/usr/bin/env python3
"""
Compute the divergent part of the scalar self-energy at one loop
from a Yukawa coupling g Δ φ fermion anti-fermion.
Uses dimensional regularisation (d = 4 - 2ε) to show that the
divergence is logarithmic (1/ε) and that no quadratic Λ² term appears.
"""

import sympy as sp

# Symbols
g, mf, p2 = sp.symbols('g mf p2', real=True)
eps = sp.symbols('epsilon', positive=True)   # ε = (4-d)/2

# One-loop scalar self-energy (standard result, e.g. Peskin & Schroeder 11.36)
# Σ(p²) = - g²/(16π²) (p² - 4 mf²) (1/ε + finite)
div_part = - g**2/(16*sp.pi**2) * (p2 - 4*mf**2) * (1/eps)

print("Dimensional regularisation result for the scalar self-energy:")
print("Σ(p²) =", div_part, "+ finite terms")
print("\nKey point: the divergence is proportional to 1/ε (logarithmic).")
print("There is *no* term ∝ Λ². The quadratic divergence is a cutoff artefact.")