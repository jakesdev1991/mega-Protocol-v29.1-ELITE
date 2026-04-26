# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
# -*- coding: utf-8 -*-
"""
Ω‑Protocol Φ‑density invariant validator.
Checks:
  - Net Φ (Φ_N) must be non‑negative.
  - Each component Φ_Delta must lie in [-10, +10] percent.
  - The sum of component deltas must equal the reported net delta (J* consistency).
"""

def validate_phi_impact(label, components, net, tol=0.01):
    """
    Validate a Φ‑impact accounting block.
    :param label: descriptive name for the block (e.g., "iPad Pro M4 error")
    :param components: list of (name, delta_percent) tuples
    :param net: claimed net delta percent
    :param tol: tolerance for J* consistency check
    :return: None (raises AssertionError on violation)
    """
    # 1. Φ_N >= 0
    assert net >= 0, f"{label}: Net Φ_N = {net}% must be non‑negative."

    # 2. Each component within bounds
    for name, d in components:
        assert -10 <= d <= 10, (
            f"{label}: Component '{name}' delta {d}% outside [-10, +10]%."
        )

    # 3. J* consistency: sum(components) == net (within tolerance)
    comp_sum = sum(d for _, d in components)
    diff = abs(comp_sum - net)
    assert diff <= tol, (
        f"{label}: J* mismatch. Sum of components = {comp_sum}%, "
        f"net claimed = {net}%, diff = {diff}% > tol {tol}%."
    )

    print(f"[✓] {label}: All Ω‑Protocol invariants satisfied.")


if __name__ == "__main__":
    # --- iPad Pro M4 error pattern (from text) ---
    ipad_components = [
        ("Immediate", -5.0),
        ("Deployment", -10.0),
        ("Trust", -3.0),
    ]
    ipad_net = -18.0  # stated total
    validate_phi_impact("iPad Pro M4 error pattern", ipad_components, ipad_net)

    # --- Current Xiaomi 14 Ultra situation ---
    xiaomi_components = [
        ("Immediate", -1.0),
        ("Deployment", 0.0),
        ("Months 1‑6", +4.0),
        ("Months 7‑12", +2.0),
        ("Trust 13‑24mo", +1.0),
    ]
    xiaomi_net = +6.0
    validate_phi_impact("Xiaomi 14 Ultra situation", xiaomi_components, xiaomi_net)

    # --- Meta‑pass Φ‑density gain ---
    metapass_components = [
        ("Pattern recognition", +2.5),
        ("Vendor‑path correction", +2.0),
        ("Φ‑density accounting honest", +1.0),
        ("Protocol learning accelerated", +1.0),
    ]
    metapass_net = +6.5
    validate_phi_impact("Meta‑pass Φ‑density gain", metapass_components, metapass_net)

    print("\nAll Φ‑density blocks validated. Ω‑Protocol invariants hold.")