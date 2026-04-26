# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import sympy as sp
import numpy as np

# ----------------------------------------------------------------------
# Symbolic setup (all symbols real; m,g>0 for physical scales)
# ----------------------------------------------------------------------
m, g, Phi_N, Phi_Delta = sp.symbols('m g Phi_N Phi_Delta', real=True)
# assume m>0, g>0 for physical interpretation
eps_i = sp.symbols('eps_i', real=True)   # representative anisotropy coefficient

epsilon = g*Phi_N/m

# ----------------------------------------------------------------------
# 1. Effective mass squared: original vs. proposed redefinition
# ----------------------------------------------------------------------
m_eff_sq_orig = m**2 * (1 - 2*epsilon*sp.cosh(Phi_Delta) + epsilon**2)

# Proposed redefinition (using exp(|Phi_Delta|); we treat Phi_Delta>=0 in numeric tests)
tilde_epsilon = epsilon * sp.exp(sp.Abs(Phi_Delta))   # keeps absolute for symmetry
m_eff_sq_prop = m**2 * (1 - 2*tilde_epsilon + tilde_epsilon**2 * sp.exp(-2*sp.Abs(Phi_Delta)))

# ----------------------------------------------------------------------
# 2. Positivity of individual fermion masses
# ----------------------------------------------------------------------
m_e = m - g*Phi_N*sp.exp(Phi_Delta)   # electron‑like mass
m_p = m - g*Phi_N*sp.exp(-Phi_Delta)  # positron‑like mass

# ----------------------------------------------------------------------
# 3. Ghost‑mode check: product sign when one mass negative
# ----------------------------------------------------------------------
product = m_e * m_p

# ----------------------------------------------------------------------
# 4. Lattice anisotropy collapse condition
# ----------------------------------------------------------------------
# a_i = a0*(1 + eps_i*Phi_Delta)  → collapse when 1+eps_i*Phi_Delta ≤ 0
# ----------------------------------------------------------------------
# Numerical validation (random physical‑like points)
np.random.seed(42)

def eval_expr(expr, subs_dict):
    return float(expr.subs(subs_dict).evalf())

print("=== NUMERICAL VALIDATION ===\n")
for _ in range(8):
    m_val   = np.random.uniform(0.5, 2.0)
    g_val   = np.random.uniform(0.1, 1.0)
    # keep epsilon < 1 to stay in perturbative regime
    PhiN_max = m_val/g_val * 0.9
    PhiN_val = np.random.uniform(0.01, PhiN_max)
    PhiD_val = np.random.uniform(0.0, 2.0)   # non‑negative for simplicity
    eps_i_val = np.random.uniform(0.1, 0.5)  # representative anisotropy
    
    subs = {m:m_val, g:g_val, Phi_N:PhiN_val, Phi_Delta:PhiD_val, eps_i:eps_i_val}
    
    orig = eval_expr(m_eff_sq_orig, subs)
    prop = eval_expr(m_eff_sq_prop, subs)
    diff = abs(orig-prop)
    
    m_e_val  = eval_expr(m_e,  subs)
    m_p_val  = eval_expr(m_p,  subs)
    prod_val = eval_expr(product, subs)
    
    # individual positivity
    pos_e = m_e_val > 0
    pos_p = m_p_val > 0
    # combined bound from rubric: Phi_N < (m/g)*exp(-|Phi_Delta|)
    bound = PhiN_val < (m_val/g_val) * np.exp(-PhiD_val)
    
    print(f"Sample {_}:")
    print(f"  m_eff^2 (orig) = {orig:.6f}, (prop) = {prop:.6f}, |Δ| = {diff:.6e}")
    print(f"  m_e = {m_e_val:.6f} (>0? {pos_e}),  m_p = {m_p_val:.6f} (>0? {pos_p})")
    print(f"  product m_e*m_p = {prod_val:.6e}  (sign {'+' if prod_val>0 else '-'})")
    print(f"  Rubric bound Φ_N < (m/g)e^{-|ΦΔ|} ? {bound}")
    print()

# ----------------------------------------------------------------------
# 5. Ghost‑mode logic test (mixed signs)
# ----------------------------------------------------------------------
print("=== GHOST‑MODE LOGIC ===\n")
PhiD_test = 1.0
m_val = 1.0
g_val = 0.2
# critical Φ_N where m_e = 0
PhiN_crit = m_val/(g_val*np.exp(PhiD_test))
print(f"Critical Φ_N (m_e=0) = {PhiN_crit:.4f}")
PhiN_test = PhiN_crit + 0.05   # slightly above → m_e negative
subs_test = {m:m_val, g:g_val, Phi_N:PhiN_test, Phi_Delta:PhiD_test}
m_e_val  = m_e.subs(subs_test).evalf()
m_p_val  = m_p.subs(subs_test).evalf()
prod_val = product.subs(subs_test).evalf()
print(f"With Φ_N = {PhiN_test:.4f}:")
print(f"  m_e = {m_e_val:.6f},  m_p = {m_p_val:.6f}")
print(f"  product = {prod_val:.6e} → {'negative' if prod_val<0 else 'positive'}")
print("→ A mixed‑sign pair makes the product negative, so m_eff would be imaginary.\n")

# ----------------------------------------------------------------------
# 6. Lattice collapse bound
# ----------------------------------------------------------------------
print("=== LATTICE COLLAPSE BOUND ===\n")
# example set of anisotropy coefficients
eps_list = [0.2, -0.3, 0.1]
max_abs_eps = max(abs(e) for e in eps_list)
collapse_limit = 1.0/max_abs_eps
print(f"Using ε_i = {eps_list} → max|ε_i| = {max_abs_eps:.3f}")
print(f"Collapse occurs when |Φ_Δ| ≥ {collapse_limit:.3f}\n")
for test_phi in [-0.8, -0.4, 0.0, 0.4, 0.8]:
    collapsed = any(1.0 + e*test_phi <= 0 for e in eps_list)
    within = abs(test_phi) < collapse_limit
    print(f"Φ_Δ = {test_phi:4.1f}: collapsed? {collapsed},  |Φ_Δ|<limit? {within}")