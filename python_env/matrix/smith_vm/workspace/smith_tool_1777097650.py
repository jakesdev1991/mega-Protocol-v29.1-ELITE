# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
# Omega Protocol Audit Validation Script
# Validates the mathematical soundness and rule compliance of Agent Smith's audit report.

import math
import re

# ==================== DATA FROM AUDIT REPORT ====================

# Φ-density impact table (values in Φ units)
impact_table = {
    "Alpha": {
        "Task Compliance": float("-inf"),
        "Originality": -0.15,
        "Code Integrity": +0.05,
        "Self-Audit Quality": +0.00,
        "Quantum Insight": -0.10,
        "Net Φ-Density": float("-inf")
    },
    "Beta": {
        "Task Compliance": float("-inf"),
        "Originality": -0.15,
        "Code Integrity": +0.05,
        "Self-Audit Quality": +0.00,
        "Quantum Insight": -0.10,
        "Net Φ-Density": float("-inf")
    },
    "Neo": {
        "Task Compliance": float("-inf"),
        "Originality": -0.15,
        "Code Integrity": -0.20,
        "Self-Audit Quality": +0.00,
        "Quantum Insight": -0.10,
        "Net Φ-Density": float("-inf")
    }
}

# Claimed net Φ-density impact for the round (from audit)
claimed_net_impact = 0.00

# Previous cumulative Φ-density (from audit)
previous_cumulative = 55.09
claimed_new_cumulative = 55.09  # audit claims unchanged

# Submission metadata for derivativity check
submissions = {
    "Alpha": {
        "namespace": "Omega_Psych_Infrastructure",
        "struct_name": "IdentityInfrastructureInvariants",
        "threshold": 0.95,
        "self_audit_text": "Present (copied)",  # placeholder; actual text would be compared
        "phi_density_claim": +0.25
    },
    "Beta": {
        "namespace": "Omega_Psych_Infrastructure",
        "struct_name": "IdentityInfrastructureInvariants",
        "threshold": 0.95,
        "self_audit_text": "Present (copied)",
        "phi_density_claim": +0.25
    },
    "Neo": {
        "namespace": "Omega_Tokamak_Domain",  # different domain
        "struct_name": "DomainIntegrityInvariants",
        "threshold": None,  # not applicable
        "self_audit_text": "Present (wrong task)",
        "phi_density_claim": None
    }
}

# Neo's code snippet (as given in audit)
neo_code_snippet = '''
double CalculateNetGain(double cod_before, double cod_after, int audit_checks) {
    double raw_gain = cod_after - cod_before;
    double audit_cost = audit_checks * DomainIntegrityInvariants::AUDIT_ENTROPY_PER_CHECK;
    return raw_gain - audit_cost;  // Missing closing brace AND missing semicolon
'''

# ==================== VALIDATION FUNCTIONS ====================

def check_finite_phi_values(table):
    """Ensure all Φ values are finite numbers (no -inf, inf, or NaN)."""
    violations = []
    for agent, categories in table.items():
        for cat, val in categories.items():
            if not isinstance(val, (int, float)) or math.isinf(val) or math.isnan(val):
                violations.append((agent, cat, val))
    return violations

def compute_net_impact(table):
    """Sum the claimed Net Φ-Density per agent and return total."""
    total = 0.0
    for agent, categories in table.items():
        net = categories.get("Net Φ-Density", 0.0)
        if math.isinf(net) or math.isnan(net):
            # treat non-finite as zero for sum? but we will flag separately
            continue
        total += net
    return total

def check_cumulative_consistency(prev, net_impact, claimed_new):
    """Verify that prev + net_impact equals claimed_new (within tolerance)."""
    tolerance = 1e-9
    return abs((prev + net_impact) - claimed_new) < tolerance

def derivativity_check(subs):
    """Detect identical submissions (excluding Neo due to different domain)."""
    # Compare Alpha and Beta only (both psychology branch)
    alpha = subs["Alpha"]
    beta = subs["Beta"]
    # Fields that should be identical if copied
    fields_to_compare = ["namespace", "struct_name", "threshold", "self_audit_text", "phi_density_claim"]
    identical = all(alpha[f] == beta[f] for f in fields_to_compare if alpha[f] is not None and beta[f] is not None)
    return identical, alpha if identical else None

def syntax_error_check(code):
    """Simple check for missing closing brace and missing semicolon after return."""
    # Count opening and closing braces
    open_braces = code.count('{')
    close_braces = code.count('}')
    missing_brace = open_braces != close_braces
    # Look for a return statement not followed by semicolon before closing brace
    # Simplistic: find 'return' and see if there is a ';' before next '}' or end of line
    lines = code.split('\n')
    missing_semicolon = False
    for line in lines:
        if 'return' in line and ';' not in line:
            # check if the line ends with comment or nothing; assume missing
            missing_semicolon = True
            break
    return missing_brace, missing_semicolon

# ==================== EXECUTION & REPORTING ====================

print("=== Omega Protocol Audit Validation ===\n")

# 1. Φ-density finiteness
phi_violations = check_finite_phi_values(impact_table)
if phi_violations:
    print("❌ VIOLATION: Non-finite Φ values detected:")
    for agent, cat, val in phi_violations:
        print(f"   - {agent}.{cat} = {val}")
else:
    print("✅ PASS: All Φ values are finite numbers.")

# 2. Net impact calculation
computed_net = compute_net_impact(impact_table)
print(f"\n📊 Net Φ-density impact:")
print(f"   Claimed: {claimed_net_impact:.2f}Φ")
print(f"   Computed from table: {computed_net:.2f}Φ")
if math.isclose(computed_net, claimed_net_impact, rel_tol=1e-9):
    print("   ✅ PASS: Net impact matches sum of table.")
else:
    print("   ❌ FAIL: Net impact mismatch.")

# 3. Cumulative consistency
cum_ok = check_cumulative_consistency(previous_cumulative, computed_net, claimed_new_cumulative)
print(f"\n📈 Cumulative Φ-density:")
print(f"   Previous: {previous_cumulative:.2f}Φ")
print(f"   Net impact: {computed_net:.2f}Φ")
print(f"   Expected new: {previous_cumulative + computed_net:.2f}Φ")
print(f"   Claimed new: {claimed_new_cumulative:.2f}Φ")
if cum_ok:
    print("   ✅ PASS: Cumulative consistency holds.")
else:
    print("   ❌ FAIL: Cumulative inconsistency.")

# 4. Derivativity check
identical, agent = derivativity_check(submissions)
print(f"\n🔍 Derivativity check (Alpha vs Beta):")
if identical:
    print("   ❌ VIOLATION: Submissions are identical (self-plagiarism/plagiarism).")
    print(f"      Matching fields: namespace, struct_name, threshold, self-audit text, Φ-density claim.")
else:
    print("   ✅ PASS: No derivativity detected between Alpha and Beta.")

# 5. Neo's syntax error check
missing_brace, missing_semicolon = syntax_error_check(neo_code_snippet)
print(f"\n💻 Neo's code syntax check:")
if missing_brace:
    print("   ❌ VIOLATION: Missing closing brace.")
else:
    print("   ✅ Brace count balanced.")
if missing_semicolon:
    print("   ❌ VIOLATION: Missing semicolon after return statement.")
else:
    print("   ✅ Semicolon present after return.")

# ==================== SUMMARY ====================
print("\n=== VALIDATION SUMMARY ===")
all_checks = [
    len(phi_violations) == 0,
    math.isclose(computed_net, claimed_net_impact, rel_tol=1e-9),
    cum_ok,
    not identical,  # we want NO derivativity
    not (missing_brace or missing_semicolon)  # we want NO syntax errors
]
if all(all_checks):
    print("🟢 Overall: Audit is mathematically sound and protocol-compliant.")
else:
    print("🔴 Overall: Audit contains violations; see details above.")
print("==========================")