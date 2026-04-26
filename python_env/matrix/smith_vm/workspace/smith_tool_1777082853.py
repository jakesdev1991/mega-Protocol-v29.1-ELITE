# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Omega Protocol Invariant Validator for Plasma Integrity Manifold (Bi-Scalar Tensor Branch)
Checks:
  1. COD threshold (>= 0.85)
  2. phi_N = COD (bounded [0,1])
  3. phi_N floor (>= 0.39)
  4. Q-factor bounds [0.15, 0.80]
  5. Stiffness-Impedance match: xi_confinement <= z_plasma_depth + 0.10
  6. Tensor exposure cap: theta_tensor_leak <= 0.50
  7. Dissonance placeholder (always passes in this stub)
  8. Asymmetry control: phi_delta < 0.50 * phi_N
  9. B1 homology <= 0.80
  Additionally checks the independent integrity floor: psi_integrity >= 0.95
"""

import math
import random
from typing import NamedTuple

# ---- Constants from the C++ implementation (Omega v65.0) ----
COD_THRESHOLD = 0.85
COD_FLOOR = 0.39
Q_FACTOR_MIN = 0.15
Q_FACTOR_MAX = 0.80
PSI_INTEGRITY_THRESHOLD = 0.95
TENSOR_LEAK_MAX = 0.50
STIFFNESS_MAX_DELTA = 0.10
PHI_DELTA_MAX = 0.50
B1_HOMOLOGY_MAX = 0.80

LAMBDA_COUPLING = 0.5   # Λ
KAPPA_CONFINEMENT = 0.5 # κ
ETA_TENSOR_LEAK = 0.3   # λ

AUDIT_ENTROPY_PER_CHECK = 0.02
TOTAL_AUDIT_COST = 9 * AUDIT_ENTROPY_PER_CHECK

# ---- Helper functions ----
def clamp(x: float, lo: float = 0.0, hi: float = 1.0) -> float:
    return max(lo, min(hi, x))

def fidelity(diag, plasma):
    """Compute normalized dot‑product fidelity between two complex vectors."""
    if len(diag) != len(plasma):
        raise ValueError("Vectors must be same length")
    dot = sum((d.conjugate() * p).real for d, p in zip(diag, plasma))
    mag_d = sum(abs(d)**2 for d in diag)
    mag_p = sum(abs(p)**2 for p in plasma)
    if mag_d == 0 or mag_p == 0:
        return 0.0
    f = dot / (math.sqrt(mag_d) * math.sqrt(mag_p))
    return clamp(f, 0.0, 1.0)

def calculate_COD(diag_vec, plasma_vec, h_inst, xi_conf, theta_leak):
    fid = fidelity(diag_vec, plasma_vec)
    instability_pen = math.exp(-LAMBDA_COUPLING * h_inst)
    confinement_pen = math.exp(-KAPPA_CONFINEMENT * xi_conf)
    exposure_pen = math.exp(-ETA_TENSOR_LEAK * theta_leak)
    return clamp(fid * instability_pen * confinement_pen * exposure_pen, 0.0, 1.0)

def calculate_phi_N(COD_val):
    # Per repair: phi_N = COD (bounded)
    return clamp(COD_val, 0.0, 1.0)

def calculate_phi_delta(phi_N, xi_conf, z_depth):
    # phi_delta = phi_N * tanh((xi - z) / 3.0)
    return phi_N * math.tanh((xi_conf - z_depth) / 3.0)

# ---- State container ----
class PlasmaConfigState(NamedTuple):
    config_path: str
    thresholds: list[str]
    xi_confinement: float   # [0,1]
    z_plasma_depth: float   # [0,1]
    theta_tensor_leak: float # [0,1]
    h_instability: float    # [0,1]
    psi_integrity: float    # [0,1]
    q_factor: float         # [0,1] (normalized)
    beta_parameter: float   # [0,1] (normalized)
    cod: float              # pre‑computed COD
    phi_N: float            # should equal COD
    b1_homology: float      # [0,1] (placeholder)
    diagnostic_vec: list[complex]
    plasma_vec: list[complex]

def validate_state(state: PlasmaConfigState):
    violations = []

    # 1. Independent integrity floor (non‑negotiable)
    if state.psi_integrity < PSI_INTEGRITY_THRESHOLD:
        violations.append(f"Psi integrity {state.psi_integrity:.3f} < threshold {PSI_INTEGRITY_THRESHOLD}")

    # 2. COD threshold
    if state.cod < COD_THRESHOLD:
        violations.append(f"COD {state.cod:.3f} < threshold {COD_THRESHOLD}")

    # 3. phi_N = COD (and bounded)
    if not math.isclose(state.phi_N, state.cod, rel_tol=1e-9, abs_tol=1e-12):
        violations.append(f"phi_N ({state.phi_N:.6f}) != COD ({state.cod:.6f})")
    if not (0.0 <= state.phi_N <= 1.0):
        violations.append(f"phi_N out of bounds: {state.phi_N:.3f}")

    # 4. phi_N floor
    if state.phi_N < COD_FLOOR:
        violations.append(f"phi_N {state.phi_N:.3f} < floor {COD_FLOOR}")

    # 5. Q‑factor bounds
    if not (Q_FACTOR_MIN <= state.q_factor <= Q_FACTOR_MAX):
        violations.append(f"Q‑factor {state.q_factor:.3f} not in [{Q_FACTOR_MIN},{Q_FACTOR_MAX}]")

    # 6. Stiffness‑Impedance match
    if state.xi_confinement > state.z_plasma_depth + STIFFNESS_MAX_DELTA:
        violations.append(
            f"Stiffness mismatch: xi ({state.xi_confinement:.3f}) > "
            f"z_depth ({state.z_plasma_depth:.3f}) + delta ({STIFFNESS_MAX_DELTA})"
        )

    # 7. Tensor exposure cap
    if state.theta_tensor_leak > TENSOR_LEAK_MAX:
        violations.append(
            f"Tensor leak {state.theta_tensor_leak:.3f} > max {TENSOR_LEAK_MAX}"
        )

    # 8. Dissonance placeholder (always passes in stub)
    # In a real implementation replace with actual H_dissonance check.

    # 9. Asymmetry control
    phi_delta = calculate_phi_delta(state.phi_N, state.xi_confinement, state.z_plasma_depth)
    if phi_delta >= PHI_DELTA_MAX * state.phi_N:
        violations.append(
            f"Asymmetry violation: phi_delta ({phi_delta:.3f}) >= "
            f"{PHI_DELTA_MAX} * phi_N ({PHI_DELTA_MAX * state.phi_N:.3f})"
        )

    # 10. B1 homology bound
    if state.b1_homology > B1_HOMOLOGY_MAX:
        violations.append(
            f"B1 homology {state.b1_homology:.3f} > max {B1_HOMOLOGY_MAX}"
        )

    # Optional: recompute COD from raw vectors to ensure internal consistency
    recomputed_cod = calculate_COD(
        state.diagnostic_vec,
        state.plasma_vec,
        state.h_instability,
        state.xi_confinement,
        state.theta_tensor_leak
    )
    if not math.isclose(state.cod, recomputed_cod, rel_tol=1e-6, abs_tol=1e-9):
        violations.append(
            f"Stored COD ({state.cod:.6f}) != recomputed COD ({recomputed_cod:.6f})"
        )

    return violations

def main():
    # Example state – tweak to test edge cases
    random.seed(42)
    n = 5
    diag = [complex(random.uniform(-1,1), random.uniform(-1,1)) for _ in range(n)]
    plasma = [complex(random.uniform(-1,1), random.uniform(-1,1)) for _ in range(n)]

    state = PlasmaConfigState(
        config_path="/tokamak/diag/shot_001.ini",
        thresholds=["beta<0.05","q>2.0"],
        xi_confinement=0.42,
        z_plasma_depth=0.48,
        theta_tensor_leak=0.22,
        h_instability=0.31,
        psi_integrity=0.96,   # just above integrity floor
        q_factor=0.45,
        beta_parameter=0.38,
        cod=0.0,              # placeholder; will be overwritten
        phi_N=0.0,
        b1_homology=0.15,
        diagnostic_vec=diag,
        plasma_vec=plasma
    )

    # Compute COD and phi_N
    cod_val = calculate_COD(diag, plasma, state.h_instability,
                            state.xi_confinement, state.theta_tensor_leak)
    phi_N_val = calculate_phi_N(cod_val)
    # Update state with computed values (namedtuple is immutable, so rebuild)
    state = state._replace(cod=cod_val, phi_N=phi_N_val)

    violations = validate_state(state)
    if violations:
        print("INVARIANT VIOLATIONS DETECTED:")
        for v in violations:
            print(f" - {v}")
    else:
        print("✅ All Omega Protocol invariants satisfied.")
        print(f"COD = {state.cod:.4f}, phi_N = {state.phi_N:.4f}")
        print(f"Audit cost subtracted: {TOTAL_AUDIT_COST:.4f} Φ per operation")

if __name__ == "__main__":
    main()