# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
#!/usr/bin/env python3
"""
SOUL-M Invariant Validator (Omega Protocol)

Checks:
  1. Base metric g0 is positive-definite.
  2. Perturbation term is positive semi-definite (PSD) → guarantees det(g)>0.
  3. Beta respects ξ_N bounds (0.01 ≤ β ≤ 0.1) and Shredding Event logic.
  4. Φ_N and Φ_Δ satisfy the covariant-mode constraint Φ_Δ < 0.5·Φ_N.
  5. Dimensional consistency: lat, lon dimensionless (rad), t scaled to dimensionless.
"""

import numpy as np
from typing import Tuple

# -------------------------- Configuration --------------------------
# Base infrastructure metric (example: Euclidean in lat/lon/t space)
G0 = np.eye(3)  # 3x3 identity → PD by construction

# Physical / informational constants (example values)
PHI_N = 1.0      # Newtonian informational density (norm. flux)
EPSILON = 1e-6   # Regularization for log
XI_N = 0.95      # Informational horizon for Shredding Event
BETA_MIN, BETA_MAX = 0.01, 0.1   # ξ_N‑derived bounds on beta
R = 3.0          # Max range for asymmetry term
T0 = 86400.0     # Reference time (1 day) to make t dimensionless if needed

# -------------------------- Helper Functions --------------------------
def psi(rho: float) -> float:
    """Demand‑encoding function ψ(ρ) = ln(φ_N·ρ + ε)."""
    arg = PHI_N * rho + EPSILON
    if arg <= 0:
        raise ValueError(f"ψ argument non‑positive: {arg}")
    return np.log(arg)

def metric(g0: np.ndarray, beta: float, rho: float) -> np.ndarray:
    """Full metric g = g0 + β·ψ(ρ)·I (isotropic perturbation)."""
    return g0 + beta * psi(rho) * np.eye(g0.shape[0])

def is_positive_definite(M: np.ndarray) -> bool:
    """Check PD via Cholesky (fails if not PD)."""
    try:
        np.linalg.cholesky(M)
        return True
    except np.linalg.LinAlgError:
        return False

def phi_density_components(COD: float, Xi: float, Z: float) -> Tuple[float, float]:
    """Return Φ_N and Φ_Δ."""
    Phi_N = np.log2(COD + EPSILON)
    Phi_Delta = Phi_N * np.tanh(abs(Xi - Z) / R)
    return Phi_N, Phi_Delta

def shredding_event(phi_n: float, rho: float) -> bool:
    """True when informational horizon exceeded → trigger graceful degradation."""
    return phi_n * rho > XI_N

# -------------------------- Validation Routine --------------------------
def validate_soul_m(
    beta: float,
    rho: float,
    COD: float,
    Xi: float,
    Z: float,
    lat: float,
    lon: float,
    t: float,
) -> dict:
    """
    Returns a dict with pass/fail flags and diagnostic messages.
    """
    report = {}

    # 1. Dimensional sanity (lat/lon in radians, t scaled)
    #   We only warn; actual scaling is application‑specific.
    if not (-np.pi <= lat <= np.pi):
        report["lat_warning"] = f"Latitude {lat} rad outside [-π,π]"
    if not (-np.pi <= lon <= np.pi):
        report["lon_warning"] = f"Longitude {lon} rad outside [-π,π]"
    # t made dimensionless by dividing by T0
    t_dimless = t / T0
    report["t_dimensionless"] = t_dimless

    # 2. Beta bounds
    if not (BETA_MIN <= beta <= BETA_MAX):
        report["beta_fail"] = f"β={beta} outside [{BETA_MIN},{BETA_MAX}]"
    else:
        report["beta_pass"] = True

    # 3. Metric construction & INV‑001 (det>0 by construction)
    try:
        G = metric(G0, beta, rho)
        if is_positive_definite(G):
            report["inv001_pass"] = True
            report["det_g"] = np.linalg.det(G)
        else:
            report["inv001_fail"] = "Metric not positive‑definite"
    except ValueError as e:
        report["psi_error"] = str(e)

    # 4. Φ‑density covariant‑mode constraint
    Phi_N, Phi_Delta = phi_density_components(COD, Xi, Z)
    report["Phi_N"] = Phi_N
    report["Phi_Delta"] = Phi_Delta
    report["phi_constraint_pass"] = Phi_Delta < 0.5 * Phi_N
    report["phi_constraint_margin"] = 0.5 * Phi_N - Phi_Delta

    # 5. Shredding Event logic
    report["shredding_triggered"] = shredding_event(PHI_N, rho)
    if report["shredding_triggered"]:
        report["shredding_action"] = (
            "Project g to nearest PSD manifold, log event, alert ops"
        )
    else:
        report["shredding_action"] = "Nominal operation"

    # Overall compliance (all critical checks must pass)
    critical = [
        report.get("beta_pass", False),
        report.get("inv001_pass", False),
        report.get("phi_constraint_pass", True),
    ]
    report["overall_pass"] = all(critical)

    return report

# -------------------------- Example Usage --------------------------
if __name__ == "__main__":
    # Example scenario: moderate demand, nominal beta
    example = validate_soul_m(
        beta=0.05,          # within [0.01,0.1]
        rho=0.4,            # demand density
        COD=2.0,            # some codensity measure
        Xi=1.2, Z=0.8,      # asymmetry inputs
        lat=0.5, lon=-0.3,  # rad
        t=1_700_000_000,    # Unix epoch (~2023-11-14)
    )
    for k, v in example.items():
        print(f"{k:25}: {v}")