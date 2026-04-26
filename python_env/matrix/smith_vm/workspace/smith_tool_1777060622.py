# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import re
import sys
from typing import Tuple, List, Optional

def validate_makefile(makefile_content: str) -> Tuple[bool, List[str]]:
    """
    Validate the Makefile for Samsung Galaxy A16 automation framework
    against Omega Protocol invariants.
    
    Returns:
        (is_valid, list_of_errors)
    """
    errors = []
    lines = makefile_content.splitlines()
    
    # Track state for recipe parsing
    in_automation_rule = False
    automation_rule_lines = []
    found_readme_rule = False
    found_automation_pattern = False
    
    # Check 1: Explicit README.md rule
    readme_pattern = r'^\s*automations/phones/Samsung_Galaxy_A16/README.md\s*:\s*structure\s*$'
    readme_recipe_pattern = r'^\s*@true\s*$'
    
    for i, line in enumerate(lines):
        if re.match(readme_pattern, line):
            # Check next non-empty line for recipe
            j = i + 1
            while j < len(lines) and not lines[j].strip():
                j += 1
            if j < len(lines) and re.match(readme_recipe_pattern, lines[j]):
                found_readme_rule = True
            break
    
    if not found_readme_rule:
        errors.append("Missing or incorrect explicit rule for README.md (should depend on 'structure' with '@true' recipe)")
    
    # Check 2: Automation pattern rule (must restrict to stems with at least one underscore)
    automation_pattern = r'^\s*automations/phones/Samsung_Galaxy_A16/%_%.md\s*:\s*$'
    
    for i, line in enumerate(lines):
        if re.match(automation_pattern, line):
            found_automation_pattern = True
            # Capture the recipe lines (indented with tab)
            j = i + 1
            while j < len(lines) and (lines[j].startswith('\t') or lines[j].startswith(' ')):
                automation_rule_lines.append(lines[j])
                j += 1
            break
    
    if not found_automation_pattern:
        errors.append("Missing automation pattern rule (should match '%_%.md' to exclude README.md)")
    
    # Check 3: Correct stem extraction in automation recipe
    if automation_rule_lines:
        recipe_block = '\n'.join(automation_rule_lines)
        
        # Define required stem extraction patterns
        stem_patterns = [
            r'^\s*STEM\s*:=\s*\$\*\s*$',
            r'^\s*WORDS\s*:=\s*\$\(subst\s*_,\s*,\s*\$\(STEM\)\)\s*$',
            r'^\s*TYPE\s*:=\s*\$\(word\s*1,\s*\$\(WORDS\)\)\s*$',
            r'^\s*NAME\s*:=\s*\$\(wordlist\s*2,\s*\$\(words\s*\$\(WORDS\)\)\s*,\s*\$\(WORDS\)\)\s*$'
        ]
        
        # Check each pattern appears in order
        pattern_index = 0
        for line in automation_rule_lines:
            if pattern_index < len(stem_patterns) and re.match(stem_patterns[pattern_index], line):
                pattern_index += 1
        
        if pattern_index < len(stem_patterns):
            missing = []
            for i in range(pattern_index, len(stem_patterns)):
                missing.append(stem_patterns[i])
            errors.append(f"Missing or incorrect stem extraction in automation recipe. Expected patterns: {missing}")
    else:
        if found_automation_pattern:
            errors.append("Automation pattern rule found but no recipe captured")
    
    # Check 4: Verify no over-matching pattern (catch-all %.md)
    overmatch_pattern = r'^\s*automations/phones/Samsung_Galaxy_A16/%.md\s*:\s*$'
    for line in lines:
        if re.match(overmatch_pattern, line):
            errors.append("Dangerous over-matching pattern found (%.md) - would overwrite README.md")
            break
    
    return len(errors) == 0, errors

def main():
    # Read Makefile from stdin or file
    if len(sys.argv) > 1:
        with open(sys.argv[1], 'r') as f:
            content = f.read()
    else:
        content = sys.stdin.read()
    
    is_valid, errors = validate_makefile(content)
    
    if is_valid:
        print("PASS: Makefile complies with Omega Protocol invariants")
        sys.exit(0)
    else:
        print("FAIL: Makefile violations detected:")
        for error in errors:
            print(f"  - {error}")
        sys.exit(1)

if __name__ == "__main__":
    main()