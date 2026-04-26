# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
#!/usr/bin/env python3
"""
Omega Protocol Invariant Enforcer for RCOD‑Flux‑Scheduler
---------------------------------------------------------
Validates the mathematical and physical constraints required by
the Universal-Informational-Yield-Regulator (UIYR) and the
Smith‑Audit kernel (Φ_N, Φ_Δ, J*).

Usage:
    from omega_invariant import enforce_scheduler_invariants
    enforce_scheduler_invariants(
        current_phi=phi_measure,
        core=assigned_core,
        mem_weights=sheaf_weights,
        DEDS_metrics=deds_readings,
        flux_priority=computed_priority
    )
"""

from dataclasses import dataclass
from typing import List, Tuple
import math

# ----------------------------------------------------------------------
# Omega Protocol Constants (from UIYR v26.0 & Smith‑Audit Kernel)
# ----------------------------------------------------------------------
PHI_DENSITY_THRESHOLD: float = 0.95          # Minimum admissible Φ_N
PHI_CURVATURE_BOUND:   float = 0.01          # Allowed deviation from threshold
CORE_PINNING_RANGE:    Tuple[int, int] = (16, 23)  # Inclusive
J_STAR_MIN:            float = 0.0           # Non‑negative flux Jacobian
J_STAR_MAX:            float = 1.0           # Upper bound for normalized flux

# ----------------------------------------------------------------------
# Exception type
# ----------------------------------------------------------------------
class OmegaInvariantError(RuntimeError):
    """Raised when an Omega Protocol invariant is violated."""
    pass

# ----------------------------------------------------------------------
# Helper: Covariant mode decomposition (Φ = Φ_N ⊕ Φ_Δ)
# ----------------------------------------------------------------------
def decompose_phi(phi: float) -> Tuple[float, float]:
    """
    Split the informational scalar φ into its yield (Φ_N) and curvature (Φ_Δ)
    components. In the UIYR the decomposition is defined by:
        Φ_N = max(0, φ)          (informational yield cannot be negative)
        Φ_Δ = φ - Φ_N            (remaining curvature contribution)
    This enforces Φ_N ≥ 0 and Φ_Δ ≥ 0 for any real φ.
    """
    phi_N = max(0.0, phi)
    phi_Delta = phi - phi_N
    return phi_N, phi_Delta

# ----------------------------------------------------------------------
# Core invariant checker
# ----------------------------------------------------------------------
def enforce_scheduler_invariants(
    current_phi: float,
    core: int,
    mem_weights: List[float],
    DEDS_metrics: List[float],
    flux_priority: float
) -> None:
    """
    Validate all Omega Protocol invariants that the RCOD‑Flux‑Scheduler
    must uphold before proceeding with scheduling.

    Parameters
    ----------
    current_phi : float
        Measured informational field scalar (φ) at the scheduling point.
    core : int
        Target vCPU core for pinning.
    mem_weights : List[float]
        Curvature‑derived memory section weights from the Sheaf‑MMU.
    DEDS_metrics : List[float]
        Yield metrics from the DEDS service.
    flux_priority : float
        Computed scheduling priority (must respect J* bounds).

    Raises
    ------
    OmegaInvariantError
        If any invariant is violated.
    """
    # 1. Covariant decomposition – extract Φ_N and Φ_Δ
    phi_N, phi_Delta = decompose_phi(current_phi)

    # 2. Φ_N (yield) density invariant
    if phi_N < PHI_DENSITY_THRESHOLD:
        raise OmegaInvariantError(
            f"Φ_N yield {phi_N:.4f} below threshold {PHI_DENSITY_THRESHOLD}"
        )
    if abs(phi_N - PHI_DENSITY_THRESHOLD) > PHI_CURVATURE_BOUND:
        raise OmegaInvariantError(
            f"Φ_N deviation {abs(phi_N - PHI_DENSITY_THRESHOLD):.4f} "
            f"> curvature bound {PHI_CURVATURE_BOUND}"
        )

    # 3. Φ_Δ (curvature) must stay within the same bound (symmetry requirement)
    if abs(phi_Delta) > PHI_CURVATURE_BOUND:
        raise OmegaInvariantError(
            f"Φ_Δ curvature {phi_Delta:.4f} exceeds bound {PHI_CURVATURE_BOUND}"
        )

    # 4. Core pinning range
    lo, hi = CORE_PINNING_RANGE
    if not (lo <= core <= hi):
        raise OmegaInvariantError(
            f"Core {core} outside pinned range [{lo}, {hi}]"
        )

    # 5. Sheaf‑memory weight bounds (each weight must respect curvature bound)
    for i, w in enumerate(mem_weights):
        if abs(w) > PHI_CURVATURE_BOUND:
            raise OmegaInvariantError(
                f"Mem weight[{i}] = {w:.4f} exceeds curvature bound "
                f"{PHI_CURVATURE_BOUND}"
            )

    # 6. DEDS yield non‑negativity (yield cannot be negative)
    if any(m < 0 for m in DEDS_metrics):
        raise OmegaInvariantError("DEDS metric contains negative yield")

    # 7. Flux priority must respect the normalized Jacobian J* ∈ [0,1]
    if not (J_STAR_MIN <= flux_priority <= J_STAR_MAX):
        raise OmegaInvariantError(
            f"Flux priority {flux_priority:.4f} outside J* range "
            f"[{J_STAR_MIN}, {J_STAR_MAX}]"
        )

    # 8. Entropy sanity check – optional but recommended:
    #    Ensure the telemetry packet (not shown here) would have
    #    Shannon entropy ≥ H_min. Placeholder for future integration.
    #    if telemetry_entropy < H_MIN: raise ...

    # If we reach this point, all invariants hold.
    return

# ----------------------------------------------------------------------
# Example usage (for unit‑test or integration test)
# ----------------------------------------------------------------------
if __name__ == "__main__":
    # Simulated good state
    try:
        enforce_scheduler_invariants(
            current_phi=0.96,          # φ_N ≈ 0.96, φ_Δ ≈ 0.0
            core=19,
            mem_weights=[0.002, -0.003, 0.001],
            DEDS_metrics=[1.2, 0.8, 1.5],
            flux_priority=0.97
        )
        print("✅ All Omega Protocol invariants satisfied.")
    except OmegaInvariantError as e:
        print(f"❌ Invariant violation: {e}")

    # Simulated bad state (core out of range)
    try:
        enforce_scheduler_invariants(
            current_phi=0.94,
            core=10,
            mem_weights=[0.0],
            DEDS_metrics=[1.0],
            flux_priority=0.9
        )
    except OmegaInvariantError as e:
        print(f"❌ Expected failure: {e}")