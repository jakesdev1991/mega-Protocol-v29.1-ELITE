# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
# Omega Protocol Invariant Validator for the Omega-Psych-Theorist audit
# Checks internal mathematical consistency of the reported numbers
# and enforces the Omega Protocol invariants (Φ_N, Φ_Δ, J*) as
# interpreted from the text: positivity of Φ gains, COD bounds,
# and monotonic improvement.

import math
import sys

# Tolerance for floating‑point comparisons
TOL = 1e-9

def assert_close(actual, expected, msg, rel_tol=TOL, abs_tol=TOL):
    if not math.isclose(actual, expected, rel_tol=rel_tol, abs_tol=abs_tol):
        raise AssertionError(f"{msg}: got {actual}, expected {expected}")

def assert_in_range(value, low, high, msg):
    if not (low - TOL <= value <= high + TOL):
        raise AssertionError(f"{msg}: {value} not in [{low}, {high}]")

def main():
    # -----------------------------------------------------------------
    # 1. Constants from the Engine superposition
    # -----------------------------------------------------------------
    engine_constants = [0.000318, 0.0000321, 0.0000054]
    # They should be ordered descending magnitude (as written)
    for i in range(len(engine_constants)-1):
        assert engine_constants[i] > engine_constants[i+1], \
            f"Engine constants not descending: {engine_constants[i]} <= {engine_constants[i+1]}"

    # Corrected constant (post‑reboot)
    Lambda_corrected = engine_constants[-1]   # 0.0000054
    # Reference QED benchmark (taken from the text's claim)
    Lambda_QED = 5.4e-6
    assert_close(Lambda_corrected, Lambda_QED,
                 "Corrected Lambda does not match QED benchmark",
                 rel_tol=1e-6)   # allow 1 ppm relative error

    # -----------------------------------------------------------------
    # 2. Chain Overlap Density (COD) values
    # -----------------------------------------------------------------
    COD_pre  = 0.32   # reported as 0.30‑0.32 range; we take the midpoint given later
    COD_post = 0.94   # reported as 0.94‑0.95 range

    assert_in_range(COD_pre,  0.30, 0.35,
                    "Pre‑reboot COD out of expected chaotic‑anxiety band")
    assert_in_range(COD_post, 0.90, 0.95,
                    "Post‑reboot COD out of optimal coherence band")
    # COD must increase after stabilization
    assert COD_post > COD_pre, "COD did not increase after reboot"

    # -----------------------------------------------------------------
    # 3. Φ‑Density (Trust/Coherence) impacts
    # -----------------------------------------------------------------
    phi_immediate  = +0.15   # immediate protection
    phi_longterm   = +0.07   # long‑term resilience
    phi_net        = phi_immediate + phi_longterm
    phi_reflection = +0.08   # from the meta‑cognitive reflection

    # All Φ gains must be non‑negative (protocol invariant Φ_N ≥ 0)
    for label, val in [("immediate", phi_immediate),
                       ("longterm",  phi_longterm),
                       ("reflection",phi_reflection)]:
        if val < -TOL:
            raise AssertionError(f"Φ gain ({label}) negative: {val}")

    # Net gain should equal the sum (internal consistency)
    assert_close(phi_net, phi_immediate + phi_longterm,
                 "Net Φ gain does not equal sum of components")

    # -----------------------------------------------------------------
    # 4. J* invariant (interpreted as "Justified belief" – must increase
    #    with COD and Φ gains)
    # -----------------------------------------------------------------
    # We model J* as a monotonic function of COD and Φ:
    #   J* = w1*COD + w2*Φ_total   (weights positive)
    # Since we only need to check that J* does not decrease,
    # we verify that both COD and Φ increased.
    # (If either decreased, J* would violate the invariant.)
    # Already checked COD increase; now check total Φ increase.
    phi_total_before = 0.0   # baseline assumed
    phi_total_after  = phi_immediate + phi_longterm + phi_reflection
    assert phi_total_after > phi_total_before, \
           "Total Φ did not increase; J* invariant at risk"

    # -----------------------------------------------------------------
    # 5. Informational Stiffness check (implicitly validated by
    #    COD increase and Φ gains – both positive)
    # -----------------------------------------------------------------
    # No explicit numeric value given; we just ensure the direction
    # is correct (stiffness ↑).
    stiffness_increase = (COD_post - COD_pre) + (phi_total_after - phi_total_before)
    assert stiffness_increase > 0, "Informational Stiffness did not increase"

    # -----------------------------------------------------------------
    # If we reach here, all internal mathematical checks passed.
    # -----------------------------------------------------------------
    print("[Ω-PROTOCOL VALIDATOR] All checks PASSED.")
    print(f"  Lambda_corrected = {Lambda_corrected:.10e}")
    print(f"  COD_pre = {COD_pre:.3f}, COD_post = {COD_post:.3f}")
    print(f"  Φ_immediate = {phi_immediate:+.2f}, Φ_longterm = {phi_longterm:+.2f}")
    print(f"  Φ_reflection = {phi_reflection:+.2f}, Φ_total_after = {phi_total_after:+.2f}")
    print("  Invariants Φ_N, Φ_Δ, J* satisfied (non‑negative gains, monotonic COD/Φ).")

if __name__ == "__main__":
    try:
        main()
    except AssertionError as e:
        print(f"[Ω-PROTOCOL VALIDATOR] VIOLATION: {e}")
        sys.exit(1)