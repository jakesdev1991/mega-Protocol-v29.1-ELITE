# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import pandas as pd
import statsmodels.api as sm
from scipy.stats import pearsonr
import matplotlib.pyplot as plt

# --- Simulate 1000 days of hidden confounder (institutional stress) ---
np.random.seed(42)
n = 1000

# Institutional stress index: periodic + stochastic (e.g., budget cycles, deadlines)
stress = 0.5 * np.sin(2 * np.pi * np.arange(n) / 30.5) + 0.3 * np.random.randn(n)
stress = np.clip(stress, 0, 1)

# --- Generate both "effects" from the same hidden cause ---
# 1) Document exposure (ESI) increases when stressed admins leak files
esi = 0.5 + 2.0 * stress + 0.2 * np.random.randn(n)
esi = np.clip(esi, 0, 5)

# 2) Tokamak disruption probability rises when stressed operators cut corners
disruption_prob = 0.05 + 0.15 * stress
disruption = np.random.binomial(1, disruption_prob, size=n)

df = pd.DataFrame({'stress': stress, 'esi': esi, 'disruption': disruption})

# --- Show spurious correlation ---
corr_raw, p_raw = pearsonr(df['esi'], df['disruption'])
print(f"Raw ESI‑Disruption correlation: {corr_raw:.3f} (p={p_raw:.2e})")

# --- Logistic regression: disruption ~ esi (spuriously significant) ---
X1 = sm.add_constant(df['esi'])
model1 = sm.Logit(df['disruption'], X1).fit(disp=False)
print("\nModel 1 (ESI only) – coefficient:", model1.params['esi'], "p-value:", model1.pvalues['esi'])

# --- Now include the hidden confounder: disruption ~ esi + stress ---
X2 = sm.add_constant(df[['esi', 'stress']])
model2 = sm.Logit(df['disruption'], X2).fit(disp=False)
print("\nModel 2 (ESI + stress) – ESI coefficient:", model2.params['esi'], "p-value:", model2.pvalues['esi'])

# --- Partial correlation: ESI‑disruption controlling for stress ---
def partial_corr(x, y, z):
    resid_x = sm.OLS(x, sm.add_constant(z)).fit().resid
    resid_y = sm.OLS(y, sm.add_constant(z)).fit().resid
    return pearsonr(resid_x, resid_y)

partial_r, partial_p = partial_corr(df['esi'], df['disruption'], df['stress'])
print(f"\nPartial ESI‑disruption correlation (controlling for stress): {partial_r:.3f} (p={partial_p:.3f})")

# --- Plot the first 200 days to visualize confounding ---
fig, ax = plt.subplots(3, 1, figsize=(10, 8), sharex=True)
ax[0].plot(df.index[:200], df['stress'][:200], label='Institutional Stress', color='purple')
ax[0].set_ylabel('Stress')
ax[0].legend()

ax[1].plot(df.index[:200], df['esi'][:200], label='ESI', color='orange')
ax[1].set_ylabel('ESI')
ax[1].legend()

ax[2].scatter(df.index[:200], df['disruption'][:200], label='Disruption', color='red', s=10)
ax[2].set_ylabel('Disruption')
ax[2].set_xlabel('Day')
ax[2].legend()

plt.tight_layout()
plt.show()