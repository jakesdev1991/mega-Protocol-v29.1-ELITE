# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
#!/usr/bin/env python3
"""
Omega Protocol Invariant Validator for QALF (Quantum‑Adaptive Lattice Footwear)

This script checks the mathematical soundness of the informational‑first
claims made in the QALF proposal against the Omega Protocol invariants:
    ψ = ln(Φ_L)
    ξ_E ≤ 0.015
    ξ_L = Δt * c / d ≤ 1
    Φ_L = 1 - S_defects / S_max   (must be in (0,1])
    Φ_E = Δt_quantum / Δt_classical (dimensionless)
    Net Φ = Φ_L + Φ_E - ξ_E       (dimensionless)

If any invariant fails, the script reports a non‑compliant result.
"""

import math
from dataclasses import dataclass

# Physical constants (SI)
C_LIGHT = 299_792_458  # m/s

@dataclass
class QALFParams:
    # Entropic quantities
    S_defects: float          # Shannon entropy of lattice defects (nats)
    S_max: float              # Maximum possible entropy (nats)
    # Temporal quantities
    dt_quantum: float         # Quantum actuation time (s)
    dt_classical: float       # Classical actuation time (s)
    # Latency & distance
    dt: float                 # Actual actuation latency used in ξ_L (s)
    d: float                  # Characteristic distance over which signal propagates (m)
    # Entropy budget
    S_initial: float          # Initial entropy before operation (nats)
    # Optional: total entropy after operation (if known)
    S_final: float = None     # If provided, used to compute ξ_E directly

def compute_phi_L(p: QALFParams) -> float:
    """Lattice informational advantage Φ_L = 1 - S_defects / S_max."""
    if p.S_max <= 0:
        raise ValueError("S_max must be positive.")
    phi_L = 1.0 - p.S_defects / p.S_max
    return phi_L

def compute_phi_E(p: QALFParams) -> float:
    """Causal response advantage Φ_E = Δt_quantum / Δt_classical."""
    if p.dt_classical <= 0:
        raise ValueError("Δt_classical must be positive.")
    return p.dt_quantum / p.dt_classical

def compute_psi(phi_L: float) -> float:
    """Informational potential ψ = ln(Φ_L). Requires Φ_L > 0."""
    if phi_L <= 0:
        raise ValueError("Φ_L must be > 0 to take logarithm.")
    return math.log(phi_L)

def compute_xi_E(p: QALFParams) -> float:
    """Entropy‑budget invariant ξ_E = (S_final - S_initial) / S_max."""
    if p.S_max <= 0:
        raise ValueError("S_max must be positive.")
    if p.S_final is None:
        # If final entropy not supplied, we cannot compute ξ_E directly.
        raise ValueError("S_final must be provided to evaluate ξ_E.")
    return (p.S_final - p.S_initial) / p.S_max

def compute_xi_L(p: QALFParams) -> float:
    """Latency invariant ξ_L = Δt * c / d."""
    if p.d <= 0:
        raise ValueError("Characteristic distance d must be positive.")
    return p.dt * C_LIGHT / p.d

def validate(p: QALFParams) -> dict:
    """Run all checks and return a dict of results."""
    results = {}

    # 1. Φ_L and ψ
    try:
        phi_L = compute_phi_L(p)
        results["Φ_L"] = phi_L
        results["Φ_L_ok"] = 0 < phi_L <= 1.0
        results["ψ"] = compute_psi(phi_L)
        results["ψ_ok"] = True   # defined if Φ_L>0
    except Exception as e:
        results["Φ_L_error"] = str(e)
        results["Φ_L_ok"] = False
        results["ψ_ok"] = False

    # 2. Φ_E
    try:
        phi_E = compute_phi_E(p)
        results["Φ_E"] = phi_E
        results["Φ_E_ok"] = True   # dimensionless, any positive value allowed
    except Exception as e:
        results["Φ_E_error"] = str(e)
        results["Φ_E_ok"] = False

    # 3. ξ_E
    try:
        xi_E = compute_xi_E(p)
        results["ξ_E"] = xi_E
        results["ξ_E_ok"] = xi_E <= 0.015
    except Exception as e:
        results["ξ_E_error"] = str(e)
        results["ξ_E_ok"] = False

    # 4. ξ_L
    try:
        xi_L = compute_xi_L(p)
        results["ξ_L"] = xi_L
        results["ξ_L_ok"] = xi_L <= 1.0
    except Exception as e:
        results["ξ_L_error"] = str(e)
        results["ξ_L_ok"] = False

    # 5. Net Φ (only if we have the needed pieces)
    if "Φ_L" in results and "Φ_E" in results and "ξ_E" in results:
        phi_net = results["Φ_L"] + results["Φ_E"] - results["ξ_E"]
        results["Φ_net"] = phi_net
        # Net Φ should be dimensionless; we only warn if absurdly large/small
        results["Φ_net_reasonable"] = -10 <= phi_net <= 10  # generous bound
    else:
        results["Φ_net"] = None
        results["Φ_net_reasonable"] = False

    # Overall compliance
    required_ok = [
        results.get("Φ_L_ok", False),
        results.get("ψ_ok", False),
        results.get("Φ_E_ok", False),
        results.get("ξ_E_ok", False),
        results.get("ξ_L_ok", False),
        results.get("Φ_net_reasonable", False)
    ]
    results["overall_compliant"] = all(required_ok)

    return results

def pretty_print(res: dict):
    """Human‑readable output."""
    print("\n=== Omega Protocol Invariant Check ===")
    for key in ["Φ_L", "ψ", "Φ_E", "ξ_E", "ξ_L", "Φ_net"]:
        if key in res:
            print(f"{key:6}: {res[key]:.6g}")
    print("\n--- Invariant Status ---")
    print(f"Φ_L in (0,1]   : {'OK' if res.get('Φ_L_ok') else 'FAIL'}")
    print(f"ψ defined      : {'OK' if res.get('ψ_ok') else 'FAIL'}")
    print(f"ξ_E ≤ 0.015    : {'OK' if res.get('ξ_E_ok') else 'FAIL'}")
    print(f"ξ_L ≤ 1        : {'OK' if res.get('ξ_L_ok') else 'FAIL'}")
    print(f"Φ_net reasonable: {'OK' if res.get('Φ_net_reasonable') else 'FAIL'}")
    print("\nOverall compliance:", "PASS" if res.get("overall_compliant") else "FAIL")
    if not res.get("overall_compliant"):
        print("\nFailed checks:")
        for flag in ["Φ_L_ok", "ψ_ok", "ξ_E_ok", "ξ_L_ok", "Φ_net_reasonable"]:
            if not res.get(flag, True):
                print(f" - {flag}")

if __name__ == "__main__":
    # Example input – replace with measured or claimed values.
    # These numbers are deliberately chosen to illustrate a *failing* case
    # that matches the criticisms in the analysis.
    example = QALFParams(
        S_defects=0.2,          # nats (arbitrary)
        S_max=1.0,              # nats => Φ_L = 0.8
        dt_quantum=5e-9,        # 5 ns quantum actuation
        dt_classical=2e-8,      # 20 ns classical actuation => Φ_E = 0.25
        dt=1e-9,                # 1 ns latency used for ξ_L
        d=0.01,                 # 1 cm characteristic distance
        S_initial=0.0,
        S_final=0.012           # => ξ_E = 0.012 (1.2 %)
    )
    results = validate(example)
    pretty_print(results)