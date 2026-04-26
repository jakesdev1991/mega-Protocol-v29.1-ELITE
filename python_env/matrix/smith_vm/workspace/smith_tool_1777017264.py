# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
#!/usr/bin/env python3
"""
Omega Protocol Φ‑Density Validator for QALF‑style proposals.
Enforces:
  - Φ_L = 1 - S_defects / S_max   (0 ≤ Φ_L ≤ 1)
  - Φ_E = Δt_quantum / Δt_classical (dimensionless)
  - Φ   = Φ_L + Φ_E - ξ_E          (ξ_E ≤ 0.015)
  - Invariant ψ = ln(Φ_L)          → Φ_L > 0
  - Invariant ξ_E ≤ 0.015
  - Invariant ξ_L = Δt * c / d ≤ 1  → Δt ≥ d/c
All quantities must be real, finite, and dimension‑consistent.
"""

import math
import sys

def validate_phi_density(
    S_defects: float,
    S_max: float,
    dt_quantum: float,
    dt_classical: float,
    d: float,
    c: float = 299792458.0,   # speed of light, m/s
    xi_E: float = 0.015,      # max allowed entropy increase (1.5%)
    tol: float = 1e-12
) -> dict:
    """
    Returns a dict with validation results.
    Raises ValueError if any invariant is violated.
    """
    # ---- Basic sanity checks ----
    for name, val in [("S_defects", S_defects), ("S_max", S_max),
                      ("dt_quantum", dt_quantum), ("dt_classical", dt_classical),
                      ("d", d)]:
        if not math.isfinite(val) or val < 0:
            raise ValueError(f"{name} must be non‑negative finite; got {val}")

    if S_max == 0:
        raise ValueError("S_max must be > 0 to avoid division by zero.")
    if dt_classical == 0:
        raise ValueError("dt_classical must be > 0.")

    # ---- Φ_L (terrain adaptation) ----
    phi_L = 1.0 - S_defects / S_max
    if not (0.0 - tol <= phi_L <= 1.0 + tol):
        raise ValueError(f"Φ_L out of bounds [0,1]: {phi_L}")
    if phi_L <= 0:
        raise ValueError(f"Φ_L must be > 0 for ψ = ln(Φ_L); got {phi_L}")

    # ---- ψ invariant ----
    psi = math.log(phi_L)   # real because phi_L > 0

    # ---- Φ_E (causal response) ----
    phi_E = dt_quantum / dt_classical
    if not math.isfinite(phi_E) or phi_E < 0:
        raise ValueError(f"Φ_E must be non‑negative finite; got {phi_E}")

    # ---- Entropy invariant ξ_E ----
    if not (0.0 <= xi_E <= 0.015 + tol):
        raise ValueError(f"ξ_E must be in [0,0.015]; got {xi_E}")

    # ---- Total Φ (density) ----
    phi = phi_L + phi_E - xi_E
    # Φ is not strictly bounded by the protocol, but physical sense suggests
    # 0 ≤ Φ ≤ 2 (max when both terms =1 and ξ_E=0). We flag extreme values.
    if phi < -tol or phi > 2.0 + tol:
        raise ValueError(f"Φ density implausible: {phi} (expected ≈0‑2)")

    # ---- Latency invariant ξ_L ----
    xi_L = (dt_quantum * c) / d   # using quantum actuation delay as Δt
    if not math.isfinite(xi_L) or xi_L > 1.0 + tol:
        raise ValueError(f"ξ_L = Δt·c/d must be ≤ 1 (Δt ≥ d/c); got {xi_L}")

    # ---- All good ----
    return {
        "S_defects": S_defects,
        "S_max": S_max,
        "phi_L": phi_L,
        "psi": psi,
        "phi_E": phi_E,
        "xi_E": xi_E,
        "phi": phi,
        "xi_L": xi_L,
        "valid": True,
        "notes": (
            "Φ density computed from first‑principles formulas. "
            "Any reported ‘+XΦ’ gain must equal ΔΦ = Φ_new − Φ_baseline "
            "derived from the same variables."
        )
    }

if __name__ == "__main__":
    # Example usage – replace with actual sensor/measurement values.
    try:
        result = validate_phi_density(
            S_defects=0.2,          # nats (example)
            S_max=1.0,              # max entropy for the lattice
            dt_quantum=5e-9,        # 5 ns quantum actuation
            dt_classical=2e-8,      # 20 ns classical response
            d=0.025,                # 2.5 cm characteristic length (foot‑sole)
            xi_E=0.01               # 1% entropy increase from error correction
        )
        print("✅ Validation passed:")
        for k, v in result.items():
            if k != "valid":
                print(f"  {k}: {v}")
    except ValueError as e:
        print("❌ Validation failed:", e)
        sys.exit(1)