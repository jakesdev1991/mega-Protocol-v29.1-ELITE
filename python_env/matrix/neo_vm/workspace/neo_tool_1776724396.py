# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import sympy as sp

# Symbols
ε, ΦΔ = sp.symbols('ε ΦΔ', real=True)

# Exact log term
log_exact = sp.log(1 - 2*ε*sp.cosh(ΦΔ) + ε**2)

# Correct series up to O(ε^2)
log_series_correct = sp.series(log_exact, ε, 0, 3).removeO()
# Multiply by 1/2 as required for Π(0)
Pi_series_correct = sp.Rational(1,2) * log_series_correct

# Engine's (incorrect) series
Pi_series_engine = ε*sp.cosh(ΦΔ) - (ε**2/2)*(1 - 2*sp.cosh(ΦΔ)**2)

# Difference
diff = sp.simplify(Pi_series_correct - Pi_series_engine)
print("Correct Π(0) series:", Pi_series_correct)
print("Engine's Π(0) series:", Pi_series_engine)
print("Difference (should be zero if correct):", diff)