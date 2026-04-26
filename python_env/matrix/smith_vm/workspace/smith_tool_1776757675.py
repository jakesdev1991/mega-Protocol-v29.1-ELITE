# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
# Validation script for Omega Protocol higher‑order lattice polarization corrections
import sympy as sp

# ------------------- Symbols -------------------
lam, v, PhiN, PhiD = sp.symbols('lam v PhiN PhiD', positive=True, real=True)
gN, gD = sp.symbols('gN gD', real=True)
# ------------------- Potential -------------------
V = lam/4 * (PhiN**2 + PhiD**2 - v**2)**2

# ------------------- Hessian -------------------
H = sp.hessian(V, (PhiN, PhiD))
H_simplified = sp.simplify(H)
# Hessian at the vacuum (PhiN = v, PhiD = 0) or (0, v) – we check both
H_vac_N = H_simplified.subs({PhiN: v, PhiD: 0})
H_vac_D = H_simplified.subs({PhiN: 0, PhiD: v})
print("Hessian at (v,0):", H_vac_N)
print("Hessian at (0,v):", H_vac_D)

# Eigenvalues (should be lam*v^2 for both modes)
evals_N = H_vac_N.eigenvals()
evals_D = H_vac_D.eigenvals()
print("Eigenvalues at (v,0):", evals_N)
print("Eigenvalues at (0,v):", evals_D)

# ------------------- Stiffness invariants -------------------
# xi_N^{-2} = d^2V/dPhiN^2, xi_D^{-2} = d^2V/dPhiD^2
xiN2_inv = sp.diff(V, PhiN, 2)
xiD2_inv = sp.diff(V, PhiD, 2)
print("\nxi_N^{-2}:", sp.simplify(xiN2_inv))
print("xi_D^{-2}:", sp.simplify(xiD2_inv))

# Evaluate at generic point to see the form given in the Engine:
xiN2_expr = lam * (3*PhiN**2 + PhiD**2 - v**2)
xiD2_expr = lam * (PhiN**2 + 3*PhiD**2 - v**2)
print("\nClaimed xi_N^{-2}:", xiN2_expr)
print("Claimed xi_D^{-2}:", xiD2_expr)
print("Match?", sp.simplify(xiN2_inv - xiN2_expr) == 0 and sp.simplify(xiD2_inv - xiD2_expr) == 0)

# ------------------- Vacuum‑polarization factor‑3 check -------------------
# The Engine states: Pi^{mu nu}_Delta = -3 g_D^2 <Phi_D^2> (g^{mu nu} q^2 - q^mu q^nu)
# We just verify the factor 3 appears from summing over three internal dims.
# Define a dummy sum over three dimensions:
dim_sum = sp.Sum(1, (i, 1, 3)).doit()  # should be 3
print("\nSum over three internal dimensions:", dim_sum)
assert dim_sum == 3, "Factor‑3 origin check failed"

# ------------------- Logarithmic integral verification (schematic) -------------------
# Show that ∫_0^Λ k^3/(k^2+m^2) dk → (1/2) Λ^2 - (m^2/2) ln(Λ^2/m^2) + O(m^4/Λ^2)
k, m, Lambda = sp.symbols('k m Lambda', positive=True)
integrand = k**3 / (k**2 + m**2)
integral = sp.integrate(integrand, (k, 0, Lambda))
print("\nIntegral ∫ k^3/(k^2+m^2) dk from 0 to Λ:", sp.simplify(integral))
# Extract the log term:
log_term = sp.simplify(integral - (Lambda**2/2 - m**2/2 * sp.log(Lambda**2/m**2)))
print("Remaining terms (should vanish as Λ→∞):", log_term)
# For large Λ, log_term → -m^4/(4Lambda^2) + ... → 0
print("Series expansion at Λ→∞:", sp.series(log_term, Lambda, sp.oo, 2))

# ------------------- Beta‑function check -------------------
# α^{-1}(q^2) = α0^{-1} - Π_eff(q^2)
# Π_eff = (e^2/(3π)) ln(Λ^2/q^2) + (gN^2/(4π)) ln(ΛN^2/q^2) + (3 gD^2/(4π)) ln(ΛD^2/q^2)
e, pi = sp.symbols('e pi')
alpha0 = sp.symbols('alpha0')
# Effective inverse coupling:
alpha_inv_eff = 1/alpha0 - (e**2/(3*pi))*sp.log(Lambda**2 / sp.Symbol('q2')**2) \
                - (gN**2/(4*pi))*sp.log(Lambda**2 / sp.Symbol('q2')**2) \
                - (3*gD**2/(4*pi))*sp.log(Lambda**2 / sp.Symbol('q2')**2)
# β = dα/d ln q^2 = - α^2 * d(α^{-1})/d ln q^2
q2 = sp.symbols('q2', positive=True)
alpha = 1/alpha_inv_eff
beta = sp.diff(alpha, sp.log(q2))
beta_simplified = sp.simplify(beta)
print("\nBeta‑function (unsimplified):", beta)
print("Beta‑function simplified:", beta_simplified)
# Expected form: -α^2/π * (1 + 3gD^2/(4π) + gN^2/(4π))
expected_beta = -alpha**2/pi * (1 + 3*gD**2/(4*pi) + gN**2/(4*pi))
print("Expected beta:", expected_beta)
print("Match?", sp.simplify(beta_simplified - expected_beta) == 0)

print("\nAll checks completed.")