# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
# -*- coding: utf-8 -*-
"""
Omega Protocol Invariant Validator for the Q-Systemic Self‑audit
----------------------------------------------------------------
Checks:
    * COD in [0,1]
    * Target COD > Current COD (stability direction)
    * Φ changes are bounded by a user‑defined Φ_Δ_max
    * Immediate protection does not exceed the magnitude of the
      threatened loss (cannot "over‑compensate" beyond avoidance)
    * Net Φ change relative to the *do‑nothing* baseline is non‑negative
    * J* (derived from COD shift) is positive
"""

def validate_audit(
    cod_current: float,
    cod_target: float,
    phi_loss_risk: float,      # negative number, e.g. -0.30
    phi_immediate: float,      # claimed immediate gain, e.g. +0.12
    phi_longterm: float,       # claimed long‑term gain, e.g. +0.18
    phi_delta_max: float = 0.5 # safety bound on |ΔΦ| per cycle
) -> None:
    """Raise AssertionError if any invariant is violated."""
    # 1. COD bounds
    assert 0.0 <= cod_current <= 1.0, f"COD_current out of range: {cod_current}"
    assert 0.0 <= cod_target <= 1.0, f"COD_target out of range: {cod_target}"

    # 2. Direction of improvement (target should be higher COD)
    assert cod_target > cod_current, (
        f"Target COD ({cod_target}) must exceed current COD ({cod_current}) "
        "for a stabilizing intervention."
    )

    # 3. Φ‑Δ bounds (each reported change must be within the allowed magnitude)
    for name, val in [("phi_immediate", phi_immediate),
                      ("phi_longterm", phi_longterm),
                      ("phi_loss_risk", phi_loss_risk)]:
        assert abs(val) <= phi_delta_max, (
            f"{name} = {val} exceeds permitted Φ_Δ max = {phi_delta_max}"
        )

    # 4. Immediate protection logic:
    #    The immediate gain must NOT be larger than the magnitude of the loss it
    #    purports to avoid (you cannot "gain more" than the loss you prevent).
    #    If you claim to *prevent* a loss L (<0), the immediate gain G must satisfy
    #    0 <= G <= |L|.
    assert phi_loss_risk < 0, "phi_loss_risk should be negative (a loss)."
    assert 0.0 <= phi_immediate <= abs(phi_loss_risk), (
        f"Immediate gain {phi_immediate} must be between 0 and |loss|={abs(phi_loss_risk)}"
    )

    # 5. Net Φ effect relative to the *do‑nothing* baseline:
    #    Baseline ΔΦ = phi_loss_risk (the loss that would happen if we did nothing).
    #    Intervention ΔΦ = phi_immediate + phi_longterm.
    #    We require the intervention to be at least as good as baseline:
    delta_baseline = phi_loss_risk               # negative
    delta_intervention = phi_immediate + phi_longterm
    assert delta_intervention >= delta_baseline, (
        f"Intervention ΔΦ ({delta_intervention}) must not be worse than baseline "
        f"({delta_baseline})."
    )
    #    Additionally, for a *stabilizing* claim we often want net non‑negative
    #    relative to a healthy baseline (Φ_N = 0).  This is optional but
    #    reflects the “preserves Φ density” wording.
    assert delta_intervention >= 0.0, (
        f"Intervention ΔΦ ({delta_intervention}) should be non‑negative "
        "to claim preservation/growth of Φ density."
    )

    # 6. J* positivity (scalar proxy: COD increase factor)
    #    J* = (cod_target - cod_current) / cod_current   (>0 if cod_current>0)
    if cod_current > 0:
        j_star = (cod_target - cod_current) / cod_current
        assert j_star > 0, f"Derived J* = {j_star} must be positive."
    else:
        # If COD_current is zero, any positive target yields infinite J*; we treat as OK.
        assert cod_target > 0, "COD_target must be >0 when COD_current == 0."

    # If we reach here, all invariants hold.
    print("[OK] All Omega Protocol invariants satisfied.")


if __name__ == "__main__":
    # Values extracted from the audit:
    validate_audit(
        cod_current=0.28,
        cod_target=0.90,
        phi_loss_risk=-0.30,   # risk of catastrophic loss
        phi_immediate=0.12,    # claimed immediate gain
        phi_longterm=0.18,     # claimed long‑term gain
        phi_delta_max=0.5      # generous safety bound
    )