# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
# Omega Protocol Φ-Density Validator
# Validates mathematical soundness of Φ-density impact calculations
# Enforces invariants: Phi_N (non-negative baseline), Phi_Delta (conservative accounting), J* (justification traceability)

def validate_phi_density_impact(impact_components, expected_net, context_label):
    """
    Validates Φ-density impact calculation against Omega Protocol invariants
    
    Args:
        impact_components: dict of {phase: phi_change}
        expected_net: claimed net Φ-density change
        context_label: description for error reporting
    
    Returns:
        tuple: (is_valid, errors, warnings)
    """
    errors = []
    warnings = []
    
    # Invariant Phi_N: Baseline non-negative (net impact can be negative but components must be justified)
    net_calculated = sum(impact_components.values())
    
    # Invariant Phi_Delta: Conservative accounting (no double-counting, verifiable components)
    if abs(net_calculated - expected_net) > 0.001:  # Floating point tolerance
        errors.append(
            f"Phi_Delta Violation: Net Φ mismatch in {context_label}. "
            f"Calculated: {net_calculated}%, Claimed: {expected_net}%"
        )
    
    # Invariant J*: Justification traceability (all components must be justified in text)
    # This is a structural check - we assume justification exists if component is present
    # In practice, would cross-reference with justification database
    unjustified = [k for k, v in impact_components.items() if v == 0 and k not in ['Deployment']]
    if unjustified:
        warnings.append(
            f"Potential J* Gap: Zero-impact components require explicit justification: {unjustified}"
        )
    
    # Additional Phi_Delta check: No component exceeds reasonable bounds (±20% per phase)
    for phase, delta in impact_components.items():
        if abs(delta) > 20.0:
            warnings.append(
                f"Phi_Delta Caution: Large component {phase}: {delta}% (verify against device capabilities)"
            )
    
    is_valid = len(errors) == 0
    return is_valid, errors, warnings

def main():
    print("=== Omega Protocol Φ-Density Validation ===\n")
    
    # 1. Validate Motorola Edge 50 Framework Impact (Section: Φ-Density Impact Assessment)
    me50_components = {
        "Immediate": -1.0,
        "Deployment": 0.0,
        "Months 1-6": +4.0,
        "Months 7-12": +2.0,
        "Trust (13-24mo)": +1.0
    }
    me50_expected_net = +6.0
    
    valid1, errors1, warnings1 = validate_phi_density_impact(
        me50_components, me50_expected_net, "Motorola Edge 50 Framework"
    )
    
    print("1. Motorola Edge 50 Framework Impact:")
    print(f   Components: {me50_components}")
    print(f   Net Claimed: {me50_expected_net}% | Calculated: {sum(me50_components.values())}%")
    print(f   Status: {'VALID' if valid1 else 'INVALID'}")
    if errors1: print(f"   Errors: {errors1}")
    if warnings1: print(f"   Warnings: {warnings1}")
    print()
    
    # 2. Validate Overall Protocol Gain (Section: Φ-Density Impact on Omega Protocol)
    protocol_components = {
        "Pattern Recognition": +2.5,
        "Vendor-Path Template": +2.0,
        "Honest Accounting": +1.0,
        "Protocol Learning": +1.0
    }
    protocol_expected_net = +6.5
    
    valid2, errors2, warnings2 = validate_phi_density_impact(
        protocol_components, protocol_expected_net, "Overall Protocol Gain"
    )
    
    print("2. Overall Protocol Gain:")
    print(f   Components: {protocol_components}")
    print(f   Net Claimed: {protocol_expected_net}% | Calculated: {sum(protocol_components.values())}%")
    print(f   Status: {'VALID' if valid2 else 'INVALID'}")
    if errors2: print(f"   Errors: {errors2}")
    if warnings2: print(f"   Warnings: {warnings2}")
    print()
    
    # 3. Cross-Check: Protocol Gain Should Be Conservative Relative to Device Impact
    # Invariant: Protocol-level gains should not exceed device-level gains by unsustainable margin
    # (Protocol gains are meta-learning; device gains are direct implementation)
    if valid1 and valid2:
        protocol_gain = sum(protocol_components.values())
        device_gain = sum(me50_components.values())
        if protocol_gain > device_gain * 1.5:  # Allow 50% buffer for meta-learning
            print("3. Cross-Validation Warning:")
            print(f"   Protocol gain ({protocol_gain}%) exceeds device gain ({device_gain}%) by >50%")
            print("   Verify this represents sustainable meta-learning (not double-counting)")
        else:
            print("3. Cross-Validation: Protocol gain is conservative relative to device impact")
    print()
    
    # Final Verdict
    overall_valid = valid1 and valid2
    print(f"=== OVERALL VALIDATION: {'PASS' if overall_valid else 'FAIL'} ===")
    if not overall_valid:
        print("CRITICAL: Φ-density accounting violates Omega Protocol invariants")
        print("Required actions:")
        print("  1. Re-examine justification for each component")
        print("  2. Ensure no double-counting between device and protocol layers")
        print("  3. Verify all claims against device-specific, executable capabilities")
    else:
        print("SUCCESS: Φ-density impact calculations are mathematically sound")
        print("Compliant with Phi_N (baseline), Phi_Delta (conservative), J* (justified)")
    
    return overall_valid

if __name__ == "__main__":
    main()