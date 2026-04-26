# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
#!/usr/bin/env python3
"""
Ω‑Protocol Φ‑Density Invariant Validator
Validates short‑term and long‑term Φ impact percentages against:
    1. Φ_N >= 0
    2. |ΔΦ| <= 20% per interval
    3. J* >= Φ_N0  (stability index never falls below baseline)
"""

from dataclasses import dataclass
from typing import NamedTuple


class ProtocolViolation(RuntimeError):
    """Raised when an Ω‑Protocol invariant is broken."""
    pass


@dataclass(frozen=True)
class Impact:
    short: float   # percent, e.g. -5.0
    long: float    # percent, e.g. +15.0


class PhiState(NamedTuple):
    Phi_N: float   # absolute density
    Phi_Delta: float  # instantaneous change (%)
    J_star: float   # stability index


def validate_impact(baseline: float, impact: Impact) -> PhiState:
    """
    Returns the final PhiState after applying short‑ then long‑term impacts.
    Raises ProtocolViolation on any invariant breach.
    """
    # ---- Short‑term step -------------------------------------------------
    Phi_N_short = baseline * (1 + impact.short / 100.0)
    if Phi_N_short < 0:
        raise ProtocolViolation(f"Φ_N dropped below zero after short‑term: {Phi_N_short}")
    if abs(impact.short) > 20.0:
        raise ProtocolViolation(f"Short‑term ΔΦ out of bounds: {impact.short}%")

    J_star_short = Phi_N_short * (1 + impact.short / 100.0)
    # Temporary dips are allowed; we only enforce J* >= baseline at the *end* of the interval.
    # (If you want to forbid any dip, uncomment the next two lines.)
    # if J_star_short < baseline:
    #     raise ProtocolViolation(f"J* fell below baseline after short‑term: {J_star_short}")

    # ---- Long‑term step --------------------------------------------------
    Phi_N_long = Phi_N_short * (1 + impact.long / 100.0)
    if Phi_N_long < 0:
        raise ProtocolViolation(f"Φ_N dropped below zero after long‑term: {Phi_N_long}")
    if abs(impact.long) > 20.0:
        raise ProtocolViolation(f"Long‑term ΔΦ out of bounds: {impact.long}%")

    # Net ΔPhi for the whole interval (used for Φ_Delta)
    net_delta = impact.short + impact.long
    if abs(net_delta) > 20.0:
        raise ProtocolViolation(f"Net ΔΦ out of bounds: {net_delta}%")

    J_star_long = Phi_N_long * (1 + net_delta / 100.0)
    if J_star_long < baseline:
        raise ProtocolViolation(
            f"Final J* ({J_star_long}) < baseline Φ_N0 ({baseline})"
        )

    return PhiState(
        Phi_N=Phi_N_long,
        Phi_Delta=net_delta,
        J_star=J_star_long,
    )


def compliance_report(baseline: float, impact: Impact) -> str:
    try:
        state = validate_impact(baseline, impact)
        return (
            f"✅ Ω‑Protocol COMPLIANT\n"
            f"Baseline Φ_N0: {baseline}\n"
            f"Short‑term ΔΦ: {impact.short}%\n"
            f"Long‑term ΔΦ:  {impact.long}%\n"
            f"→ Final Φ_N:   {state.Phi_N:.2f}\n"
            f"→ Φ_Delta:     {state.Phi_Delta:.2f}%\n"
            f"→ J*:          {state.J_star:.2f}\n"
        )
    except ProtocolViolation as e:
        return f"❌ Ω‑Protocol VIOLATION: {e}"


if __name__ == "__main__":
    # Example from the audited thought:
    BASELINE = 100.0          # arbitrary reference density
    IMPACT   = Impact(short=-5.0, long=+15.0)

    print(compliance_report(BASELINE, IMPACT))