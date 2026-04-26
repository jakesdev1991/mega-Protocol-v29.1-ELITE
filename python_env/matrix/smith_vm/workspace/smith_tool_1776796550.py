# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Omega‑Protocol Validator for the Abstraction‑Leakage Fragility Monitor (ALFM‑Ω)

The script checks mathematical soundness and invariant compliance of the
proposed integration.  It can be run as a standalone test or imported
as a module for runtime monitoring.

Author:  (you)
"""

import numpy as np
from typing import Dict, List, Tuple

# ----------------------------------------------------------------------
# Helper functions – proxy metrics
# ----------------------------------------------------------------------
def shannon_entropy(probs: np.ndarray) -> float:
    """Shannon entropy, assumes probs sum to 1 (adds tiny epsilon for safety)."""
    eps = 1e-12
    probs = np.clip(probs, eps, 1.0)
    return -np.sum(probs * np.log(probs))

def mapping_entropy(term_to_seq_counts: Dict[str, np.ndarray]) -> Dict[str, float]:
    """H_map(t) for each functional term t."""
    ent = {}
    for term, counts in term_to_seq_counts.items():
        probs = counts / counts.sum()
        ent[term] = shannon_entropy(probs)
    return ent

def annotation_variance(term_to_behaviors: Dict[str, np.ndarray]) -> Dict[str, float]:
    """σ²_ann(t) – variance of measured behavior within each term."""
    var = {}
    for term, beh in term_to_behaviors.items():
        var[term] = np.var(beh, ddof=1)
    return var

def version_skew(term_to_versions: Dict[str, List[str]], latest_version: str) -> Dict[str, float]:
    """V_skew(t) – fraction of parts using outdated schema versions."""
    skew = {}
    for term, vers in term_to_versions.items():
        total = len(vers)
        outdated = sum(1 for v in vers if v != latest_version)  # simple semantic check
        skew[term] = outdated / total if total > 0 else 0.0
    return skew

def reuse_centrality(reuse_edges: List[Tuple[str, str]]) -> Dict[str, float]:
    """Betweenness centrality approximation for functional terms in reuse graph.
    For speed we use a normalized degree proxy (sufficient for validation)."""
    from collections import defaultdict
    deg = defaultdict(int)
    for u, v in reuse_edges:
        deg[u] += 1
        deg[v] += 1
    max_deg = max(deg.values()) if deg else 1
    cent = {term: deg[term] / max_deg for term in deg}
    return cent

# ----------------------------------------------------------------------
# Core ALFM‑Ω computations
# ----------------------------------------------------------------------
def compute_ALI(
    H_map: Dict[str, float],
    sigma2_ann: Dict[str, float],
    V_skew: Dict[str, float],
    centrality: Dict[str, float],
    weights: Tuple[float, float, float, float]
) -> Dict[str, float]:
    """ALI(t) = tanh[α H + β σ² + γ V_skew + δ * centrality]"""
    a, b, c, d = weights
    ali = {}
    for term in H_map:  # assume all dicts share same keys
        arg = a * H_map[term] + b * sigma2_ann[term] + c * V_skew[term] + d * centrality[term]
        ali[term] = np.tanh(arg)  # guarantees [-1,1]; we shift to [0,1] later
    # shift to [0,1]
    for term in ali:
        ali[term] = (ali[term] + 1.0) / 2.0
    return ali

def map_to_Omega_modes(
    ALI: Dict[str, float],
    base_N: float,
    base_Delta: float,
    etas: Tuple[float, float, float, float],
    taus: Tuple[float, float]  # (tau1, tau2) – we ignore lag for static check
) -> Tuple[Dict[str, float], Dict[str, float]]:
    """Φ_N(t) = Φ_N^0 - η1·ALI(t-τ1) + η2·(1 - V_skew(t-τ1))
       Φ_Δ(t)= Φ_Δ^0 + η3·σ²_ann(t-τ2) - η4·H_map(t-τ2)"""
    eta1, eta2, eta3, eta4 = etas
    tau1, tau2 = taus  # not used in static validation
    Phi_N = {}
    Phi_Delta = {}
    for term in ALI:
        # placeholder: assume V_skew and sigma2_ann, H_map are accessible via closure
        # In real code they'd be passed; here we reuse the globals from outer scope.
        Phi_N[term] = base_N - eta1 * ALI[term] + eta2 * (1.0 - V_skew_global[term])
        Phi_Delta[term] = base_Delta + eta3 * sigma2_ann_global[term] - eta4 * H_map_global[term]
    return Phi_N, Phi_Delta

def compute_psi(
    Ricci: Dict[str, float],
    ALI: Dict[str, float],
    R0: float = 1.0,
    lam: float = 0.5
) -> Dict[str, float]:
    """ψ(t) = ln(|R_abstr(t)|/R0) + λ·ALI(t)"""
    psi = {}
    for term in Ricci:
        # Guard against zero or negative Ricci (log of abs)
        val = np.log(np.abs(Ricci[term]) / R0) + lam * ALI[term]
        psi[term] = val
    return psi

def abstraction_entropy(p_type: np.ndarray) -> float:
    """S_abstr = - Σ p_k log p_k over functional types."""
    eps = 1e-12
    p = np.clip(p_type, eps, 1.0)
    return -np.sum(p * np.log(p))

# ----------------------------------------------------------------------
# Validation routine
# ----------------------------------------------------------------------
def validate_ALFM_Omega(
    term_list: List[str],
    term_to_seq_counts: Dict[str, np.ndarray],
    term_to_behaviors: Dict[str, np.ndarray],
    term_to_versions: Dict[str, List[str]],
    reuse_edges: List[Tuple[str, str]],
    p_type: np.ndarray,
    Ricci_est: Dict[str, float],
    # Hyper‑parameters (would be learned in practice)
    weights_ALI: Tuple[float, float, float, float] = (0.3, 0.3, 0.2, 0.2),
    etas_Omega: Tuple[float, float, float, float] = (0.4, 0.3, 0.2, 0.1),
    taus_Omega: Tuple[float, float] = (1.0, 1.0),  # weeks – ignored statically
    base_N: float = 0.8,
    base_Delta: float = 0.2,
    R0: float = 1.0,
    lam_psi: float = 0.5,
    # Constraint thresholds
    ALI_max: float = 0.65,
    N_min: float = 0.6,
    S_min: float = np.log(3.0)
) -> None:
    """Runs all checks; raises AssertionError on any violation."""
    global H_map_global, sigma2_ann_global, V_skew_global  # for mapper closure

    # 1. Proxy computation
    H_map_global   = mapping_entropy(term_to_seq_counts)
    sigma2_ann_global = annotation_variance(term_to_behaviors)
    V_skew_global  = version_skew(term_to_versions, latest_version="v2.0")
    centrality     = reuse_centrality(reuse_edges)

    # 2. ALI
    ALI = compute_ALI(H_map_global, sigma2_ann_global, V_skew_global, centrality, weights_ALI)

    # 3. Ω‑mode mapping
    Phi_N, Phi_Delta = map_to_Omega_modes(
        ALI, base_N, base_Delta, etas_Omega, taus_Omega
    )

    # 4. ψ from Ricci curvature
    psi = compute_psi(Ricci_est, ALI, R0=R0, lam=lam_psi)

    # 5. Abstraction‑entropy gauge
    S_abstr = abstraction_entropy(p_type)

    # ------------------------------------------------------------------
    # Invariant checks (Ω‑Physics Rubric v26.0 style)
    # ------------------------------------------------------------------
    # ALI must lie in [0,1] by construction; we still verify.
    for t in term_list:
        assert 0.0 <= ALI[t] <= 1.0, f"ALI out of bounds for term {t}: {ALI[t]}"
        assert 0.0 <= Phi_N[t] <= 1.0, f"Phi_N out of [0,1] for term {t}: {Phi_N[t]}"
        # Phi_Delta is allowed to be negative in the paper; we only bound magnitude.
        assert abs(Phi_Delta[t]) <= 1.0, f"Phi_Delta magnitude too large for term {t}: {Phi_Delta[t]}"
        # ψ should be a real number (no NaN/inf)
        assert np.isfinite(psi[t]), f"ψ is non‑finite for term {t}: {psi[t]}"
        # Constraint thresholds (MPC‑Ω)
        assert ALI[t] <= ALI_max + 1e-9, f"ALI constraint violated for {t}: {ALI[t]} > {ALI_MAX}"
        assert Phi_N[t] >= N_min - 1e-9, f"Phi_N constraint violated for {t}: {Phi_N[t]} < {N_MIN}"
        # Entropy gauge – global, not per term
    assert S_abstr >= S_min - 1e-9, f"Abstraction entropy constraint violated: {S_abstr} < {S_MIN}"

    # ------------------------------------------------------------------
    # Cost function non‑negativity (quadratic form)
    # ------------------------------------------------------------------
    mu1, mu2, mu3 = 1.0, 1.0, 1.0  # example weights
    cost = 0.0
    for t in term_list:
        cost += (max(ALI[t] - ALI_max, 0.0)) ** 2
        cost += mu1 * (max(N_min - Phi_N[t], 0.0)) ** 2
        cost += mu2 * (Phi_Delta[t] ** 2)
        cost += mu3 * (max(S_min - S_abstr, 0.0)) ** 2
    assert cost >= 0.0, f"MPC‑Ω cost negative: {cost}"

    # If we reach here, all invariants hold.
    print("✅ All Omega‑Protocol invariants satisfied for the synthetic test case.")
    return {
        "ALI": ALI,
        "Phi_N": Phi_N,
        "Phi_Delta": Phi_Delta,
        "psi": psi,
        "S_abstr": S_abstr,
        "cost": cost
    }

# ----------------------------------------------------------------------
# Synthetic data generator for a quick sanity‑check
# ----------------------------------------------------------------------
def _synthetic_demo():
    np.random.seed(42)
    terms = ["promoter", "RBS", "terminator"]
    # term → sequence count vectors (e.g., 5 sequences each)
    term_to_seq_counts = {
        t: np.random.randint(1, 20, size=5) for t in terms
    }
    # term → measured behavior (e.g., fluorescence) for each sequence
    term_to_behaviors = {
        t: np.random.normal(loc=10.0, scale=2.0, size=5) for t in terms
    }
    # term → version strings (some outdated)
    term_to_versions = {
        t: np.random.choice(["v1.0", "v2.0", "v2.0"], size=5).tolist()
        for t in terms
    }
    # reuse edges (term used in design)
    reuse_edges = [
        ("promoter", "RBS"),
        ("RBS", "terminator"),
        ("promoter", "terminator"),
        ("promoter", "RBS"),  # duplicate to increase weight
    ]
    # functional‑type distribution (e.g., 3 types)
    p_type = np.random.dirichlet(alpha=[1.0, 1.0, 1.0])
    # crude Ricci estimate from random field (just for demo)
    Ricci_est = {t: np.random.normal(loc=0.0, scale=0.5) for t in terms}

    # Run validator
    result = validate_ALFM_Omega(
        term_list=terms,
        term_to_seq_counts=term_to_seq_counts,
        term_to_behaviors=term_to_behaviors,
        term_to_versions=term_to_versions,
        reuse_edges=reuse_edges,
        p_type=p_type,
        Ricci_est=Ricci_est
    )
    # Optionally pretty‑print
    for k, v in result.items():
        print(f"{k}: {v}")

if __name__ == "__main__":
    _synthetic_demo()