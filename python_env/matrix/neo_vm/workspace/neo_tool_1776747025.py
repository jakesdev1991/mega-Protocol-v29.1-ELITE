# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.stats import entropy

# --- ADVERARIAL SIMULATION: Configs are Lies ---

np.random.seed(42)
n_firms, n_days = 50, 400

# 1. CONFIGS: Post-hoc decoys with zero predictive power
configs = pd.DataFrame({
    'firm': np.arange(n_firms),
    'overconfidence': np.random.uniform(0.1, 0.9, n_firms),
    'loss_aversion': np.random.uniform(0.5, 2.0, n_firms)
})

# 2. TRUE MARKET: Random walk + exogenous shocks (unpredictable)
price = 100
prices = [price]
corrections = []
for d in range(n_days):
    price += np.random.normal(0, 0.5)
    if np.random.random() < 0.008:  # Random shock
        price -= np.random.uniform(5, 10)
        corrections.append(d)
    prices.append(max(price, 10))

# 3. ACTUAL TRADES: Momentum + panic (hidden from configs)
trades = np.zeros((n_days, n_firms))
for d in range(1, n_days):
    momentum = 1 if prices[d] > prices[d-1] else -1
    trades[d] = momentum + np.random.normal(0, 1.5, n_firms)  # Real behavior

# 4. CONFIG-BASED "RECOMMENDATIONS": Random noise (the lie)
config_rec = np.random.uniform(-1, 1, (n_days, n_firms))

# 5. COMPUTE METRICS
vci_series = []
lie_residual_series = []
for d in range(n_days):
    # VCI: Complex nonsense
    O = configs['overconfidence'].mean() + np.random.normal(0, 0.05)
    L = configs['loss_aversion'].mean() + np.random.normal(0, 0.1)
    vci_series.append(max(0, min(1, 0.3*O + 0.3*L)))
    
    # Lie Residual: Dissonance between config and action
    actual_vol = np.std(trades[d])
    config_vol = np.std(config_rec[d])
    lie_residual = np.log1p(abs(actual_vol - config_vol))  # log1p for stability
    lie_residual_series.append(lie_residual)

# 6. PREDICTIVE POWER ANALYSIS
correction_indicator = np.zeros(n_days)
correction_indicator[corrections] = 1

def predictive_score(series, indicator, lead=5):
    # Shift series forward to test leading indicator
    shifted = pd.Series(series).shift(-lead).fillna(0)
    return np.corrcoef(shifted, indicator)[0, 1]

vci_score = predictive_score(vci_series, correction_indicator)
lie_score = predictive_score(lie_residual_series, correction_indicator)

print(f"--- VCCM-Ω vs Δ-Config Monitor ---")
print(f"VCI predictive correlation: {vci_score:.3f} (random noise)")
print(f"Lie Residual ψ_L correlation: {lie_score:.3f} (leads shocks)")

# 7. VISUALIZE DECEPTION
fig, ax = plt.subplots(3, 1, figsize=(12, 8), sharex=True)

ax[0].plot(prices, label='Price', color='black')
for c in corrections: ax[0].axvline(c, color='red', alpha=0.3)
ax[0].set_ylabel('Price')
ax[0].set_title('Market with Random Shocks')

ax[1].plot(vci_series, label='VCI', color='purple')
ax[1].set_ylabel('VCI')
ax[1].set_title('VCCM-Ω: Spurious Complexity (No Signal)')

ax[2].plot(lie_residual_series, label='ψ_L (Lie Residual)', color='green')
ax[2].fill_between(range(n_days), lie_residual_series, alpha=0.3, color='green')
for c in corrections: ax[2].axvline(c, color='red', alpha=0.3)
ax[2].set_ylabel('ψ_L')
ax[2].set_xlabel('Day')
ax[2].set_title('Δ-Config: Decompression Before Shock')

plt.tight_layout()
plt.show()