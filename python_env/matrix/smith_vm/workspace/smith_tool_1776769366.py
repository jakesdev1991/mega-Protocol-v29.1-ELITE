# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
#!/usr/bin/env python3
"""
Omega Protocol invariant validator for NCSM-Ω proposal.
Checks:
  - No boilerplate (markdown headings, list markers)
  - Presence of an entropy-based observable
  - Symbolic consistency of ξ_N, ξ_Δ, ψ, Φ_N, Φ_Δ definitions
"""

import re
import sympy as sp

# -------------------- 1. Boilerplate detection --------------------
BOILERPLATE_PATTERNS = [
    r'^#{1,6}\s',          # markdown heading
    r'^\s*[-*+]\s',        # unordered list
    r'^\s*\d+\.\s',        # ordered list
    r'^\s*>\s',            # blockquote
]

def has_boilerplate(text: str) -> bool:
    lines = text.splitlines()
    for pat in BOILERPLATE_PATTERNS:
        if any(re.match(pat, line) for line in lines):
            return True
    return False

# -------------------- 2. Entropy observable --------------------
ENTROPY_KEYWORDS = [
    r'\bShannon\b',
    r'\bentropy\b',
    r'\bS_embed\b',
    r'\bS_\w*entropy\b',
    r'\b-\s*\\sum\s*.*log\b',  # rough sum‑log pattern
]

def has_entropy_observable(text: str) -> bool:
    combined = ' '.join(ENTROPY_KEYWORDS)
    pattern = re.compile(combined, re.IGNORECASE)
    return bool(pattern.search(text))

# -------------------- 3. Symbolic invariant check --------------------
def check_invariants(xi_N_sq_expr: str,
                     xi_Delta_sq_expr: str,
                     psi_expr: str,
                     Phi_N_expr: str,
                     Phi_Delta_expr: str) -> bool:
    """
    Expected relationships (derived from the proposal):
        xi_N^{-2} = λ_eff * (3*I0**2 + <R>)
        xi_Δ^{-2} = λ_eff * (I0**2 + 3*<R>)
        ψ = ln(xi/xi0)   with xi = sqrt(xi_N * xi_Δ)
        ξ_N = ∂Φ_N/∂ψ ,   ξ_Δ = ∂Φ_Δ/∂ψ
    We verify the first two and the definitional ψ; the derivative
    links are checked symbolically if Φ_N, Φ_Δ are given as functions of ψ.
    """
    # Define symbols
    λ_eff, I0, R_bar, xi0 = sp.symbols('λ_eff I0 R_bar xi0', positive=True)
    # Parse expressions
    try:
        xi_N_sq = sp.sympify(xi_N_sq_expr)
        xi_D_sq = sp.sympify(xi_Delta_sq_expr)
        psi = sp.sympify(psi_expr)
        Phi_N = sp.sympify(Phi_N_expr)
        Phi_D = sp.sympify(Phi_Delta_expr)
    except Exception as e:
        print(f"Sympy parsing error: {e}")
        return False

    # Invariants from definitions
    xi_N_sq_def = λ_eff * (3*I0**2 + R_bar)
    xi_D_sq_def = λ_eff * (I0**2 + 3*R_bar)

    # Check first two equalities
    if not sp.simplify(xi_N_sq - xi_N_sq_def) == 0:
        print("ξ_N^{-2} mismatch")
        return False
    if not sp.simplify(xi_D_sq - xi_D_sq_def) == 0:
        print("ξ_Δ^{-2} mismatch")
        return False

    # ψ definition: ψ = ln(xi/xi0) where xi = sqrt(xi_N * xi_Δ)
    xi = sp.sqrt(1/sp.sqrt(xi_N_sq) * 1/sp.sqrt(xi_D_sq))  # xi = sqrt(xi_N * xi_Δ) -> xi^2 = xi_N*xi_Δ
    # Actually xi = sqrt(xi_N * xi_Δ) => xi^2 = xi_N * xi_Δ
    xi_sq = xi_N_sq**(-1/2) * xi_D_sq**(-1/2)  # because xi_N_sq = 1/xi_N^2 etc.
    # Simpler: compute xi from inverses
    xi_N = xi_N_sq**(-1/2)
    xi_D = xi_D_sq**(-1/2)
    xi_calc = sp.sqrt(xi_N * xi_D)
    psi_def = sp.log(xi_calc / xi0)

    if not sp.simplify(psi - psi_def) == 0:
        print("ψ definition mismatch")
        return False

    # Derivative links: ξ_N = ∂Φ_N/∂ψ, ξ_Δ = ∂Φ_Δ/∂ψ
    # Compute derivatives symbolically
    dPhiN_dpsi = sp.diff(Phi_N, sp.symbols('psi'))
    dPhiD_dpsi = sp.diff(Phi_D, sp.symbols('psi'))
    if not sp.simplify(xi_N - dPhiN_dpsi) == 0:
        print("∂Φ_N/∂ψ != ξ_N")
        return False
    if not sp.simplify(xi_D - dPhiD_dpsi) == 0:
        print("∂Φ_Δ/∂ψ != ξ_Δ")
        return False

    return True

# -------------------- Main validation --------------------
if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python validate_ncsm.py <path_to_proposal_text>")
        sys.exit(1)

    with open(sys.argv[1], 'r', encoding='utf-8') as f:
        proposal = f.read()

    print("=== Boilerplate check ===")
    if has_boilerplate(proposal):
        print("FAIL: Markdown headings or list-like structures detected.")
    else:
        print("PASS: No boilerplate found.")

    print("\n=== Entropy observable check ===")
    if has_entropy_observable(proposal):
        print("PASS: Entropy‑based term found.")
    else:
        print("FAIL: No Shannon‑entropy‑based observable detected.")

    print("\n=== Symbolic invariant check (example placeholders) ===")
    # The user should replace these strings with the actual expressions from their proposal.
    # Example placeholders (these should match the derivations above):
    xi_N_sq_str   = "lambda_eff * (3*I0**2 + R_bar)"
    xi_D_sq_str   = "lambda_eff * (I0**2 + 3*R_bar)"
    psi_str       = "log(sqrt(xi_N * xi_D) / xi0)"
    Phi_N_str     = "Phi_N0 + alpha * psi"   # linear in psi for illustration
    Phi_D_str     = "Phi_D0 - beta * psi + gamma * Var_phi"

    # To actually test, the user must supply the correct expressions.
    # Here we just demonstrate the call; replace with real strings.
    try:
        ok = check_invariants(xi_N_sq_str, xi_D_sq_str, psi_str,
                              Phi_N_str, Phi_D_str)
        print("PASS" if ok else "FAIL: Invariant relationships not satisfied.")
    except Exception as e:
        print(f"Error during invariant check: {e}")