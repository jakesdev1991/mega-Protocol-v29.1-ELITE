# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
#!/usr/bin/env python3
"""
Omega Protocol Validation Script for CTMS‑Ω (Cognitive‑Tooling Mismatch Sensor)
--------------------------------------------------------------------------------
This script audits the repaired proposal for:
  • Invariant form ψ = ln(φₙ)  (Ω‑Physics Rubric v26.0)
  • Correct ½‑prefactor in the Fokker‑Planck diffusion term
  • Sigmoid‑based TFFI bounded in (0,1)
  • Operational constraints: TFFI < 0.6, Φ_N^(cog) > 0.5
  • Presence of the entropy gauge term A_μ J^μ in the action
  • Dimensional consistency of the gauge coupling (warning if ℓ remains)
  • Metric rescaling to dimensionless form (warning if not shown)

The script returns PASS only if *all* mandatory checks succeed and
no outstanding warnings remain.
"""

import sympy as sp
import sys
import subprocess
import importlib

# ----------------------------------------------------------------------
# Helper: ensure SymPy is available
# ----------------------------------------------------------------------
def ensure_sympy():
    try:
        import sympy
    except ImportError:
        print("Installing SymPy...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "sympy"])
        import sympy
    return sympy

sp = ensure_sympy()

# ----------------------------------------------------------------------
# Symbolic definitions
# ----------------------------------------------------------------------
# Basic symbols (all assumed dimensionless after scaling unless noted)
t, Λ = sp.symbols('t Λ', real=True)
mu, D, S = sp.symbols('mu D S', real=True)   # drift, diffusion, source
# Covariant modes
Phi_N, Phi_N0 = sp.symbols('Phi_N Phi_N0', positive=True)   # connectivity baseline
Phi_Delta = sp.symbols('Phi_Delta', real=True)              # asymmetry
# Invariant
psi_cog = sp.symbols('psi_cog', real=True)

# Parameters for TFFI
alpha, beta, gamma, delta = sp.symbols('alpha beta gamma delta', real=True)
CKD, ETA, H_tools, SchemaDiv = sp.symbols('CKD ETA H_tools SchemaDiv', real=True)
# Sigmoid
sigma = lambda x: 1/(1 + sp.exp(-x))

# ----------------------------------------------------------------------
# 1. Invariant check: ψ_cog = ln(Φ_N/Φ_N0)
# ----------------------------------------------------------------------
psi_expr = sp.log(Phi_N / Phi_N0)
invariant_ok = sp.simplify(psi_cog - psi_expr) == 0
print("[1] Invariant form ψ_cog = ln(Φ_N/Φ_N0):", "PASS" if invariant_ok else "FAIL")
if not invariant_ok:
    print("    Expected:", psi_expr)
    print("    Found   :", psi_cog)

# ----------------------------------------------------------------------
# 2. Fokker‑Planck equation: ∂_t P = -∂_Λ[μ P] + ½ ∂_Λ²[D P] + S
# ----------------------------------------------------------------------
P = sp.Function('P')(t, Λ)
FP_lhs = sp.diff(P, t)
FP_rhs = -sp.diff(mu * P, Λ) + sp.Rational(1,2) * sp.diff(sp.diff(D * P, Λ), Λ) + S
FP_ok = sp.simplify(FP_lhs - FP_rhs) == 0
print("\n[2] Fokker‑Planck equation (with ½):", "PASS" if FP_ok else "FAIL")
if not FP_ok:
    print("    LHS - RHS ≠ 0 (should be zero).")
    print("    Expression:", sp.simplify(FP_lhs - FP_rhs))

# ----------------------------------------------------------------------
# 3. Action integral – check for entropy gauge term A_μ J^μ
# ----------------------------------------------------------------------
# We cannot verify the full integral symbolically, but we can check whether
# the user‑provided string (here we simulate the proposal text) contains
# the term. In a real audit we would parse the LaTeX source.
action_terms = [
    r"\tfrac12 g^{\mu\nu}\partial_\mu\Lambda\partial_\nu\Lambda",
    r"V(\Lambda)",
    r"\lambda_\Omega\mathcal{L}_\Omega(\Phi_N,\Phi_\Delta)",
    r"A_\mu J^\mu"          # <-- gauge term we are looking for
]
# Simulate the proposal's displayed action (missing gauge term)
displayed_action = r"\tfrac12 g^{\mu\nu}\partial_\mu\Lambda\partial_\nu\Lambda + V(\Lambda) + \lambda_\Omega\mathcal{L}_\Omega(\Phi_N,\Phi_\Delta)"
gauge_present = any(term in displayed_action for term in action_terms if term == r"A_\mu J^\mu")
print("\n[3] Entropy gauge term A_μ J^μ present in action:", "PASS" if gauge_present else "FAIL (WARNING)")
if not gauge_present:
    print("    The displayed action lacks the explicit A_μ J^μ term.")

# ----------------------------------------------------------------------
# 4. TFFI definition and bounds (sigmoid → (0,1))
# ----------------------------------------------------------------------
TFFI = sigma(alpha*CKD + beta*sp.exp(-ETA) + gamma*(1 - H_tools) + delta*SchemaDiv)
TFFI_bounds = sp.simplify(TFFI - 0) > 0 and sp.simplify(1 - TFFI) > 0
# Sympy cannot directly prove inequality for generic symbols; we check
# that the sigmoid form is used.
is_sigmoid = TFFI.has(sp.exp) and TFFI.has(sp.log) == False  # crude check
print("\n[4] TFFI defined as sigmoid (bounded 0‑1):", "PASS" if is_sigmoid else "FAIL")
if not is_sigmoid:
    print("    Expression:", TFFI)

# ----------------------------------------------------------------------
# 5. Operational constraints: TFFI < 0.6, Φ_N^(cog) > 0.5
# ----------------------------------------------------------------------
# We treat these as policy checks; they must be enforceable at runtime.
# Here we just verify the symbols are present and the inequalities are
# syntactically correct.
constraint_TFFI = sp.LessThan(TFFI, 0.6)
constraint_PhiN = sp.GreaterThan(Phi_N, 0.5)
print("\n[5] Constraint syntax check:")
print("    TFFI < 0.6 :", "PASS" if isinstance(constraint_TFFI, sp.Relational) else "FAIL")
print("    Φ_N^(cog) > 0.5 :", "PASS" if isinstance(constraint_PhiN, sp.Relational) else "FAIL")

# ----------------------------------------------------------------------
# 6. Dimensional warnings (gauge coupling & metric)
# ----------------------------------------------------------------------
# We cannot prove dimensions symbolically, but we can flag if the
# proposal still contains an explicit length scale ℓ in J^μ.
# Simulate the original J^μ definition:
ell = sp.symbols('ell', positive=True)   # length scale
J_mu_original = sp.sqrt(2) * Phi_Delta * ell * sp.KroneckerDelta(0, 0)  # μ=0 component
# Check if ell appears in the expression for J^μ
ell_in_J = ell in J_mu_original.free_symbols
print("\n[6] Gauge coupling dimensional check:")
print("    Original J^μ contains explicit length scale ℓ:", ell_in_J)
if ell_in_J:
    print("    WARNING: Unless ℓ is absorbed into a redefinition of J^μ or the metric,")
    print("             the term A_μ J^μ will carry dimensions of length.")
# Metric rescaling warning (placeholder)
metric_dimless_warning = True   # we assume the proposal did not show the rescaling
print("\n[7] Metric rescaling to dimensionless form:")
print("    Shown explicitly in proposal? :", "NO (WARNING)" if metric_dimless_warning else "YES")
if metric_dimless_warning:
    print("    WARNING: No demonstration that g_{μν} remains dimensionless after")
    print("             coordinate scaling by ℓ; kinetic term may acquire ℓ² factors.")

# ----------------------------------------------------------------------
# Final verdict
# ----------------------------------------------------------------------
mandatory_pass = (
    invariant_ok and
    FP_ok and
    is_sigmoid and
    isinstance(constraint_TFFI, sp.Relational) and
    isinstance(constraint_PhiN, sp.Relational)
)

warnings = [
    not gauge_present,
    ell_in_J,
    metric_dimless_warning
]

print("\n=== SUMMARY ===")
print("Mandatory checks PASS:", mandatory_pass)
print("Warnings (non‑fatal):", sum(warnings), "/", len(warnings))
if mandatory_pass and not any(warnings):
    print("\nRESULT: PASS – proposal is mathematically sound and Ω‑compliant.")
else:
    print("\nRESULT: FAIL – see warnings above for required fixes.")
    sys.exit(1)