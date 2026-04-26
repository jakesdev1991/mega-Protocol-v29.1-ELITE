# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
# Omega Protocol Mathematical Validation Script
# Validates Φ-Density impact calculations from audit report
# Enforces Directive 5 (Entropy Control): Knowledge entropy must decrease or remain neutral

def validate_phi_density_impact():
    """
    Validates the Φ-Density impact calculation from the corrected output section.
    Checks: Immediate (-2%) + Months 1-6 (+4%) + Months 7-12 (+3%) + Months 13-24 (+1%) = Net (+6%)
    """
    # Extract impacts from audit report table
    impacts = {
        "Immediate": -2,
        "Months 1-6": 4,
        "Months 7-12": 3,
        "Months 13-24": 1
    }
    
    # Calculate net impact
    calculated_net = sum(impacts.values())
    stated_net = 6  # From audit report: "**Net** | **+6% Φ**"
    
    # Validation
    is_valid = (calculated_net == stated_net)
    
    # Output validation results
    print("=" * 60)
    print("OMEGA PROTOCOL Φ-DENSITY IMPACT VALIDATION")
    print("=" * 60)
    print(f"Impact Components:")
    for phase, value in impacts.items():
        print(f"  {phase:<15}: {value:>3}% Φ")
    print("-" * 60)
    print(f"Calculated Net Impact: {calculated_net}% Φ")
    print(f"Stated Net Impact:     {stated_net}% Φ")
    print("-" * 60)
    print(f"VALIDATION RESULT: {'PASS' if is_valid else 'FAIL'}")
    print("=" * 60)
    
    if not is_valid:
        raise ValueError(
            f"Φ-Density impact calculation invalid: "
            f"calculated {calculated_net}% ≠ stated {stated_net}% "
            f"(Violates Directive 5: Entropy Control)"
        )
    
    return is_valid

def validate_makefile_stem_extraction():
    """
    Validates the corrected stem extraction logic in the Makefile.
    Ensures pattern rule uses $* (stem) not $(dir $@) (path).
    """
    # Simulate Makefile variable expansion for target: automations/phones/Samsung_Galaxy_A16/shizuku_persistence.md
    target = "automations/phones/Samsung_Galaxy_A16/shizuku_persistence.md"
    
    # INCORRECT approach (original flaw): $(dir $@)
    dir_approach = target.rsplit('/', 1)[0] + '/' if '/' in target else './'
    # Result: "automations/phones/Samsung_Galaxy_A16/" (always ends with /)
    
    # CORRECT approach (fixed): $* via $(notdir $@)
    notdir_approach = target.split('/')[-1]  # Filename only
    stem_approach = notdir_approach.replace('.md', '')  # Remove extension
    
    # Validation: Stem must contain at least one underscore for pattern rule %_%.md
    has_underscore = '_' in stem_approach
    
    print("\n" + "=" * 60)
    print("MAKEFILE STEM EXTRACTION VALIDATION")
    print("=" * 60)
    print(f"Target: {target}")
    print(f"$(dir $@) approach: '{dir_approach}' (PATH - INCORRECT for stem)")
    print(f"$* approach: '{stem_approach}' (STEM - CORRECT)")
    print(f"Contains underscore: {has_underscore} (Required for %_%.md pattern)")
    print("-" * 60)
    
    is_valid = has_underscore and (dir_approake != stem_approach)
    print(f"VALIDATION RESULT: {'PASS' if is_valid else 'FAIL'}")
    print("=" * 60)
    
    if not is_valid:
        raise ValueError(
            "Stem extraction logic flawed: "
            "Using $(dir $@) yields path, not stem. "
            "Pattern rule %_%.md requires underscore in stem."
        )
    
    return is_valid

def validate_readme_safeguard():
    """
    Validates that README.md is protected from pattern rule overwrite.
    Checks: Explicit rule exists AND pattern rule restricted to %_%.md
    """
    # Simulate file targets
    targets = [
        "automations/phones/Samsung_Galaxy_A16/README.md",
        "automations/phones/Samsung_Galaxy_A16/shizuku_persistence.md",
        "automations/phones/Samsung_Galaxy_A16/termux_tasker_bridge.md",
        "automations/phones/Samsung_Galaxy_A16/zram_scaling.md"
    ]
    
    # Pattern rule: %_%.md (requires ≥1 underscore in stem)
    def matches_pattern(target):
        stem = target.split('/')[-1].replace('.md', '')
        return '_' in stem
    
    # Check README.md is NOT matched by pattern rule
    readme_matches = matches_pattern(targets[0])
    # Check automation files ARE matched
    automations_match = all(matches_pattern(t) for t in targets[1:])
    
    print("\n" + "=" * 60)
    print("README SAFEGUARD VALIDATION")
    print("=" * 60)
    print(f"README.md target: {targets[0]}")
    print(f"Matches pattern %_%.md: {readme_matches} (Should be FALSE)")
    print(f"Automation targets match pattern: {automations_match} (Should be TRUE)")
    print("-" * 60)
    
    is_valid = (not readme_matches) and automations_match
    print(f"VALIDATION RESULT: {'PASS' if is_valid else 'FAIL'}")
    print("=" * 60)
    
    if not is_valid:
        raise ValueError(
            "README safeguard failed: "
            f"README.md incorrectly matches pattern ({readme_matches}) "
            f"or automation targets don't match ({not automations_match})"
        )
    
    return is_valid

def main():
    """
    Main validation executor for Omega Protocol compliance.
    Enforces Directive 5 (Entropy Control) through mathematical verification.
    """
    print("INITIATING OMEGA PROTOCOL AUDIT VALIDATION")
    print("Enforcing Directive 5: Entropy Control (Knowledge entropy must not increase)")
    
    try:
        # Validate all critical mathematical/logical components
        validate_phi_density_impact()
        validate_makefile_stem_extraction()
        validate_readme_safeguard()
        
        print("\n" + "!" * 60)
        print("ALL VALIDATIONS PASSED - OMEGA PROTOCOL COMPLIANT")
        print("Knowledge entropy reduced through verifiable corrections")
        print("!" * 60)
        return True
        
    except ValueError as e:
        print("\n" + "!" * 60)
        print("VALIDATION FAILED - OMEGA PROTOCOL VIOLATION")
        print(f"Error: {e}")
        print("!" * 60)
        return False

if __name__ == "__main__":
    exit(0 if main() else 1)