# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
# -*- coding: utf-8 -*-
"""
Validator for the Cognitive‑Tooling Mismatch Sensor (CTMS‑Ω) proposal.
Checks compliance with the Omega Physics Rubric v26.0 as discussed in the
audit/meta‑scrutiny dialogue.

The validator looks for the following required elements in the proposal text:
1. Invariant definition: ψ_cog = ln( Φ_N^(cog) / Φ_N^(0) )
2. Fokker‑Planck equation with the ½ prefactor on the diffusion term.
3. Omega action containing the explicit entropy gauge term A_μ J^μ.
4. Dimensionless statement (all terms dimensionless after scaling).
5. Boundary definitions: Shredding Event and Informational Freeze linked to
   Φ_N^(cog) and Φ_Δ^(cog) thresholds.
6. Covariant modes mapping (Φ_N as connectivity, Φ_Δ as asymmetry) – we only
   check that the symbols appear with the expected interpretation.
7. TFFI definition (sigmoid form) – optional but checked for completeness.

If any required element is missing or malformed, the validator reports a
FAIL and lists the issues. Otherwise it returns PASS.

Note: This is a syntactic/semantic sanity check; it does not perform a full
symbolic verification of the field theory.
"""

import re
import textwrap

def normalize_whitespace(s: str) -> str:
    """Collapse whitespace and strip for easier regex matching."""
    return re.sub(r'\s+', ' ', s).strip()

def check_invariant(text: str):
    """Look for ψ_cog = ln( Φ_N^(cog) / Φ_N^(0) ) (allowing variations)."""
    # Acceptable variations: ψ_cog, psi_cog, Φ_N^(cog), Phi_N^(cog), etc.
    pattern = r'ψ_cog\s*=\s*ln\s*\(\s*Φ_N\s*\(\s*cog\s*\)\s*/\s*Φ_N\s*\(\s*0\s*\)\s*\)'
    # Also accept plain ASCII names
    pattern2 = r'psi_cog\s*=\s*ln\s*\(\s*Phi_N\s*\(\s*cog\s*\)\s*/\s*Phi_N\s*\(\s*0\s*\)\s*\)'
    if re.search(pattern, text, re.IGNORECASE) or re.search(pattern2, text, re.IGNORECASE):
        return True, "Invariant ψ_cog = ln(Φ_N^(cog)/Φ_N^(0)) found."
    return False, "Invariant definition not found or malformed."

def check_fokker_planck(text: str):
    """Check for ∂_t P = -∂_Λ[μ P] + ½ ∂_Λ^2[D P] + S."""
    # Look for the ½ factor (could be written as \tfrac12, 1/2, 0.5)
    pattern = r'∂_t\s*P\s*=\s*-∂_Λ\[[^\]]*\]\s*\+\s*(\\tfrac12|1/2|0\.5)\s*∂_Λ\^2\[[^\]]*\]\s*\+\s*S'
    if re.search(pattern, text):
        return True, "Fokker‑Planck equation with ½ prefactor found."
    return False, "Fokker‑Planck equation missing the ½ factor or malformed."

def check_action_gauge(text: str):
    """Check that the action integral contains + A_μ J^μ term."""
    # Look for + A_μ J^μ or + A^\mu J_\mu etc.
    pattern = r'\+.*A_\s*mu\s*J\s*^\s*mu|\+.*A^\s*mu\s*J_\s*mu|\+.*A_\mu J^\mu'
    if re.search(pattern, text, re.IGNORECASE):
        return True, "Action contains entropy gauge term A_μ J^μ."
    return False, "Action integral missing explicit A_μ J^μ term."

def check_dimensionless(text: str):
    """Check for a statement that all terms are dimensionless after scaling."""
    # Look for phrases like "dimensionless", "natural units", "after normalization"
    pattern = r'dimensionless.*after.*scaling|all.*terms.*dimensionless|coordinates.*dimensionless|metric.*dimensionless'
    if re.search(pattern, text, re.IGNORECASE):
        return True, "Dimensionless scaling statement found."
    return False, "No explicit statement that all terms are dimensionless after scaling."

def check_boundaries(text: str):
    """Check for Shredding Event and Informational Freeze definitions."""
    shred_pattern = r'Shredding.*Event.*ψ_cog\s*→\s*\+∞.*Φ_N\s*\(\s*cog\s*\)\s*<\s*0\.5'
    freeze_pattern = r'Informational.*Freeze.*ψ_cog\s*→\s*-∞.*Φ_Δ\s*\(\s*cog\s*\)\s*>\s*0\.8'
    if re.search(shred_pattern, text, re.IGNORECASE) and re.search(freeze_pattern, text, re.IGNORECASE):
        return True, "Both Shredding Event and Informational Freeze boundaries defined."
    missing = []
    if not re.search(shred_pattern, text, re.IGNORECASE):
        missing.append("Shredding Event")
    if not re.search(freeze_pattern, text, re.IGNORECASE):
        missing.append("Informational Freeze")
    return False, f"Missing boundary definition(s): {', '.join(missing)}."

def check_covariant_modes(text: str):
    """Check that Φ_N is described as connectivity/inverse path length and Φ_Δ as asymmetry/skewness."""
    conn_pattern = r'Φ_N\s*\(\s*cog\s*\).*inverse.*average.*path.*length|connectivity'
    asym_pattern = r'Φ_Δ\s*\(\s*cog\s*\).*skewness|asymmetry'
    conn_ok = re.search(conn_pattern, text, re.IGNORECASE) is not None
    asym_ok = re.search(asym_pattern, text, re.IGNORECASE) is not None
    if conn_ok and asym_ok:
        return True, "Covariant modes Φ_N (connectivity) and Φ_Δ (asymmetry) described."
    missing = []
    if not conn_ok:
        missing.append("Φ_N connectivity description")
    if not asym_ok:
        missing.append("Φ_Δ asymmetry description")
    return False, f"Missing covariant mode description(s): {', '.join(missing)}."

def check_tffi(text: str):
    """Optional: check for TFFI sigmoid definition."""
    pattern = r'TFFI.*σ\s*\(|TFFI.*sigmoid'
    if re.search(pattern, text, re.IGNORECASE):
        return True, "TFFI sigmoid definition present."
    return False, "TFFI definition not found (optional)."

def validate_proposal(proposal_text: str):
    """Run all checks and return a structured result."""
    text = normalize_whitespace(proposal_text)
    checks = [
        ("Invariant", check_invariant),
        ("Fokker‑Planck", check_fokker_planck),
        ("Action Gauge Term", check_action_gauge),
        ("Dimensionless Scaling", check_dimensionless),
        ("Boundary Conditions", check_boundaries),
        ("Covariant Modes", check_covariant_modes),
        ("TFFI (optional)", check_tffi),
    ]
    passed = []
    failed = []
    for name, func in checks:
        ok, msg = func(text)
        if ok:
            passed.append((name, msg))
        else:
            failed.append((name, msg))
    return passed, failed

if __name__ == "__main__":
    # Load the proposal text from a file or embed directly.
    # For this demonstration we assume the proposal is provided via stdin
    # or we can read from a file named 'proposal.txt'.
    import sys
    if len(sys.argv) > 1:
        with open(sys.argv[0], 'r', encoding='utf-8') as f:
            proposal = f.read()
    else:
        # Read from stdin if piped
        proposal = sys.stdin.read()

    passed, failed = validate_proposal(proposal)

    print("=== Omega Protocol Compliance Validation ===\n")
    if passed:
        print("Passed checks:")
        for name, msg in passed:
            print(f"  ✔ {name}: {msg}")
    else:
        print("No checks passed.")

    if failed:
        print("\nFailed checks:")
        for name, msg in failed:
            print(f"  ✘ {name}: {msg}")
    else:
        print("\nAll checks passed!")

    # Summary
    print("\n--- Summary ---")
    print(f"Passed: {len(passed)} / {len(passed)+len(failed)}")
    if failed:
        print("Result: FAIL – proposal does not fully satisfy Omega Physics Rubric v26.0.")
        sys.exit(1)
    else:
        print("Result: PASS – proposal meets all verified rubric requirements.")
        sys.exit(0)