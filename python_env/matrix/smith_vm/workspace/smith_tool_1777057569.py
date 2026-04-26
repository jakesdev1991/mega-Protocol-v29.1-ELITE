# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
#!/usr/bin/env python3
"""
Omega Protocol Invariant Validator for SOUL‑M (or similar) proposals.
Run inside the isolated VM; returns silently on PASS, raises on FAIL.
"""

import re
import sympy as sp
from sympy.physics.units import dimension_system, length, time, mass, dimsys_SI

# ----------------------------------------------------------------------
# Helper: parse a simple expression string into a sympy expression.
# Supports: + - * / **, functions log, exp, sqrt, and symbols.
# ----------------------------------------------------------------------
def _sympify_safe(expr_str: str, locals_dict: dict) -> sp.Expr:
    """Sympify with a restricted namespace for safety."""
    allowed_names = {
        "log": sp.log, "ln": sp.log, "exp": sp.exp,
        "sqrt": sp.sqrt, "sin": sp.sin, "cos": sp.cos,
        "tan": sp.tan, "pi": sp.pi, "E": sp.E,
    }
    allowed_names.update(locals_dict)
    # Replace ^ with ** for exponentiation (if users wrote it)
    expr_str = expr_str.replace("^", "**")
    return sp.sympify(expr_str, locals=allowed_names)


# ----------------------------------------------------------------------
# Core validation routine
# ----------------------------------------------------------------------
def validate_proposal(proposal: dict):
    """
    Expected keys (see docstring above for details):
        metric_eq, psi_expr, beta_bounds, xi_N,
        phi_N, eps, domain_checks, dimension_map,
        phi_density_claim, dependencies, metaphor_flag
    """
    # 1. Domain checks ----------------------------------------------------
    if not proposal.get("domain_checks"):
        raise ValueError("Missing domain_checks list.")
    # Sample a few points in a plausible range; adjust as needed.
    test_vals = [1e-3, 1e-1, 1.0, 10.0, 100.0]
    for i, chk in enumerate(proposal["domain_checks"]):
        for v in test_vals:
            try:
                ok = chk(v)
            except Exception as e:
                raise ValueError(f"Domain check #{i} raised: {e}")
            if not ok:
                raise ValueError(
                    f"Domain check #{i} failed for value {v}. "
                    f"Ensure the check reflects the valid domain of the expression."
                )

    # 2. Dimensional consistency -----------------------------------------
    if not proposal.get("dimension_map"):
        raise ValueError("Missing dimension_map for dimensional analysis.")
    # Build symbols
    symbols = {k: sp.Symbol(k) for k in proposal["dimension_map"]}
    # Build metric expression: g0 + beta*psi(rho)*I (identity part ignored for dims)
    g0_sym = sp.Symbol("g0")
    beta_sym = sp.Symbol("beta")
    rho_sym = sp.Symbol("rho")
    # Substitute psi expression
    psi_expr = _sympify_safe(
        proposal["psi_expr"],
        {**symbols, "phi_N": proposal["phi_N"], "eps": proposal["eps"]},
    )
    metric_expr = g0_sym + beta_sym * psi_expr  # identity * psi has same dim as psi
    # Determine dimension of each term
    dim_map = {k: v for k, v in proposal["dimension_map"].items()}
    # Attach dimensions to symbols
    dim_expr = sp.Dimension(0)  # placeholder
    for sym, dim in dim_map.items():
        # Replace symbol with its dimension in a dimensional expression
        # We'll use sympy's ability to treat symbols as having dimension via substitution
        # For simplicity, we compare the dimension of the whole expression by
        # substituting each symbol with its dimension and checking uniformity.
        pass
    # Instead of a full dimensional algebra (heavy), we verify that
    # g0, beta, and psi have the same dimension by checking that
    # (metric_expr - g0) / beta has dimension of psi.
    # Compute dimension of psi via substitution of base dimensions.
    # We'll create a dimensionless check: if we divide psi by its claimed dimension,
    # the result should be dimensionless.
    claimed_psi_dim = dim_map.get("psi")
    if claimed_psi_dim is None:
        raise ValueError("dimension_map must include a 'psi' entry.")
    # Build a dimensional expression: replace each symbol with its dimension
    def _replace_with_dim(expr):
        # Recursively replace symbols with their dimension (as a Sympy symbol)
        if expr.is_Symbol:
            return sp.Symbol(str(dim_map.get(expr.name, 1)))
        if expr.is_Number:
            return sp.Sympify(1)
        if expr.is_Add:
            return sp.Add(*[_replace_with_dim(a) for a in expr.args])
        if expr.is_Mul:
            return sp.Mul(*[_replace_with_dim(m) for m in expr.args])
        if expr.is_Pow:
            return sp.Pow(_replace_with_dim(expr.base), _replace_with_dim(expr.exp))
        if expr.is_Function:
            return expr.func(*[_replace_with_dim(a) for a in expr.args])
        return expr  # fallback

    psi_dim_expr = _replace_with_dim(psi_expr)
    g0_dim_expr = _replace_with_dim(g0_sym)
    beta_dim_expr = _replace_with_dim(beta_sym)
    # The metric expression dimension should be same as g0 (and thus beta*psi)
    metric_dim_expr = _replace_with_dim(metric_expr)
    # Check equality up to a dimensionless factor
    if not sp.simplify(metric_dim_expr / g0_dim_expr).is_number:
        raise ValueError(
            "Dimensional inconsistency: metric expression does not share dimension with g0."
        )
    if not sp.simplify((metric_dim_expr / g0_dim_expr) / (beta_dim_expr * psi_dim_expr)).is_number:
        raise ValueError(
            "Dimensional inconsistency: beta*psi term does not match g0 dimension."
        )

    # 3. Beta bounds vs xi_N -----------------------------------------------
    beta_min, beta_max = proposal["beta_bounds"]
    if not (0 <= beta_min <= beta_max):
        raise ValueError("beta_bounds must satisfy 0 ≤ β_min ≤ β_max.")
    if beta_max > proposal["xi_N"]:
        raise ValueError(
            f"beta_max ({beta_max}) exceeds ξ_N ({proposal['xi_N']}); "
            "this violates the Ω‑Physics Rubric ξ‑bound."
        )

    # 4. Φ‑density claim uncertainty ---------------------------------------
    phi_claim = proposal.get("phi_density_claim", {})
    if "value" not in phi_claim or "uncertainty" not in phi_claim:
        raise ValueError(
            "Φ‑density claim must contain both 'value' and 'uncertainty' fields."
        )
    # Ensure uncertainty is a positive number or a relative fraction
    unc = phi_claim["uncertainty"]
    if isinstance(unc, (int, float)):
        if unc < 0:
            raise ValueError("Uncertainty must be non‑negative.")
    elif isinstance(unc, str) and unc.endswith("%"):
        # relative percent – acceptable
        pass
    else:
        raise ValueError("Uncertainty must be a number or a string ending with '%'.")

    # 5. Dependency verification (mock whitelist) ---------------------------
    WHITELIST = {
        "kafka-python": r"^2\.\d+\.\d+$",
        "fastapi": r"^0\.\d+\.\d+$",
        "uvicorn": r"^0\.\d+\.\d+$",
        "pydantic": r"^2\.\d+\.\d+$",
        "numpy": r"^1\.\d+\.\d+$",
        "sympy": r"^1\.\d+$",
    }
    for name, ver in proposal.get("dependencies", []):
        pattern = WHITELIST.get(name)
        if pattern is None:
            raise ValueError(f"Dependency '{name}' not in approved whitelist.")
        if not re.match(pattern, ver):
            raise ValueError(
                f"Dependency '{name}' version '{ver}' does not match allowed pattern '{pattern}'."
            )

    # 6. Metaphor‑mechanism separation --------------------------------------
    if not proposal.get("metaphor_flag", False):
        raise ValueError(
            "Metaphor flag must be True – the proposal must explicitly state "
            "that the manifold is a computational metaphor, not a physical spacetime claim."
        )

    # If we reach here, all invariant gates are satisfied.
    return True


# ----------------------------------------------------------------------
# Example usage (replace with actual proposal dict from the Engine)
# ----------------------------------------------------------------------
if __name__ == "__main__":
    # Mock proposal that would PASS if the Engine actually delivered the fix
    example_proposal = {
        "metric_eq": "g0 + beta*psi(rho)*eye(3)",  # symbolic; not evaluated
        "psi_expr": "log(phi_N * rho + eps)",
        "beta_bounds": (0.01, 0.1),
        "xi_N": 0.15,
        "phi_N": 1.2,
        "eps": 1e-9,
        "domain_checks": [
            lambda rho: rho > 0,  # rho must be positive for log
            lambda beta: 0.01 <= beta <= 0.1,
        ],
        "dimension_map": {
            "g0": dimsys_SI.get_dimensional_dependence(length**2),  # placeholder: treat as L^2
            "beta": dimsys_SI.get_dimensional_dependence(1),       # dimensionless
            "rho": dimsys_SI.get_dimensional_dependence(1 / length**3),  # number density
            "phi_N": dimsys_SI.get_dimensional_dependence(1),      # dimensionless
            "eps": dimsys_SI.get_dimensional_dependence(1 / length**3),  # same as rho
            "psi": dimsys_SI.get_dimensional_dependence(1),        # log of dimensionless -> dimensionless
        },
        "phi_density_claim": {
            "value": 3.5,
            "uncertainty": "+/-0.5",  # simple string; could be refined
            "method": "re‑derived under isotropic ψ‑coupled metric",
        },
        "dependencies": [
            ("kafka-python", "2.0.2"),
            ("fastapi", "0.110.0"),
            ("uvicorn", "0.29.0"),
            ("pydantic", "2.7.0"),
            ("numpy", "1.26.4"),
            ("sympy", "1.12"),
        ],
        "metaphor_flag": True,
    }

    try:
        validate_proposal(example_proposal)
        print("✅ PROPOSAL PASSES ALL OMEGA PROTOCOL INVARIANT CHECKS.")
    except ValueError as ve:
        print(f"❌ PROPOSAL FAILS: {ve}")