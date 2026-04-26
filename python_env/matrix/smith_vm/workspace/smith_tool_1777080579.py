# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
#!/usr/bin/env python3
"""
Omega Protocol Invariant Validator for QFAG‑style proposals.

This script checks the mathematical soundness of the core Φ‑density
accounting and the three absolute invariants (ψ, ξ_N, ξ_Δ) as defined
in the Omega Physics Rubric.

Usage:
    >>> from omega_validator import validate_qfag
    >>> result = validate_qfag(
    ...     stress_energy_bits_per_cm3=5e10,   # revised compliant value
    ...     S_flux=0.3,                        # flux defect entropy (nats)
    ...     S_max=1.0,                         # maximum possible flux entropy
    ...     delta_t_quantum=2e-6,              # s
    ...     delta_t_classical=5e-6,            # s
    ...     d=10.0,                            # m (characteristic distance)
    ...     c=299792458.0,                     # m/s
    ...     xi_N=0.003                         # entropy governance term
    ... )
    >>> print(result)
"""

import math
from typing import Dict, Any

# ----------------------------------------------------------------------
# Helper functions
# ----------------------------------------------------------------------
def _in_range(val: float, low: float, high: float, name: str) -> Dict[str, Any]:
    """Return a dict describing whether `val` lies in [low, high]."""
    ok = low <= val <= high
    return {
        "name": name,
        "value": val,
        "bounds": (low, high),
        "pass": ok,
        "message": f"{name} = {val:.6g} {'∈' if ok else '∉'} [{low}, {high}]"
    }

def _safe_log(x: float) -> float:
    """Natural log with guard against non‑positive argument."""
    if x <= 0:
        raise ValueError(f"Log argument must be > 0, got {x}")
    return math.log(x)

# ----------------------------------------------------------------------
# Core validation routine
# ----------------------------------------------------------------------
def validate_qfag(
    *,
    stress_energy_bits_per_cm3: float,
    S_flux: float,
    S_max: float,
    delta_t_quantum: float,
    delta_t_classical: float,
    d: float,
    c: float = 299792458.0,
    xi_N: float,
    bek_limit: float = 5e10   # revised Bekenstein‑compliant bound (bits/cm³)
) -> Dict[str, Any]:
    """
    Validate the QFAG design against Omega Protocol invariants.

    Returns a dictionary with detailed pass/fail information for each
    check and an overall ``overall_pass`` flag.
    """
    results = {}

    # ------------------------------------------------------------------
    # 1. Bekenstein‑type stress‑energy sanity check (informational‑first)
    # ------------------------------------------------------------------
    results["bekenstein"] = _in_range(
        stress_energy_bits_per_cm3,
        0.0,
        bek_limit,
        "Stress‑energy density (bits/cm³)"
    )

    # ------------------------------------------------------------------
    # 2. Flux defect entropy → causal stability (Φ_N)
    # ------------------------------------------------------------------
    if S_max <= 0:
        raise ValueError("S_max must be > 0")
    Phi_N = 1.0 - S_flux / S_max
    results["Phi_N"] = _in_range(
        Phi_N,
        0.0,
        1.0,
        "Causal stability Φ_N = 1 - S_flux/S_max"
    )
    # ψ invariant (only defined if Φ_N > 0)
    try:
        psi = _safe_log(Phi_N)
        results["psi"] = {
            "name": "ψ = ln(Φ_N)",
            "value": psi,
            "pass": True,   # ψ is a derived quantity; no explicit bound
            "message": f"ψ = ln({Phi_N:.6g}) = {psi:.6g}"
        }
    except ValueError as e:
        results["psi"] = {
            "name": "ψ = ln(Φ_N)",
            "value": None,
            "pass": False,
            "message": str(e)
        }

    # ------------------------------------------------------------------
    # 3. Quantum response → Φ_Δ
    # ------------------------------------------------------------------
    if delta_t_classical <= 0:
        raise ValueError("Classical latency must be > 0")
    Phi_Delta = delta_t_quantum / delta_t_classical
    # By definition quantum latency cannot be *smaller* than the light‑travel
    # time, but we only enforce the rubric‑implied bound Φ_Δ ≤ 1.
    results["Phi_Delta"] = _in_range(
        Phi_Delta,
        0.0,
        1.0,
        "Quantum response Φ_Δ = Δt_quantum/Δt_classical"
    )

    # ------------------------------------------------------------------
    # 4. Entropy governance term ξ_N
    # ------------------------------------------------------------------
    results["xi_N"] = _in_range(
        xi_N,
        0.0,
        0.005,          # 0.5 %
        "Entropy governance ξ_N"
    )

    # ------------------------------------------------------------------
    # 5. Overall Φ‑density (must stay within theoretical bounds)
    # ------------------------------------------------------------------
    Phi = Phi_N + Phi_Delta - xi_N
    results["Phi_density"] = _in_range(
        Phi,
        0.0,
        2.0,            # theoretical maximum from Φ_N,Φ_Δ∈[0,1], ξ_N≥0
        "Overall Φ‑density = Φ_N + Φ_Δ - ξ_N"
    )

    # ------------------------------------------------------------------
    # 6. Actuation latency invariant ξ_Δ = Δt ⋅ c / d ≤ 0.95
    # ------------------------------------------------------------------
    xi_Delta = delta_t_quantum * c / d
    results["xi_Delta"] = _in_range(
        xi_Delta,
        0.0,
        0.95,
        "Actuation latency invariant ξ_Δ = Δt⋅c/d"
    )

    # ------------------------------------------------------------------
    # 7. Consistency check: ψ must match ln(Φ_N) (already computed)
    # ------------------------------------------------------------------
    if results["psi"]["pass"]:
        # Re‑compute to catch any rounding mismatch
        psi_check = _safe_log(Phi_N)
        psi_ok = math.isclose(psi_check, results["psi"]["value"], rel_tol=1e-12)
        results["psi_consistency"] = {
            "name": "ψ consistency check",
            "value": psi_ok,
            "pass": psi_ok,
            "message": f"Re‑computed ψ = {psi_check:.6g} vs stored {results['psi']['value']:.6g}"
        }
    else:
        results["psi_consistency"] = {
            "name": "ψ consistency check",
            "value": False,
            "pass": False,
            "message": "ψ undefined (Φ_N ≤ 0)"
        }

    # ------------------------------------------------------------------
    # 8. Overall verdict
    # ------------------------------------------------------------------
    all_checks = [
        results["bekenstein"],
        results["Phi_N"],
        results["Phi_Delta"],
        results["xi_N"],
        results["Phi_density"],
        results["xi_Delta"],
        results["psi_consistency"]
    ]
    overall_pass = all(chk["pass"] for chk in all_checks)

    return {
        "checks": results,
        "overall_pass": overall_pass,
        "summary": (
            "PASS – all Omega Protocol invariants satisfied"
            if overall_pass
            else "FAIL – see individual check messages"
        )
    }

# ----------------------------------------------------------------------
# Example usage (when run as a script)
# ----------------------------------------------------------------------
if __name__ == "__main__":
    # Example numbers taken from the revised QFAG v2.0 proposal
    example = validate_qfag(
        stress_energy_bits_per_cm3=5e10,
        S_flux=0.32,
        S_max=1.0,
        delta_t_quantum=2.0e-6,   # 2 µs
        delta_t_classical=5.0e-6, # 5 µs
        d=12.0,                   # 12 m characteristic engagement range
        c=299792458.0,
        xi_N=0.004                # 0.4 % entropy governance
    )
    print("=== Omega Protocol QFAG Validator ===")
    for key, chk in example["checks"].items():
        print(f"{chk['name']:40} : {'PASS' if chk['pass'] else 'FAIL'}  ({chk['message']})")
    print("-" * 60)
    print(example["summary"])