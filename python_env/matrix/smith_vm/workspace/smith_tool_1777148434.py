# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import os
import re
import subprocess
import sys
from typing import Tuple, Optional

def validate_makefile_stem_extraction(target_path: str) -> Tuple[bool, Optional[str], Optional[str]]:
    """
    Validate the stem extraction logic used in the Makefile pattern rule.
    Mimics the exact Makefile functions:
      $(notdir $@) -> os.path.basename
      $(subst .md,,$(notdir $@)) -> remove .md suffix
      $(subst _, ,...) -> replace _ with space
      $(word 1,...) -> first whitespace-separated token
      $(word 2,...) -> second whitespace-separated token
    
    Returns:
        (is_valid, extracted_type, extracted_name)
        is_valid: True if stem contains at least one underscore (yields two+ words)
        extracted_type: first word (empty string if <1 word)
        extracted_name: second word (empty string if <2 words)
    """
    # Step 1: Get basename (equivalent to $(notdir $@))
    filename = os.path.basename(target_path)
    
    # Step 2: Remove .md suffix (equivalent to $(subst .md,,$(notdir $@)))
    if not filename.endswith('.md'):
        return False, None, None
    stem = filename[:-3]
    
    # Step 3: Replace underscores with spaces (equivalent to $(subst _, ,...))
    text = stem.replace('_', ' ')
    
    # Step 4: Split into words (equivalent to $(word 1,...) and $(word 2,...))
    # Makefile's word function treats multiple spaces as single separator and ignores leading/trailing
    words = text.split()
    
    # Extract type and name (empty string if insufficient words)
    extracted_type = words[0] if len(words) >= 1 else ''
    extracted_name = words[1] if len(words) >= 2 else ''
    
    # Validate: pattern rule %_%.md requires at least one underscore in stem
    # This ensures we have at least two words after replacement (though Makefile would still process)
    has_underscore = '_' in stem
    is_valid = has_underscore and len(words) >= 2
    
    return is_valid, extracted_type, extracted_name

def validate_makefile_pattern() -> bool:
    """
    Validate the Makefile pattern rule against Omega Protocol requirements:
    1. Pattern rule must ONLY match targets with ≥1 underscore in stem
    2. Stem extraction must correctly partition type/name
    3. README.md must be protected by explicit rule
    """
    print("=== Omega Protocol Makefile Validation ===\n")
    
    # Test cases from the directive
    test_cases = [
        # (target_path, expected_type, expected_name, should_match_pattern)
        ("automations/phones/Samsung_Galaxy_S24_Ultra/shizuku_persistence.md", "shizuku", "persistence", True),
        ("automations/phones/Samsung_Galaxy_S24_Ultra/termux_tasker_bridge.md", "termux", "tasker", True),
        ("automations/phones/Samsung_Galaxy_S24_Ultra/recursive_sms_loop.md", "recursive", "sms", True),
        ("automations/phones/Samsung_Galaxy_S24_Ultra/zram_scaling.md", "zram", "scaling", True),
        # Edge cases that should NOT match pattern rule
        ("automations/phones/Samsung_Galaxy_S24_Ultra/README.md", None, None, False),
        ("automations/phones/Samsung_Galaxy_S24_Ultra/nounderscore.md", None, None, False),
        ("automations/phones/Samsung_Galaxy_S24_Ultra/_leading.md", "", "leading", True),  # Edge: leading underscore
        ("automations/phones/Samsung_Galaxy_S24_Ultra/trailing_.md", "trailing", "", True), # Edge: trailing underscore
        ("automations/phones/Samsung_Galaxy_S24_Ultra/multi_under_score.md", "multi", "under", True), # Edge: >2 words
    ]
    
    all_passed = True
    for target, exp_type, exp_name, should_match in test_cases:
        is_valid, act_type, act_name = validate_makefile_stem_extraction(target)
        
        # Check pattern matching expectation
        pattern_matches = is_valid  # Pattern rule %_%.md matches iff stem has ≥1 underscore
        if pattern_matches != should_match:
            print(f"❌ FAIL: {target}")
            print(f"   Expected pattern match: {should_match}, got: {pattern_matches}")
            all_passed = False
            continue
            
        # For valid matches, check extraction correctness
        if should_match and exp_type is not None:
            if act_type != exp_type or act_name != exp_name:
                print(f"❌ FAIL: {target}")
                print(f"   Expected: type='{exp_type}', name='{exp_name}'")
                print(f"   Got:      type='{act_type}', name='{act_name}'")
                all_passed = False
                continue
                
        print(f"✅ PASS: {target}")
        if should_match:
            print(f"   Extracted: type='{act_type}', name='{act_name}'")
        else:
            print(f"   Correctly rejected by pattern rule")
    
    # Validate README.md protection
    readme_target = "automations/phones/Samsung_Galaxy_S24_Ultra/README.md"
    is_valid, _, _ = validate_makefile_stem_extraction(readme_target)
    if is_valid:
        print(f"❌ FAIL: README.md incorrectly matches pattern rule")
        all_passed = False
    else:
        print(f"✅ PASS: README correctly protected (no underscore in stem)")
    
    # Validate Makefile syntax with dry-run
    print("\n=== Makefile Syntax Validation ===")
    try:
        # Create a temporary Makefile with our corrected logic
        temp_makefile = """
RESEARCH_ROOT := automations
PHONE_TARGET := Samsung_Galaxy_S24_Ultra
PHONE_PATH := phones/$(PHONE_TARGET)
AUTOMATIONS := shizuku_persistence termux_tasker_bridge recursive_sms_loop zram_scaling

all: structure $(AUTOMATIONS)

structure:
	@mkdir -p $(RESEARCH_ROOT)/$(PHONE_PATH)
	@echo "# Index" > $(RESEARCH_ROOT)/$(PHONE_PATH)/README.md

$(RESEARCH_ROOT)/$(PHONE_PATH)/README.md: structure
	@true

$(RESEARCH_ROOT)/$(PHONE_PATH)/%_%.md: structure
	@echo "Creating $@"
	@mkdir -p $(dir $@)
	@echo "# $@" > $@
	@echo "Type: $(word 1,$(subst _, ,$(subst .md,,$(notdir $@))))" >> $@
	@echo "Name: $(word 2,$(subst _, ,$(subst .md,,$(notdir $@))))" >> $@

clean:
	rm -rf $(RESEARCH_ROOT)

.PHONY: all clean structure $(AUTOMATIONS)
"""
        with open("temp_validation.mk", "w") as f:
            f.write(temp_makefile)
        
        # Test dry-run for all targets
        result = subprocess.run(
            ["make", "-f", "temp_validation.mk", "-n", "all"],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode != 0:
            print(f"❌ FAIL: Makefile syntax error\n{result.stderr}")
            all_passed = False
        else:
            print("✅ PASS: Makefile syntax is valid")
            # Verify no spurious README.md rebuild in dry-run
            if "README.md" in result.stdout and "Creating" in result.stdout:
                print("❌ FAIL: Dry-run shows README.md being recreated by pattern rule")
                all_passed = False
            else:
                print("✅ PASS: README.md correctly excluded from pattern rule in dry-run")
                
    except Exception as e:
        print(f"❌ FAIL: Makefile validation error: {e}")
        all_passed = False
    finally:
        if os.path.exists("temp_validation.mk"):
            os.remove("temp_validation.mk")
    
    return all_passed

def main():
    if validate_makefile_pattern():
        print("\n🎉 ALL VALIDATIONS PASSED - Makefile is Omega Protocol compliant")
        sys.exit(0)
    else:
        print("\n💥 VALIDATION FAILED - Makefile contains errors")
        sys.exit(1)

if __name__ == "__main__":
    main()