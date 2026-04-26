# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import sys
import re

def normalize_text(s):
    """Remove LaTeX escapes, non-alphanumeric/underscore chars, and lowercase for invariant matching."""
    # Remove LaTeX command markers (backslashes) and curly braces
    s = re.sub(r'\\[a-zA-Z]+', '', s)  # Remove \command
    s = re.sub(r'[{}]', '', s)         # Remove curly braces
    # Keep only alphanumeric and underscore, then lowercase
    return ''.join(c for c in s if c.isalnum() or c == '_').lower()

def main():
    data = sys.stdin.read()
    
    # Extract Engine's output
    engine_start = "### **Internal Thought Process – Repairing the Higher-Order Lattice Polarization Derivation**"
    engine_end = "SCRUTINY AUDIT:"
    start_idx = data.find(engine_start)
    if start_idx == -1:
        print("ERROR: Engine start marker not found")
        return "META-FAIL (Engine output not found)"
    end_idx = data.find(engine_end, start_idx)
    engine_output = data[start_idx:end_idx] if end_idx != -1 else data[start_idx:]
    
    # Extract Scrutiny audit
    scrutiny_start = "SCRUTINY AUDIT: **Internal Thought Process (Audit Procedure)**"
    scrutiny_end = "### Final Output (Critique)"
    start_scrut = data.find(scrutiny_start)
    if start_scrut == -1:
        print("ERROR: Scrutiny start marker not found")
        return "META-FAIL (Scrutiny audit not found)"
    end_scrut = data.find(scrutiny_end, start_scrut)
    scrutiny_output = data[start_scrut:end_scrut] if end_scrut != -1 else data[start_scrut:]
    
    # Normalize texts for invariant checks
    norm_engine = normalize_text(engine_output)
    norm_scrutiny = normalize_text(scrutiny_output)
    
    # Define required invariants (normalized forms)
    invariants = [
        ("psi = ln(phi_n)", "psilnphin"),   # ψ = ln(Φ_N)
        ("xi_n", "xinu"),                   # ξ_N
        ("xi_delta", "xidelta")             # ξ_Δ (using 'delta' as subscript)
    ]
    
    # Check Engine output for missing invariants
    missing_invariants = []
    for display, norm_pattern in invariants:
        if norm_pattern not in norm_engine:
            missing_invariants.append(display)
    
    # Check Scrutiny audit: did it mention the invariants (indicating it checked for them)?
    scrutiny_checked = any(norm_pattern in norm_scrutiny for _, norm_pattern in invariants)
    
    # Output validation results
    print("=== OMEGA PROTOCOL VALIDATION ===")
    print(f"Engine output normalized snippet (first 200 chars): {norm_engine[:200]}...")
    print(f"\nMissing invariants in Engine output: {missing_invariants if missing_invariants else 'None'}")
    print(f"Scrutiny audit checked for invariants: {scrutiny_checked}")
    
    # Determine compliance
    engine_compliant = len(missing_invariants) == 0
    scrutiny_did_its_job = scrutiny_checked
    
    if engine_compliant and scrutiny_did_its_job:
        print("\nRESULT: META-PASS")
        print("Engine output satisfies Omega Protocol invariants, and Scrutiny correctly verified them.")
        return "META-PASS"
    else:
        print("\nRESULT: META-FAIL")
        if not engine_compliant:
            print(f"- Engine output missing required invariants: {', '.join(missing_invariants)}")
        if not scrutiny_did_its_job:
            print("- Scrutiny audit failed to check for required Omega Protocol invariants (psi, xi_N, xi_Δ)")
        print("Required actions:")
        print("  1. Revise Engine output to explicitly include:")
        print("     - ψ = ln(Φ_N) in metric coupling discussion")
        print("     - ξ_N and ξ_Δ as stiffness terms in entropy gauge")
        print("  2. Update Scrutiny auditing protocol to mandate invariant verification per Directive 1.3 (Rubric Adherence)")
        return "META-FAIL"

if __name__ == "__main__":
    result = main()
    # For VM execution, we output the result as the final verdict
    print(f"\nFINAL VERDICT: {result}")