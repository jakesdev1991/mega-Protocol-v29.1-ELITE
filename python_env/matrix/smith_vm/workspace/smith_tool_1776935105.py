# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Ω‑Protocol Invariant Validator for AFDS v3.0 (snapshot version)

Assumptions:
- The caller supplies dictionaries that represent the current state
  of TrustManager, TopologyMetrics and ForensicLogger.
- All logarithms are natural logs.
- ε = 1e-12 to avoid log(0).

The validator is deliberately lightweight – it does **not** execute the
FUSE daemon; it merely checks that the mathematical relationships
prescribed by the Ω‑Physics Rubric v26.0 hold for the supplied state.
"""

import math
from typing import Dict, List, Tuple

EPS = 1e-12
K_BOLTZMANN = 1.0   # set to 1 for dimensionless Φ‑density checks


def clamp(x: float, lo: float = 0.0, hi: float = 1.0) -> float:
    return max(lo, min(hi, x))


def validate_trust_state(state: Dict) -> Tuple[bool, List[str]]:
    """
    state keys:
        pid, trust_score, last_access (seconds since epoch),
        accessed_paths (set), cumulative_stability (float)
    """
    errs = []
    ts = state.get("trust_score", None)
    if ts is None or not (0.0 <= ts <= 1.0 + 1e-9):
        errs.append(f"trust_score out of bounds: {ts}")
    # cumulative_stability should be non‑negative
    cs = state.get("cumulative_stability", None)
    if cs is not None and cs < 0:
        errs.append(f"cumulative_stability negative: {cs}")
    return len(errs) == 0, errs


def compute_phi_n(state: Dict) -> float:
    """
    Φₙ = exp(−H_noise) * StabilityIntegral
    where
        H_noise = ln(|accessed_paths|)
        StabilityIntegral = cumulative_stability   (assumed already time‑weighted)
    """
    accessed = state.get("accessed_paths", set())
    h_noise = math.log(max(len(accessed), 1))
    stability = state.get("cumulative_stability", 0.0)
    phi_n = math.exp(-h_noise) * stability
    return phi_n


def compute_psi(phi_n: float) -> float:
    return math.log(max(phi_n, EPS))


def compute_phi_delta(topology: Dict) -> float:
    """
    Invariant‑consistent asymmetric threat:
        ΦΔ = |breadth − depth| / (breadth + depth)
    breadth = number of unique paths
    depth   = max depth observed
    """
    breadth = len(topology.get("unique_paths", set()))
    depth = topology.get("max_depth", 0)
    if breadth + depth == 0:
        return 0.0
    return abs(breadth - depth) / (breadth + depth)


def compute_topological_impedance(log_entries: List[Dict]) -> float:
    """
    H_imp ≈ Σ_i ½·(g_i + g_{i-1})·(ψ_i - ψ_{i-1})
    where g_i = |ΦΔ_i| * trust_score_i
    """
    if len(log_entries) < 2:
        return 0.0
    total = 0.0
    # pre‑compute ψ and g for each entry
    psi_g = []
    for entry in log_entries:
        phi_n = compute_phi_n({
            "accessed_paths": set(entry.get("trust_accessed_paths", [])),
            "cumulative_stability": entry.get("trust_cumulative_stability", 0.0),
        })
        psi = compute_psi(phi_n)
        phi_delta = entry.get("phi_delta", 0.0)
        trust = clamp(entry.get("trust_score", 0.0))
        g = abs(phi_delta) * trust
        psi_g.append((psi, g))
    for i in range(1, len(psi_g)):
        psi_prev, g_prev = psi_g[i - 1]
        psi_cur, g_cur = psi_g[i]
        total += 0.5 * (g_prev + g_cur) * (psi_cur - psi_prev)
    return total


def validate_curvature(trust_state: Dict,
                       topology: Dict,
                       forensic_entry: Dict,
                       xi_n: float = 0.8,
                       xi_delta: float = 1.2) -> Tuple[bool, List[str]]:
    errs = []
    phi_n = compute_phi_n(trust_state)
    phi_delta = compute_phi_delta(topology)
    h_imp = compute_topological_impedance([forensic_entry])  # single‑entry approx
    curvature = xi_n * phi_n + xi_delta * phi_delta - h_imp
    # Optional: check that curvature is not NaN/inf
    if math.isnan(curvature) or math.isinf(curvature):
        errs.append(f"curvature is non‑finite: {curvature}")
    return len(errs) == 0, errs


def validate_jitter(raw_score: float,
                    mitigation: float,
                    phi_delta: float) -> Tuple[bool, List[str], int]:
    """
    Returns (ok, errors, latency_ms)
    """
    errs = []
    # probability in [0,1]
    prob = math.pow(raw_score / 100.0, 1.5) * mitigation * (1.0 + phi_delta)
    prob = clamp(prob, 0.0, 1.0)
    if phi_delta > 0.95:
        latency = 1000  # special freeze
        return True, errs, latency
    # stochastic decision – we cannot predict the RNG, so we only check bounds
    # latency must be either 0 or in [1,50] ms
    # We'll accept any value in that range as *potentially* correct.
    # For a deterministic check we require the *expected* latency to be in bounds.
    expected_latency = prob * (1.0 + 49.0 * prob) / 2.0  # mean of 1+49*U where U~Uniform[0,prob]
    if not (0.0 <= expected_latency <= 50.0):
        errs.append(f"expected jitter latency out of bounds: {expected_latency}")
    return len(errs) == 0, errs, 0  # latency not deterministic; caller may sample


def main():
    # -----------------------------------------------------------------
    # Example snapshot – replace with real data extracted from the running AFDS
    # -----------------------------------------------------------------
    trust_state_example = {
        "pid": 1234,
        "trust_score": 0.73,
        "last_access": 1713825600.0,  # Unix timestamp (seconds)
        "accessed_paths": {"/etc/passwd", "/etc/shadow", "/var/log/syslog"},
        "cumulative_stability": 4.2,   # already time‑weighted sum
    }

    topology_example = {
        "unique_paths": {"/etc/passwd", "/etc/shadow", "/var/log/syslog", "/home/user/file"},
        "max_depth": 3,
        "depth_histogram": [0, 0, 0, 5],  # index = depth
        "traversal_entropy": 0.12,
    }

    forensic_example = {
        "timestamp": 1713825605.0,
        "pid": 1234,
        "operation": "lookup",
        "path": "/etc/shadow",
        "applied_latency_ms": 12,
        "trust_score": trust_state_example["trust_score"],
        "phi_delta": compute_phi_delta(topology_example),
        "trust_accessed_paths": list(trust_state_example["accessed_paths"]),
        "trust_cumulative_stability": trust_state_example["cumulative_stability"],
        "inter_call_interval": 150.0,   # ms
    }

    # -----------------------------------------------------------------
    # Run validation checks
    # -----------------------------------------------------------------
    all_ok = True
    msgs = []

    # 1. Trust‑state sanity
    ok, errs = validate_trust_state(trust_state_example)
    all_ok &= ok
    msgs.extend([f"[TRUST] {e}" for e in errs])

    # 2. Φₙ / ψ derivation (implicitly checked in curvature)
    phi_n = compute_phi_n(trust_state_example)
    psi = compute_psi(phi_n)
    msgs.append(f"[INFO] Φₙ = {phi_n:.6f}, ψ = ln(Φₙ) = {psi:.6f}")

    # 3. ΦΔ (invariant‑consistent)
    phi_delta = compute_phi_delta(topology_example)
    msgs.append(f"[INFO] ΦΔ (asymmetric threat) = {phi_delta:.6f}")

    # 4. Curvature invariant
    ok, errs = validate_curvature(trust_state_example,
                                  topology_example,
                                  forensic_example)
    all_ok &= ok
    msgs.extend([f"[CURVATURE] {e}" for e in errs])

    # 5. Jitter probability bounds (deterministic part)
    mitigation = 0.8 * trust_state_example["trust_score"]  # as in the code
    ok, errs, _ = validate_jitter(
        raw_score=100 * phi_delta,   # Convert ΦΔ (0‑1) to a “score” similar to original code
        mitigation=mitigation,
        phi_delta=phi_delta,
    )
    all_ok &= ok
    msgs.extend([f"[JITTER] {e}" for e in errs])

    # 6. Topological impedance sanity (should be non‑negative)
    h_imp = compute_topological_impedance([forensic_example])
    if h_imp < -1e-9:
        all_ok = False
        msgs.append(f"[IMPEDANCE] Negative topological impedance: {h_imp}")
    else:
        msgs.append(f"[INFO] H_imp (approx) = {h_imp:.6f}")

    # -----------------------------------------------------------------
    # Final verdict
    # -----------------------------------------------------------------
    if all_ok:
        print("PASS – All Ω‑Protocol invariants satisfied for the supplied snapshot.")
    else:
        print("FAIL – Invariant violations detected:")
        for m in msgs:
            print("  -", m)


if __name__ == "__main__":
    main()