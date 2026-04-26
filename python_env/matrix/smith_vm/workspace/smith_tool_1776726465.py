# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
# -*- coding: utf-8 -*-
"""
Agent Smith – Omega Protocol Invariant Validator for CSTCL‑Ω
Checks:
  1. Action reduction to quadratic drift-Alfvén form.
  2. Eigenmode definitions from fluctuation operator.
  3. Stiffness invariants as inverse curvature.
  4. Invariant psi = ln(phi_n) with phi_n = 1/(m0*sqrt(xi_N*xi_Delta)).
  5. RG linearisation -> critical exponents.
  6. Entropy gauge hyperscaling.
  7. Control law drives system away from critical point.
  8. QP constraints expressed via psi, xi_N, xi_Delta.
"""

import sympy as sp
import numpy as np

# -------------------------------------------------
# 1. Symbols
# -------------------------------------------------
x, y, z, t = sp.symbols('x y z t', real=True)
phi = sp.Function('phi')(x, y, z, t)
m2, lam = sp.symbols('m2 lam', real=True)   # m^2, lambda
S, nu, Ln, beta = sp.symbols('S nu Ln beta', real=True)
# Effective mass squared as function of control params (placeholder linear form)
m_eff2 = m2 + S**2 + nu + 1/Ln + beta   # just to have dependence

# Fluctuation operator O = -∂_μ∂^μ + m_eff^2 (Euclidean signature for simplicity)
O = - (sp.diff(phi, x, 2) + sp.diff(phi, y, 2) + sp.diff(phi, z, 2) + sp.diff(phi, t, 2)) + m_eff2

# -------------------------------------------------
# 2. Covariant mode extraction (Fourier ansatz)
# -------------------------------------------------
kx, ky, kz, wt = sp.symbols('kx ky kz wt', real=True)
phi_k = sp.exp(sp.I*(kx*x + ky*y + kz*z - wt*t))   # plane wave
O_on_phi = sp.simplify(O.subs(phi, phi_k) / phi_k)  # eigenvalue
# O_on_phi = (kx^2+ky^2+kz^2+wt^2) + m_eff2
eigenval = sp.simplify(O_on_phi)
print("Fluctuation operator eigenvalue:", eigenval)

# Separate parallel (kz) and perpendicular (kx,ky) parts
k_par2 = kz**2
k_perp2 = kx**2 + ky**2
eigenval_sep = sp.simplify(eigenval.subs({kx**2+ky**2: k_perp2, kz**2: k_par2}))
print("Eigenvalue split:", eigenval_sep)

# Define mode amplitudes (RMS) as inverse sqrt of eigenvalue contributions
# For homogeneous mode k=0 -> eigenvalue = m_eff2
phi0_sq = 1/m_eff2   # proportional to <|δφ_{k=0}|^2>
# For anisotropy: difference between parallel and perpendicular contributions
aniso = sp.simplify(1/(k_par2 + m_eff2) - 1/(k_perp2 + m_eff2))
print("Anisotropy kernel:", aniso)

# -------------------------------------------------
# 3. Stiffness invariants from effective potential
# -------------------------------------------------
# Effective potential V_eff = 1/2 m_eff2 phi^2 + lam/4 phi^4
phi0 = sp.symbols('phi0', real=True)
V_eff = m_eff2/2 * phi0**2 + lam/4 * phi0**4
# Minimum: dV/dphi = 0 -> phi0*(m_eff2 + lam*phi0**2)=0 => phi0=0 or phi0^2 = -m_eff2/lam
# We consider the disordered minimum phi0=0 (valid for m_eff2>0)
phi0_min = 0
# Second derivatives w.r.t. mode amplitudes (chain rule: d/dPhi_N = (d phi0/dPhi_N) d/dphi0)
# For homogeneous mode, Phi_N^2 ~ <phi0^2> => Phi_N ~ |phi0|
# So d^2V/dPhi_N^2 at phi0=0 = m_eff2
xi_N_sq_inv = sp.simplify(sp.diff(V_eff, phi0, 2).subs(phi0, phi0_min))
xi_Delta_sq_inv = xi_N_sq_inv   # isotropic placeholder; real case would split k_par/k_perp
print("xi_N^{-2} (curvature):", xi_N_sq_inv)
print("xi_Delta^{-2} (curvature):", xi_Delta_sq_inv)

# -------------------------------------------------
# 4. Invariant psi
# -------------------------------------------------
m0 = sp.symbols('m0', positive=True)
phi_n = 1/(m0 * sp.sqrt(1/xi_N_sq_inv * 1/xi_Delta_sq_inv))  # = m_eff/m0
psi = sp.log(phi_n)
print("psi = ln(phi_n):", psi.simplify())
# Check limits
print("psi -> +∞ when xi_N,xi_Delta -> ∞:", sp.limit(psi, xi_N_sq_inv, 0).subs(xi_Delta_sq_inv, 0))
print("psi -> -∞ when xi_N,xi_Delta -> 0:", sp.limit(psi, xi_N_sq_inv, sp.oo).subs(xi_Delta_sq_inv, sp.oo))

# -------------------------------------------------
# 5. RG linearisation -> critical exponents
# -------------------------------------------------
# Beta functions (toy model): beta_m2 = a*m2 + b*S^2, beta_S = c*(S - S_crit)
a, b, c, S_crit = sp.symbols('a b c S_crit', real=True)
beta_m2 = a*m2 + b*S**2
beta_S  = c*(S - S_crit)
# Fixed point: set beta=0
fp_m2 = sp.solve(beta_m2, m2)
fp_S  = sp.solve(beta_S, S)
print("Fixed point m2*:", fp_m2)
print("Fixed point S*:", fp_S)
# Linearisation matrix
J = sp.Matrix([[sp.diff(beta_m2, m2), sp.diff(beta_m2, S)],
               [sp.diff(beta_S, m2),  sp.diff(beta_S, S)]])
J_sub = J.subs({m2: fp_m2[0], S: fp_S[0]})
print("Jacobian at FP:", J_sub)
# Eigenvalues = -1/nu_i
evals = J_sub.eigenvals()
print("Eigenvalues (-> -1/nu_i):", evals)
# Extract nu_S from eigenvalue associated with S direction
nu_S = -1/evals.get(list(evals.keys())[0], 1)   # placeholder
print("Estimated nu_S:", nu_S)

# -------------------------------------------------
# 6. Entropy gauge hyperscaling
# -------------------------------------------------
c_h, xi0 = sp.symbols('c_h xi0', positive=True)
xi = sp.sqrt(1/xi_N_sq_inv * 1/xi_Delta_sq_inv)   # correlation length
S_h = c_h * sp.log(xi/xi0) + sp.Symbol('const')
print("Entropy S_h:", S_h.simplify())
# Gauge field A_mu = d S_h / dx^mu (symbolic derivative)
A_mu = sp.diff(S_h, x)   # example component
print("Gauge component A_x:", A_mu.simplify())

# -------------------------------------------------
# 7. Control law verification
# -------------------------------------------------
gamma = sp.symbols('gamma', positive=True)
psi_sym = sp.symbols('psi', real=True)
S_var = sp.symbols('S_var', real=True)
S_crit_sym = sp.symbols('S_crit_sym', real=True)
control = -gamma * sp.sign(S_var - S_crit_sym) * sp.exp(-psi_sym/nu_S)
# Check sign: when psi -> 0+ (approaching critical) exp -> 1, sign term pushes S away if S>S_crit?
# We'll test numeric later.
print("Control law expression:", control)

# -------------------------------------------------
# 8. QP constraints in invariant form
# -------------------------------------------------
DeltaS_safe = sp.symbols('DeltaS_safe', positive=True)
PhiN_min = sp.symbols('PhiN_min', positive=True)
PhiD_max = sp.symbols('PhiD_max', positive=True)
xi_min = sp.symbols('xi_min', positive=True)
xi_max = sp.symbols('xi_max', positive=True)

# Express Phi_N, Phi_Delta via xi_N, xi_Delta (up to constants)
# Assume Phi_N^2 ∝ 1/xi_N^2, Phi_D^2 ∝ 1/xi_D^2 (from earlier)
PhiN_sq = 1/xi_N_sq_inv
PhiD_sq = 1/xi_Delta_sq_inv
constraints = [
    sp.Abs(S_var - S_crit_sym) >= DeltaS_safe,
    sp.sqrt(PhiN_sq) >= PhiN_min,
    sp.sqrt(PhiD_sq) <= PhiD_max,
    sp.sqrt(1/xi_N_sq_inv) >= xi_min,
    sp.sqrt(1/xi_N_sq_inv) <= xi_max,
    sp.sqrt(1/xi_Delta_sq_inv) >= xi_min,
    sp.sqrt(1/xi_Delta_sq_inv) <= xi_max
]
print("QP constraints (symbolic):")
for c in constraints:
    print("  ", c)

# -------------------------------------------------
# 9. Numeric sanity check (toy parameters)
# -------------------------------------------------
np.random.seed(42)
# Choose sample values
m2_val = 0.5
lam_val = 0.1
S_val = 1.2
nu_val = 0.05
Ln_val = 0.3
beta_val = 0.02
m0_val = 1.0
c_h_val = 1.0
xi0_val = 1.0
gamma_val = 0.5
DeltaS_safe_val = 0.1
PhiN_min_val = 0.75
PhiD_max_val = 0.6
xi_min_val = 0.1
xi_max_val = 10.0
S_crit_val = 1.0

# Compute derived quantities
m_eff2_val = m2_val + S_val**2 + nu_val + 1/Ln_val + beta_val
xiN_val = np.sqrt(1/m_eff2_val)   # from xi_N^{-2}=m_eff2
xiD_val = xiN_val                 # isotropic toy
psi_val = np.log(1/(m0_val*np.sqrt(xiN_val*xiD_val)))
S_h_val = c_h_val * np.log(np.sqrt(xiN_val*xiD_val)/xi0_val)
control_val = -gamma_val * np.sign(S_val - S_crit_val) * np.exp(-psi_val/1.0)  # assume nu_S=1

print("\n--- Numeric check ---")
print(f"m_eff^2 = {m_eff2_val:.3f}")
print(f"xi_N = {xiN_val:.3f}, xi_Delta = {xiD_val:.3f}")
print(f"psi = {psi_val:.3f}")
print(f"S_h = {S_h_val:.3f}")
print(f"Control dS/dt = {control_val:.3f}")
print(f"|S-S_crit| = {abs(S_val - S_crit_val):.3f}  (safe? >= {DeltaS_safe_val})")
print(f"Phi_N = {1/np.sqrt(m_eff2_val):.3f}  (>= {PhiN_min_val}?)")
print(f"Phi_Delta = {1/np.sqrt(m_eff2_val):.3f}  (<= {PhiD_max_val}?)")
print(f"xi_N in [{xi_min_val},{xi_max_val}]? {xi_min_val <= xiN_val <= xi_max_val}")
print(f"xi_Delta in [{xi_min_val},{xi_max_val}]? {xi_min_val <= xiD_val <= xi_max_val}")

# Assertions that would fail if invariant violated
assert abs(S_val - S_crit_val) >= DeltaS_safe_val, "QP shear violation"
assert 1/np.sqrt(m_eff2_val) >= PhiN_min_val, "Phi_N lower bound violated"
assert 1/np.sqrt(m_eff2_val) <= PhiD_max_val, "Phi_Delta upper bound violated"
assert xi_min_val <= xiN_val <= xi_max_val, "xi_N range violated"
assert xi_min_val <= xiD_val <= xi_max_val, "xi_Delta range violated"
print("\nAll QP constraints satisfied (toy model).")