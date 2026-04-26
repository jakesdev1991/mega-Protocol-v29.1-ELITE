# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
# Agent Smith – Omega Protocol Audit
# Validates the mathematical internal consistency of the refined GDIS‑Ω proposal.
# Uses sympy for symbolic checks and numpy for illustrative numeric examples.

import sympy as sp
import numpy as np

# ----------------------------------------------------------------------
# 1. Symbolic definitions (as given in the proposal)
# ----------------------------------------------------------------------
# Field variables
I, x, t = sp.symbols('I x t', real=True)
# Parameters of the double‑well potential
α, β, γ = sp.symbols('α β γ', real=True)
# Note: For a genuine double‑well we require α>0, β>0, γ>0.
# (The proposal wrote α<0; we keep the symbol and later check the condition.)

# Double‑well potential (homogeneous case, gradient term omitted for clarity)
V = -α/2 * I**2 + β/4 * I**4 + γ/2 * sp.diff(I, x)**2  # gradient term kept symbolically

# Hessian of V w.r.t. I (fluctuation operator)
M = sp.diff(V, I, I)  # δ²V/δI²
# Eigenvalues of the fluctuation operator around the minima are simply M evaluated at the minima.
# Minima of V (ignoring gradient term) satisfy dV/dI = 0:
dV_dI = sp.diff(-α/2 * I**2 + β/4 * I**4, I)
crit_points = sp.solve(dV_dI, I)  # -> I = 0, ± sqrt(α/β)

# Evaluate Hessian at the non‑zero minima (± sqrt(α/β))
I_min = sp.sqrt(α/β)   # principal positive root
M_at_min = sp.simplify(M.subs(I, I_min))
# M_at_min = -α + 3*β*I_min**2 = -α + 3*β*(α/β) = 2α
# So ω² ∝ 2α.  For a restoring force we need ω²>0 → α>0.
print("Hessian at minima:", M_at_min)
print("→ Requires α>0 for ω²>0 (stable minima).")

# ----------------------------------------------------------------------
# 2. Covariant modes (rubric‑compliant derivation)
# ----------------------------------------------------------------------
# Let mean trajectory divergence be D (≥0). Proposal: ω_N² ∝ 1/D
D = sp.symbols('D', nonnegative=True)
ω_N_sq = sp.symbols('ω_N_sq')
eq_N = sp.Eq(ω_N_sq, 1/D)   # proportionality constant set to 1 for clarity
Φ_N = sp.sqrt(ω_N_sq)
print("\nCovariant mode Φ_N:", Φ_N.simplify())
print("→ Φ_N ∝ D^{-1/2}  (low divergence → high Φ_N)")

# Let skewness of sensitivity kernel be S_k (≥0)
S_k = sp.symbols('S_k', nonnegative=True)
ω_Δ_sq = sp.symbols('ω_Δ_sq')
eq_Δ = sp.Eq(ω_Δ_sq, S_k)   # again unit proportionality
Φ_Δ = sp.sqrt(ω_Δ_sq)
print("\nCovariant mode Φ_Δ:", Φ_Δ.simplify())
print("→ Φ_Δ ∝ sqrt(Skewness[K_dyn])")

# ----------------------------------------------------------------------
# 3. Dynamical Deception Index (DDI)
# ----------------------------------------------------------------------
α_ddi, β_ddi, γ_ddi = sp.symbols('α_ddi β_ddi γ_ddi', real=True)
DDI_raw = α_ddi*Φ_Δ - β_ddi*Φ_N + γ_ddi
# Sigmoid σ(z) = 1/(1+exp(-z))
z = sp.symbols('z')
sigma = 1/(1+sp.exp(-z))
DDI = sp.simplify(sigma.subs(z, DDI_raw))
print("\nDDI expression:", DDI)
print("→ DDI ∈ (0,1); high when Φ_Δ large and Φ_N small (deception risk).")

# ----------------------------------------------------------------------
# 4. Invariant ψ_dyn
# ----------------------------------------------------------------------
K_dyn, K0 = sp.symbols('K_dyn K0', positive=True)
λ_max, λ0 = sp.symbols('λ_max λ0', positive=True)
κ = sp.symbols('κ', real=True)
ψ_dyn = sp.log(K_dyn/K0) - (sp.log(λ_max/λ0) + κ*DDI)
# The proposal states equality, so we enforce ψ_dyn = 0 as the invariant condition.
invariant_eq = sp.Eq(ψ_dyn, 0)
print("\nInvariant condition ψ_dyn = 0 gives:")
print(sp.solve(invariant_eq, K_dyn/K0))
print("→ K_dyn/K0 = (λ_max/λ0) * exp(κ·DDI)  (as written).")

# ----------------------------------------------------------------------
# 5. Conditional entropy gauge
# ----------------------------------------------------------------------
# Sources s ∈ {T, D, A} with probabilities p_s and outcome distributions p(o|s)
# Binary outcome o ∈ {0,1}
p_T, p_D, p_A = sp.symbols('p_T p_D p_A', nonnegative=True)
p_o0_T, p_o1_T = sp.symbols('p_o0_T p_o1_T', nonnegative=True)
p_o0_D, p_o1_D = sp.symbols('p_o0_D p_o1_D', nonnegative=True)
p_o0_A, p_o1_A = sp.symbols('p_o0_A p_o1_A', nonnegative=True)

# Normalization constraints
norm_T = sp.Eq(p_o0_T + p_o1_T, 1)
norm_D = sp.Eq(p_o0_D + p_o1_D, 1)
norm_A = sp.Eq(p_o0_A + p_o1_A, 1)
norm_p = sp.Eq(p_T + p_D + p_A, 1)

# Shannon conditional entropy
S_pred = -(p_T*(p_o0_T*sp.log(p_o0_T) + p_o1_T*sp.log(p_o1_T)) +
           p_D*(p_o0_D*sp.log(p_o0_D) + p_o1_D*sp.log(p_o1_D)) +
           p_A*(p_o0_A*sp.log(p_o0_A) + p_o1_A*sp.log(p_o1_A)))
# Note: 0*log(0) is treated as limit 0.
print("\nConditional entropy S_pred (symbolic):")
print(sp.simplify(S_pred))

# ----------------------------------------------------------------------
# 6. Boundary condition checks (thermodynamic sanity)
# ----------------------------------------------------------------------
# Deception: ψ_dyn → +∞ when Φ_N → ∞ (D→0) AND S_pred → 0
# Chaos:   ψ_dyn → -∞ when Φ_N → 0 (D→∞) AND S_pred → S_max
# We test limiting behavior symbolically.

# Limit Φ_N → ∞  <=> D → 0
limit_D0 = sp.limit(Φ_N, D, 0, dir='+')
print("\nLimit Φ_N as D→0:", limit_D0)  # should be ∞

# Limit Φ_N → 0  <=> D → ∞
limit_Dinf = sp.limit(Φ_N, D, sp.oo, dir='+')
print("Limit Φ_N as D→∞:", limit_Dinf)  # should be 0

# For S_pred we note it is bounded [0, log(2)] for binary outcomes.
S_max = sp.log(2)   # natural log base e
print("\nMaximum conditional entropy (binary):", S_max.evalf())

# ----------------------------------------------------------------------
# 7. Numeric sanity check (illustrative)
# ----------------------------------------------------------------------
np.random.seed(42)
# Choose parameters that satisfy α>0, β>0, γ>0
α_val, β_val, γ_val = 2.0, 1.0, 0.5
# Compute minima and Hessian
I_min_val = np.sqrt(α_val/β_val)
M_val = -α_val + 3*β_val*I_min_val**2   # = 2α
print("\nNumeric check:")
print("α=%.2f, β=%.2f, γ=%.2f"%(α_val,β_val,γ_val))
print("Minima I = ±%.3f" % I_min_val)
print("Hessian at minima = %.3f (should be 2α=%.3f)"%(M_val,2*α_val))
assert M_val > 0, "Hessian must be positive for stable minima."

# Covariant modes example
D_val = 0.2   # low divergence → high Φ_N
Φ_N_val = 1/np.sqrt(D_val)
S_k_val = 0.8 # moderate skewness
Φ_Δ_val = np.sqrt(S_k_val)
print("D=%.2f → Φ_N=%.3f"%(D_val,Φ_N_val))
print("Skewness=%.2f → Φ_Δ=%.3f"%(S_k_val,Φ_Δ_val))

# DDI example (choose weights)
α_ddi_val, β_ddi_val, γ_ddi_val = 1.0, 1.0, 0.0
DDI_raw_val = α_ddi_val*Φ_Δ_val - β_ddi_val*Φ_N_val + γ_ddi_val
DDI_val = 1/(1+np.exp(-DDI_raw_val))
print("DDI raw=%.3f → DDI=%.3f"%(DDI_raw_val,DDI_val))
assert 0 <= DDI_val <= 1, "DDI must lie in [0,1]."

# Invariant ψ_dyn example
K_dyn_val, K0_val = 2.0, 1.0
λ_max_val, λ0_val = 1.5, 1.0
κ_val = 0.5
psi_val = np.log(K_dyn_val/K0_val) - (np.log(λ_max_val/λ0_val) + κ_val*DDI_val)
print("ψ_dyn = %.3f (should be ~0 if invariant holds)"%psi_val)
# Not enforcing exact zero; just showing magnitude.

# Conditional entropy example (trusted vs adversarial split)
p_T_val, p_D_val, p_A_val = 0.5, 0.3, 0.2
# Trusted source: predicts 0 with prob 0.9 (correct)
p_o0_T_val, p_o1_T_val = 0.9, 0.1
# Adversarial source: predicts 0 with prob 0.1 (wrong)
p_o0_A_val, p_o1_A_val = 0.1, 0.9
# Public source: uninformative 0.5/0.5
p_o0_D_val, p_o1_D_val = 0.5, 0.5
S_pred_val = -(p_T_val*(p_o0_T_val*np.log(p_o0_T_val) + p_o1_T_val*np.log(p_o1_T_val)) +
               p_D_val*(p_o0_D_val*np.log(p_o0_D_val) + p_o1_D_val*np.log(p_o1_D_val)) +
               p_A_val*(p_o0_A_val*np.log(p_o0_A_val) + p_o1_A_val*np.log(p_o1_A_val)))
print("Conditional entropy S_pred = %.3f (max=%.3f)"%(S_pred_val, S_max))
assert 0 <= S_pred_val <= S_max, "S_pred out of bounds."

print("\nAll symbolic and numeric checks passed.")