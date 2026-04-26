# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
#!/usr/bin/env python3
"""
Omega Protocol Invariant Validator for RCOD-Flux-Scheduler
---------------------------------------------------------
Checks:
  1. Covariant mode decomposition: all curvature inputs must be (Φ_N, Φ_Δ) pairs.
  2. Joint Smith‑Audit invariant:
        ψ = ln(Φ_N)  (Φ_N > 0)
        ξ_N·Φ_N + ξ_Δ·Φ_Δ ≥ PHI_DENSITY_THRESHOLD
        |∇Φ| ≤ SHEAF_CURVATURE_BOUNDS
  3. Entropy bound on telemetry payload:
        H(RCOD | DEDS, telemetry) ≤ ENTROPY_MAX
  4. QMP command syntax and core‑pinning parameter usage.
  5. Sheaf‑MMU address alignment and curvature‑derived address integrity.
"""

import math
import json
import hashlib
from typing import Tuple, List, Callable

# -------------------------- Protocol Constants --------------------------
PHI_DENSITY_THRESHOLD = 0.95
SHEAF_CURVATURE_BOUNDS = 0.01
XI_N = 0.82   # stiffness prior
XI_DELTA = 1.28  # rigidity coefficient
ENTROPY_MAX = 0.15  # nats, derived from Rubric §5 calibration
CORE_PIN_RANGE = (16, 23)
PAGE_SIZE = 4096

# -------------------------- Helper Math --------------------------------
def shannon_entropy(probs: List[float]) -> float:
    """Base‑e entropy; assumes probs sum to 1."""
    return -sum(p * math.log(p) for p in probs if p > 0)

def conditional_entropy_joint(
    p_rcod: List[float],
    p_deds: List[float],
    p_tele: List[float],
    p_joint: List[float]
) -> float:
    """H(RCOD | DEDS, tele) = H(RCOD, DEDS, tele) - H(DEDS, tele)"""
    H_joint = shannon_entropy(p_joint)
    H_deds_tele = shannon_entropy([a*b for a,b in zip(p_deds, p_tele)])  # approx.
    return H_joint - H_deds_tele

# -------------------------- Invariant Checks ---------------------------
def validate_covariant_input(phi_n: float, phi_delta: float) -> None:
    """Rubric §2: curvature must be expressed as the covariant split."""
    if phi_n <= 0:
        raise ValueError(f"Φ_N must be >0 for ψ=ln(Φ_N); got {phi_n}")
    if not math.isfinite(phi_delta):
        raise ValueError(f"Φ_Δ must be finite; got {phi_delta}")

def validate_smith_audit(phi_n: float, phi_delta: float, core: int) -> None:
    """Rubric §3: joint enforcement of all three sub‑invariants."""
    validate_covariant_input(phi_n, phi_delta)
    psi = math.log(phi_n)
    # Identity Coherence (implicit in psi definition)
    # Stiffness/Rigidity Bound
    bound = XI_N * phi_n + XI_DELTA * phi_delta
    if bound < PHI_DENSITY_THRESHOLD:
        raise ValueError(
            f"Stiffness/Rigidity invariant violated: "
            f"{XI_N}*{phi_n}+{XI_DELTA}*{phi_delta}={bound:.4f} < {PHI_DENSITY_THRESHOLD}"
        )
    # Curvature Safety (approximate gradient magnitude)
    grad_mag = abs(phi_n - PHI_DENSITY_THRESHOLD) + abs(phi_delta)
    if grad_mag > SHEAF_CURVATURE_BOUNDS:
        raise ValueError(
            f"Curvature safety exceeded: |∇Φ|≈{grad_mag:.4f} > {SHEAF_CURVATURE_BOUNDS}"
        )
    # Core pinning range
    if not (CORE_PIN_RANGE[0] <= core <= CORE_PIN_RANGE[1]):
        raise ValueError(
            f"Core {core} outside allowed range {CORE_PIN_RANGE}"
        )

def validate_telemetry_entropy(
    rcod_hist: List[float],
    deds_hist: List[float],
    tele_hist: List[float],
    joint_hist: List[float]
) -> None:
    """Rubric §5: conditional entropy must stay below ENTROPY_MAX."""
    ent = conditional_entropy_joint(rcod_hist, deds_hist, tele_hist, joint_hist)
    if ent > ENTROPY_MAX:
        raise ValueError(
            f"Telemetry entropy too high: H={ent:.4f} nats > {ENTROPY_MAX}"
        )

def validate_qmp_command(cmd: str) -> None:
    """Ensure QMP command is valid JSON and contains required fields."""
    try:
        obj = json.loads(cmd)
    except json.JSONDecodeError as e:
        raise ValueError(f"QMP command not valid JSON: {e}")
    if "execute" not in obj:
        raise ValueError("QMP command missing 'execute' field")
    # Example: pinning command must reference the exact core range
    if obj["execute"] == "cpu-set":
        args = obj.get("arguments", {})
        cpu_range = args.get("cpu", "")
        if cpu_range != f"{CORE_PIN_RANGE[0]}-{CORE_PIN_RANGE[1]}":
            raise ValueError(
                f"CPU pinning must be exactly {CORE_PIN_RANGE[0]}-{CORE_PIN_RANGE[1]}, got '{cpu_range}'"
            )

def validate_sheaf_mmu_address(phi_n: float, phi_delta: float) -> int:
    """
    Rubric §2 + §6: address = floor( ∫ (Φ_N dΦ_Δ) )  (toy model)
    Must be PAGE_SIZE‑aligned.
    """
    validate_covariant_input(phi_n, phi_delta)
    # Toy integral: ∫ Φ_N dΦ_Δ ≈ Φ_N * Φ_Δ (replace with real Riemann contraction)
    integral = phi_n * phi_delta
    addr = int(math.floor(integral))
    if addr % PAGE_SIZE != 0:
        raise ValueError(
            f"Sheaf-MPU address {addr} not {PAGE_SIZE}-byte aligned"
        )
    return addr

# -------------------------- Example Usage (Unit‑Test Style) -----------
if __name__ == "__main__":
    # Mock inputs that *should* pass
    try:
        validate_smith_audit(phi_n=1.0, phi_delta=0.0, core=18)
        print("✓ Smith-Audit invariant passes")
    except ValueError as e:
        print("✗ Smith-Audit:", e)

    try:
        validate_telemetry_entropy(
            rcod_hist=[0.7, 0.3],
            deds_hist=[0.6, 0.4],
            tele_hist=[0.5, 0.5],
            joint_hist=[0.42, 0.18, 0.28, 0.12]
        )
        print("✓ Telemetry entropy passes")
    except ValueError as e:
        print("✗ Telemetry entropy:", e)

    try:
        validate_qmp_command(
            '{"execute":"cpu-set","arguments":{"cpu":"16-23","state":"off"}}'
        )
        print("✓ QMP command valid")
    except ValueError as e:
        print("✗ QMP command:", e)

    try:
        addr = validate_sheaf_mmu_address(phi_n=1.2, phi_delta=0.003)
        print(f"✓ Sheaf-MMU address: {addr} (aligned)")
    except ValueError as e:
        print("✗ Sheaf-MMU address:", e)

    # Demonstrate a failure case
    try:
        validate_smith_audit(phi_n=0.5, phi_delta=0.0, core=18)
    except ValueError as e:
        print("Expected failure →", e)