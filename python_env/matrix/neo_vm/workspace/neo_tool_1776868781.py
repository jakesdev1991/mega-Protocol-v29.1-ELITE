# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np, random, math, sys, json, os
from urllib.request import urlopen
from urllib.error import URLError

# ──────────────────────────────────────────────────────────────────────────────
# 1. Synthetic chaotic tokamak dynamics (logistic map + stochastic shock)
#    x[t+1] = r * x[t] * (1 - x[t]) + shock[t]
#    Disruption occurs if x exceeds critical threshold x_crit.
# ──────────────────────────────────────────────────────────────────────────────
def chaotic_plasma_trajectory(r=3.8, x0=0.5, shock_std=0.05, n_steps=1000):
    x = np.empty(n_steps)
    x[0] = x0
    shock = np.random.normal(0, shock_std, n_steps)
    for t in range(1, n_steps):
        x[t] = r * x[t-1] * (1 - x[t-1]) + shock[t]
    return x, shock

# ──────────────────────────────────────────────────────────────────────────────
# 2. Static Governor (the engine's & audit's approach)
#    Uses fixed SHOCK_LIMIT, VAA_SENSITIVITY, MANIFOLD_DIVERGENCE.
#    Returns binary prediction (0=stable, 1=disruption) for each time step.
# ──────────────────────────────────────────────────────────────────────────────
def static_governor(x, shock, shock_limit, vaa_sens, manifold_div):
    # Simple linear scoring: higher score → higher predicted risk.
    score = (x - shock_limit) + vaa_sens * shock + manifold_div * np.random.random(len(x))
    # Threshold at 0: positive score → predict disruption.
    return (score > 0).astype(int)

# ──────────────────────────────────────────────────────────────────────────────
# 3. Chaotic‑Aware Adaptive Controller (the disruption)
#    Estimates local Lyapunov exponent on the fly; if λ > λ_thr, it *flips*
#    the sign of the manifold divergence, effectively “pushing” the trajectory
#    back toward the stable manifold. This is the *non‑linear* manipulation
#    that static constexpr cannot capture.
# ──────────────────────────────────────────────────────────────────────────────
def adaptive_chaotic_controller(x, shock, shock_limit, vaa_sens, manifold_div, lyap_thr=0.5):
    pred = np.zeros(len(x), dtype=int)
    # Estimate Lyapunov exponent over a short sliding window.
    window = 10
    for t in range(window, len(x)):
        # Approximate λ ≈ (1/window) * Σ log|df/dx|
        # For logistic map, df/dx = r * (1 - 2*x)
        deriv = 3.8 * (1 - 2 * x[t-window:t])
        lyap = np.mean(np.log(np.abs(deriv + 1e-12)))  # avoid log(0)
        # If λ > threshold, flip manifold divergence sign (i.e., invert feedback).
        effective_md = manifold_div if lyap <= lyap_thr else -manifold_div
        score = (x[t] - shock_limit) + vaa_sens * shock[t] + effective_md * np.random.random()
        pred[t] = int(score > 0)
    return pred

# ──────────────────────────────────────────────────────────────────────────────
# 4. AUC computation (rank‑based, no sklearn dependency)
# ──────────────────────────────────────────────────────────────────────────────
def auc_score(y_true, y_score):
    # Compute area under ROC via Wilcoxon‑Mann‑Whitney statistic.
    # y_true is binary, y_score is real‑valued predictor.
    n_pos = np.sum(y_true == 1)
    n_neg = np.sum(y_true == 0)
    if n_pos == 0 or n_neg == 0:
        return 0.5
    # Rank sum of positives.
    order = np.argsort(y_score)
    ranks = np.arange(1, len(y_true) + 1)
    pos_ranks = ranks[order][y_true[order] == 1]
    rank_sum = np.sum(pos_ranks)
    auc = (rank_sum - n_pos * (n_pos + 1) / 2) / (n_pos * n_neg)
    return auc

# ──────────────────────────────────────────────────────────────────────────────
# 5. Data‑source validation: attempt to fetch a few URLs.
#    The script will report which links are dead, exposing the “harvest” as fiction.
# ──────────────────────────────────────────────────────────────────────────────
def check_data_links(links):
    results = {}
    for url in links:
        try:
            with urlopen(url, timeout=5) as response:
                status = response.getcode()
                results[url] = status
        except URLError as e:
            results[url] = str(e)
    return results

# ──────────────────────────────────────────────────────────────────────────────
# 6. Main experiment: compare static vs adaptive control.
# ──────────────────────────────────────────────────────────────────────────────
def main():
    # Parameters.
    N_SHOTS = 5000
    r, x0, shock_std = 3.8, 0.5, 0.05
    # Critical threshold for disruption label.
    x_crit = 0.75

    # Constants to test.
    baseline = {"shock_limit": 0.85, "vaa_sens": 1.0, "manifold_div": 0.30}
    engine = {"shock_limit": 0.82, "vaa_sens": 1.15, "manifold_div": 0.35}
    disruptive = {"shock_limit": 0.5, "vaa_sens": 2.0, "manifold_div": 0.5}

    # Containers for AUCs.
    auc_static = {name: [] for name in ["baseline", "engine", "disruptive"]}
    auc_adaptive = {name: [] for name in ["baseline", "engine", "disruptive"]}

    # Run many simulated shots.
    for shot_id in range(N_SHOTS):
        # Each shot is a trajectory of 1000 steps.
        x, shock = chaotic_plasma_trajectory(r=r, x0=np.random.random(), shock_std=shock_std, n_steps=1000)
        # True label: 1 if x exceeds critical threshold at any point.
        y_true = (x > x_crit).astype(int)

        # Static governor predictions.
        for name, params in zip(["baseline", "engine", "disruptive"],
                                [baseline, engine, disruptive]):
            pred_static = static_governor(x, shock, **params)
            # Use the maximum prediction along trajectory as shot‑level prediction.
            shot_pred_static = float(np.max(pred_static))
            # For AUC we need a continuous score; use the proportion of time steps predicted as disrupted.
            score_static = np.mean(pred_static)
            auc_static[name].append((y_true.max(), score_static))

        # Adaptive controller predictions.
        for name, params in zip(["baseline", "engine", "disruptive"],
                                [baseline, engine, disruptive]):
            pred_adaptive = adaptive_chaotic_controller(x, shock, **params)
            shot_pred_adaptive = float(np.max(pred_adaptive))
            score_adaptive = np.mean(pred_adaptive)
            auc_adaptive[name].append((y_true.max(), score_adaptive))

    # Compute AUC for each method.
    results = {}
    for name in ["baseline", "engine", "disruptive"]:
        true_static, score_static = zip(*auc_static[name])
        results[f"static_{name}_auc"] = auc_score(np.array(true_static), np.array(score_static))
        true_adapt, score_adapt = zip(*auc_adaptive[name])
        results[f"adaptive_{name}_auc"] = auc_score(np.array(true_adapt), np.array(score_adapt))

    # Print results.
    print("=== AUC Comparison (Static vs Adaptive) ===")
    for key, val in results.items():
        print(f"{key}: {val:.4f}")

    # Validate data links.
    sample_links = [
        "http://golem.fjfi.cvut.cz/shots/",
        "https://eudat.eu/use-cases/tokamak-data-mirror-for-jet-and-mast-data-0",
        "https://data.iaea.org/dataset/incident-and-trafficking-database-itdb"
    ]
    link_status = check_data_links(sample_links)
    print("\n=== Data‑source reality check ===")
    for url, status in link_status.items():
        print(f"{url} -> {status}")

if __name__ == "__main__":
    main()