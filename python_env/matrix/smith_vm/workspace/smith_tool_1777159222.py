# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
# Omega Protocol Φ-Density Math Validator
# Validates internal consistency of claimed Φ-density impacts
# Enforces: Σ(claimed impacts) = reported net Φ change
#           All impacts must be numeric (int/float)
#           No double-counting of same time period unless explicitly layered

def validate_phi_impacts(impacts_dict, reported_net, tolerance=0.01):
    """
    impacts_dict: dict of label -> float impact (can be positive or negative)
    reported_net: float claimed net Φ change
    tolerance:   float allowed floating-point difference
    Returns: (is_valid, message, computed_sum)
    """
    # Filter out non-numeric entries (should not happen if data is clean)
    numeric_impacts = {k: v for k, v in impacts_dict.items() if isinstance(v, (int, float))}
    computed_sum = sum(numeric_impacts.values())
    diff = abs(computed_sum - reported_net)
    is_valid = diff <= tolerance
    msg = (
        f"✅ VALID: Σimpacts = {computed_sum:.2f}% matches reported net {reported_net:.2f}% "
        f"(diff={diff:.4f}%)" if is_valid else
        f"❌ INVALID: Σimpacts = {computed_sum:.2f}% ≠ reported net {reported_net:.2f}% "
        f"(diff={diff:.4f}% > tolerance {tolerance})"
    )
    return is_valid, msg, computed_sum

# --- Data extracted from Engine's output ---

# 1. Φ-Density Impact Assessment table (OnePlus 12)
impact_assessment = {
    "Immediate": -1.0,
    "Deployment": 0.0,
    "Months 1–6": 4.0,
    "Months 7–12": 2.0,
    "Trust (13–24mo)": 1.0,
}
reported_net_from_table = 6.0  # Engine stated NET: +6% Φ

# 2. Later "Net Protocol Φ-Gain" breakdown
phi_gain_breakdown = {
    "+2.5% Φ: Pattern recognition solidified": 2.5,
    "+2.0% Φ: Vendor-path correction template established": 2.0,
    "+1.0% Φ: Φ-density accounting remains honest and verifiable": 1.0,
    "+1.0% Φ: Protocol learning accelerated": 1.0,
}
reported_net_from_breakdown = 6.5  # Engine stated Net Protocol Φ-Gain: +6.5%

# 3. For reference, the iPad Pro M4 error pattern (should sum to -18%)
ipad_impacts = {
    "Immediate": -5.0,
    "Deployment": -10.0,
    "Trust": -3.0,
}
reported_ipad_net = -18.0

# Run validations
print("=== Omega Protocol Φ-Density Math Audit ===\n")

# Validate OnePlus 12 impact assessment table
valid1, msg1, sum1 = validate_phi_impacts(impact_assessment, reported_net_from_table)
print(f"[OnePlus 12 Impact Table] {msg1}\n")

# Validate Φ-Gain breakdown
valid2, msg2, sum2 = validate_phi_impacts(phi_gain_breakdown, reported_net_from_breakdown)
print(f"[Φ-Gain Breakdown] {msg2}\n")

# Validate iPad Pro M4 pattern (sanity check)
valid3, msg3, sum3 = validate_phi_impacts(ipad_impacts, reported_ipad_net)
print(f"[iPad Pro M4 Error Pattern] {msg3}\n")

# Cross-check: The two OnePlus 12 nets should be consistent if they describe the same scenario
if valid1 and valid2:
    net_diff = abs(sum1 - sum2)
    if net_diff <= 0.01:
        print("✅ CROSS-CHECK: Both OnePlus 12 net calculations agree (within tolerance).")
    else:
        print(f"⚠️  CROSS-CHECK: OnePlus 12 nets disagree: {sum1:.2f}% vs {sum2:.2f}% (diff={net_diff:.2f}%).")
else:
    print("❌ CROSS-CHECK: One or both OnePlus 12 validations failed; cannot compare.")

print("\n=== Audit Summary ===")
all_valid = valid1 and valid2 and valid3
if all_valid:
    print("✅ All Φ-density calculations are mathematically sound.")
else:
    print("❌ Mathematical inconsistencies detected. See above for details.")
    # Optionally, we could halt or request correction per Omega Protocol
    # For demonstration, we output a directive:
    print("\n🔧 ENFORCEMENT: Submit corrected Φ-density table with consistent sums.")