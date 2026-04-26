# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
#!/usr/bin/env python3
"""
Omega Protocol Invariant Validator for Quantum‑Adaptive Lattice Footwear (QALF)

Usage:
    >>> from omega_validator import validate_qalf_spec
    >>> spec = {
    ...     "phi_density": 0.89,               # claimed instantaneous Φ‑density (dimensionless)
    ...     "phi_gain": 4.8,                   # claimed additive Φ gain (must be zero if phi_density used as density)
    ...     "initial_entropy": 1.0e-3,         # Shannon entropy of lattice defect distribution at t=0 (bits)
    ...     "final_entropy": 1.014e-3,         # Shannon entropy after actuation (bits)
    ...     "actuation_latency_s": 5.0e-9,     # worst‑case latency measured from sensor to actuation (s)
    ...     "max_distance_m": 0.01,            # longest propagation path inside the shoe (m)
    ...     "betti_numbers": [1, 0, 0],        # [b0, b1, b2] from persistent homology of the lattice
    ...     "subplanckian_metric_det_nonzero": True,  # QLS claim: det(g') != 0
    ...     "deds_throughput_hz": 1e6,         # DTN simulation rate (simulations/sec)
    ...     "rcod_gate_spec": "ENT-LOG-12",    # identifier; must be in allowed list
    ... }
    >>> validate_qalf_spec(spec)
    >>> print("Spec passes all Ω‑Protocol checks.")
"""

from dataclasses import dataclass
from typing import List, Dict, Any
import math


class ValidationError(RuntimeError):
    """Raised when a spec violates an Ω‑Protocol absolute rule."""


# ----------------------------------------------------------------------
# Helper functions (pure, side‑effect free – easy to unit‑test)
# ----------------------------------------------------------------------
def check_phi_dimensional_consistency(phi_density: float, phi_gain: float) -> None:
    """
    The Ω‑Protocol treats Φ as a *single* information‑theoretic quantity.
    If a spec reports a "density" value (< 1) it must NOT also report an
    additive gain unless the gain is expressed in the *same* units and
    the total Φ = density + gain is still a dimensionless information metric.
    For simplicity we require that either:
        * phi_gain == 0   (density‑only mode), OR
        * phi_density == 0 (gain‑only mode).
    Mixed usage triggers a violation.
    """
    if not math.isclose(phi_density, 0.0, abs_tol=1e-12) and not math.isclose(phi_gain, 0.0, abs_tol=1e-12):
        raise ValidationError(
            f"Φ‑dimensional inconsistency: phi_density={phi_density} (non‑zero) "
            f"and phi_gain={phi_gain} (non‑zero). Provide Φ in a single representation."
        )


def check_structural_invariant(betti_numbers: List[int]) -> None:
    """
    Φ‑1: lattice must be genus‑0 → Betti₀ = 1 (single connected component),
    Betti₁ = 0 (no 1‑dimensional holes), Betti₂ = 0 (no voids).
    Persistent homology must return these values for *all* filtration steps;
    we only check the final reported Betti numbers.
    """
    expected = [1, 0, 0]
    if betti_numbers != expected:
        raise ValidationError(
            f"Structural invariant Φ‑1 violated: expected Betti numbers {expected}, "
            f"got {betti_numbers}. Lattice must remain genus‑0."
        )


def check_entropic_invariant(initial_entropy: float, final_entropy: float) -> None:
    """
    Φ‑2: total entropy may increase by at most 1.5 % of the initial value.
    Entropy is measured in bits (Shannon entropy of the defect distribution).
    """
    max_allowed = initial_entropy * 1.015
    if final_entropy > max_allowed + 1e-15:  # tiny tolerance for FP error
        raise ValidationError(
            f"Entropic invariant Φ‑2 violated: final entropy {final_entropy:.3e} "
            f"bits > allowed {max_allowed:.3e} bits (1.5 % increase)."
        )


def check_causal_invariant(latency_s: float, max_distance_m: float) -> None:
    """
    Φ‑3: actuation latency must respect relativistic causality:
         Δt ≥ d / c
    where c = 299 792 458 m/s.
    """
    C = 299_792_458.0  # m/s
    min_latency = max_distance_m / C
    if latency_s < min_latency - 1e-15:  # allow tiny numerical slack
        raise ValidationError(
            f"Causal invariant Φ‑3 violated: latency {latency_s:.3e}s "
            f"< light‑travel time {min_latency:.3e}s for distance {max_distance_m}m."
        )


def check_subplanckian_metric_nonzero(det_nonzero: bool) -> None:
    """
    Placeholder for TOE Step 4 verification. The spec must assert that the
    regulator guarantees det(g') ≠ 0. If the claim is false, the invariant
    fails.
    """
    if not det_nonzero:
        raise ValidationError(
            "Physics link to TOE Step 4 failed: sub‑Planckian metric determinant is zero or undefined."
        )


def check_deds_throughput(throughput_hz: float, min_required: float = 1e5) -> None:
    """
    DEDS engine must meet a *minimum* simulated‑steps‑per‑second threshold.
    The exact value is protocol‑dependent; we use a conservative floor.
    """
    if throughput_hz < min_required:
        raise ValidationError(
            f"DEDS throughput {throughput_hz:.2e} Hz below required minimum {min_required:.2e} Hz."
        )


def check_rcod_gate(gate_spec: str, allowed_gates: List[str]) -> None:
    """
    RCOD gate must be one of the protocol‑approved logical primitives.
    """
    if gate_spec not in allowed_gates:
        raise ValidationError(
            f"RCOD gate '{gate_spec}' not in allowed list {allowed_gates}."
        )


# ----------------------------------------------------------------------
# Main validation entry point
# ----------------------------------------------------------------------
@dataclass(frozen=True)
class QALFSpec:
    phi_density: float
    phi_gain: float
    initial_entropy: float
    final_entropy: float
    actuation_latency_s: float
    max_distance_m: float
    betti_numbers: List[int]
    subplanckian_metric_det_nonzero: bool
    deds_throughput_hz: float
    rcod_gate_spec: str


# Protocol‑approved RCOD gates (example list – extend as needed)
_ALLOWED_RCOD_GATES = [
    "ENT-LOG-12",
    "ENT-LOG-07",
    "ENT-LOG-03",
    # add any other gates that have been formally vetted
]


def validate_qalf_spec(spec: Dict[str, Any]) -> None:
    """
    Validate a QALF design spec against the Ω‑Protocol absolute invariants
    and basic consistency rules. Raises ValidationError on the first
    encountered violation.
    """
    # Cast to typed object for readability & immutability
    qspec = QALFSpec(
        phi_density=float(spec["phi_density"]),
        phi_gain=float(spec["phi_gain"]),
        initial_entropy=float(spec["initial_entropy"]),
        final_entropy=float(spec["final_entropy"]),
        actuation_latency_s=float(spec["actuation_latency_s"]),
        max_distance_m=float(spec["max_distance_m"]),
        betti_numbers=list(map(int, spec["betti_numbers"])),
        subplanckian_metric_det_nonzero=bool(spec["subplanckian_metric_det_nonzero"]),
        deds_throughput_hz=float(spec["deds_throughput_hz"]),
        rcod_gate_spec=str(spec["rcod_gate_spec"]),
    )

    # 1. Dimensional consistency of Φ
    check_phi_dimensional_consistency(qspec.phi_density, qspec.phi_gain)

    # 2. Structural invariant (Φ‑1)
    check_structural_invariant(qspec.betti_numbers)

    # 3. Entropic invariant (Φ‑2)
    check_entropic_invariant(qspec.initial_entropy, qspec.final_entropy)

    # 4. Causal invariant (Φ‑3)
    check_causal_invariant(qspec.actuation_latency_s, qspec.max_distance_m)

    # 5. TOE Step 4 link (metric non‑degeneracy)
    check_subplanckian_metric_nonzero(qspec.subplanckian_metric_det_nonzero)

    # 6. DEDS throughput sanity check
    check_deds_throughput(qspec.deds_throughput_hz)

    # 7. RCOD gate validity
    check_rcod_gate(qspec.rcod_gate_spec, _ALLOWED_RCOD_GATES)

    # If we reach here, all checks passed
    return


# ----------------------------------------------------------------------
# Example usage (can be removed or placed under __main__ guard)
# ----------------------------------------------------------------------
if __name__ == "__main__":
    # Example spec that *should* pass (feel free to edit)
    example_spec = {
        "phi_density": 0.89,
        "phi_gain": 0.0,                     # gain set to zero → density‑only usage
        "initial_entropy": 1.0e-3,
        "final_entropy": 1.014e-3,           # exactly +1.4 % → within 1.5 %
        "actuation_latency_s": 5.0e-9,
        "max_distance_m": 0.01,              # 1 cm path inside the sole
        "betti_numbers": [1, 0, 0],
        "subplanckian_metric_det_nonzero": True,
        "deds_throughput_hz": 1.2e6,
        "rcod_gate_spec": "ENT-LOG-12",
    }

    try:
        validate_qalf_spec(example_spec)
        print("✅ Spec passes all Ω‑Protocol checks.")
    except ValidationError as ve:
        print(f"❌ Validation failed: {ve}")