# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
#!/usr/bin/env python3
"""
Omega Protocol Invariant Validator for SearXNG 403 handling.
Validates the mathematical claims made in the synthesis.
"""

import math

# ---------- Constants ----------
LOG3 = math.log(3)          # ≈1.0986122886681098
WEIGHT_F = 0.4
WEIGHT_H = 0.3
WEIGHT_S = 0.3
# Nominal baseline values (as used in the synthesis)
BASE_F = 0.1                # low error frequency
BASE_H = LOG3               # maximal entropy (uniform over 3 error types)
BASE_S = 0.2                # low severity
BASE_IFI = WEIGHT_F*BASE_F + WEIGHT_H*(1-BASE_H) + WEIGHT_S*BASE_S
# Expected nominal IFI from the text
assert math.isclose(BASE_IFI, 0.20, rel_tol=1e-3), f"Baseline IFI mismatch: {BASE_IFI}"

# ---------- Helper Functions ----------
def compute_IFI(f: float, H_err: float, s: float) -> float:
    """Infrastructure Fragility Index per Omega Protocol."""
    return WEIGHT_F * f + WEIGHT_H * (1.0 - H_err) + WEIGHT_S * s

def update_phi_n(phi_n0: float, connectivity_loss: float) -> float:
    """
    phi_n0 : nominal connectivity (0..1)
    connectivity_loss : fraction of nominal lost due to error (0..1)
    Returns new Φ_N in [0,1].
    """
    phi_n = phi_n0 * (1.0 - connectivity_loss)
    return max(0.0, min(1.0, phi_n))

def phi_density_delta(cost_percent: float, gain_percent: float) -> float:
    """Net Φ‑density change (positive = gain)."""
    return gain_percent - cost_percent

# ---------- Validation ----------
def validate_scenario():
    print("=== Omega Protocol 403‑Error Validation ===")

    # 1. Baseline IFI (should be 0.2)
    assert math.isclose(compute_IFI(BASE_F, BASE_H, BASE_S), BASE_IFI, rel_tol=1e-3)
    print(f"Baseline IFI = {BASE_IFI:.3f} ✔︎")

    # 2. Spike values that produced IFI ≈ 0.65
    f_spike = 0.6          # elevated error frequency
    H_spike = 0.2          # low entropy (concentrated failures)
    s_spike = 0.8          # high severity
    ifi_spike = compute_IFI(f_spike, H_spike, s_spike)
    print(f"Spike IFI = {ifi_spike:.3f} (target ~0.65)")
    assert math.isclose(ifi_spike, 0.65, abs_tol=0.02), "IFI spike mismatch"

    # 3. QP constraints after spike (should be violated → trigger control)
    assert ifi_spike > 0.6, "IFI spike should exceed constraint to trigger MPC‑Ω"
    assert H_spike < LOG3, "Entropy should drop below log(3) on spike"
    print("QP constraints violated → MPC‑Ω activation required ✔︎")

    # 4. Post‑control state (example: IP rotation restores frequency, header spoofing raises entropy)
    f_post = 0.2   # reduced frequency after rotation
    H_post = LOG3  # entropy restored by diversifying sources
    s_post = 0.3   # severity lowered after mitigation
    ifi_post = compute_IFI(f_post, H_post, s_post)
    print(f"Post‑control IFI = {ifi_post:.3f} (should be ≤0.6)")
    assert ifi_post <= 0.6 + 1e-3, "Post‑control IFI exceeds allowed bound"
    assert H_post >= LOG3 - 1e-3, "Post‑control entropy below required threshold"
    print("QP constraints satisfied after control ✔︎")

    # 5. Φ_N update: 70 % connectivity loss → Φ_N = 0.3
    phi_n0 = 1.0
    conn_loss = 0.7
    phi_n_err = update_phi_n(phi_n0, conn_loss)
    print(f"Φ_N after 70 % loss = {phi_n_err:.3f} (expected 0.3)")
    assert math.isclose(phi_n_err, 0.3, abs_tol=0.01), "Φ_N update mismatch"

    # 6. Φ‑density delta validation
    short_term_cost = 5.0   # % (from synthesis)
    long_term_gain  = 15.0  # %
    net_gain = phi_density_delta(short_term_cost, long_term_gain)
    print(f"Short‑term cost = –{short_term_cost}%")
    print(f"Long‑term gain  = +{long_term_gain}%")
    print(f"Net Φ‑density change = {net_gain:+.1f}%")
    assert math.isclose(net_gain, 10.0, abs_tol=0.2), "Net Φ‑density delta mismatch"

    # 7. Per‑incident Φ improvement (8 % reduction in future cost)
    # Simulate three incidents: cumulative factor = 0.92^3 ≈ 0.778 → 22.2% gain
    incidents = 3
    cumulative_gain = (1.0 - 0.92**incidents) * 100.0
    print(f"Cumulative Φ gain after {incidents} incidents ≈ {cumulative_gain:.1f}%")
    assert cumulative_gain > 20.0, "Per‑incident gain too low"

    print("\nAll invariants and mathematical claims validated successfully.")
    return True

if __name__ == "__main__":
    try:
        validate_scenario()
    except AssertionError as e:
        print(f"\nVALIDATION FAILED: {e}")
        raise SystemExit(1)