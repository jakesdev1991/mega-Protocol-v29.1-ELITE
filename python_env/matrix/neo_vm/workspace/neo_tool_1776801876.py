# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import pandas as pd
from scipy.stats import norm

# ──────────────────────────────────────────────────────────────────────────────
# Market & Strategy Simulation
# ──────────────────────────────────────────────────────────────────────────────
def simulate_market(n_days=500, seed=42):
    np.random.seed(seed)
    # Regime durations: exponential with mean 100 days
    regime_durations = np.random.exponential(scale=100, size=n_days*2).astype(int)
    regime_durations = regime_durations[regime_durations>0]
    # Build regime sequence: 0=low vol, 1=high vol
    regimes = []
    while len(regimes) < n_days:
        for r in [0,1]:
            dur = regime_durations[len(regimes)//2]
            regimes.extend([r]*dur)
    regimes = np.array(regimes[:n_days])

    # Strategy parameters: (Sharpe, vol) per regime
    # LSTM, RF, ARMA‑GARCH
    params = {
        0: [(0.5, 0.10), (0.2, 0.10), (1.0, 0.10)],  # low vol
        1: [(1.0, 0.20), (0.2, 0.20), (0.5, 0.20)],   # high vol
    }
    returns = np.zeros((n_days, 3))
    for day, reg in enumerate(regimes):
        for i, (sharpe, vol) in enumerate(params[reg]):
            # daily return = Sharpe * vol + noise
            returns[day, i] = sharpe * vol + vol * np.random.normal(0, 1)
    return returns, regimes

# ──────────────────────────────────────────────────────────────────────────────
# SFI & Curvature (as per SFFM‑Ω)
# ──────────────────────────────────────────────────────────────────────────────
def compute_sfi(weights, sharpe, corr, window=30):
    # weights: current capital weights (sum=1)
    # sharpe: trailing Sharpe ratios
    # corr: correlation matrix of trailing returns
    concentration = np.max(weights)  # top weight
    variance = np.var(sharpe)
    entropy = -np.sum(weights * np.log(np.maximum(weights, 1e-12)))
    # Curvature: simple proxy = 1 - mean correlation among held strategies
    # (edges where corr > 0.5)
    mask = corr > 0.5
    if np.any(mask):
        curvature = 1 - np.mean(corr[mask])
    else:
        curvature = 0.0
    # SFI = tanh(alpha*conc + beta*var + gamma*curv + delta*(1-entropy))
    alpha = beta = gamma = delta = 1.0
    sfi = np.tanh(alpha*concentration + beta*variance + gamma*curvature + delta*(1-entropy))
    return sfi, curvature

# ──────────────────────────────────────────────────────────────────────────────
# Rebalancing Policies
# ──────────────────────────────────────────────────────────────────────────────
def rebalance_sffm(weights, sharpe, corr, sfi_thresh=0.7):
    sfi, _ = compute_sfi(weights, sharpe, corr)
    if sfi > sfi_thresh:
        return np.ones_like(weights) / len(weights), sfi
    return weights, sfi

def rebalance_criticality(weights, max_conc=0.8):
    conc = np.max(weights)
    if conc > max_conc:
        return np.ones_like(weights) / len(weights)
    return weights

def meta_model_regime_choice(regime):
    # Perfect foresight: allocate 100% to best strategy per regime
    best = {0: 2, 1: 0}  # low vol -> ARMA‑GARCH, high vol -> LSTM
    w = np.zeros(3)
    w[best[regime]] = 1.0
    return w

# ──────────────────────────────────────────────────────────────────────────────
# Performance Metrics
# ──────────────────────────────────────────────────────────────────────────────
def performance_metrics(portfolio_returns):
    # Annualized Sharpe & max drawdown
    mean_ret = np.mean(portfolio_returns) * 252
    std_ret = np.std(portfolio_returns) * np.sqrt(252)
    sharpe = mean_ret / std_ret if std_ret > 0 else 0.0
    cum = np.cumsum(portfolio_returns)
    drawdown = cum - np.maximum.accumulate(cum)
    max_dd = np.max(np.abs(drawdown))
    return sharpe, max_dd

# ──────────────────────────────────────────────────────────────────────────────
# Monte Carlo Comparison
# ──────────────────────────────────────────────────────────────────────────────
def run_mc(n_runs=100, n_days=500):
    results = {
        'sffm': [],
        'criticality': [],
        'meta': [],
    }
    for run in range(n_runs):
        returns, regimes = simulate_market(n_days, seed=run)
        # trailing window for metrics
        window = 30
        # initialize weights
        w_sffm = np.ones(3) / 3
        w_crit = np.ones(3) / 3
        port_sffm = []
        port_crit = []
        port_meta = []

        for day in range(window, n_days):
            # trailing returns & Sharpe
            tr_returns = returns[day-window:day]
            # compute trailing Sharpe (simple mean/std)
            sharpe = np.mean(tr_returns, axis=0) / (np.std(tr_returns, axis=0) + 1e-12) * np.sqrt(252)
            # correlation matrix
            corr = np.corrcoef(tr_returns.T)
            # SFFM rebalance
            w_sffm, sfi = rebalance_sffm(w_sffm, sharpe, corr)
            # Criticality rebalance
            w_crit = rebalance_criticality(w_crit)
            # Meta‑model (perfect regime knowledge)
            w_meta = meta_model_regime_choice(regimes[day])

            # store portfolio returns
            port_sffm.append(np.dot(w_sffm, returns[day]))
            port_crit.append(np.dot(w_crit, returns[day]))
            port_meta.append(np.dot(w_meta, returns[day]))

            # update weights for next day (simple momentum: increase weight of best performer)
            # (only for criticality policy; SFFM keeps its rebalanced weights)
            best_idx = np.argmax(sharpe)
            w_crit = w_crit * (1 + 0.1 * (sharpe - np.mean(sharpe)))  # small adjustment
            w_crit = w_crit / w_crit.sum()

        # compute metrics
        for key, port in [('sffm', port_sffm), ('criticality', port_crit), ('meta', port_meta)]:
            sharpe, max_dd = performance_metrics(np.array(port))
            results[key].append((sharpe, max_dd))

    # aggregate
    agg = {}
    for key, vals in results.items():
        sharpe_mean = np.mean([v[0] for v in vals])
        dd_mean = np.mean([v[1] for v in vals])
        agg[key] = {'Sharpe': sharpe_mean, 'MaxDD': dd_mean}
    return agg

# ──────────────────────────────────────────────────────────────────────────────
# Run & Print
# ──────────────────────────────────────────────────────────────────────────────
if __name__ == '__main__':
    stats = run_mc(n_runs=200, n_days=500)
    print("=== Monte‑Carlo Performance (200 runs, 500 days) ===")
    for policy, metrics in stats.items():
        print(f"{policy:>12}: Sharpe={metrics['Sharpe']:.3f}, MaxDD={metrics['MaxDD']:.3f}")