# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
#!/usr/bin/env python3
"""
Omega Protocol Invariant Validator for QALF (Quantum-Adaptive Lattice Footwear)

Checks:
 1. Φ-L = 1 - S_defects / S_max   (0 < Φ-L ≤ 1)
 2. ψ = ln(Φ-L)                  (real-valued)
 3. Φ-E = Δt_quantum / Δt_classical   (0 < Φ-E ≤ 1 for causal speed‑up)
 4. ξ_E = (S_total - S_initial) / S_max   ≤ 0.015
 5. ξ_L = Δt * c / d               ≤ 1.0
 6. Φ = Φ-L + Φ-E - ξ_E            (dimensionless, no explicit bound but
                                    physically sensible to keep Φ ≤ 2)
All inputs must be supplied as floats or ints.
"""

import math
import sys

def validate(
    S_defects: float,
    S_max: float,
    S_initial: float,
    S_total: float,
    Delta_t_q: float,
    Delta_t_c: float,
    d: float,
    c: float = 299_792_458.0,  # speed of light in m/s
    eps: float = 1e-12
) -> bool:
    """Return True if all Omega invariants hold."""
    failures = []

    # ---- Φ-L and ψ (Invariant Φ-1) ----
    if S_max <= 0:
        failures.append("S_max must be > 0")
    else:
        Phi_L = 1.0 - S_defects / S_max
        if not (0.0 < Phi_L <= 1.0 + eps):
            failures.append(f"Φ-L = {Phi_L:.6f} out of range (0,1]")
        else:
            try:
                psi = math.log(Phi_L)
                # psi is real by construction if Phi_L>0
            except ValueError:
                failures.append("ψ = ln(Φ-L) undefined (Φ-L ≤ 0)")

    # ---- Φ-E (used in Φ-density) ----
    if Delta_t_c <= 0:
        failures.append("Δt_classical must be > 0")
    else:
        Phi_E = Delta_t_q / Delta_t_c
        if not (0.0 < Phi_E <= 1.0 + eps):
            failures.append(f"Φ-E = {Phi_E:.6f} out of causal range (0,1]")
        # Note: Φ-E > 1 would imply super‑luminal signalling, disallowed.

    # ---- Entropy increase (Invariant Φ-2) ----
    if S_max <= 0:
        failures.append("S_max must be > 0 for entropy bound")
    else:
        xi_E = (S_total - S_initial) / S_max
        if xi_E > 0.015 + eps:
            failures.append(f"ξ_E = {xi_E*100:.3f}% > 1.5% bound")

    # ---- Latency bound (Invariant Φ-3) ----
    if d <= 0:
        failures.append("Characteristic distance d must be > 0")
    else:
        xi_L = Delta_t_q * c / d
        if xi_L > 1.0 + eps:
            failures.append(f"ξ_L = {xi_L:.6f} > 1 (violates Δt ≥ d/c)")

    # ---- Φ-density (derived quantity) ----
    if 'Phi_L' in locals() and 'Phi_E' in locals() and 'xi_E' in locals():
        Phi = Phi_L + Phi_E - xi_E
        # No hard bound in the protocol, but we flag absurd values.
        if Phi < 0 or Phi > 3.0:   # generous upper limit
            failures.append(f"Φ-density = {Phi:.6f} outside plausible range [0,3]")

    if failures:
        print("Ω VALIDATION FAILED:")
        for f in failures:
            print(f"  - {f}")
        return False
    else:
        print("Ω VALIDATION PASSED")
        return True


if __name__ == "__main__":
    # Example usage – replace with measured or design values.
    # These are deliberately chosen to be *within* protocol limits.
    S_defects   = 0.10   # bits (defect entropy)
    S_max       = 0.20   # bits
    S_initial   = 0.05   # bits
    S_total     = 0.052  # bits → 4% increase? actually 0.002/0.20 = 1%
    Delta_t_q   = 1e-9   # s (quantum actuation)
    Delta_t_c   = 2e-9   # s (classical baseline)
    d           = 0.02   # m (2 cm characteristic actuation length)
    c           = 299_792_458.0

    ok = validate(
        S_defects=S_defects,
        S_max=S_max,
        S_initial=S_initial,
        S_total=S_total,
        Delta_t_q=Delta_t_q,
        Delta_t_c=Delta_t_c,
        d=d,
        c=c,
    )
    sys.exit(0 if ok else 1)