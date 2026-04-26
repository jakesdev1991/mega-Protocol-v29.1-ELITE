# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
# --------------------------------------------------------------
# BGSM-Ω Mathematical Validation (SymPy)
# --------------------------------------------------------------
import sympy as sp

# --- Symbols ---------------------------------------------------
x, t, mu, nu = sp.symbols('x t mu nu', real=True)
# Field and gauge parameters
phi = sp.Function('phi')(x, t)          # complex scalar field
e   = sp.symbols('e', real=True)       # gauge coupling
# Gauge field (we keep it generic; later we set A = dS)
A = sp.Function('A')(x, t)             # real 4‑vector, component mu
# Gauge transformation parameter
alpha = sp.Function('alpha')(x, t)     # real scalar

# Covariant derivative (mu component)
def D_mu(f, A_mu):
    return sp.diff(f, x) - sp.I * e * A_mu   # simplified 1‑D for clarity

# Kinetic term: (D_mu phi)^\dagger D^mu phi
# In 1‑D we just use the same derivative for upper/lower index with metric = 1
Dphi = D_mu(phi, A)
Dphi_dag = sp.conjugate(Dphi)   # hermitian conjugate
kinetic = sp.simplify(Dphi_dag * Dphi)

# --- Gauge transformation ---------------------------------------
phi_t   = sp.exp(sp.I * e * alpha) * phi
A_t     = A + sp.diff(alpha, x)   # A_mu -> A_mu + ∂_mu alpha

Dphi_t   = D_mu(phi_t, A_t)
Dphi_t_dag = sp.conjugate(Dphi_t)
kinetic_t = sp.simplify(Dphi_t_dag * Dphi_t)

# Check invariance: kinetic_t - kinetic should be zero (up to total derivative)
inv_check = sp.simplify(kinetic_t - kinetic)
print("Gauge invariance of kinetic term:")
print("  Expression:", inv_check)
print("  Simplifies to zero?", inv_check == 0)
print()

# --- Correlation length and invariant psi -----------------------
m, lam, phi0 = sp.symbols('m lam phi0', real=True)
m_eff_sq = m**2 + 3*lam*phi0**2          # effective mass squared
xi       = 1/sp.sqrt(m_eff_sq)          # correlation length
xi0      = sp.symbols('xi0', positive=True)  # reference length
psi      = sp.log(xi / xi0)

# Optional: express psi in terms of distance to critical point
# Let m^2 = a*(T - Tc) (linear near criticality)
a, T, Tc = sp.symbols('a T Tc', real=True)
m_sq_expr = a * (T - Tc)
m_eff_sq_crit = m_sq_expr + 3*lam*phi0**2
psi_crit = sp.log(1/sp.sqrt(m_eff_sq_crit) / xi0)

print("Invariant ψ from correlation length:")
print("  ψ =", psi)
print("  Near criticality (m^2 = a(T-Tc)):")
print("  ψ =", psi_crit)
print()

# --- Summary ----------------------------------------------------
if inv_check == 0:
    print("✅ Kinetic term is gauge invariant (as expected).")
else:
    print("⚠️  Kinetic term shows non‑invariant remainder:", inv_check)

# End of script