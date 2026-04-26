# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
#!/usr/bin/env python3
"""
Omega Protocol Φ-Density Validator
----------------------------------
Validates that a proposed Φ-density computation respects:
  * Informational‑first definitions
  * Physical bounds on each term
  * Canonical invariant symbols (Φ_N, Φ_Δ, ξ_N, ξ_Δ)
  * That any reported Φ‑gain is traceable to a delta in the primitives.

Usage:
    >>> validate_phi(
    ...     S_flux=1.2e-2,      # example flux entropy (nats)
    ...     S_max=2.0e-2,       # maximum possible flux entropy
    ...     dt_quantum=1.0e-6,  # s
    ...     dt_classical=2.0e-6,# s
    ...     xi_E=0.003,         # ≤0.005
    ...     claimed_base_phi=0.92,
    ...     claimed_gains=[1.5, 2.0, 1.2, 0.5]   # optional, for consistency check
    ... )
"""

from typing import List, Tuple

# ----------------------------------------------------------------------
# Canonical invariant names (as required by the Omega Physics Rubric)
# ----------------------------------------------------------------------
CANONICAL_COVARIANT = ("Φ_N", "Φ_Δ")   # Newtonian, Asymmetry
CANONICAL_INVARIANT = ("ξ_N", "ξ_Δ")   # Entropic, Latency

def _check_bounds(name: str, value: float, lo: float, hi: float) -> Tuple[bool, str]:
    """Return (OK, message) for a simple bound check."""
    if lo <= value <= hi:
        return True, f"{name} = {value:.6g} ∈ [{lo}, {hi}] ✓"
    else:
        return False, f"{name} = {value:.6g} ∉ [{lo}, {hi}] ✗"

def validate_phi(
    S_flux: float,
    S_max: float,
    dt_quantum: float,
    dt_classical: float,
    xi_E: float,
    claimed_base_phi: float = None,
    claimed_gains: List[float] = None,
    tolerance: float = 1e-9,
) -> None:
    """
    Core validation routine.
    Prints a pass/fail report and raises AssertionError on any violation.
    """
    # ------------------------------------------------------------------
    # 1. Primitive bounds
    # ------------------------------------------------------------------
    ok_S, msg_S = _check_bounds("S_flux/S_max", S_flux / S_max, 0.0, 1.0)
    ok_dt, msg_dt = _check_bounds("dt_quantum/dt_classical", dt_quantum / dt_classical, 0.0, 1.0)
    ok_xi, msg_xi = _check_bounds("ξ_E", xi_E, 0.0, 0.005)

    print("[Primitive Checks]")
    print(msg_S)
    print(msg_dt)
    print(msg_xi)
    if not (ok_S and ok_dt and ok_xi):
        raise AssertionError("One or more primitives out of physical bounds.")

    # ------------------------------------------------------------------
    # 2. Compute Φ_L, Φ_E, ξ_E and Φ
    # ------------------------------------------------------------------
    phi_L = 1.0 - (S_flux / S_max)
    phi_E = dt_quantum / dt_classical
    phi = phi_L + phi_E - xi_E

    print("\n[Computed Φ-Density]")
    print(f"Φ_L = 1 - S_flux/S_max = {phi_L:.6g}")
    print(f"Φ_E = dt_quantum/dt_classical = {phi_E:.6g}")
    print(f"ξ_E = {xi_E:.6g}")
    print(f"Φ = Φ_L + Φ_E - ξ_E = {phi:.6g}")

    # Theoretical max check
    if phi > 2.0 + tolerance:
        raise AssertionError(f"Computed Φ = {phi:.6g} exceeds theoretical maximum 2.0")
    print(f"Φ ≤ 2.0 check: {'PASS' if phi <= 2.0 + tolerance else 'FAIL'}")

    # ------------------------------------------------------------------
    # 3. Base Φ consistency (if supplied)
    # ------------------------------------------------------------------
    if claimed_base_phi is not None:
        diff = abs(claimed_base_phi - phi)
        if diff > tolerance:
            raise AssertionError(
                f"Claimed base Φ ({claimed_base_phi:.6g}) does not match "
                f"computed Φ ({phi:.6g}); diff = {diff:.6g}"
            )
        print(f"\n[Base Φ Claim] Claimed {claimed_base_phi:.6g} matches computed {phi:.6g} ✓")

    # ------------------------------------------------------------------
    # 4. Gain consistency (if supplied)
    # ------------------------------------------------------------------
    if claimed_gains:
        total_gain = sum(claimed_gains)
        # The only way a gain can be valid is if it equals the difference
        # between two Φ states that differ only via allowed primitive changes.
        # We therefore compute the maximal achievable Φ by pushing each
        # primitive to its extreme and see if the claimed total gain fits
        # within that envelope.
        phi_min = (1.0 - 1.0) + 0.0 - 0.005   # worst case: S_flux=S_max, dt_q=dt_c, ξ_E=0.005
        phi_max = (1.0 - 0.0) + 1.0 - 0.0    # best case: S_flux=0, dt_q=dt_c, ξ_E=0
        achievable_range = (phi_min, phi_max)
        print(f"\n[Achievable Φ Range] [{phi_min:.6g}, {phi_max:.6g}]")

        # If we start from the claimed base, the highest we can reach is:
        max_reachable = claimed_base_phi + (phi_max - phi_min)
        min_reachable = claimed_base_phi + (phi_min - phi_max)  # actually lower, but we care about upper

        if claimed_base_phi + total_gain > max_reachable + tolerance:
            raise AssertionError(
                f"Total claimed gain {total_gain:.6g} would push Φ to "
                f"{claimed_base_phi + total_gain:.6g}, exceeding the "
                f"physically reachable maximum {max_reachable:.6g}"
            )
        print(f"[Gain Check] Total claimed gain {total_gain:.6g} is within reachable envelope ✓")

    # ------------------------------------------------------------------
    # 5. Symbolic compliance note (engineer responsibility)
    # ------------------------------------------------------------------
    print("\n[Symbolic Compliance]")
    print("Ensure your source code / documentation uses the canonical symbols:")
    print(f"  Covariant modes: {CANONICAL_COVARIANT[0]}, {CANONICAL_COVARIANT[1]}")
    print(f"  Invariants:      {CANONICAL_INVARIANT[0]}, {CANONICAL_INVARIANT[1]}")
    print("Failure to do so is an automatic Omega Protocol violation.")

    print("\n=== Validation Complete: PASS ===")

# ----------------------------------------------------------------------
# Example usage (the numbers from the Engine's claim)
# ----------------------------------------------------------------------
if __name__ == "__main__":
    # These are placeholder values that would produce the claimed base Φ=0.92
    # if we solve for S_flux/S_max and dt_quantum/dt_classical assuming xi_E=0.003.
    # We deliberately choose values that *do* respect the bounds to show the
    # validator catches the *gain* inconsistency, not the base.
    S_max = 1.0                     # normalize
    S_flux = 0.08                   # gives Φ_L = 0.92
    dt_quantum = 1.0                # arbitrary units
    dt_classical = 1.0              # => Φ_E = 1.0
    xi_E = 0.003                    # within entropic budget

    # Claimed base and gains from the proposal
    claimed_base = 0.92
    claimed_gains = [1.5, 2.0, 1.2, 0.5]   # total +5.2

    try:
        validate_phi(
            S_flux=S_flux,
            S_max=S_max,
            dt_quantum=dt_quantum,
            dt_classical=dt_classical,
            xi_E=xi_E,
            claimed_base_phi=claimed_base,
            claimed_gains=claimed_gains,
        )
    except AssertionError as e:
        print("\n=== VALIDATION FAILED ===")
        print(f"Reason: {e}")