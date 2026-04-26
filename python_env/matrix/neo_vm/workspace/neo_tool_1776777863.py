# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
# pip install lifelines pandas numpy matplotlib

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from lifelines import CoxPHFitter

# --- Simulate 10,000 firms ---
np.random.seed(42)
n = 10000

# Transparency: openness to sharing tech details (0=stealth, 1=fully open)
transparency = np.random.beta(2, 2, size=n)  # skewed toward moderate transparency

# Negligence: propensity to accidentally leak prod credentials (0=careful, 1=negligent)
negligence = np.random.beta(2, 5, size=n)  # skewed toward low negligence

# Probability of including *any* credentials in whitepaper
# High transparency → more likely to include demo credentials
# High negligence → more likely to include real credentials (small effect)
p_credentials = 0.05 + 0.7 * transparency + 0.1 * negligence
credentials = np.random.rand(n) < p_credentials

# Survival time (Weibull) where transparency *protects* and negligence *harms*
# Scale parameter = exp(5 + 2*transparency - 3*negligence)
scale = np.exp(5 + 2 * transparency - 3 * negligence)
# Shape parameter fixed at 1.5
shape = 1.5
survival_time = np.random.weibull(shape) * scale

# Administrative censoring at time 200 (approx. 5 years)
censor_time = 200
observed_time = np.minimum(survival_time, censor_time)
event = survival_time <= censor_time

# Assemble DataFrame
df = pd.DataFrame({
    'credentials': credentials.astype(int),
    'transparency': transparency,
    'negligence': negligence,
    'duration': observed_time,
    'event': event.astype(int)
})

# --- Fit Cox models ---
# Model 1: credentials only (naive WCRM‑Ω)
cox1 = CoxPHFitter()
cox1.fit(df[['credentials', 'duration', 'event']], duration_col='duration', event_col='event')
print("=== Model 1: Credentials Only ===")
cox1.print_summary()

# Model 2: full model (transparency + negligence + credentials)
cox2 = CoxPHFitter()
cox2.fit(df[['credentials', 'transparency', 'negligence', 'duration', 'event']],
         duration_col='duration', event_col='event')
print("\n=== Model 2: Full Model ===")
cox2.print_summary()

# --- Compute Strategic Fragility Score (SFS) as defined ---
# SFS = (α*C + β*N + γ*D) * exp(-λ*T)
# For simplicity, set α=β=γ=1, λ=0.1, D=1, T=0 (fresh leak)
df['SFS'] = (df['credentials'] + df['negligence'] + 1) * np.exp(-0.1 * 0)

# Check correlation between SFS and actual hazard (neg log survival time)
df['log_hazard'] = -np.log(np.maximum(df['duration'], 1e-6))
corr = df['SFS'].corr(df['log_hazard'])
print(f"\nCorrelation between SFS and log‑hazard: {corr:.3f}")

# Plot coefficient comparison
coefs = pd.DataFrame({
    'Variable': ['credentials', 'transparency', 'negligence'],
    'Model1': [cox1.hazards_['credentials'].iloc[0], np.nan, np.nan],
    'Model2': [cox2.hazards_['credentials'].iloc[0],
               cox2.hazards_['transparency'].iloc[0],
               cox2.hazards_['negligence'].iloc[0]]
})
print("\nCoefficient comparison:")
print(coefs)

# --- Insight: Credentials appear protective in the full model ---
# The coefficient for credentials flips sign or becomes non-significant once transparency is included,
# proving the signal is confounded.

plt.figure(figsize=(6, 4))
plt.barh(['Credentials (naive)', 'Credentials (full)', 'Transparency', 'Negligence'],
         [cox1.hazards_['credentials'].iloc[0],
          cox2.hazards_['credentials'].iloc[0],
          cox2.hazards_['transparency'].iloc[0],
          cox2.hazards_['negligence'].iloc[0]],
         color=['crimson', 'steelblue', 'green', 'orange'])
plt.axvline(0, color='black', linewidth=0.8)
plt.xlabel('Hazard Ratio (log scale)')
plt.title('Hazard Ratios: The "Credential" Effect Disappears')
plt.tight_layout()
plt.show()