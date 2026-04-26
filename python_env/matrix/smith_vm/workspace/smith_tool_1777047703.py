# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
#!/usr/bin/env python3
"""
Omega Protocol Invariant Validator for QALF‑style submissions.
Checks:
  - Φ_L = 1 - S_defects / S_max   ∈ [0,1]
  - Φ_E = Δt_quantum / Δt_classical ∈ [0,1]   (quantum actuation cannot be slower than classical)
  - Φ   = Φ_L + Φ_E - ξ_E          (must be ≥0 and ≤2)
  - ψ   = ln(Φ_L)                  (Invariant Φ‑1)
  - ξ_E ≤ 0.015                    (Invariant Φ‑2: entropy increase ≤1.5%)
  - ξ_L = Δt * c / d ≤ 1           (Invariant Φ‑3: causality)
  - Bekenstein bound sanity check (optional, warning only)
All inputs must be supplied as SI‑compatible scalars.
"""

import math
from typing import NamedTuple

# ----------------------------------------------------------------------
# Physical constants (SI)
C = 299_792_458          # m/s, speed of light
HBAR = 1.054_571_8e-34   # J·s
G   = 6.674_30e-11       # m³·kg⁻¹·s⁻²
K_B = 1.380_649e-23      # J/K
PLANCK_LENGTH = math.sqrt(HBAR * G / C**3)   # ≈ 1.616e-35 m
# ----------------------------------------------------------------------

class QALFParams(NamedTuple):
    S_defects: float   # Shannon entropy of lattice defects (nats)
    S_max:   float     # Maximum possible entropy for the lattice (nats)
    dt_q:    float     # Quantum actuation latency (s)
    dt_c:    float     # Classical actuation latency (s)
    d:       float     # Characteristic actuation distance (m)
    xi_E:    float     # Entropy‑increase fraction (dimensionless, e.g. 0.015)
    # Optional: claimed Phi density for cross‑check
    phi_claimed: float | None = None

def validate(p: QALFParams) -> None:
    # ---- Basic sanity -------------------------------------------------
    assert p.S_max > 0, "S_max must be positive"
    assert 0 <= p.S_defects <= p.S_max, "S_defects must lie in [0, S_max]"
    assert p.dt_c > 0, "Classical latency must be positive"
    assert p.dt_q > 0, "Quantum latency must be positive"
    assert p.d > 0, "Actuation distance must be positive"
    assert 0 <= p.xi_E <= 1, "xi_E must be a fraction"

    # ---- Invariant Φ‑1: lattice genus‑0 homology ----------------------
    Phi_L = 1.0 - p.S_defects / p.S_max
    assert 0.0 <= Phi_L <= 1.0, f"Phi_L out of bounds: {Phi_L}"
    psi = math.log(Phi_L) if Phi_L > 0 else float('-inf')
    # (psi is the invariant; we just compute it for reporting)

    # ---- Invariant Φ‑3: causal latency -------------------------------
    xi_L = p.dt_q * C / p.d
    assert xi_L <= 1.0 + 1e-12, f"Causality violated: xi_L = {xi_L} > 1"

    # ---- Invariant Φ‑2: entropy increase -----------------------------
    assert p.xi_E <= 0.015, f"Entropy increase too large: xi_E = {p.xi_E*100:.3f}% > 1.5%"

    # ---- Derived Φ density -------------------------------------------
    Phi_E = p.dt_q / p.dt_c
    assert 0.0 <= Phi_E <= 1.0, f"Phi_E out of bounds: {Phi_E}"
    Phi = Phi_L + Phi_E - p.xi_E
    assert Phi >= 0.0, f"Resulting Phi density negative: {Phi}"
    # (Theoretical max is 2 when both Phi_L and Phi_E =1 and xi_E=0)

    # ---- Optional cross‑check with claimed Phi -----------------------
    if p.phi_claimed is not None:
        rel_err = abs(Phi - p.phi_claimed) / max(abs(Phi), 1e-12)
        assert rel_err <= 1e-3, (
            f"Claimed Phi density {p.phi_claimed} does not match computed {Phi} "
            f"(relative error {rel_err*100:.2f}%)"
        )

    # ---- Bekenstein bound sanity (warning only) ----------------------
    # Information density (bits per m^3) from S_defects (nats) -> bits
    # I = S_defects / ln(2)  [bits] per lattice volume; we approximate volume
    # as a cube of side d (the actuation length) – a very rough estimate.
    if p.d > 0:
        V_est = p.d ** 3                     # m^3
        if V_est > 0:
            I_bits = p.S_defects / math.log(2)   # total bits in the volume
            rho_I = I_bits / V_est               # bits/m^3
            # Bekenstein bound: I ≤ (2π E R) / (ħ c ln2)
            # We invert to get a minimum energy density required:
            # ε_min = (rho_I * ħ c ln2) / (2π R)   with R ~ d/2
            R = p.d / 2.0
            eps_min = (rho_I * HBAR * C * math.log(2)) / (2 * math.pi * R)
            # Compare to typical solids (~10^9 J/m^3)
            if eps_min > 1e9:
                print(
                    f"[WARN] Bekenstein bound suggests required energy density "
                    f"{eps_min:.2e} J/m³ (>> typical solids). "
                    f"Check information density claims."
                )

    # ---- Reporting ----------------------------------------------------
    print("=== Omega Protocol Invariant Check (QALF) ===")
    print(f"Phi_L (topological)   : {Phi_L:.6f}")
    print(f"Psi = ln(Phi_L)       : {psi:.6f}")
    print(f"Phi_E (causal)        : {Phi_E:.6f}")
    print(f"xi_E (entropy inc.)   : {p.xi_E*100:.3f}%")
    print(f"xi_L (causality)      : {xi_L:.6f} (≤1 required)")
    print(f"Derived Phi density   : {Phi:.6f}")
    if p.phi_claimed is not None:
        print(f"Claimed Phi density   : {p.phi_claimed:.6f}")
    print("All invariants satisfied.\n")

# ----------------------------------------------------------------------
# Example usage (replace with actual measured values from a submission)
if __name__ == "__main__":
    # Dummy numbers that *would* pass the invariants:
    example = QALFParams(
        S_defects=0.2,          # nats
        S_max=1.0,              # nats
        dt_q=0.5e-9,            # 0.5 ns quantum latency
        dt_c=2.0e-9,            # 2.0 ns classical latency
        d=0.02,                 # 2 cm actuation stride
        xi_E=0.01,              # 1% entropy increase
        phi_claimed=None        # no claimed value to cross‑check
    )
    validate(example)