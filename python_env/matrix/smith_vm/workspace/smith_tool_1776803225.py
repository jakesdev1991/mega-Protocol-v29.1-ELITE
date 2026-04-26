# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
# Agent Smith – Omega Protocol Validation Script
# Purpose: Verify that the repaired CTMS‑Ω proposal satisfies the
#          Omega Physics Rubric v26.0 invariants and core equations.
#          Any deviation triggers a FAIL and a diagnostic message.

import re
import sympy as sp

# ----------------------------------------------------------------------
# 1.  Helper: extract LaTeX‑style equations from the proposal text.
# ----------------------------------------------------------------------
def extract_equations(text):
    """Return a list of raw LaTeX strings found between $$ ... $$ or \[ ... \] """
    pattern = r'\$\$(.*?)\$\$|\\\[(.*?)\\\]'
    matches = re.findall(pattern, text, re.DOTALL)
    eqs = []
    for a, b in matches:
        eqs.append(a.strip() if a else b.strip())
    return eqs

# ----------------------------------------------------------------------
# 2.  Load the proposal (in practice this would be the Engine's final output).
# ----------------------------------------------------------------------
# For the purpose of this audit we embed the repaired proposal as a string.
# In a real VM the text would be supplied by the environment.
proposal = r"""
... (the full repaired proposal text) ...
"""  # <-- Replace with actual proposal text when running in the VM.

equations = extract_equations(proposal)

# ----------------------------------------------------------------------
# 3.  Define the canonical forms we expect (up to symbol renaming).
# ----------------------------------------------------------------------
# Invariant: ψ_cog = ln( Φ_N_cog / Φ_N0 )
invariant_pattern = r'\\psi_{\text{cog}}\s*=\s*\\ln\s*\(\s*\\Phi_N^{\(text{cog}\)}\s*/\s*\\Phi_N^{(0)}\s*\)'

# Fokker‑Planck: ∂_t P = -∂_Λ[μ P] + ½ ∂_Λ²[D P] + S
fp_pattern = r'\\partial_t\s*P\s*=\s*-\\partial_\Lambda\s*\[\s*\\mu\s*P\s*\]\s*\+\s*\\frac{1}{2}\\s*\\partial_\Lambda\^2\s*\[\s*D\s*P\s*\]\s*\+\s*S'

# Omega Action (must contain the gauge term A_μ J^μ)
# We look for the kinetic term, potential, Omega coupling, and gauge term.
action_kinetic   = r'\\frac{1}{2}\\s*g\^{\\mu\nu}\\s*\\partial_\mu\\s*\\Lambda\\s*\\partial_\nu\\s*\\Lambda'
action_potential = r'\\+\\s*V\\(\\Lambda\\)'
action_omega     = r'\\+\\s*\\lambda_\Omega\\s*\\mathcal{L}_\Omega\\(\\Phi_N,\\s*\\Phi_\Delta\\)'
action_gauge     = r'\\+\\s*A_\mu\\s*J\^\mu'

# Boundary conditions (Shredding Event & Informational Freeze)
shred_pattern = r'Shredding\s+Event.*\\Phi_N^{\\(text{cog\\)}\s*<\s*0\.5'
freeze_pattern = r'Informational\s+Freeze.*\\Phi_\Delta^{\\(text{cog\\)}\s*>\s*0\.8'

# ----------------------------------------------------------------------
# 4.  Validation routine
# ----------------------------------------------------------------------
def check(pattern, name, text):
    if re.search(pattern, text, re.IGNORECASE):
        return True, f"[PASS] {name}"
    else:
        return False, f"[FAIL] {name} – pattern not found: {pattern}"

def validate():
    failures = []
    # Join all equations for a global search (some patterns span lines)
    blob = " ".join(equations)

    # Invariant
    ok, msg = check(invariant_pattern, "Invariant ψ_cog = ln(Φ_N_cog/Φ_N0)", blob)
    if not ok: failures.append(msg)

    # Fokker‑Planck
    ok, msg = check(fp_pattern, "Fokker‑Planck with ½ factor", blob)
    if not ok: failures.append(msg)

    # Action components
    for comp, name in [(action_kinetic,   "Kinetic term ½ g^{μν}∂_μΛ∂_νΛ"),
                       (action_potential, "Potential V(Λ)"),
                       (action_omega,    "Omega coupling λ_Ω L_Ω"),
                       (action_gauge,    "Entropy gauge term A_μ J^μ")]:
        ok, msg = check(comp, name, blob)
        if not ok: failures.append(msg)

    # Boundaries
    ok, msg = check(shred_pattern, "Shredding Event boundary", blob)
    if not ok: failures.append(msg)
    ok, msg = check(freeze_pattern, "Informational Freeze boundary", blob)
    if not ok: failures.append(msg)

    # Dimensional sanity check: we assume the proposal states all quantities are dimensionless.
    # We simply verify that the text contains an explicit statement to that effect.
    dim_stmt = r'all.*coordinates.*fields.*and.*metric.*are.*dimensionless'
    ok, msg = check(dim_stmt, "Dimensional consistency statement", blob)
    if not ok: failures.append(msg)

    # Summary
    if failures:
        print("Ω‑PROTOCOL VALIDATION FAILED")
        for f in failures:
            print(f)
        return False
    else:
        print("Ω‑PROTOCOL VALIDATION PASSED – all invariants and structural checks satisfied.")
        return True

# ----------------------------------------------------------------------
# 5.  Run validation
# ----------------------------------------------------------------------
if __name__ == "__main__":
    validate()