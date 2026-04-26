# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
#!/usr/bin/env python3
"""
Omega Protocol Invariant Validator
----------------------------------
Checks the three absolute invariants required by the Smith Audit:
    Φ-1 (Causal Fidelity)   : ξ_L = Δt - d/c >= 0
    Φ-2 (Entropic Integrity): ξ_E = S_final - S_initial - 0.015 <= 0
    Φ-3 (Topological Fidelity): ξ_T = |π4(M) - π4(S^4)| == 0

All quantities must be supplied in natural units (c = 1, ħ = 1, k_B = 1).
"""

import math
from dataclasses import dataclass
from typing import Callable


class OmegaInvariantError(RuntimeError):
    """Raised when an Omega Protocol invariant is violated."""
    pass


@dataclass
class InvariantInputs:
    """Container for measurable quantities needed to evaluate invariants."""
    # Causal fidelity
    delta_t: float   # measured access latency (time)
    distance: float  # spatial separation of source and receiver (length)
    # Entropic integrity
    S_initial: float   # initial Shannon/topological entropy (nats)
    S_final: float     # final entropy after a write/read cycle (nats)
    # Topological fidelity
    pi4_M: Callable[[], int]   # function returning the 4th homotopy group of the storage manifold
    pi4_S4: int = 0            # π₄(S⁴) = 0 (known constant)


def validate_invariants(inp: InvariantInputs) -> None:
    """
    Raise OmegaInvariantError if any invariant fails.
    """
    # ---- Φ-1: Causal Fidelity ----
    xi_L = inp.delta_t - inp.distance  # c = 1
    if xi_L < -1e-12:  # allow tiny numerical tolerance
        raise OmegaInvariantError(
            f"Causal fidelity violated: ξ_L = {xi_L:.3e} < 0 "
            f"(Δt = {inp.delta_t}, d = {inp.distance})"
        )

    # ---- Φ-2: Entropic Integrity ----
    xi_E = (inp.S_final - inp.S_initial) - 0.015
    if xi_E > 1e-12:
        raise OmegaInvariantError(
            f"Entropic integrity violated: ξ_E = {xi_E:.3e} > 0 "
            f"(S_final - S_initial = {inp.S_final - inp.S_initial:.3e})"
        )

    # ---- Φ-3: Topological Fidelity ----
    try:
        pi4_M_val = inp.pi4_M()
    except Exception as exc:
        raise OmegaInvariantError(
            f"Unable to compute π₄(M): {exc}"
        ) from exc

    xi_T = abs(pi4_M_val - inp.pi4_S4)
    if xi_T > 1e-12:
        raise OmegaInvariantError(
            f"Topological fidelity violated: ξ_T = {xi_T:.3e} ≠ 0 "
            f"(π₄(M) = {pi4_M_val}, π₄(S⁴) = {inp.pi4_S4})"
        )


# ----------------------------------------------------------------------
# Example usage (mock data that would PASS)
# ----------------------------------------------------------------------
if __name__ == "__main__":
    # Mock a compliant lattice: latency just at light-speed, entropy increase 1%,
    # and a manifold with π₄(M) = 0 (same as S⁴).
    mock = InvariantInputs(
        delta_t=5.0,      # t = 5 (c=1)
        distance=5.0,     # d = 5  → ξ_L = 0
        S_initial=10.0,
        S_final=10.0095,  # increase 0.0095 < 0.015
        pi4_M=lambda: 0   # π₄(M) = 0
    )

    try:
        validate_invariants(mock)
        print("✅ All Omega Protocol invariants satisfied.")
    except OmegaInvariantError as e:
        print("❌ Invariant violation:", e)

    # ------------------------------------------------------------------
    # Example of a FAIL (causal violation)
    # ------------------------------------------------------------------
    fail_causal = InvariantInputs(
        delta_t=3.0,
        distance=5.0,
        S_initial=10.0,
        S_final=10.005,
        pi4_M=lambda: 0
    )
    try:
        validate_invariants(fail_causal)
    except OmegaInvariantError as e:
        print("Expected causal failure:", e)