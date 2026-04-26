# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
# -*- coding: utf-8 -*-
"""
TLSM-Ω (Temporal Leak Synchronization Monitor) – Mathematical Soundness Validator
================================================================================

This script checks that the core equations proposed in the TLSM‑Ω proposal
are mathematically consistent and respect the Omega Protocol invariants:

    • Φ_N (market connectivity)   ∈ [0, 1]   (upper bound 0.85 per design)
    • Φ_Δ (information asymmetry) ∈ [0, 1]   (upper bound 0.7 per design)
    • LSI (Leak Synchronization Index) ≥ 0   (design upper bound 3.0)
    • J* (cost‑to‑go)            ≥ 0       (non‑negative quadratic cost)

The validator:
    1. Accepts a list of leak records (timestamp, firm, scale, confidentiality).
    2. Computes LSI over a rolling window (default 30 days).
    3. Maps LSI → Φ_N, Φ_Δ using the proposed tanh/quadratic forms.
    4. Checks all protocol constraints.
    5. Returns a detailed report and raises AssertionError on any violation.

Usage:
    python tlsmu_validator.py   # runs with synthetic demo data
"""

from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import List, Tuple
import math
import numpy as np

# ----------------------------------------------------------------------
# Omega Protocol invariant limits (as stated in the proposal)
# ----------------------------------------------------------------------
LSI_MAX      = 3.0   # design upper bound for Leak Synchronization Index
PHI_N_MAX    = 0.85  # market connectivity ceiling
PHI_DELTA_MAX = 0.7  # information asymmetry ceiling
ETA_N, ETA_D2, ETA_D3 = 0.3, 0.4, 0.2   # example calibration constants
TAU1, TAU2, TAU3 = 60, 30, 90          # days (≈2,1,3 months)
LSI_CRIT = 2.5                         # empirical critical threshold

# ----------------------------------------------------------------------
# Data structures
# ----------------------------------------------------------------------
@dataclass(frozen=True)
class LeakRecord:
    """A single leaked H100‑cluster document."""
    leak_ts: datetime          # when the document first appeared (UTC)
    firm_id: str               # anonymized firm identifier
    gpu_count: int             # number of H100 GPUs mentioned
    confidentiality: int       # 1 (low) – 3 (high) per markings

    @property
    def scale(self) -> float:
        """Rough FLOPs scale – linear in GPU count (constant omitted)."""
        return float(self.gpu_count)

# ----------------------------------------------------------------------
# Helper functions
# ----------------------------------------------------------------------
def compute_lsi(leaks: List[LeakRecord],
                window_days: int = 30,
                reference_ts: datetime | None = None) -> float:
    """
    Leak Synchronization Index (LSI) for a rolling window.

    LSI(t) = (N_leaks / ΔT) * ( Σ (S_i * C_i) / N_firms )

    where:
        N_leaks   = number of distinct leak records in the window
        ΔT        = window length in days (float)
        S_i       = scale (GPU count) of leak i
        C_i       = confidentiality level (1‑3) of leak i
        N_firms   = number of unique firms represented in the window
    """
    if reference_ts is None:
        reference_ts = datetime.now(timezone.utc)

    window_start = reference_ts - timedelta(days=window_days)
    window_leaks = [lr for lr in leaks if window_start <= lr.leak_ts <= reference_ts]

    if not window_leaks:
        return 0.0

    N_leaks = len(window_leaks)
    delta_T = float(window_days)  # days
    sum_scale_conf = sum(lr.scale * lr.confidentiality for lr in window_leaks)
    N_firms = len({lr.firm_id for lr in window_leaks})

    # Avoid division by zero (should never happen because window_leaks non‑empty)
    lsi = (N_leaks / delta_T) * (sum_scale_conf / N_firms)
    return lsi

def map_lsi_to_phi_n(lsi: float,
                     lsi_crit: float = LSI_CRIT,
                     eta: float = ETA_N,
                     tau_days: int = TAU1,
                     reference_ts: datetime | None = None) -> float:
    """
    Φ_N(tlsm) = Φ_N^0 + η * tanh( LSI(t‑τ) / LSI_crit )
    We assume baseline Φ_N^0 = 0.5 (neutral market connectivity).
    """
    phi_n0 = 0.5
    return phi_n0 + eta * math.tanh(lsi / lsi_crit)

def map_lsi_to_phi_delta(lsi: float,
                         lsi_crit: float = LSI_CRIT,
                         eta2: float = ETA_D2,
                         eta3: float = ETA_D3,
                         tau2_days: int = TAU2,
                         tau3_days: int = TAU3,
                         reference_ts: datetime | None = None) -> float:
    """
    Φ_Δ(tlsm) = Φ_Δ^0 + η2 * LSI(t‑τ2) - η3 * LSI(t‑τ3)^2
    Baseline Φ_Δ^0 = 0.3 (moderate asymmetry).
    """
    phi_delta0 = 0.3
    # For simplicity we use the same LSI value for both lags;
    # a production system would query historic LSI at t‑τ.
    return phi_delta0 + eta2 * lsi - eta3 * (lsi ** 2)

def compute_cost(phi_n: float, phi_delta: float, lsi: float,
                 lambda_weight: float = 0.5) -> float:
    """
    Quadratic cost used in the MPC‑Ω QP:
        J = LSI + λ * |Φ_Δ|
    (Φ_N appears only in constraints, not directly in cost per proposal.)
    """
    return lsi + lambda_weight * abs(phi_delta)

# ----------------------------------------------------------------------
# Validation routine
# ----------------------------------------------------------------------
def validate_tlsmu(leaks: List[LeakRecord],
                   window_days: int = 30,
                   lambda_weight: float = 0.5) -> Tuple[bool, dict]:
    """
    Runs the full TLSM‑Ω mathematical check.
    Returns (is_valid, report_dict). Raises AssertionError on invariant breach.
    """
    ref_ts = datetime.now(timezone.utc)
    lsi = compute_lsi(leaks, window_days=window_days, reference_ts=ref_ts)

    # Map to Omega variables (using the same reference time for simplicity)
    phi_n = map_lsi_to_phi_n(lsi, reference_ts=ref_ts)
    phi_delta = map_lsi_to_phi_delta(lsi, reference_ts=ref_ts)

    # Cost (not required to be bounded, but must be non‑negative)
    j_star = compute_cost(phi_n, phi_delta, lsi, lambda_weight=lambda_weight)

    # ------------------------------------------------------------------
    # Invariant checks
    # ------------------------------------------------------------------
    report = {
        "reference_time_utc": ref_ts.isoformat(),
        "LSI": lsi,
        "Φ_N": phi_n,
        "Φ_Δ": phi_delta,
        "J*": j_star,
        "LSI ≤ LSI_MAX?": lsi <= LSI_MAX,
        "Φ_N ≤ Φ_N_MAX?": phi_n <= PHI_N_MAX,
        "Φ_Δ ≤ Φ_Δ_MAX?": phi_delta <= PHI_DELTA_MAX,
        "J* ≥ 0?": j_star >= 0.0,
        "LSI ≥ 0?": lsi >= 0.0,
        "Φ_N ∈ [0,1]?": 0.0 <= phi_n <= 1.0,
        "Φ_Δ ∈ [0,1]?": 0.0 <= phi_delta <= 1.0,
    }

    # All boolean checks must be True
    all_ok = all(v for k, v in report.items() if isinstance(v, bool))
    if not all_ok:
        # Build a readable error message
        failed = [k for k, v in report.items() if isinstance(v, bool) and not v]
        raise AssertionError(f"Omega Protocol invariant violation: {failed}")

    return True, report

# ----------------------------------------------------------------------
# Demo / synthetic data generator
# ----------------------------------------------------------------------
def _demo_leaks() -> List[LeakRecord]:
    """Create a small synthetic leak set that should satisfy the invariants."""
    base = datetime.now(timezone.utc)
    leaks = [
        LeakRecord(leak_ts=base - timedelta(days=5),  firm_id="F_A", gpu_count=64, confidentiality=3),
        LeakRecord(leak_ts=base - timedelta(days=12), firm_id="F_B", gpu_count=48, confidentiality=2),
        LeakRecord(leak_ts=base - timedelta(days=20), firm_id="F_C", gpu_count=80, confidentiality=3),
        LeakRecord(leak_ts=base - timedelta(days=28), firm_id="F_D", gpu_count=56, confidentiality=2),
        LeakRecord(leak_ts=base - timedelta(days=35), firm_id="F_E", gpu_count=72, confidentiality=3),  # outside 30‑day window
    ]
    return leaks

# ----------------------------------------------------------------------
# Main execution
# ----------------------------------------------------------------------
if __name__ == "__main__":
    synthetic_leaks = _demo_leaks()
    try:
        valid, rep = validate_tlsmu(synthetic_leaks, window_days=30, lambda_weight=0.5)
        print("✅ TLSM‑Ω mathematical validation PASSED")
        for k, v in rep.items():
            print(f"{k:30}: {v}")
    except AssertionError as e:
        print("❌ TLSM‑Ω mathematical validation FAILED")
        print(e)
        # Optionally print the report for debugging
        if 'rep' in locals():
            for k, v in rep.items():
                print(f"{k:30}: {v}")