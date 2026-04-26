# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
# Omega Protocol Φ-Density Validation Script
# Validates the mathematical soundness of the Φ-density impact assessments
# presented in the analysis. Ensures internal consistency and compliance
# with the Omega Protocol invariants (Φ_N, Φ_Δ, J*).

def validate_impact_table(name, impacts, expected_net, tolerance=0.01):
    """
    Validate a Φ-density impact table.
    :param name: Label for the table (e.g., "iPad Pro M4", "OnePlus 12")
    :param impacts: List of (phase, impact) tuples
    :param expected_net: The claimed net Φ impact
    :param tolerance: Allowed floating-point difference
    :return: True if valid, False otherwise
    """
    total = sum(impact for _, impact in impacts)
    diff = abs(total - expected_net)
    if diff > tolerance:
        print(f"[FAIL] {name}: Sum of impacts = {total:.2f}%, expected net = {expected_net:.2f}% (diff={diff:.2f}%)")
        return False
    else:
        print(f"[PASS] {name}: Sum of impacts = {total:.2f}% matches expected net = {expected_net:.2f}%")
        return True

def main():
    print("=== Omega Protocol Φ-Density Validation ===\n")

    # ---- iPad Pro M4 Impact Table (from text) ----
    ipad_impacts = [
        ("Immediate", -5.0),
        ("Deployment", -10.0),
        ("Trust", -3.0),
    ]
    ipad_net = -18.0  # claimed total
    validate_impact_table("iPad Pro M4", ipad_impacts, ipad_net)

    # ---- OnePlus 12 Impact Table (from text) ----
    oneplus_impacts = [
        ("Immediate", -1.0),
        ("Deployment", 0.0),
        ("Months 1–6", +4.0),
        ("Months 7–12", +2.0),
        ("Trust (13–24mo)", +1.0),
    ]
    oneplus_net = +6.0  # claimed net
    validate_impact_table("OnePlus 12", oneplus_impacts, oneplus_net)

    # ---- Φ-Density Impact on Omega Protocol Section ----
    protocol_impacts = [
        ("Pattern recognition solidified", +2.5),
        ("Vendor-path correction template", +2.0),
        ("Φ-density accounting honest", +1.0),
        ("Protocol learning accelerated", +1.0),
    ]
    protocol_net = +6.5  # claimed net
    validate_impact_table("Ω Protocol Φ-Gain", protocol_impacts, protocol_net)

    # ---- Additional Invariants Checks ----
    # Invariant Φ_N (net Φ) must be a real number; we already checked sums.
    # Invariant Φ_Δ (change) should be consistent with step-wise deltas.
    # We'll verify that each step's impact is additive (already done).
    # Invariant J* (some objective) is not explicitly defined; we assume
    # that the protocol aims to maximize net Φ over time, so we check
    # that the OnePlus 12 net is greater than the iPad Pro M4 net.
    if oneplus_net > ipad_net:
        print(f"\n[PASS] OnePlus 12 net Φ ({oneplus_net}%) > iPad Pro M4 net Φ ({ipad_net}%)")
    else:
        print(f"\n[FAIL] OnePlus 12 net Φ ({oneplus_net}%) not greater than iPad Pro M4 net Φ ({ipad_net}%)")

    print("\n=== Validation Complete ===")

if __name__ == "__main__":
    main()