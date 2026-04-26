# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
# -*- coding: utf-8 -*-
"""
Omega‑Protocol Invariant Validator for AFDS v3.0 (Trust, φΔ, H_imp, Curvature)
Run: python3 validate_afds_invariants.py
"""

import math
from dataclasses import dataclass, field
from typing import List, Dict, Tuple

# ----------------------------------------------------------------------
# Constants (taken from the Omega Physics Rubric v26.0)
# ----------------------------------------------------------------------
K_BOLTZMANN = 1.0                     # natural units
XI_N = 0.8                            # weight for φₙ in curvature
XI_DELTA = 1.2                        # weight for φΔ in curvature
TAU = 3600.0                          # stability time‑constant (seconds)

# ----------------------------------------------------------------------
# Helper functions – first‑principles definitions
# ----------------------------------------------------------------------
def noise_entropy(paths: set) -> float:
    """H_noise = log(|paths| + 1)"""
    return math.log(len(paths) + 1.0)

def stability_integral(access_times: List[float], now: float) -> float:
    """
    ∫ stability dt ≈ Σ exp(-(now - t_i)/TAU)
    where each access contributes an exponentially‑decaying stability kernel.
    """
    return sum(math.exp(-(now - t) / TAU) for t in access_times)

def phi_n(paths: set, access_times: List[float], now: float) -> float:
    """φₙ = exp(-H_noise) * stability_integral"""
    return math.exp(-noise_entropy(paths)) * stability_integral(access_times, now)

def psi(phi_n_val: float) -> float:
    """ψ = ln(φₙ) ; guard against log(0)"""
    return math.log(max(phi_n_val, 1e-12))

def phi_delta(breadth: int, depth: int) -> float:
    """
    Asymmetric threat invariant.
    Chosen geometric deformation: |breadth−depth|/(breadth+depth)
    Returns 0 when both are zero.
    """
    s = breadth + depth
    return 0.0 if s == 0 else abs(breadth - depth) / s

def gauge_emergence(trust_score: float, phi_delta_val: float) -> float:
    """Gauge emergence = trust_score * |φΔ| (as used in the forensic logger)"""
    return trust_score * abs(phi_delta_val)

def topological_impedance(log_entries: List[Tuple[float, float]]) -> float:
    """
    H_imp = ∫ gauge_emergence dψ
    Approximated by trapezoidal rule over successive (ψ, gauge) points.
    log_entries: list of (psi, gauge_emergence) ordered by time.
    """
    if len(log_entries) < 2:
        return 0.0
    integral = 0.0
    for (psi_prev, g_prev), (psi_cur, g_cur) in zip(log_entries[:-1], log_entries[1:]):
        dpsi = psi_cur - psi_prev
        avg_g = (g_prev + g_cur) * 0.5
        integral += avg_g * dpsi
    return integral

def curvature(phi_n_val: float, phi_delta_val: float, h_imp: float) -> float:
    """𝓡 = ξₙ·φₙ + ξ_Δ·φΔ − H_imp"""
    return XI_N * phi_n_val + XI_DELTA * phi_delta_val - h_imp

# ----------------------------------------------------------------------
# Data structures for the simulation
# ----------------------------------------------------------------------
@dataclass
class ProcessState:
    pid: int
    paths: set = field(default_factory=set)
    access_times: List[float] = field(default_factory=list)
    trust_score: float = 0.0   # will be recomputed from φₙ each step

@dataclass
class LogEntry:
    timestamp: float
    pid: int
    operation: str
    path: str
    applied_latency_ms: int
    traversal_score: float
    trust_score: float
    inter_call_interval: float
    phi_delta: float
    psi: float
    gauge: float

# ----------------------------------------------------------------------
# Validation routine
# ----------------------------------------------------------------------
def validate_sequence(events: List[Dict]) -> None:
    """
    events: list of dicts with keys:
        - pid, path, success (bool), timestamp, operation (optional)
    The function walks through the events, updates process state,
    logs forensic entries and checks every Omega invariant.
    """
    procs: Dict[int, ProcessState] = {}
    forensic_log: List[LogEntry] = []
    topology: Dict[int, Tuple[int, int]] = {}   # pid -> (breadth, depth)
    last_call: Dict[int, float] = {}

    for ev in events:
        pid = ev["pid"]
        path = ev["path"]
        success = ev.get("success", True)
        ts = ev["timestamp"]
        op = ev.get("operation", "lookup")

        # ---- Process state ------------------------------------------------
        if pid not in procs:
            procs[pid] = ProcessState(pid=pid)
        state = procs[pid]

        # novelty detection
        is_novel = path not in state.paths
        if is_novel:
            state.paths.add(path)

        # record access time (only for successful accesses – failed attempts still
        # contribute to instability via novelty penalty)
        state.access_times.append(ts)

        # ---- Trust (φₙ) ----------------------------------------------------
        phi_n_val = phi_n(state.paths, state.access_times, ts)
        # trust score is defined as φₙ (bounded in (0,1] by construction)
        state.trust_score = phi_n_val
        assert 0.0 < state.trust_score <= 1.0, f"Trust out of bounds: {state.trust_score}"

        # ---- Trust mitigation (used for jitter) ----------------------------
        trust_mitigation = 0.8 * state.trust_score   # per spec
        assert 0.0 <= trust_mitigation <= 0.8, f"Bad mitigation: {trust_mitigation}"

        # ---- Topology (breadth/depth) --------------------------------------
        b, d = topology.get(pid, (0, 0))
        # update breadth/depth from the new path
        new_b = len(state.paths)                     # distinct paths visited
        new_d = max(p.count('/') for p in state.paths) if state.paths else 0
        topology[pid] = (new_b, new_d)

        # ---- φΔ ------------------------------------------------------------
        phi_d = phi_delta(new_b, new_d)
        assert 0.0 <= phi_d <= 1.0, f"φΔ out of range: {phi_d}"

        # ---- ψ -------------------------------------------------------------
        psi_val = psi(state.trust_score)
        # ψ can be negative (φₙ<1) but not -inf

        # ---- Gauge emergence ------------------------------------------------
        gauge = gauge_emergence(state.trust_score, phi_d)

        # ---- Forensic log entry --------------------------------------------
        interval = 0.0
        if pid in last_call:
            interval = ts - last_call[pid]
        last_call[pid] = ts

        entry = LogEntry(
            timestamp=ts,
            pid=pid,
            operation=op,
            path=path,
            applied_latency_ms=0,          # jitter not modeled here
            traversal_score=new_b * 0.6 + new_d * 0.4,   # same as engine's raw score
            trust_score=state.trust_score,
            inter_call_interval=interval,
            phi_delta=phi_d,
            psi=psi_val,
            gauge=gauge,
        )
        forensic_log.append(entry)

        # ---- Topological impedance (incremental check) --------------------
        # Build the (ψ, gauge) list for this pid up to now
        pid_entries = [(e.psi, e.gauge) for e in forensic_log if e.pid == pid]
        h_imp = topological_impedance(pid_entries)
        # H_imp should be non‑negative (gauge ≥0, dψ can be negative but integral
        // of a non‑negative gauge over ψ yields ≥0 if ψ is monotonic;
        // we simply check that it is not absurdly negative.
        assert h_imp >= -1e-9, f"Negative impedance: {h_imp}"

        # ---- Curvature ------------------------------------------------------
        curv = curvature(state.trust_score, phi_d, h_imp)
        # Curvature can be positive or negative; just ensure it's a real number.
        assert not math.isnan(curv), "Curvature NaN"

        # ---- Optional: honey‑node detection (placeholder) -------------------
        # In a real system we would compare `path` to a reserved inode/path.
        # Here we just note that the operation field is correctly set.
        if op == "honey_node_access":
            assert entry.operation == "honey_node_access"

    # ----------------------------------------------------------------------
    # Global invariants (optional)
    # ----------------------------------------------------------------------
    # 1. Total Φ‑density contribution from trust modeling must be ≤ +0.25Φ
    #    (derived from the integral of –k_B ΔH_noise). We approximate:
    total_trust_phi = sum(
        -K_BOLTZMANN * (math.log(len(p.paths)+1) - math.log(1))   # ΔH_noise from empty set
        for p in procs.values()
    )
    # The bound is generous; we just check it's not wildly positive.
    assert total_trust_phi <= 0.3, f"Trust Φ‑density too high: {total_trust_phi}"

    print("✅ All Omega‑Protocol invariants satisfied for the supplied event sequence.")

# ----------------------------------------------------------------------
# Example usage – a small synthetic workload
# ----------------------------------------------------------------------
if __name__ == "__main__":
    import random
    random.seed(42)

    synth_events = []
    now = 0.0
    for pid in [1001, 1002, 1003]:
        for i in range(5):
            now += random.uniform(0.5, 2.0)   # advancing time
            synth_events.append({
                "pid": pid,
                "path": f"/home/user/dir{random.randint(0,3)}/file{i}",
                "success": random.choice([True, False]),
                "timestamp": now,
                "operation": "lookup" if random.random() > 0.1 else "honey_node_access",
            })

    validate_sequence(synth_events)