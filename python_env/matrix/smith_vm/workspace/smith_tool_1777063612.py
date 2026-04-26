# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
#!/usr/bin/env python3
"""
Omega Protocol Invariant Validator for Q‑FAN Footwear Submission
----------------------------------------------------------------
Assumes the submission provides a JSON‑serialisable "spec" with the
following minimal fields (all values in SI unless noted):

{
    "max_update_latency_s": float,          # worst‑case Δt for a topological adjustment
    "max_propagation_distance_m": float,    # largest distance over which the update acts
    "initial_entropy_bits": float,          # S_initial (Shannon entropy of lattice defect distribution)
    "final_entropy_bits": float,            # S_final after one adaptation cycle
    "homology_betti_numbers": [int, int, int, int],  # β0, β1, β2, β3 of the mesh
    "covariant_mode_usage": {               # booleans indicating actual use in equations
        "Phi_K_in_QFS": bool,
        "Phi_Sigma_in_QFS": bool,
        "Phi_K_in_DCN": bool,
        "Phi_Sigma_in_DCN": bool,
        "Phi_K_in_KLM": bool,
        "Phi_Sigma_in_KLM": bool
    },
    "toe_step3_derivation": str            # free‑text; we only check for key symbols
}
"""

import json
import sys
import math
from dataclasses import dataclass

# ----------------------------------------------------------------------
# Ω‑Protocol Constants (canonical values)
C = 299_792_458.0                     # m/s, local causal speed
MAX_ENTROPY_INCREASE_FRAC = 0.021     # 2.1 % allowed increase (Φ‑2)
REQUIRED_BETTI_S3 = [1, 0, 0, 1]      # β0=1, β1=0, β2=0, β3=1 for S³
# ----------------------------------------------------------------------


class OmegaProtocolViolation(RuntimeError):
    pass


@dataclass
class Spec:
    max_update_latency_s: float
    max_propagation_distance_m: float
    initial_entropy_bits: float
    final_entropy_bits: float
    homology_betti_numbers: list[int]
    covariant_mode_usage: dict[str, bool]
    toe_step3_derivation: str


def load_spec(path: str) -> Spec:
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return Spec(
        max_update_latency_s=data["max_update_latency_s"],
        max_propagation_distance_m=data["max_propagation_distance_m"],
        initial_entropy_bits=data["initial_entropy_bits"],
        final_entropy_bits=data["final_entropy_bits"],
        homology_betti_numbers=data["homology_betti_numbers"],
        covariant_mode_usage=data["covariant_mode_usage"],
        toe_step3_derivation=data["toe_step3_derivation"],
    )


def check_causal_fidelity(s: Spec) -> None:
    """Φ‑1: Δt ≥ d/c"""
    min_allowed_dt = s.max_propagation_distance_m / C
    if s.max_update_latency_s < min_allowed_dt - 1e-12:  # tiny tolerance for FP
        raise OmegaProtocolViolation(
            f"Φ‑1 violation: latency {s.max_update_latency_s:.3e}s < d/c "
            f"({min_allowed_dt:.3e}s)"
        )


def check_entropy_bound(s: Spec) -> None:
    """Φ‑2: ΔS/S₀ ≤ 0.021"""
    delta_s = s.final_entropy_bits - s.initial_entropy_bits
    frac_increase = delta_s / s.initial_entropy_bits if s.initial_entropy_bits != 0 else float('inf')
    if frac_increase > MAX_ENTROPY_INCREASE_FRAC + 1e-12:
        raise OmegaProtocolViolation(
            f"Φ‑2 violation: entropy increase {frac_increase*100:.3f}% > 2.1% "
            f"(ΔS={delta_s:.3f} bits)"
        )


def check_topological_integrity(s: Spec) -> None:
    """Φ‑3: mesh must be homotopy‑equivalent to S³ → Betti numbers = [1,0,0,1]"""
    if s.homology_betti_numbers != REQUIRED_BETTI_S3:
        raise OmegaProtocolViolation(
            f"Φ‑3 violation: Betti numbers {s.homology_betti_numbers} ≠ {REQUIRED_BETTI_S3}"
        )


def check_covariant_mode_usage(s: Spec) -> None:
    """Rubric: covariant modes must actually appear in the core equations."""
    required = [
        "Phi_K_in_QFS",
        "Phi_Sigma_in_QFS",
        "Phi_K_in_DCN",
        "Phi_Sigma_in_DCN",
        "Phi_K_in_KLM",
        "Phi_Sigma_in_KLM",
    ]
    missing = [k for k in required if not s.covariant_mode_usage.get(k, False)]
    if missing:
        raise OmegaProtocolViolation(
            f"Covariant‑mode usage missing in core equations: {missing}"
        )


def check_toe_step3_derivation(s: Spec) -> None:
    """Rubric: must contain a bona‑fide derivation (we look for key symbols)."""
    txt = s.toe_step3_derivation.lower()
    # Very light‑weight sanity check: presence of crossed‑product notation and a variation symbol
    if ("×" not in txt and "crossed" not in txt) or ("δ" not in txt and "variation" not in txt):
        raise OmegaProtocolViolation(
            "TOE Step 3 derivation lacks recognizable crossed‑product/variation symbols"
        )


def validate(spec_path: str) -> int:
    try:
        spec = load_spec(spec_path)
        check_causal_fidelity(spec)
        check_entropy_bound(spec)
        check_topological_integrity(spec)
        check_covariant_mode_usage(spec)
        check_toe_step3_derivation(spec)
        print("[Ω‑PASS] All invariants satisfied.")
        return 0
    except OmegaProtocolViolation as e:
        print(f"[Ω‑FAIL] {e}")
        return 1
    except Exception as exc:  # malformed JSON, missing fields, etc.
        print(f"[Ω‑ERROR] Invalid spec: {exc}")
        return 2


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python3 omega_validator.py <path-to-spec.json>")
        sys.exit(2)
    sys.exit(validate(sys.argv[1]))