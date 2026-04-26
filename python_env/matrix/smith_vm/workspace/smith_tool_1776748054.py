# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
#!/usr/bin/env python3
"""
Agent Smith – Omega Protocol Invariant Validator
Checks a proposal text for:
  - NO BOILERPLATE (no numbered headings, no markdown bold/italic section titles)
  - Presence of required invariants (psi, xi_N, xi_Delta) in equations
  - Dimensional consistency of key expressions (heuristic sympy check)
  - Existence of an equation‑level derivation from the Omega Action to an effective Hamiltonian
  - Basic Φ‑density impact quantification (look for numeric percentages or units)
Returns PASS if all checks pass, otherwise a detailed critique.
"""

import re
import sympy as sp
from sympy.physics.units import length, mass, time, energy

# ----------------------------------------------------------------------
# CONFIGURATION – edit these strings to match the proposal text
# ----------------------------------------------------------------------
PROPOSAL_TEXT = r"""<PASTE THE FULL PROPOSAL TEXT HERE>"""

# ----------------------------------------------------------------------
# 1. BOILERPLATE DETECTION
# ----------------------------------------------------------------------
def check_boilerplate(text):
    issues = []
    # Numbered headings like "1.", "2.", "Step 1 –"
    if re.search(r'(?m)^\s*\d+\.\s', text):
        issues.append("Numbered headings detected (e.g., '1. ', '2. ')")
    if re.search(r'(?m)^\s*Step\s+\d+\s*[-:]', text, re.I):
        issues.append("Explicit 'Step' numbering detected")
    # Markdown bold/italic used as section titles (e.g., **Section**)
    if re.search(r'\*\*[^*]+\*\*\s*$', text, re.M):
        issues.append("Bold markdown used as section headings")
    if re.search(r'\_\_[^_]+\_\_\s*$', text, re.M):
        issues.append("Underscore markdown used as section headings")
    return issues

# ----------------------------------------------------------------------
# 2. INVARIANT USAGE – require psi, xi_N, xi_Delta appear in at least one equation
# ----------------------------------------------------------------------
INVARIANTS = [r'\\psi', r'\\xi_N', r'\\xi_\\Delta']
def check_invariants(text):
    missing = []
    # Look for LaTeX math blocks ($...$ or $$...$$ or \[...\])
    math_blocks = re.findall(r'\$(.*?)\$|\$\$(.*?)\$\$|\\\[(.*?)\\\]', text, re.DOTALL)
    math_blobs = [m for group in math_blocks for m in group if m]
    combined = " ".join(math_blobs)
    for inv in INVARIANTS:
        if not re.search(inv, combined):
            missing.append(inv.strip('\\'))
    return missing

# ----------------------------------------------------------------------
# 3. DIMENSIONAL CONSISTENCY (heuristic)
# ----------------------------------------------------------------------
# Define symbols with dimensions
# Field amplitude φ -> sqrt(energy/length^d) ; we keep generic dimension [Φ]
phi = sp.symbols('phi', positive=True)
# Derivatives add 1/length
# We'll check a few key expressions that should appear in the text:
#   H_eff ~ - sum J sigma_z sigma_z - sum K sigma_x sigma_x   => J,K have energy dimension
#   Delta = Delta0 * f(xi_N/xi0, xi_Delta/xi0)                => Delta has energy
#   psi = ln(Phi_N/I0)                                        => dimensionless
#   xi_N, xi_Delta have dimension of length
# We'll attempt to parse expressions of the form J_{ij}(xi_N,xi_Delta) etc.
def extract_expressions(text):
    # Very naive: capture anything that looks like J_{...}(...), K_{...}(...), Delta = ...
    pattern = r'(J_\{[^}]+\}\s*\([^)]+\)|K_\{[^}]+\}\s*\([^)]+\)|\\Delta\s*=\s*[^\\n]+)'
    return re.findall(pattern, text)

def dimensional_check(text):
    issues = []
    exprs = extract_expressions(text)
    if not exprs:
        issues.append("No recognizable J/K/Delta expressions found for dimensional check.")
        return issues

    # Define dimensional symbols
    L = length
    M = mass
    T = time
    E = energy   # M*L^2/T^2
    # Assume xi_N, xi_Delta have dimension of length
    xi_N = sp.symbols('xi_N', dimension=L)
    xi_Delta = sp.symbols('xi_Delta', dimension=L)
    xi0 = sp.symbols('xi_0', dimension=L)
    # Delta0 has dimension of energy
    Delta0 = sp.symbols('Delta_0', dimension=E)
    # Generic function f is dimensionless
    f = sp.symbols('f', dimensionless=True)

    for expr in exprs:
        # Replace LaTeX with sympy symbols where possible
        e = expr.replace('\\', '').replace('{', '(').replace('}', ')')
        e = e.replace('sigma_z', '1').replace('sigma_x', '1')  # Pauli matrices dimensionless
        try:
            # Parse with sympy (will fail on unknown functions; we ignore those)
            parsed = sp.sympify(e)
            # Compute dimensions via substitution
            dims = parsed.xreplace({
                xi_N: L,
                xi_Delta: L,
                xi0: L,
                Delta0: E,
                f: 1
            })
            # If result still has undefined dimension symbols, flag
            if dims.has(sp.Symbol):
                issues.append(f"Unable to verify dimension of expression: {expr}")
            else:
                # Expect energy dimension for J/K/Delta
                if 'J_' in expr or 'K_' in expr:
                    if dims != E:
                        issues.append(f"Expression {expr} does not have energy dimension (got {dims})")
                elif '\\Delta' in expr:
                    if dims != E:
                        issues.append(f"Expression {expr} does not have energy dimension (got {dims})")
        except Exception:
            # If sympy can't parse, we skip but note
            issues.append(f"Could not parse expression for dimensional check: {expr}")
    return issues

# ----------------------------------------------------------------------
# 4. EQUATION‑LEVEL DERIVATION CHECK
# ----------------------------------------------------------------------
def check_derivation(text):
    # Look for a sequence: Omega Action -> effective Hamiltonian -> equations of motion
    markers = [
        r'\\mathcal{S}_\\Omega',          # Omega Action
        r'H_\\text{eff}',                # Effective Hamiltonian
        r'\\dot{\\Phi}_N',               # Time derivative of Phi_N
        r'\\dot{\\Phi}_\\Delta'          # Time derivative of Phi_Delta
    ]
    missing = [m for m in markers if not re.search(m, text)]
    return missing

# ----------------------------------------------------------------------
# 5. Φ‑DENSITY IMPACT QUANTIFICATION
# ----------------------------------------------------------------------
def check_phi_density(text):
    # Look for patterns like "+55%", "-15%", "Φ units", or numbers with % sign
    if not re.search(r'[+-]?\d+\s*%', text):
        return ["No percentage‑based Φ‑density change found"]
    return []

# ----------------------------------------------------------------------
# MAIN VALIDATION
# ----------------------------------------------------------------------
def main():
    critique = []

    # 1. Boilerplate
    boilerplate_issues = check_boilerplate(PROPOSAL_TEXT)
    if boilerplate_issues:
        critique.append("BOILERPLATE VIOLATIONS: " + "; ".join(boilerplate_issues))

    # 2. Invariants
    missing_invariants = check_invariants(PROPOSAL_TEXT)
    if missing_invariants:
        critique.append("MISSING INVARIANT USAGE: " + ", ".join(missing_invariants))

    # 3. Dimensional consistency
    dim_issues = dimensional_check(PROPOSAL_TEXT)
    if dim_issues:
        critique.append("DIMENSIONAL CHECK ISSUES: " + "; ".join(dim_issues))

    # 4. Equation‑level derivation
    derivation_missing = check_derivation(PROPOSAL_TEXT)
    if derivation_missing:
        critique.append("INCOMPLETE DERIVATION (missing markers): " + ", ".join(derivation_missing))

    # 5. Φ‑density impact
    phi_issues = check_phi_density(PROPOSAL_TEXT)
    if phi_issues:
        critique.append("Φ‑DENSITY QUANTIFICATION: " + "; ".join(phi_issues))

    if not critique:
        print("PASS")
    else:
        print("CRITIQUE:")
        for i, c in enumerate(critique, 1):
            print(f"{i}. {c}")

if __name__ == "__main__":
    main()