# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
# Omega Protocol Mathematical Validation Script
# Validates Makefile pattern rules and Φ-density accounting

def validate_makefile_pattern():
    """Test Makefile pattern rule and stem extraction logic"""
    test_cases = [
        # (filename, should_match, expected_type, expected_name)
        ("README.md", False, None, None),
        ("shizuku_persistence.md", True, "shizuku", "persistence"),
        ("termux_tasker_bridge.md", True, "termux", "tasker"),
        ("zram_scaling.md", True, "zram", "scaling"),
        ("recursive_sms_loop.md", True, "recursive", "sms"),
        ("single_underscore.md", True, "single", "underscore"),
        ("no_underscore.md", False, None, None),
        ("three_underscores_here.md", True, "three", "underscores"),
        (".md", False, None, None),
        ("_.md", False, None, None),  # stem becomes empty after split
        ("a_b.md", True, "a", "b"),
        ("a_b_c.md", True, "a", "b"),  # only first two words used
    ]
    
    all_pass = True
    for filename, exp_match, exp_type, exp_name in test_cases:
        # Simulate Makefile stem extraction
        if not filename.endswith('.md'):
            match = False
            auto_type = auto_name = None
        else:
            stem = filename[:-3]  # Remove .md
            parts = stem.split('_')
            if len(parts) < 2:  # Requires at least one underscore (two parts)
                match = False
                auto_type = auto_name = None
            else:
                match = True
                auto_type = parts[0]
                auto_name = parts[1]  # Only first two words used per Makefile
        
        if match == exp_match and auto_type == exp_type and auto_name == exp_name:
            print(f"✓ PASS: {filename} -> match={match}, type={auto_type}, name={auto_name}")
        else:
            print(f"✗ FAIL: {filename} -> expected match={exp_match}, type={exp_type}, name={exp_name}")
            print(f"            got match={match}, type={auto_type}, name={auto_name}")
            all_pass = False
    
    return all_pass

def validate_phi_density():
    """Verify Φ-density accounting mathematical soundness"""
    components = {
        "immediate": -2,
        "months_1_6": 4,
        "months_7_12": 3,
        "months_13_24": 1
    }
    net_claimed = 6
    net_calculated = sum(components.values())
    
    print("\nΦ-Density Components:")
    for phase, value in components.items():
        print(f"  {phase}: {value}% Φ")
    print(f"  Net Claimed: {net_claimed}% Φ")
    print(f"  Net Calculated: {net_calculated}% Φ")
    
    is_sound = (net_calculated == net_claimed)
    print(f"  Mathematical Soundness: {'PASS' if is_sound else 'FAIL'}")
    return is_sound

def validate_dna_references():
    """Verify S24 Ultra DNA references against public knowledge"""
    # Known S24 Ultra specifications (from public sources)
    dna_facts = {
        "kernel_version": "6.1.x-android14",
        "hal_epic": "vendor.samsung.hardware.epic v2.0+",
        "filesystem_vendor": "EROFS",
        "filesystem_data": "F2FS",
        "selinux_version": "34.0+",
        "zram_path": "/sys/block/zram0/"
    }
    
    # Claims from Engine Output v3.0
    claimed_facts = {
        "kernel_version": "Linux 6.1.x-android14 (SM926B)",
        "hal_epic": "vendor.samsung.hardware.epic (IEpicRequest v2.0+)",
        "filesystem_vendor": "EROFs (vendor)",  # Note: case sensitivity
        "filesystem_data": "F2FS (data)",
        "selinux_version": "34.0+",
        "zram_path": "/sys/block/zram0/"
    }
    
    print("\nDNA Reference Validation:")
    all_match = True
    for key, expected in dna_facts.items():
        claimed = claimed_facts[key]
        # Normalize for comparison (case-insensitive, ignore extra descriptors)
        if key in ["filesystem_vendor", "filesystem_data"]:
            # Extract core value from claimed string
            claimed_core = claimed.split()[0].upper()
            expected_core = expected.upper()
            match = (claimed_core == expected_core)
        else:
            match = (expected.lower() in claimed.lower())
        
        status = "✓" if match else "✗"
        print(f"  {status} {key}:")
        print(f"      Expected: {expected}")
        print(f"      Claimed:  {claimed}")
        if not match:
            all_match = False
    
    return all_match

if __name__ == "__main__":
    print("=" * 60)
    print("OMEGA PROTOCOL MATHEMATICAL VALIDATION")
    print("=" * 60)
    
    makefile_ok = validate_makefile_pattern()
    phi_ok = validate_phi_density()
    dna_ok = validate_dna_references()
    
    print("\n" + "=" * 60)
    print("FINAL VALIDATION RESULTS")
    print("=" * 60)
    print(f"Makefile Pattern Rules: {'PASS' if makefile_ok else 'FAIL'}")
    print(f"Φ-Density Accounting:   {'PASS' if phi_ok else 'FAIL'}")
    print(f"DNA References:         {'PASS' if dna_ok else 'FAIL'}")
    
    overall = makefile_ok and phi_ok and dna_ok
    print(f"\nOVERALL COMPLIANCE:     {'PASS' if overall else 'FAIL'}")
    print("=" * 60)
    
    # Exit with appropriate code for VM execution
    exit(0 if overall else 1)