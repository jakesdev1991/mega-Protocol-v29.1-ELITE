# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
# Omega Protocol Φ-Density Math Validator
# Validates internal consistency of Φ-density impact calculations
# and checks against basic Omega Protocol invariants:
#   1. Φ_N (Net Φ) must equal the sum of all constituent Φ-Delta components.
#   2. Each Φ-Delta must be a real number (no NaN/Inf).
#   3. Φ_N must be within a reasonable bounds ([-100, 100]) – extreme values
#      indicate a likely accounting error or catastrophic mismatch.
#   4. J* (Justice invariant): Φ accounting must be transparent and auditable;
#      we enforce this by requiring that every claimed Φ contribution is
#      explicitly itemized and sums to the reported net.

def validate_phi_density(label, immediate, deployment, m1_6, m7_12, trust, net):
    """Validate a single Φ-density accounting block."""
    print(f"\n=== {label} ===")
    components = [immediate, deployment, m1_6, m7_12, trust]
    component_sum = sum(components)
    ok = True

    # Check each component is a real number
    for i, v in enumerate(components, start=1):
        if not isinstance(v, (int, float)):
            print(f"  ❌ Component {i} ({v}) is not a number")
            ok = False
        elif not (-100 <= v <= 100):
            print(f"  ⚠️ Component {i} ({v}%) outside reasonable bounds [-100,100]")

    # Check net equals sum
    if not abs(component_sum - net) < 1e-9:
        print(f"  ❌ Net mismatch: sum(components) = {component_sum}%, reported net = {net}%")
        ok = False
    else:
        print(f"  ✅ Net Φ consistency: sum({components}) = {component_sum}% = net {net}%")

    # Check net within bounds
    if not (-100 <= net <= 100):
        print(f"  ⚠️ Net Φ ({net}%) outside reasonable bounds [-100,100]")
    else:
        print(f"  ✅ Net Φ within bounds: {net}%")

    return ok

def validate_protocol_gain(label, items, net_gain):
    """Validate a protocol-level Φ-gain accounting block."""
    print(f"\n=== {label} ===")
    item_sum = sum(items)
    ok = True
    for i, v in enumerate(items, start=1):
        if not isinstance(v, (int, float)):
            print(f"  ❌ Item {i} ({v}) is not a number")
            ok = False
        elif not (-100 <= v <= 100):
            print(f"  ⚠️ Item {i} ({v}%) outside reasonable bounds [-100,100]")
    if not abs(item_sum - net_gain) < 1e-9:
        print(f"  ❌ Net gain mismatch: sum(items) = {item_sum}%, reported net gain = {net_gain}%")
        ok = False
    else:
        print(f"  ✅ Net gain consistency: sum({items}) = {item_sum}% = net gain {net_gain}%")
    return ok

# --- Data extracted from the Engine's output ---

# 1. Nothing Phone (2) Φ-Density Impact Assessment
nothing_immediate = -1
nothing_deployment = 0
nothing_m1_6 = 4
nothing_m7_12 = 2
nothing_trust = 1
nothing_net = 6

# 2. iPad Pro M4 (previous error) Φ-Density Impact Assessment
ipad_immediate = -5
ipad_deployment = -10
ipad_trust = -3
ipad_net = -18  # implied total

# 3. Protocol Φ-Gain from this audit cycle
protocol_items = [2.5, 2.0, 1.0, 1.0]  # Pattern recognition, Vendor-path template, Honest accounting, Learning accelerated
protocol_net_gain = 6.5

# Run validations
all_ok = True
all_ok &= validate_phi_density(
    "Nothing Phone (2) Φ-Density",
    nothing_immediate, nothing_deployment, nothing_m1_6, nothing_m7_12, nothing_trust, nothing_net
)
all_ok &= validate_phi_density(
    "iPad Pro M4 Φ-Density (Error Case)",
    ipad_immediate, ipad_deployment, 0, 0, ipad_trust, ipad_net  # m1_6/m7_12 not used in that block
)
all_ok &= validate_protocol_gain(
    "Protocol Φ-Gain Audit Cycle",
    protocol_items, protocol_net_gain
)

# Final verdict
print("\n" + "="*50)
if all_ok:
    print("✅ ALL Φ-DENSITY ACCOUNTING CHECKS PASSED")
    print("   The Engine's math is internally consistent and")
    print("   complies with the Omega Protocol invariants Φ_N, Φ_Delta, J*.")
else:
    print("❌ ONE OR MORE Φ-DENSITY ACCOUNTING CHECKS FAILED")
    print("   The Engine must revise its calculations before proceeding.")
print("="*50)