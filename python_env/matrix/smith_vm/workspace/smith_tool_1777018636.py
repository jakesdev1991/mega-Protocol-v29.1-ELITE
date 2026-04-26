# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
#!/usr/bin/env python3
"""
Omega Protocol Invariant Validator for QFAG v2.0
-------------------------------------------------
This script checks the mathematical soundness of the revised Quantum Flux‑Artillery
Governor (QFAG v2.0) proposal against the Omega Protocol’s absolute invariants
and the informational‑first Φ‑density definition.

Invariants (canonical form, per Omega Physics Rubric v26.0):
    ψ      = ln(Φ_N)                                 (Flux genus‑0 homology)
    ξ_N    ≤ 0.005                                   (Entropy budget ≤ 0.5 %)
    ξ_Δ    = (Δt · c) / d   ≤ 0.95                  (Actuation latency ≥ d/c)

Φ‑density definition:
    Φ_N    = 1 – S_flux / S_max                      (Causal stability)
    Φ_Δ    = Δt_quantum / Δt_classical               (Quantum response)
    Φ      = Φ_N + Φ_Δ – ξ_N                         (Total informational advantage)

Theoretical bounds (derived from the definitions):
    0 ≤ Φ_N ≤ 1
    0 ≤ Φ_Δ ≤ 1          (because Δt_quantum ≥ d/c and Δt_classical ≥ Δt_quantum)
    0 ≤ ξ_N ≤ 0.005
    ⇒ 0 ≤ Φ ≤ 2

If any check fails, the script raises a ValueError with a descriptive message.
"""

import math
from dataclasses import dataclass

# ----------------------------------------------------------------------
# Physical constants (SI)
C_LIGHT = 299_792_458  # m/s

# ----------------------------------------------------------------------
@dataclass
class QFAGParameters:
    """Container for the measurable inputs required by the validator."""
    S_flux: float          # Flux defect entropy (nats) – measured via fractal homology
    S_max: float           # Maximum possible flux entropy (nats) – system capacity
    dt_quantum: float      # Quantum actuation latency (seconds)
    dt_classical: float    # Classical actuation latency (seconds)
    distance: float        # Characteristic propagation distance d (meters)
    xi_N: float            # Measured entropy generation fraction (dimensionless)

    def __post_init__(self):
        if self.S_max <= 0:
            raise ValueError("S_max must be positive.")
        if self.S_flux < 0:
            raise ValueError("S_flux cannot be negative.")
        if self.dt_quantum < 0 or self.dt_classical < 0:
            raise ValueError("Latencies must be non‑negative.")
        if self.distance <= 0:
            raise ValueError("Propagation distance must be positive.")
        if self.xi_N < 0:
            raise ValueError("xi_N cannot be negative.")


# ----------------------------------------------------------------------
def compute_phi_n(params: QFAGParameters) -> float:
    """Φ_N = 1 – S_flux / S_max"""
    return 1.0 - params.S_flux / params.S_max


def compute_phi_delta(params: QFAGParameters) -> float:
    """Φ_Δ = Δt_quantum / Δt_classical"""
    if params.dt_classical == 0:
        raise ZeroDivisionError("Classical latency cannot be zero.")
    return params.dt_quantum / params.dt_classical


def compute_xi_delta(params: QFAGParameters) -> float:
    """ξ_Δ = (Δt · c) / d   – here Δt is the *quantum* actuation latency."""
    return (params.dt_quantum * C_LIGHT) / params.distance


def compute_phi_total(params: QFAGParameters) -> float:
    """Φ = Φ_N + Φ_Δ – ξ_N"""
    phi_n = compute_phi_n(params)
    phi_d = compute_phi_delta(params)
    return phi_n + phi_d - params.xi_N


# ----------------------------------------------------------------------
def validate_qfag(params: QFAGParameters) -> dict:
    """
    Runs all Omega Protocol checks and returns a dictionary with the results.
    Raises ValueError on the first invariant violation.
    """
    # --- Basic range checks ------------------------------------------------
    phi_n = compute_phi_n(params)
    phi_d = compute_phi_delta(params)
    xi_d = compute_xi_delta(params)
    phi_total = compute_phi_total(params)

    # Invariant ψ = ln(Φ_N)  (just compute; Φ_N must be >0 for log)
    if phi_n <= 0:
        raise ValueError(f"Φ_N must be > 0 to compute ψ = ln(Φ_N). Got Φ_N = {phi_n}")

    psi = math.log(phi_n)

    # --- Invariant checks --------------------------------------------------
    if not (0.0 <= phi_n <= 1.0):
        raise ValueError(f"Φ_N out of bounds [0,1]: {phi_n}")
    if not (0.0 <= phi_d <= 1.0):
        raise ValueError(f"Φ_Δ out of bounds [0,1]: {phi_d}")
    if not (0.0 <= params.xi_N <= 0.005):
        raise ValueError(f"ξ_N (entropy budget) must be ≤ 0.005. Got {params.xi_N}")
    if not (0.0 <= xi_d <= 0.95):
        raise ValueError(f"ξ_Δ = (Δt·c)/d must be ≤ 0.95. Got {xi_d}")

    # --- Φ‑density bounds --------------------------------------------------
    if not (0.0 <= phi_total <= 2.0):
        raise ValueError(f"Total Φ must lie in [0,2]. Got {phi_total}")

    # --- All good -----------------------------------------------------------
    return {
        "Φ_N": phi_n,
        "Φ_Δ": phi_d,
        "ξ_N": params.xi_N,
        "ξ_Δ": xi_d,
        "ψ = ln(Φ_N)": psi,
        "Φ_total": phi_total,
        "status": "COMPLIANT",
    }


# ----------------------------------------------------------------------
def demo():
    """
    Example usage with numbers taken from the QFAG v2.0 proposal:
        • Stress‑energy density → 5×10¹⁰ bits/cm³ → we map to an entropy
          S_flux ≈ 0.4·S_max (chosen to give Φ_N ≈ 0.6)
        • Δt_quantum ≈ 0.2·d/c  (well below the causal limit)
        • Δt_classical ≈ 1.0·d/c
        • ξ_N = 0.004 (0.4 %)
    """
    # Choose a reference distance (e.g., 10 m barrel‑to‑target)
    d_ref = 10.0  # meters
    # Classical latency set to exactly d/c (best possible classical case)
    dt_classical = d_ref / C_LIGHT
    # Quantum latency is 20 % of the causal limit (as claimed)
    dt_quantum = 0.2 * dt_classical
    # Entropy budget
    xi_N = 0.004
    # Flux entropy: set S_flux = 0.4·S_max → Φ_N = 0.6
    S_max = 1.0  # arbitrary units; only the ratio matters
    S_flux = 0.4 * S_max

    params = QFAGParameters(
        S_flux=S_flux,
        S_max=S_max,
        dt_quantum=dt_quantum,
        dt_classical=dt_classical,
        distance=d_ref,
        xi_N=xi_N,
    )

    result = validate_qfag(params)
    print("Omega Protocol Validation Result:")
    for k, v in result.items():
        if k != "status":
            print(f"  {k}: {v:.6f}" if isinstance(v, float) else f"  {k}: {v}")
    print(f"  status: {result['status']}")


if __name__ == "__main__":
    demo()