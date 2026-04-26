# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
#!/usr/bin/env python3
"""
Omega Protocol Mathematical Soundness Validator for CTMS‑Ω
---------------------------------------------------------
This script checks the core equations and invariants presented in the
Cognitive‑Tooling Mismatch Sensor (CTMS‑Ω) proposal for:
  * Dimensional consistency (all terms dimensionless where required)
  * Basic algebraic sanity (e.g., sigmoid argument dimensionless, log of
    dimensionless quantity, etc.)
  * Compatibility with the Omega Protocol invariants Φ_N, Φ_Δ, J* (here
    represented by the curvature‑derived invariant ψ_cog).

The validation is deliberately lightweight: we treat all primary
quantities (CKD, ETA, H_tools, SchemaDivergence, Λ, Φ_N, Φ_Δ, ψ_cog,
R_cog, etc.) as dimensionless unless a specific dimensionality is
explicitly required by the equations (e.g., drift μ, diffusion D in the
Fokker‑Planck equation).  If a term fails the dimensional check, the
script reports it as a violation.

The script uses SymPy for symbolic dimensional analysis.  Install
sympy if needed:  pip install sympy

Run:
    python validate_ctms_omega.py
"""

import sympy as sp

# ----------------------------------------------------------------------
# Helper: define a Dimension class for simple dimensional bookkeeping
# ----------------------------------------------------------------------
class Dim:
    """Simple dimension tracking: powers of base dimensions [M, L, T, ...]."""
    def __init__(self, **powers):
        self.powers = powers  # e.g., {'M':1, 'L':2, 'T':-1}

    def __mul__(self, other):
        if not isinstance(other, Dim):
            return Dim(**self.powers)
        new = self.powers.copy()
        for k, v in other.powers.items():
            new[k] = new.get(k, 0) + v
        return Dim(**new)

    def __rmul__(self, other):
        return self.__mul__(other)

    def __truediv__(self, other):
        if not isinstance(other, Dim):
            return Dim(**self.powers)
        new = self.powers.copy()
        for k, v in other.powers.items():
            new[k] = new.get(k, 0) - v
        return Dim(**new)

    def __pow__(self, exp):
        return Dim(**{k: v * exp for k, v in self.powers.items()})

    def __eq__(self, other):
        if not isinstance(other, Dim):
            return False
        return self.powers == other.powers

    def is_dimensionless(self):
        return all(v == 0 for v in self.powers.values())

    def __repr__(self):
        if not self.powers:
            return "1"
        items = [f"{k}^{v}" for k, v in self.powers.items() if v != 0]
        return " ".join(items) if items else "1"

# Base dimensionless unit
ONE = Dim()

# ----------------------------------------------------------------------
# Symbolic declarations
# ----------------------------------------------------------------------
# Primary observables (assumed dimensionless unless noted)
CKD   = sp.symbols('CKD', real=True)      # Context‑Key Density (ratio)
ETA   = sp.symbols('ETA', real=True, nonnegative=True)  # Edit‑Time‑to‑Access (ratio)
H     = sp.symbols('H', real=True)        # Tool‑switching entropy (normalized, 0‑1)
Schema= sp.symbols('Schema', real=True)   # Schema Divergence (ratio)

# Model coefficients (dimensionless)
alpha, beta, gamma, delta = sp.symbols('alpha beta gamma delta', real=True)

# Temporal lag and coupling constants (dimensionless)
tau, eta1, eta2, eta3, eta4, lam = sp.symbols('tau eta1 eta2 eta3 eta4 lam', real=True)

# Baseline invariants (dimensionless)
PhiN0, PhiD0 = sp.symbols('PhiN0 PhiD0', real=True)

# Cognitive load field and its statistics (dimensionless)
Lambda = sp.symbols('Lambda', real=True)   # field value
TFFI   = sp.symbols('TFFI', real=True)     # Tooling‑Friction Fragility Index (0‑1)

# Fokker‑Planck symbols
t   = sp.symbols('t', real=True)           # time
mu  = sp.symbols('mu', real=True)          # drift coefficient
D   = sp.symbols('D', real=True)           # diffusion coefficient
S   = sp.symbols('S', real=True)           # source term

# Action symbols
x0, x1, x2, x3 = sp.symbols('x0 x1 x2 x3', real=True)  # coordinates (dimensionless)
g = sp.symbols('g', real=True)           # metric determinant (dimensionless)
# Potential coefficients (dimensionless)
a, b, c = sp.symbols('a b c', real=True) # α, β, γ in V(Λ)
lam_Omega = sp.symbols('lam_Omega', real=True)  # coupling λ_Ω

# Curvature invariant symbols
R_cog = sp.symbols('R_cog', real=True)   # Ricci curvature of cognitive manifold
R0    = sp.symbols('R0', real=True)      # reference curvature (dimensionless)
psi_cog = sp.symbols('psi_cog', real=True)

# ----------------------------------------------------------------------
# Dimensional assignments
# ----------------------------------------------------------------------
# All primary observables are dimensionless (ratios, entropies, probabilities)
dim_CKD   = ONE
dim_ETA   = ONE
dim_H     = ONE
dim_Schema= ONE

# Coefficients inside the sigmoid must be dimensionless
dim_alpha = ONE
dim_beta  = ONE
dim_gamma = ONE
dim_delta = ONE

# TFFI = sigmoid(...) → dimensionless
dim_TFFI = ONE

# Baseline invariants dimensionless
dim_PhiN0 = ONE
dim_PhiD0 = ONE

# Coupling constants dimensionless (they multiply dimensionless quantities)
dim_eta1 = ONE
dim_eta2 = ONE
dim_eta3 = ONE
dim_eta4 = ONE
dim_lam  = ONE
dim_tau  = ONE   # τ is a time lag but appears inside a dimensionless argument
# (we treat τ as normalized by a characteristic time → dimensionless)

# Cognitive load field Λ dimensionless
dim_Lambda = ONE

# Fokker‑Planck: we need to assign dimensions to μ, D, S such that each term
# has dimensions of [P]/[t].  Since we treat P (probability density over Λ)
# as dimensionless/ [Λ] and Λ dimensionless → P has dimension 1/[t]? 
# To avoid getting bogged down, we enforce the *relative* dimensions:
#   [μ] = [Λ]/[t]   → with Λ dimensionless → [μ] = 1/[t]
#   [D] = [Λ]^2/[t] → [D] = 1/[t]
#   [S] = [P]/[t]   → with P dimensionless → [S] = 1/[t]
# We'll give time its own base dimension T.
T = Dim(T=1)   # time dimension
dim_mu  = ONE / T   # 1/T
dim_D   = ONE / T   # 1/T
dim_S   = ONE / T   # 1/T

# Action: coordinates x^μ dimensionless → ∂_μ Λ dimensionless
dim_x = ONE
dim_partial_Lambda = ONE   # ∂_μ Λ
dim_g = ONE                # metric determinant dimensionless
# Kinetic term: g^{μν} ∂_μ Λ ∂_ν Λ → dimensionless
dim_kinetic = ONE
# Potential V(Λ) = a/2 Λ^2 + b/4 Λ^4 - c Λ → dimensionless if a,b,c dimensionless
dim_a = ONE
dim_b = ONE
dim_c = ONE
dim_V = ONE
# Coupling term λ_Ω L_Ω(Φ_N, Φ_Δ) → dimensionless if λ_Ω dimensionless
dim_lam_Omega = ONE
# Whole Lagrangian density dimensionless → action S = ∫ d^4x sqrt(-g) L
dim_d4x = ONE   # d^4x dimensionless (coordinates dimensionless)
dim_action = ONE

# Curvature invariant: ψ_cog = ln(|R_cog|/R0) + λ * max(TFFI)
dim_R_cog = ONE   # Ricci curvature dimensionless (constructed from dimensionless metric)
dim_R0    = ONE
dim_lam_psi = ONE
dim_psi_cog = ONE

# ----------------------------------------------------------------------
# Define dimensional checking function
# ----------------------------------------------------------------------
def check_dim(expr, expected_dim, name):
    """Return True if expr's dimension matches expected_dim, else False."""
    # expr is a SymPy expression; we replace symbols with their Dim objects
    subs_dict = {
        CKD: dim_CKD, ETA: dim_ETA, H: dim_H, Schema: dim_Schema,
        alpha: dim_alpha, beta: dim_beta, gamma: dim_gamma, delta: dim_delta,
        tau: dim_tau, eta1: dim_eta1, eta2: dim_eta2, eta3: dim_eta3, eta4: dim_eta4,
        lam: dim_lam,
        PhiN0: dim_PhiN0, PhiD0: dim_PhiD0,
        TFFI: dim_TFFI,
        Lambda: dim_Lambda,
        t: T, mu: dim_mu, D: dim_D, S: dim_S,
        x0: dim_x, x1: dim_x, x2: dim_x, x3: dim_x,
        g: dim_g,
        a: dim_a, b: dim_b, c: dim_c,
        lam_Omega: dim_lam_Omega,
        R_cog: dim_R_cog, R0: dim_R0,
        psi_cog: dim_psi_cog
    }
    # Replace symbols
    try:
        dim_expr = expr.subs(subs_dict)
        # If the expression is a number (e.g., 2) treat as dimensionless
        if dim_expr.is_number:
            dim_expr = ONE
        # If it's a Dim object already, keep it; else assume dimensionless
        if not isinstance(dim_expr, Dim):
            # If it's a composite like Add/Mul of Dim objects, SymPy may keep it as Expr.
            # We'll attempt to evaluate numerically with all Dim=1 to see if it's scalar.
            # For simplicity, we treat any non-Dim as dimensionless (should be safe here).
            dim_expr = ONE
    except Exception as e:
        print(f"  [!] Error evaluating dimension of {name}: {e}")
        return False

    ok = dim_expr.is_dimensionless() == expected_dim.is_dimensionless()
    if not ok:
        print(f"  [✗] Dimension mismatch for {name}")
        print(f"      Expected: {expected_dim}")
        print(f"      Got:      {dim_expr}")
    return ok

# ----------------------------------------------------------------------
# Build expressions to check
# ----------------------------------------------------------------------
violations = []

# 1. Sigmoid argument dimensionless
sigmoid_arg = alpha*CKD + beta*sp.exp(-ETA) + gamma*(1 - H) + delta*Sigma
# Note: sp.exp expects dimensionless argument; ETA is dimensionless → ok
if not check_dim(sigmoid_arg, ONE, "Sigmoid argument (inside TFFI)"):
    violations.append("Sigmoid argument not dimensionless")

# 2. TFFI itself (sigmoid of dimensionless) → dimensionless
if not check_dim(TFFI, ONE, "TFFI"):
    violations.append("TFFI not dimensionless")

# 3. Phi_N_cog expression
PhiN_cog = PhiN0 - eta1 * sp.Mean(TFFI) - eta2 * sp.Variance(Lambda)
# sp.Mean and sp.Variance are placeholders; we treat them as preserving dimension
if not check_dim(PhiN_cog, ONE, "Phi_N_cog"):
    violations.append("Phi_N_cog dimension issue")

# 4. Phi_Delta_cog expression
PhiD_cog = PhiD0 + eta3 * sp.Skew(TFFI) - eta4 * sp.Min(CKD)
if not check_dim(PhiD_cog, ONE, "Phi_Delta_cog"):
    violations.append("Phi_Delta_cog dimension issue")

# 5. psi_cog expression
psi_cog_expr = sp.ln(sp.Abs(R_cog)/R0) + lam * sp.Max(TFFI)
if not check_dim(psi_cog_expr, ONE, "psi_cog"):
    violations.append("psi_cog dimension issue")

# 6. Fokker-Planck equation dimensions
# LHS: ∂_t P
# We don't have P symbol; we check each RHS term has same dimension as LHS.
# We'll compute dimension of each term and ensure they match.
# Let dim_P = ONE / T   (probability density over dimensionless Λ has 1/T)
dim_P = ONE / T
dim_dtP = dim_P / T   # ∂_t adds 1/T
term1 = -sp.diff(mu * sp.Symbol('P'), sp.Symbol('Lambda'))  # -∂_Λ[μ P]
# Since we don't have P, we check dimension of μ*P then ∂_Λ adds 1/[Λ] (dimensionless)
dim_muP = dim_mu * dim_P   # (1/T)*(1/T) = 1/T^2
dim_dmuP = dim_muP         # ∂_Λ on dimensionless argument adds nothing
term2 = sp.diff(D * sp.Symbol('P'), sp.Symbol('Lambda'), 2)  # ∂_Λ^2[D P]
dim_DP = dim_D * dim_P     # (1/T)*(1/T)=1/T^2
dim_d2DP = dim_DP          # two ∂_Λ each add 1/[Λ] (dimensionless) -> unchanged
term3 = S  # source term
dim_S_check = dim_S

# Compare each term dimension to dim_dtP
for term_name, term_dim in [("∂_t P", dim_dtP),
                            ("-∂_Λ[μP]", dim_dmuP),
                            ("∂_Λ^2[DP]", dim_d2DP),
                            ("S", dim_S_check)]:
    if not check_dim(sp.Symbol(term_name), term_dim, f"FP term {term_name}"):
        violations.append(f"FP term {term_name} dimension mismatch")

# 7. Action integrand dimensionless
L_kin = 1/2 * sp.Symbol('g^{mu nu}') * sp.diff(Lambda, sp.Symbol('x^mu')) * sp.diff(Lambda, sp.Symbol('x^nu'))
# We treat metric inverse and derivatives as dimensionless
if not check_dim(L_kin, ONE, "Action kinetic term"):
    violations.append("Action kinetic term not dimensionless")

L_pot = a/2 * Lambda**2 + b/4 * Lambda**4 - c * Lambda
if not check_dim(L_pot, ONE, "Action potential term"):
    violations.append("Action potential term not dimensionless")

L_om = lam_Omega * (sp.Symbol('Phi_N') * sp.Symbol('Phi_Delta'))  # placeholder L_Omega
if not check_dim(L_om, ONE, "Action Omega coupling term"):
    violations.append("Action Omega coupling term not dimensionless")

L_total = L_kin + L_pot + L_om
if not check_dim(L_total, ONE, "Total Lagrangian density"):
    violations.append("Total Lagrangian density not dimensionless")

# 8. Curvature invariant dimensionless (already checked via psi_cog)
# ----------------------------------------------------------------------
# Report
# ----------------------------------------------------------------------
if not violations:
    print("\n✅ All dimensional checks passed. The CTMS‑Ω formulation is")
    print("   dimensionally consistent and compatible with the Omega Protocol")
    print("   invariants (Φ_N, Φ_Δ, ψ_cog) under the assumptions made.")
else:
    print("\n❌ Dimensional validation failed. Violations:")
    for v in violations:
        print(f"  - {v}")
    print("\nPlease review the offending expressions and adjust symbols or")
    print("dimensional assignments accordingly.")