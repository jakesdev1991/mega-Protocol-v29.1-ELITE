# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import re
import os
import sys

def validate_makefile(makefile_path='Makefile'):
    """Validate Makefile fixes for Omega Protocol compliance."""
    if not os.path.exists(makefile_path):
        print(f"ERROR: Makefile not found at {makefile_path}")
        return False
    
    with open(makefile_path, 'r') as f:
        content = f.read()
    
    # Check 1: Pattern rule syntax (must be $(RESEARCH_ROOT)/%/%/%.md)
    pattern_rule_match = re.search(r'\$\(RESEARCH_ROOT\)/%/%/%.md:', content)
    if not pattern_rule_match:
        print("ERROR: Pattern rule incorrect. Expected: $(RESEARCH_ROOT)/%/%/%.md:")
        return False
    
    # Check 2: Stem extraction uses word 1 and word 2 (not word 2/3)
    # Find the pattern rule recipe
    recipe_match = re.search(
        r'\$\(RESEARCH_ROOT\)/%/%/%.md:\s*\n((?:\s*@.*\n)*)', 
        content, 
        re.MULTILINE
    )
    if not recipe_match:
        print("ERROR: Could not find pattern rule recipe")
        return False
    
    recipe = recipe_match.group(1)
    
    # Check for Type assignment (word 1)
    type_match = re.search(
        r'Type:\s*\$\\(word\s+1,\s*\$\(subst\s+/,\s*,\s*\$\(subst\s+\$\(RESEARCH_ROOT\)/,.*,\$\\(dir\s+\$@\)\)\)\\)',
        recipe
    )
    if not type_match:
        print("ERROR: Type extraction incorrect. Must use word 1")
        return False
    
    # Check for Name assignment (word 2)
    name_match = re.search(
        r'Name:\s*\$\\(word\s+2,\s*\$\(subst\s+/,\s*,\s*\$\(subst\s+\$\(RESEARCH_ROOT\)/,.*,\$\\(dir\s+\$@\)\)\)\\)',
        recipe
    )
    if not name_match:
        print("ERROR: Name extraction incorrect. Must use word 2")
        return False
    
    # Check 3: Documentation target has no unsatisfied prerequisites
    doc_target_match = re.search(r'^documentation:\s*$', content, re.MULTILINE)
    if not doc_target_match:
        print("ERROR: Documentation target missing or malformed")
        return False
    
    # Check documentation target has no prerequisites (only recipe lines after)
    doc_recipe_match = re.search(
        r'^documentation:\s*$\n((?:\s*@.*\n)*)', 
        content, 
        re.MULTILINE
    )
    if not doc_recipe_match:
        print("ERROR: Documentation target recipe missing")
        return False
    
    # Verify no file prerequisites (only @commands)
    doc_recipe = doc_recipe_match.group(1)
    if re.search(r'^[^@\t#]', doc_recipe, re.MULTILINE):
        print("ERROR: Documentation target has file prerequisites (must be phony)")
        return False
    
    print("✓ Makefile validation PASSED")
    return True

def validate_phi_trajectory(response_text):
    """Validate Φ trajectory math from response text."""
    # Extract the Net Φ Trajectory table
    table_match = re.search(
        r'## Net Φ Trajectory\s*\n\| Phase \| Φ Impact \| Rationale \|\n\|.*?\|\n(.*?)\n\|\*\*Net\*\*\|',
        response_text,
        re.DOTALL
    )
    
    if not table_match:
        print("WARNING: Could not find Φ trajectory table in response")
        return False
    
    table_content = table_match.group(1)
    lines = [line.strip() for line in table_content.split('\n') if line.strip()]
    
    impacts = []
    for line in lines:
        # Match: | Phase | ±X% | Rationale |
        impact_match = re.search(r'\|\s*[^|]+\s*\|\s*([+-]?\d+)%\s*\|\s*[^|]+\s*\|', line)
        if impact_match:
            impacts.append(int(impact_match.group(1)))
    
    if len(impacts) != 4:
        print(f"ERROR: Expected 4 impact values, found {len(impacts)}")
        return False
    
    # Extract net impact
    net_match = re.search(
        r'\|\*\*Net\*\*\|\s*\*\*([+-]?\d+)%\*\*\s*\|', 
        table_match.group(0)
    )
    if not net_match:
        print("ERROR: Could not find net impact in table")
        return False
    
    net_impact = int(net_match.group(1))
    calculated_impact = sum(impacts)
    
    if net_impact != calculated_impact:
        print(f"ERROR: Φ trajectory math invalid. Sum of impacts {calculated_impact}% ≠ net {net_impact}%")
        return False
    
    print(f"✓ Φ trajectory validation PASSED: {impacts} → {net_impact}%")
    return True

def main():
    """Main validation routine for Omega Protocol compliance."""
    print("=== Omega Protocol Invariant Validation ===\n")
    
    # Validate Makefile (concrete audit fix)
    makefile_ok = validate_makefile()
    
    # Validate Φ trajectory math (if response provided)
    response_ok = True
    if len(sys.argv) > 1:
        # Assume first argument is path to response file
        response_path = sys.argv[1]
        if os.path.exists(response_path):
            with open(response_path, 'r') as f:
                response_text = f.read()
            response_ok = validate_phi_trajectory(response_text)
        else:
            print(f"WARNING: Response file not found at {response_path}")
            response_ok = False
    else:
        print("INFO: No response file provided for Φ trajectory validation")
    
    print("\n=== Summary ===")
    if makefile_ok and response_ok:
        print("✓ ALL VALIDATIONS PASSED - Omega Protocol invariants upheld")
        sys.exit(0)
    else:
        print("✗ VALIDATION FAILED - Protocol violation detected")
        sys.exit(1)

if __name__ == "__main__":
    main()