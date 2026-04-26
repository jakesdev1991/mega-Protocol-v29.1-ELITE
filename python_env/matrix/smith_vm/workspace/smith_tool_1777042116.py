# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
# Omega Protocol Makefile Validator for Samsung Galaxy A16 Automation Framework
# Validates mathematical soundness and compliance with Omega Protocol invariants
# Checks: pattern rule restrictions, stem extraction correctness, prerequisite chains

import re
import sys
from typing import List, Tuple, Dict, Optional

class MakefileValidator:
    def __init__(self, makefile_content: str):
        self.content = makefile_content
        self.lines = makefile_content.splitlines()
        self.errors = []
        self.warnings = []
        
        # Extract key variables
        self.research_root = self._extract_var("RESEARCH_ROOT")
        self.phone_target = self._extract_var("PHONE_TARGET")
        self.phone_path = self._extract_var("PHONE_PATH")
        self.automations = self._extract_var_list("AUTOMATIONS")
        
        # Build expected paths
        self.base_path = f"{self.research_root}/phones/{self.phone_target}" if self.research_root and self.phone_target else None
        self.readme_path = f"{self.base_path}/README.md" if self.base_path else None
        
    def _extract_var(self, var_name: str) -> Optional[str]:
        """Extract variable value (simple := assignment)"""
        pattern = rf'^{var_name}\s*:=\s*(.*)$'
        for line in self.lines:
            match = re.match(pattern, line.strip())
            if match:
                return match.group(1).strip()
        return None
    
    def _extract_var_list(self, var_name: str) -> List[str]:
        """Extract space-separated variable list"""
        val = self._extract_var(var_name)
        if val:
            return [x.strip() for x in val.split() if x.strip()]
        return []
    
    def _find_target_line(self, target: str) -> Optional[int]:
        """Find line number where target is defined"""
        # Look for target: [prerequisites]
        pattern = rf'^{re.escape(target)}\s*:'
        for i, line in enumerate(self.lines):
            if re.match(pattern, line.strip()):
                return i
        return None
    
    def _get_recipe_lines(self, target_line_idx: int) -> List[str]:
        """Get recipe lines (indented with tab) following target line"""
        recipe = []
        i = target_line_idx + 1
        while i < len(self.lines):
            line = self.lines[i]
            if line.startswith('\t') or line.startswith('    '):  # Tab or 4 spaces
                recipe.append(line)
                i += 1
            else:
                break
        return recipe
    
    def validate(self) -> Tuple[bool, List[str]]:
        """Run all validations"""
        self.errors = []
        self.warnings = []
        
        # 1. Validate pattern rule restriction
        self._validate_pattern_rule()
        
        # 2. Validate README.md protection
        self._validate_readme_protection()
        
        # 3. Validate explicit automation targets
        self._validate_explicit_targets()
        
        # 4. Validate stem extraction in pattern rule
        self._validate_stem_extraction()
        
        # 5. Validate prerequisite chains
        self._validate_prerequisite_chains()
        
        return len(self.errors) == 0, self.errors
    
    def _validate_pattern_rule(self):
        """Ensure pattern rule restricts to stems with underscores"""
        # Look for pattern rule: %_%.md
        pattern_rule_found = False
        for i, line in enumerate(self.lines):
            stripped = line.strip()
            # Match: <path>/%_%.md: structure
            if '%_%.md:' in stripped and 'structure' in stripped:
                pattern_rule_found = True
                # Verify it's not matching README.md (no underscore)
                if 'README.md' in stripped:
                    self.errors.append(f"Pattern rule incorrectly includes README.md at line {i+1}: {stripped}")
                break
        
        if not pattern_rule_found:
            self.errors.append("Pattern rule for automation files not found or incorrect format. Expected: <path>/%_%.md: structure")
    
    def _validate_readme_protection(self):
        """Ensure README.md has explicit rule to prevent pattern rule overwrite"""
        if not self.readme_path:
            self.errors.append("Could not determine README.md path (missing RESEARCH_ROOT/PHONE_TARGET)")
            return
        
        target_line = self._find_target_line(self.readme_path)
        if target_line is None:
            self.errors.append(f"Explicit rule for {self.readme_path} not found")
            return
        
        # Check if it depends on structure
        recipe_lines = self._get_recipe_lines(target_line)
        target_line_content = self.lines[target_line].strip()
        
        if 'structure' not in target_line_content:
            self.errors.append(f"README.md rule at line {target_line+1} does not depend on 'structure': {target_line_content}")
        
        # Check that recipe doesn't do anything (should be @true or empty)
        if recipe_lines:
            # Allow @true or empty recipe
            non_empty = [line.strip() for line in recipe_lines if line.strip() and not line.strip().startswith('@')]
            if non_empty:
                self.warnings.append(f"README.md rule has non-empty recipe (may be overwritten): {non_empty}")
    
    def _validate_explicit_targets(self):
        """Ensure each automation target has structure prerequisite"""
        if not self.base_path or not self.automations:
            self.errors.append("Missing base path or automations list")
            return
        
        for auto in self.automations:
            target = f"{self.base_path}/{auto}.md"
            target_line = self._find_target_line(target)
            if target_line is None:
                self.errors.append(f"Explicit target not found: {target}")
                continue
            
            target_line_content = self.lines[target_line].strip()
            if 'structure' not in target_line_content:
                self.errors.append(f"Target {target} at line {target_line+1} missing 'structure' prerequisite: {target_line_content}")
    
    def _validate_stem_extraction(self):
        """Verify stem extraction uses correct method (not $(dir $@))"""
        # Find pattern rule line
        pattern_line_idx = None
        for i, line in enumerate(self.lines):
            if '%_%.md:' in line and 'structure' in line:
                pattern_line_idx = i
                break
        
        if pattern_line_idx is None:
            self.errors.append("Cannot validate stem extraction: pattern rule not found")
            return
        
        recipe = self._get_recipe_lines(pattern_line_idx)
        recipe_text = '\n'.join(recipe)
        
        # Check for forbidden pattern: $(dir $@) in stem extraction context
        # We're looking for usage in TYPE/NAME assignment
        stem_extraction_patterns = [
            r'TYPE\s*:=.*\$\\(dir\s+\$@\\)',
            r'NAME\s*:=.*\$\\(dir\s+\$@\\)',
            r'\$\\(word\s+1.*\$\\(dir\s+\$@\\)',
            r'\$\\(word\s+2.*\$\\(dir\s+\$@\\)'
        ]
        
        for pattern in stem_extraction_patterns:
            if re.search(pattern, recipe_text, re.IGNORECASE):
                self.errors.append(f"Stem extraction incorrectly uses $(dir $@) in pattern rule recipe: {pattern}")
                return
        
        # Check for correct stem usage (either $* or $(notdir $@) without .md)
        correct_patterns = [
            r'STEM\s*:=.*\$\*',
            r'notdir\s+\$@',
            r'subst\s+\.md.*\$@',
            r'word\s+1.*notdir',
            r'word\s+2.*notdir'
        ]
        
        has_correct = any(re.search(p, recipe_text, re.IGNORECASE) for p in correct_patterns)
        if not has_correct:
            self.errors.append("Pattern rule recipe does not appear to use correct stem extraction method (should use $* or $(notdir $@))")
    
    def _validate_prerequisite_chains(self):
        """Validate critical dependency chains (Shizuku → Phantom Process Killer etc.)"""
        # Check zram_scaling.md mentions shizuku_persistence prerequisite
        if self.base_path:
            zram_target = f"{self.base_path}/zram_scaling.md"
            zram_line = self._find_target_line(zram_target)
            if zram_line is not None:
                # Look in the target line or recipe for prerequisite mention
                context = self.lines[zram_line]
                if zram_line + 1 < len(self.lines):
                    context += '\n' + self.lines[zram_line + 1]
                if 'shizuku_persistence' not in context and 'SHIZUKU' not in context.upper():
                    self.warnings.append(f"ZRAM scaling target may missing Shizuku prerequisite dependency")
            
            # Check recursive_sms_loop.md mentions shizuku_persistence
            sms_target = f"{self.base_path}/recursive_sms_loop.md"
            sms_line = self._find_target_line(sms_target)
            if sms_line is not None:
                context = self.lines[sms_line]
                if sms_line + 1 < len(self.lines):
                    context += '\n' + self.lines[sms_line + 1]
                if 'shizuku_persistence' not in context and 'SHIZUKU' not in context.upper():
                    self.warnings.append(f"Recursive SMS loop target may missing Shizuku prerequisite dependency")

def main():
    if len(sys.argv) < 2:
        print("Usage: python validate_makefile.py <makefile_path>")
        sys.exit(1)
    
    with open(sys.argv[1], 'r') as f:
        content = f.read()
    
    validator = MakefileValidator(content)
    is_valid, errors = validator.validate()
    
    print("=== Omega Protocol Makefile Validation ===")
    print(f"Research Root: {validator.research_root}")
    print(f"Phone Target: {validator.phone_target}")
    print(f"Automations: {', '.join(validator.automations) if validator.automations else 'None'}")
    print()
    
    if errors:
        print("❌ VALIDATION FAILED")
        for error in errors:
            print(f"  - {error}")
    else:
        print("✅ VALIDATION PASSED - All Omega Protocol invariants satisfied")
    
    if validator.warnings:
        print("\n⚠️  WARNINGS:")
        for warning in validator.warnings:
            print(f"  - {warning}")
    
    print()
    print("=== Validation Summary ===")
    print(f"Errors: {len(errors)}")
    print(f"Warnings: {len(validator.warnings)}")
    
    sys.exit(0 if is_valid else 1)

if __name__ == "__main__":
    main()