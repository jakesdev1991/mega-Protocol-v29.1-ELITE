# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
# -*- coding: utf-8 -*-
"""
Validation script for the Q-SCOUT proposal.
Checks mathematical soundness and compliance with Omega Protocol invariants:
  - Net Φ gain must be > 0 (specifically > +0.05Φ for deployment per proposal).
  - Ethical constraint: exclude_configphp must remain 1 (hardcoded).
  - Minimum lead volume V >= 5 per scouting cycle.
  - Parameter bounds respected.
  - Risk penalty formulation non‑negative.
"""

import numpy as np
import itertools

# --------------------------
# Helper functions (model)
# --------------------------

def lead_volume(T_sent, T_urg, w_bounty, w_longterm, w_urgent, w_agentic,
                include_github, include_upwork, include_reddit):
    """
    Simplified model for expected lead volume.
    Base volume = 10 leads (simulated).
    Volume increases with lower thresholds (more permissive) and higher weights.
    Source inclusion scales volume.
    """
    base = 10.0
    # threshold effect: linear penalty for being too strict
    thresh_factor = (1.0 - T_sent) * (1.0 - T_urg)  # higher when thresholds low
    # weight effect: sum of weights normalized (assume nominal weight=1)
    weight_factor = (w_bounty + w_longterm + w_urgent + w_agentic) / 4.0
    # source factor: proportion of selected sources
    src_factor = (include_github + include_upwork + include_reddit) / 3.0
    return base * thresh_factor * weight_factor * src_factor

def avg_revenue(T_sent, T_urg, w_bounty, w_longterm, w_urgent, w_agentic,
                include_github, include_upwork, include_reddit):
    """
    Expected average revenue per converted lead.
    Higher thresholds -> higher quality -> higher revenue.
    Weights for 'bounty', 'longterm' increase revenue; 'urgent', 'agentic' slightly less.
    Source dependent revenue: GitHub $500, Upwork $2000, Reddit $800.
    """
    # base revenue per source (weighted by inclusion)
    rev_src = {
        'github': 500.0 * include_github,
        'upwork': 2000.0 * include_upwork,
        'reddit': 800.0 * include_reddit
    }
    total_rev = sum(rev_src.values())
    total_src = include_github + include_upwork + include_reddit
    avg_rev = total_rev / max(total_src, 1)  # avoid div0

    # threshold quality boost: higher thresholds -> +20% revenue per 0.1 increase
    qual_boost = 1.0 + 0.2 * ((T_sent - 0.7) + (T_urg - 0.6)) / 0.2  # normalized around baseline
    # weight boost: bounty and longterm increase revenue, urgent/agentic slight decrease
    weight_boost = 1.0 + 0.1*(w_bounty - 1.0) + 0.1*(w_longterm - 1.0) - 0.05*(w_urgent - 1.0) - 0.05*(w_agentic - 1.0)
    return avg_rev * qual_boost * weight_boost

def conversion_rate(T_sent, T_urg, w_bounty, w_longterm, w_urgent, w_agentic):
    """
    Baseline conversion rate 20% at nominal thresholds/weights.
    Increases with higher thresholds (better quality) and with bounty/longterm weights.
    """
    base_cr = 0.20
    thresh_effect = 0.08 * ((T_sent - 0.7) + (T_urg - 0.6)) / 0.2  # +8% per 0.2 increase
    weight_effect = 0.04*(w_bounty - 1.0) + 0.04*(w_longterm - 1.0)  # +4% per unit weight
    return np.clip(base_cr + thresh_effect + weight_effect, 0.0, 1.0)

def risk_penalty(T_sent, T_urg, w_bounty, w_longterm, w_urgent, w_agentic,
                 include_github, include_upwork, include_reddit, exclude_configphp):
    """
    Simple risk model: penalty increases if thresholds too low (low quality) or if
    unethical source (config.php) would be included. Here we enforce exclude_configphp=1.
    """
    # low threshold risk
    low_thresh_risk = np.clip(0.7 - T_sent, 0, 1) + np.clip(0.6 - T_urg, 0, 1)
    # weight extremity risk (too high weights may indicate spam)
    weight_extre = np.clip((w_bounty - 2.0), 0, 1) + np.clip((w_longterm - 2.0), 0, 1) \
                   + np.clip((w_urgent - 2.0), 0, 1) + np.clip((w_agentic - 2.0), 0, 1)
    # source risk: picking only low‑revenue sources increases risk (simplistic)
    src_risk = (include_github + include_reddit) / max(include_github + include_upwork + include_reddit, 1)
    # ethical risk: if config.php not excluded -> huge penalty
    ethical_risk = 0.0 if exclude_configphp == 1 else 10.0
    return low_thresh_risk + weight_extre + src_risk + ethical_risk

def net_phi(params):
    """
    Compute NetΦ = (V * R) - C_effort - λ * R_risk
    Returns NetΦ in Φ units (we treat $1 ≈ 0.0001Φ for scaling; arbitrary but consistent).
    """
    (T_sent, T_urg, w_b, w_lt, w_ur, w_ag,
     inc_gh, inc_up, inc_rd, exc_cfg) = params
    V = lead_volume(T_sent, T_urg, w_b, w_lt, w_ur, w_ag, inc_gh, inc_up, inc_rd)
    R = avg_revenue(T_sent, T_urg, w_b, w_lt, w_ur, w_ag, inc_gh, inc_up, inc_rd)
    cr = conversion_rate(T_sent, T_urg, w_b, w_lt, w_ur, w_ag)
    # Expected revenue per cycle = V * cr * R (but R already avg per converted lead)
    expected_rev = V * cr * R
    C_effort = 0.1  # Φ cost per cycle (given)
    lam = 0.5       # risk aversion coefficient
    R_risk = risk_penalty(T_sent, T_urg, w_b, w_lt, w_ur, w_ag,
                          inc_gh, inc_up, inc_rd, exc_cfg)
    # Convert $ to Φ: assume 1$ = 0.0001Φ (so $5000 ≈ 0.5Φ). Adjust scaling to match proposal magnitudes.
    phi_per_dollar = 0.0001
    net = (expected_rev * phi_per_dollar) - C_effort - lam * R_risk * 0.001  # scale risk penalty
    return net

# --------------------------
# Validation
# --------------------------

def validate_baseline():
    """Baseline parameters as described in the proposal."""
    baseline = (0.70, 0.60, 1.0, 1.0, 1.0, 1.0,   # thresholds & weights
                1, 1, 1,                         # include GH, Upwork, Reddit
                1)                               # exclude_configphp = 1
    base_phi = net_phi(baseline)
    print(f"Baseline NetΦ: {base_phi:.5f} Φ")
    return base_phi

def validate_constraints(params):
    """Check all hard constraints."""
    T_sent, T_urg, w_b, w_lt, w_ur, w_ag, inc_gh, inc_up, inc_rd, exc_cfg = params
    # Ethical
    if exc_cfg != 1:
        return False, "Ethical violation: config.php not excluded"
    # Minimum quality gates
    if T_sent < 0.7 or T_urg < 0.6:
        return False, f"Quality gate violation: T_sent={T_sent}, T_urg={T_urg}"
    # Minimum lead volume
    V = lead_volume(T_sent, T_urg, w_b, w_lt, w_ur, w_ag, inc_gh, inc_up, inc_rd)
    if V < 5:
        return False, f"Lead volume too low: V={V:.2f}"
    # Parameter bounds
    if not (0.0 <= T_sent <= 1.0 and 0.0 <= T_urg <= 1.0):
        return False, "Threshold out of [0,1]"
    if any(w < 0 for w in [w_b, w_lt, w_ur, w_ag]):
        return False, "Negative weight"
    if any(not (0 <= inc <= 1) for inc in [inc_gh, inc_up, inc_rd]):
        return False, "Source flag not binary"
    if exc_cfg not in (0,1):
        return False, "exclude_configphp not binary"
    return True, "All constraints satisfied"

def random_search(iterations=20000):
    """Random search for improved parameters within bounds."""
    best_phi = -np.inf
    best_params = None
    base_phi = validate_baseline()
    for _ in range(iterations):
        # Sample thresholds
        T_sent = np.random.uniform(0.6, 0.95)
        T_urg = np.random.uniform(0.5, 0.9)
        # Sample weights [0.5, 2.0] as per spec
        w_b = np.random.uniform(0.5, 2.0)
        w_lt = np.random.uniform(0.5, 2.0)
        w_ur = np.random.uniform(0.5, 2.0)
        w_ag = np.random.uniform(0.5, 2.0)
        # Source flags: we keep all three active (as in baseline) to maximize volume
        inc_gh, inc_up, inc_rd = 1,1,1
        exc_cfg = 1  # ethical lock
        params = (T_sent, T_urg, w_b, w_lt, w_ur, w_ag, inc_gh, inc_up, inc_rd, exc_cfg)
        ok, msg = validate_constraints(params)
        if not ok:
            continue
        phi = net_phi(params)
        if phi > best_phi:
            best_phi = phi
            best_params = params
    gain = best_phi - base_phi
    return base_phi, best_phi, gain, best_params

if __name__ == "__main__":
    print("=== Q-SCOUT Mathematical & Invariant Validation ===\n")
    base_phi, opt_phi, gain, best_params = random_search(iterations=50000)
    print(f"Baseline NetΦ: {base_phi:.5f} Φ")
    print(f"Optimized NetΦ: {opt_phi:.5f} Φ")
    print(f"NetΦ Gain: {gain:.5f} Φ")
    print("\nOptimized parameters:")
    names = ["T_sentiment","T_urgency","w_bounty","w_longterm","w_urgent","w_agentic",
             "inc_github","inc_upwork","inc_reddit","exclude_configphp"]
    for n, v in zip(names, best_params):
        print(f"  {n}: {v}")
    # Check constraint satisfaction
    ok, msg = validate_constraints(best_params)
    print(f"\nConstraint check: {ok} ({msg})")
    # Protocol deployment threshold
    if gain > 0.05:
        print("\n✅ NetΦ gain exceeds deployment threshold (+0.05Φ). Proceed.")
    else:
        print("\n❌ NetΦ gain below deployment threshold. Revision needed.")
    # Ethical lock verification
    if best_params[-1] == 1:
        print("✅ Ethical lock (exclude_configphp=1) satisfied.")
    else:
        print("❌ Ethical lock violated.")
    # Lead volume check
    V = lead_volume(*best_params[:6], *best_params[6:9])
    print(f"🔎 Expected lead volume with optimized params: {V:.2f} (≥5 required)")