# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SCCRM‑Ω Invariant Validator
---------------------------
Validates the mathematical soundness of the SCCRM‑Ω integration
against the Omega Protocol invariants (Φ_N, Φ_Δ, J*) and the MPC
constraints.

Run:  python3 sccrm_omega_validator.py
"""

import numpy as np
from dataclasses import dataclass
from typing import Dict, List, Tuple

# ----------------------------------------------------------------------
# Hyper‑parameters (these would be calibrated in practice)
# ----------------------------------------------------------------------
ALPHA = 0.6      # weight for credential criticality
BETA  = 0.4      # weight for dissemination scale
LAMBDA_DECAY = 0.1   # per‑day decay (≈ 0.1 → half‑life ~6.93 days)
KAPPA = 0.5      # clustering amplification factor
ETA_N = 0.3      # Φ_N sensitivity
ETA_D = 0.2      # Φ_Δ sensitivity
TAU_N = 90.0     # days (≈3 months)
TAU_D = 60.0     # days (≈2 months)
PHI_N0 = 0.8     # baseline strategic connectivity
PHI_D0 = 0.2     # baseline information asymmetry
LAMBDA1 = 1.0    # cost weight for Φ_Δ
LAMBDA2 = 1.0    # cost weight for anomaly score

# MPC constraints
MAX_SRS_ECO = 10.0
MIN_PHI_N   = 0.4
MAX_PHI_D   = 0.8

# ----------------------------------------------------------------------
# Data structures
# ----------------------------------------------------------------------
@dataclass
class Leak:
    firm: str
    service: str
    criticality: int   # 1‑5
    dissemination: float  # e.g., log(downloads+1)
    t_leak: float      # days since epoch

# ----------------------------------------------------------------------
# Helper functions
# ----------------------------------------------------------------------
def service_level_srs(service: str, leaks: List[Leak], t: float) -> float:
    """SRS_s(t) = Σ[αC+βD]·exp(-λ(t‑t_leak)) for leaks of a given service."""
    total = 0.0
    for l in leaks:
        if l.service != service:
            continue
        weight = ALPHA * l.criticality + BETA * l.dissemination
        total += weight * np.exp(-LAMBDA_DECAY * (t - l.t_leak))
    return total

def clustering_coefficient(service: str, leaks: List[Leak]) -> float:
    """
    Approximate CC(s) = fraction of firms that share ≥2 services.
    For simplicity we compute:
        CC = ( #firms with degree≥2 ) / ( #firms that use the service )
    """
    firms_using = {l.firm for l in leaks if l.service == service}
    # degree of each firm across all services
    firm_deg: Dict[str, int] = {}
    for l in leaks:
        firm_deg[l.firm] = firm_deg.get(l.firm, 0) + 1
    firms_multi = sum(1 for f in firms_using if firm_deg.get(f, 0) >= 2)
    return firms_multi / max(len(firms_using), 1)

def ecosystem_srs(leaks: List[Leak], t: float) -> float:
    """SRS_eco(t) = (1/|S|) Σ SRS_s(t)·[1+κ·CC(s)]"""
    services = {l.service for l in leaks}
    if not services:
        return 0.0
    total = 0.0
    for s in services:
        srs = service_level_srs(s, leaks, t)
        cc  = clustering_coefficient(s, leaks)
        total += srs * (1.0 + KAPPA * cc)
    return total / len(services)

def phi_n(srs_eco: float, t_delay: float = TAU_N) -> float:
    """Φ_N = Φ_N0 – η_N·tanh(SRS_eco(t‑τ_N))"""
    # shift time by τ_N is already done by caller (pass delayed SRS)
    return PHI_N0 - ETA_N * np.tanh(srs_eco)

def phi_delta(srs_eco: float, t_delay: float = TAU_D) -> float:
    """Φ_Δ = Φ_D0 + η_D·SRS_eco(t‑τ_D)  (with hard clip to [0,1])"""
    raw = PHI_D0 + ETA_D * srs_eco
    return min(max(raw, 0.0), 1.0)   # enforce invariant bounds

def anomaly_score(srs_eco_series: np.ndarray) -> float:
    """
    Simple STL‑like anomaly: residual = value - moving average.
    s_SRS = |residual| / std(residual)
    """
    if len(srs_eco_series) < 3:
        return 0.0
    # moving average (window=3)
    ma = np.convolve(srs_eco_series, np.ones(3)/3, mode='same')
    # pad edges
    ma[0] = srs_eco_series[0]
    ma[-1] = srs_eco_series[-1]
    residual = srs_eco_series - ma
    sigma = np.std(residual)
    if sigma == 0:
        return 0.0
    return np.abs(residual[-1]) / sigma

def cost_integral(phi_n_seq: np.ndarray,
                  phi_d_seq: np.ndarray,
                  srs_anom_seq: np.ndarray,
                  dt: float = 1.0) -> float:
    """Discrete approximation of J = ∫[(1‑Φ_N)²+λ₁Φ_Δ²+λ₂ s_SRS²] dt."""
    integrand = (1.0 - phi_n_seq)**2 + LAMBDA1 * (phi_d_seq**2) + LAMBDA2 * (srs_anom_seq**2)
    return np.trapz(integrand, dx=dt)

# ----------------------------------------------------------------------
# Validation routine
# ----------------------------------------------------------------------
def validate_sccrm_omega(leaks: List[Leak],
                         times: np.ndarray) -> Tuple[bool, List[str]]:
    """
    Returns (is_valid, list_of_violations).
    """
    violations = []

    # Pre‑compute SRS_eco for each time point
    srs_eco_vals = np.array([ecosystem_srs(leaks, t) for t in times])

    # Apply time‑delayed versions for Φ_N and Φ_Δ
    # Simple shift: assume we have enough history; otherwise use earliest value.
    def delayed(arr, lag_days):
        idx = int(np.round(lag_days))  # assuming 1‑day step in `times`
        if idx >= len(arr):
            return arr[-1] * np.ones_like(arr)
        return np.concatenate([arr[:idx]*0, arr[:-idx]])  # zero‑pad early

    srs_eco_N = delayed(srs_eco_vals, TAU_N)
    srs_eco_D = delayed(srs_eco_vals, TAU_D)

    phi_n_vals = phi_n(srs_eco_N)
    phi_d_vals = phi_delta(srs_eco_D)

    # Anomaly score (needs a series)
    anomaly_vals = np.array([anomaly_score(srs_eco_vals[:i+1]) for i in range(len(times))])

    # ---- Invariant checks ----
    # Φ_N ∈ [0,1]
    if np.any(phi_n_vals < 0) or np.any(phi_n_vals > 1):
        violations.append("Φ_N out of bounds [0,1]")
    # Φ_Δ ∈ [0,1] (already clipped, but double‑check)
    if np.any(phi_d_vals < 0) or np.any(phi_d_vals > 1):
        violations.append("Φ_Δ out of bounds [0,1]")
    # Monotonicity: Φ_N should not increase when SRS_eco rises
    # Check discrete derivative sign
    dphi_n = np.diff(phi_n_vals)
    dsrs   = np.diff(srs_eco_vals)
    if np.any((dphi_n > 0) & (dsrs > 0)):
        violations.append("Φ_N not monotonic decreasing with SRS_eco")
    # Φ_Δ should not decrease when SRS_eco rises
    dphi_d = np.diff(phi_d_vals)
    if np.any((dphi_d < 0) & (dsrs > 0)):
        violations.append("Φ_Δ not monotonic increasing with SRS_eco")

    # ---- MPC constraint checks ----
    if np.any(srs_eco_vals > MAX_SRS_ECO):
        violations.append(f"SRS_eco exceeds max {MAX_SRS_ECO}")
    if np.any(phi_n_vals < MIN_PHI_N):
        violations.append(f"Φ_N below minimum {MIN_PHI_N}")
    if np.any(phi_d_vals > MAX_PHI_D):
        violations.append(f"Φ_Δ exceeds maximum {MAX_PHI_D}")

    # ---- Cost functional sanity (should be finite) ----
    J = cost_integral(phi_n_vals, phi_d_vals, anomaly_vals, dt=np.diff(times)[0] if len(times)>1 else 1.0)
    if not np.isfinite(J):
        violations.append("Cost functional J is non‑finite")
    # Optionally, we could enforce J ≤ J_max, but Omega does not prescribe a hard cap.

    return len(violations) == 0, violations

# ----------------------------------------------------------------------
# Example usage with synthetic data
# ----------------------------------------------------------------------
if __name__ == "__main__":
    # Create a small synthetic leak set
    leaks = [
        Leak(firm="Alpha",  service="AWS_RDS", criticality=5, dissemination=2.0, t_leak=0.0),
        Leak(firm="Beta",   service="AWS_RDS", criticality=4, dissemination=1.5, t_leak=10.0),
        Leak(firm="Gamma",  service="GCP_BQ",  criticality=3, dissemination=1.0, t_leak=20.0),
        Leak(firm="Delta",  service="AzureSQL",criticality=5, dissemination=2.5, t_leak=30.0),
        Leak(firm="Epsilon",service="AWS_RDS", criticality=5, dissemination=3.0, t_leak=40.0),
    ]

    times = np.arange(0, 80, 1)   # daily samples for 80 days

    ok, errs = validate_sccrm_omega(leaks, times)
    if ok:
        print("✅ SCCRM‑Ω integration passes all Omega Protocol invariants and MPC constraints.")
    else:
        print("❌ Violations detected:")
        for e in errs:
            print(" -", e)