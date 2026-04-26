# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Omega Protocol – Smith‑Audit Invariant Enforcer for RCOD‑Flux‑Scheduler
--------------------------------------------------------------------
Invariants (as per the Neo‑Smith‑Audit‑Kernel):
    1. Φ‑density must never fall below PHI_DENSITY_THRESHOLD.
    2. Core pinning integrity: only cores 16‑23 may be assigned to the RCOD VM.
    3. Sheaf curvature must stay within SHEAF_CURVATURE_BOUNDS (±0.01).

The enforcer is deliberately lightweight – O(1) checks – and raises
RuntimeError on any violation, forcing the caller to abort or fallback.
"""

from dataclasses import dataclass
from typing import Tuple, List
import json
import struct

# -------------------------- Invariant Constants --------------------------
PHI_DENSITY_THRESHOLD: float = 0.95
CORE_PINNING_RANGE: Tuple[int, int] = (16, 23)   # inclusive
SHEAF_CURVATURE_BOUNDS: float = 0.01
PAGE_SIZE: int = 4096   # typical 4KB page, used for alignment check

# -------------------------- Helper Data Structures -----------------------
@dataclass(frozen=True)
class SheafMetrics:
    phi: float                     # state‑space curvature scalar
    curvature_integral: float      # result of Gaussian_Curvature_Integral(phi)
    sheaf_section: float           # Memory_Sheaf_Section() output

@dataclass(frozen=True)
class TelemetryPacket:
    payload: bytes                 # FlatBuffers‑encoded RCOD metrics

# -------------------------- Invariant Checks -----------------------------
def check_phi_density(current_phi: float) -> None:
    """Raise if Φ‑density drops below the threshold."""
    if current_phi < PHI_DENSITY_THRESHOLD:
        raise RuntimeError(
            f"Φ‑density violation: {current_phi:.4f} < {PHI_DENSITY_THRESHOLD}"
        )

def check_core_pinning(requested_cores: List[int]) -> None:
    """Ensure every core in the request lies inside the pinned range."""
    lo, hi = CORE_PINNING_RANGE
    for c in requested_cores:
        if not (lo <= c <= hi):
            raise RuntimeError(
                f"Core‑pinning violation: core {c} not in range [{lo},{hi}]"
            )

def check_sheaf_curvature(metrics: SheafMetrics) -> None:
    """Validate that curvature‑derived address stays within safe bounds."""
    # The raw sheaf address (pre‑alignment) is the product of the two scalars.
    raw_addr = metrics.curvature_integral * metrics.sheaf_section
    # We only care about the fractional part that would cause mis‑alignment.
    # If the absolute deviation from the nearest page multiple exceeds the bound,
    # the invariant is broken.
    nearest_page = round(raw_addr / PAGE_SIZE) * PAGE_SIZE
    deviation = abs(raw_addr - nearest_page) / PAGE_SIZE  # in pages
    if deviation > SHEAF_CURVATURE_BOUNDS:
        raise RuntimeError(
            f"Sheaf‑curvature violation: deviation {deviation:.4f} pages "
            f"> {SHEAF_CURVATURE_BOUNDS} pages (raw={raw_addr:.2f})"
        )

def validate_telemetry(packet: TelemetryPacket, max_size: int = 4096) -> None:
    """Virtio‑serial packet size guard (optional but recommended)."""
    if len(packet.payload) > max_size:
        raise RuntimeError(
            f"Telemetry packet too large: {len(packet.payload)} > {max_size} bytes"
        )

# -------------------------- QMP Helper (Correct JSON) --------------------
def build_qmp_pin_command(vm_name: str, core_list: List[int]) -> str:
    """
    Return a properly‑formed QMP JSON command to set the given cores online
    for the specified VM.  The caller must send this string over the QMP socket.
    """
    # QMP expects a list of CPU IDs; we turn the range into a list.
    cpu_args = {"cpu": ",".join(str(c) for c in core_list), "state": "on"}
    exec_obj = {"execute": "cpu-set", "arguments": cpu_args}
    return json.dumps(exec_obj)

# -------------------------- Example Usage (Scheduler Hook) ---------------
def schedule_rcod_flux(
    deds_metrics: List[float],
    sheaf_metrics: SheafMetrics,
    target_vm: str = "omega-vm"
) -> None:
    """
    High‑level scheduler entry point that enforces all Smith‑Audit invariants
    before performing any RCOD‑flux allocation.
    """
    # 1. Φ‑density guard (read from telemetry or internal estimator)
    current_phi = sheaf_metrics.phi          # placeholder: in reality read from a monitor
    check_phi_density(current_phi)

    # 2. Sheaf curvature guard (address resolution safety)
    check_sheaf_curvature(sheaf_metrics)

    # 3. Core‑pinning guard – we intend to pin the whole range 16‑23.
    check_core_pinning(list(range(*CORE_PINNING_RANGE)))

    # 4. (Optional) Telemetry size guard – assume we have a packet ready.
    #    In a real implementation you would serialize DEDS_metrics here.
    #    telemetry = TelemetryPacket(payload=serialize_rcod(deds_metrics))
    #    validate_telemetry(telemetry)

    # If we reach this point, all invariants hold → proceed with actual work.
    # -----------------------------------------------------------------
    # Example: issue QMP command to pin cores (send over QMP socket)
    qmp_cmd = build_qmp_pin_command(target_vm, list(range(*CORE_PINNING_RANGE)))
    # send_qmp_over_socket(qmp_cmd)   # <-- left as an exercise for the integrator
    # -----------------------------------------------------------------
    # Finally, compute flux priority and schedule tasks …
    # flux_priority = compute_priority(sheaf_metrics, deds_metrics)
    # apply_scheduler(flux_priority, sheaf_metrics)
    # -----------------------------------------------------------------
    print("[SMITH‑AUDIT] All invariants satisfied. Scheduler may proceed.")

# -------------------------- Simple Self‑Test -----------------------------
if __name__ == "__main__":
    # Nominal case – should pass
    ok_metrics = SheafMetrics(
        phi=0.97,
        curvature_integral=1.23e6,   # arbitrary large number
        sheaf_section=0.0041         # chosen so that product ≈ 5046 ≈ 1.23*PAGE_SIZE
    )
    try:
        schedule_rcod_flux(deds_metrics=[0.5, 0.6, 0.7], sheaf_metrics=ok_metrics)
        print("[SELF‑TEST] Nominal case passed.")
    except RuntimeError as e:
        print(f"[SELF‑TEST] Nominal case FAILED: {e}")

    # Violate Φ‑density
    bad_phi = SheafMetrics(phi=0.90, curvature_integral=1.0, sheaf_section=1.0)
    try:
        schedule_rcod_flux(deds_metrics=[], sheaf_metrics=bad_phi)
    except RuntimeError as e:
        print(f"[SELF‑TEST] Φ‑density catch: {e}")

    # Violate sheaf curvature (mis‑aligned address)
    bad_curv = SheafMetrics(
        phi=0.96,
        curvature_integral=1.0,
        sheaf_section=0.003   # product = 0.003 → far from any page multiple
    )
    try:
        schedule_rcod_flux(deds_metrics=[], sheaf_metrics=bad_curv)
    except RuntimeError as e:
        print(f"[SELF‑TEST] Sheaf‑curvature catch: {e}")

    # Violate core pinning (ask for core 5)
    # This would be caught inside check_core_pinning if we passed a weird list.
    # For demo, we manually call the checker:
    try:
        check_core_pinning([5, 17])
    except RuntimeError as e:
        print(f"[SELF‑TEST] Core‑pinning catch: {e}")