# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Omega Protocol Invariant Validator for DBHN‑style proposals.
Usage:
    python3 omega_validator.py --phi_h 0.95 --phi_q 0.95 \
                               --xi_h 0.001 --xi_q 0.85 \
                               --contribs 0.8 0.7 0.4 0.0
"""

import argparse
import math
import sys
from typing import List, Tuple

# ----------------------------------------------------------------------
# Helper functions
# ----------------------------------------------------------------------
def phi_h_from_entropy(s_bio: float, s_max: float) -> float:
    """Φ_H = 1 - S_bio / S_max  (clipped to [0,1])"""
    val = 1.0 - s_bio / s_max
    return max(0.0, min(1.0, val))

def phi_q_from_times(delta_t_q: float, delta_t_c: float) -> float:
    """Φ_Q = Δt_quantum / Δt_classical  (requires Δt_q ≥ d/c_bio)"""
    if delta_t_c <= 0:
        raise ValueError("Classical Δt must be > 0")
    val = delta_t_q / delta_t_c
    return max(0.0, min(1.0, val))   # protocol caps at 1

def xi_h_from_entropy(s_bio: float, s_max: float, xi_h_budget: float = 0.003) -> float:
    """Invariant ξ_H ≤ 0.3% of S_max; we return the actual fraction used."""
    return min(xi_h_budget, max(0.0, (s_bio / s_max)))  # simplified proxy

def xi_q_from_latency(delta_t: float, d: float, c_bio: float) -> float:
    """ξ_Q = Δt * c_bio / d ; must be ≤ 0.90"""
    if d <= 0 or c_bio <= 0:
        raise ValueError("Distance and bio‑signal speed must be > 0")
    return delta_t * c_bio / d

def psi_from_phi_h(phi_h: float) -> float:
    """ψ = ln(Φ_H) ; Φ_H must be > 0"""
    if phi_h <= 0:
        raise ValueError("Φ_H must be strictly positive for ψ")
    return math.log(phi_h)

def validate_bounds(phi_h: float, phi_q: float, xi_h: float, xi_q: float,
                    eps: float = 1e-9) -> List[str]:
    errors = []
    if not (0.0 - eps <= phi_h <= 1.0 + eps):
        errors.append(f"Φ_H out of bounds: {phi_h}")
    if not (0.0 - eps <= phi_q <= 1.0 + eps):
        errors.append(f"Φ_Q out of bounds: {phi_q}")
    if not (0.0 - eps <= xi_h <= 0.003 + eps):
        errors.append(f"ξ_H out of bounds: {xi_h}")
    if not (0.0 - eps <= xi_q <= 0.90 + eps):
        errors.append(f"ξ_Q out of bounds: {xi_q}")
    return errors

def validate_phi_density(phi_h: float, phi_q: float, xi_h: float,
                         eps: float = 1e-9) -> Tuple[float, List[str]]:
    """Returns Φ and list of consistency errors."""
    phi = phi_h + phi_q - xi_h
    max_phi = 2.0 - xi_h
    min_phi = 0.0
    errors = []
    if not (min_phi - eps <= phi <= max_phi + eps):
        errors.append(f"Φ density {phi} not in [{min_phi}, {max_phi}]")
    return phi, errors

def validate_additive_claim(claimed: List[float],
                            recomputed_phi: float,
                            eps: float = 1e-6) -> List[str]:
    """Checks that the sum of claimed Φ‑contributions matches recomputed Φ."""
    total = sum(claimed)
    if abs(total - recomputed_phi) > eps:
        return [f"Additive Φ‑claim sum ({total}) ≠ recomputed Φ ({recomputed_phi})"]
    return []

def validate_informational_traceability(contribs: List[float],
                                        phi_h: float,
                                        phi_q: float,
                                        s_bio: float,
                                        s_max: float,
                                        delta_t_q: float,
                                        delta_t_c: float,
                                        eps: float = 1e-6) -> List[str]:
    """
    Very lightweight traceability check:
    - Any contribution that is not explainable by a change in S_bio or Δt
      is flagged as *notional*.
    We approximate the maximum explainable Φ‑shift from entropy and timing:
        ΔΦ_H_max = |ΔS_bio|/S_max
        ΔΦ_Q_max = |ΔΔt|/Δt_c   (with ΔΔt = delta_t_q - delta_t_c)
    If a contribution exceeds both bounds, we deem it untraceable.
    """
    errors = []
    # compute theoretical max shifts (absolute)
    delta_s = s_bio  # assume worst‑case change from zero to measured
    max_phi_h_from_s = delta_s / s_max if s_max > 0 else float('inf')
    delta_t = abs(delta_t_q - delta_t_c)
    max_phi_q_from_t = delta_t / delta_t_c if delta_t_c > 0 else float('inf')
    for i, c in enumerate(contribs):
        if c > max_phi_h_from_s + eps and c > max_phi_q_from_t + eps:
            errors.append(
                f"Contribution #{i+1} = {c:.3f} cannot be traced to "
                f"ΔS_bio (max {max_phi_h_from_s:.3f}) or ΔΔt (max {max_phi_q_from_t:.3f})"
            )
    return errors

# ----------------------------------------------------------------------
# Main CLI
# ----------------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(
        description="Omega Protocol invariant validator for DBHN‑style proposals."
    )
    parser.add_argument("--phi_h", type=float, required=True,
                        help="Homeostatic Φ_H (0‑1)")
    parser.add_argument("--phi_q", type=float, required=True,
                        help="Quantum coordination Φ_Q (0‑1)")
    parser.add_argument("--xi_h", type=float, required=True,
                        help="Entropy governance ξ_H (0‑0.003)")
    parser.add_argument("--xi_q", type=float, required=True,
                        help="Latency invariant ξ_Q (0‑0.90)")
    parser.add_argument("--contribs", nargs="*", type=float, default=[],
                        help="List of claimed Φ‑contributions (e.g. 0.8 0.7 0.4 0.0)")
    parser.add_argument("--s_bio", type=float, default=0.05,
                        help="Measured bio‑entropy S_bio (nats)")
    parser.add_argument("--s_max", type=float, default=0.1,
                        help="Maximum possible bio‑entropy S_max (nats)")
    parser.add_argument("--delta_t_q", type=float, default=0.5e-6,
                        help="Quantum‑timed actuation interval Δt_q (s)")
    parser.add_argument("--delta_t_c", type=float, default=1.0e-6,
                        help="Classical actuation interval Δt_c (s)")
    parser.add_argument("--d", type=float, default=10e-6,
                        help="Characteristic distance d (m)")
    parser.add_argument("--c_bio", type=float, default=1.5e-3,
                        help="Bio‑signal propagation speed c_bio (m/s)")
    args = parser.parse_args()

    # ------------------------------------------------------------------
    # Core validation
    # ------------------------------------------------------------------
    errs = []
    errs.extend(validate_bounds(args.phi_h, args.phi_q, args.xi_h, args.xi_q))

    phi, phi_errs = validate_phi_density(args.phi_h, args.phi_q, args.xi_h)
    errs.extend(phi_errs)

    # ψ invariant (just compute; will raise if Φ_H ≤ 0)
    try:
        psi = psi_from_phi_h(args.phi_h)
    except ValueError as e:
        errs.append(str(e))

    # ξ_Q from latency (check against supplied ξ_Q)
    try:
        xi_q_calc = xi_q_from_latency(args.delta_t_q, args.d, args.c_bio)
        if abs(xi_q_calc - args.xi_q) > 1e-6:
            errs.append(
                f"Supplied ξ_Q ({args.xi_q}) does not match latency‑derived value "
                f"({xi_q_calc:.6f})"
            )
    except ValueError as e:
        errs.append(str(e))

    # Additive Φ‑claim check
    if args.contribs:
        errs.extend(validate_additive_claim(args.contribs, phi))

    # Informational traceability (soft warning)
    if args.contribs:
        errs.extend(
            validate_informational_traceability(
                args.contribs,
                args.phi_h,
                args.phi_q,
                args.s_bio,
                args.s_max,
                args.delta_t_q,
                args.delta_t_c,
            )
        )

    # ------------------------------------------------------------------
    # Outcome
    # ------------------------------------------------------------------
    if errs:
        print("❌ VALIDATION FAILED")
        for e in errs:
            print(f" - {e}")
        sys.exit(1)
    else:
        print("✅ VALIDATION PASSED")
        print(f"Φ_H = {args.phi_h:.6f}")
        print(f"Φ_Q = {args.phi_q:.6f}")
        print(f"ξ_H = {args.xi_h:.6f}")
        print(f"ξ_Q = {args.xi_q:.6f}")
        print(f"ψ   = {psi:.6f}")
        print(f"Φ   = {phi:.6f}  (allowed ∈ [0, {2.0 - args.xi_h:.6f}])")
        if args.contribs:
            print(f"Sum of claimed Φ‑contributions = {sum(args.contribs):.6f}")

if __name__ == "__main__":
    main()