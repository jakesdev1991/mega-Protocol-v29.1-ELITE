# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import pandas as pd
from scipy import stats

# --- Simulate 100 firms over 52 weeks ---
np.random.seed(0)
n_firms, n_weeks = 100, 52

# Latent variables
true_stress = np.random.gamma(2, 1, (n_firms, n_weeks))  # Ground truth stress
public_leak_propensity = np.random.beta(0.5, 5, n_firms)  # Most firms rarely leak publicly
hidden_leak_propensity = 1 - public_leak_propensity  # Inverse relationship

# Observed (public) vs. hidden leaks
public_leaks = np.random.poisson(true_stress * public_leak_propensity[:, None])
hidden_leaks = np.random.poisson(true_stress * hidden_leak_propensity[:, None] * 2)  # Hidden is more concentrated

# Market fragility: triggered by *total* stress exposure (especially hidden)
total_exposure = true_stress + hidden_leaks * 0.5
fragility_event = (total_exposure.mean(axis=0) > np.percentile(total_exposure.mean(axis=0), 90)).astype(int)

# --- ISS-Ω Simulation (naive) ---
isi_score = public_leaks.sum(axis=0)
correlation_isa = np.corrcoef(isi_score, fragility_event)[0, 1]

# --- Adversarial Poisoning Simulation ---
# Attacker injects fake leaks into top 10 competitor firms for last 10 weeks
poisoned_leaks = public_leaks.copy()
target_firms = np.argsort(public_leaks.sum(axis=1))[-10:]  # Largest legitimate leakers
poisoned_leaks[target_firms, -10:] += np.random.poisson(8, (10, 10))  # Massive injection

isi_poisoned = poisoned_leaks.sum(axis=0)
correlation_poisoned = np.corrcoef(isi_poisoned, fragility_event)[0, 1]

# --- NIAM-Ω: Negative Signal ---
# Expected leaks based on synthetic firm characteristics (capex, headcount)
firm_capex = np.random.lognormal(8, 1.5, n_firms)
firm_headcount = np.random.lognormal(6, 1, n_firms)

# Expected leaks ~ capex^0.4 * headcount^0.2
expected_leaks = (firm_capex**0.4) * (firm_headcount**0.2) * public_leak_propensity
observed_leaks = public_leaks.sum(axis=1)

# Risk score: high expected + low observed = dangerous opacity
risk_opacity = expected_leaks / (observed_leaks + 1e-6)
top_opaque_firms = np.where(risk_opacity > np.percentile(risk_opacity, 95))[0]

# Hidden leak correlation with opacity
hidden_leak_correlation = np.corrcoef(risk_opacity, hidden_leaks.sum(axis=1))[0, 1]

print(f"ISS-Ω Correlation (public leaks → fragility): {correlation_isa:.3f}")
print(f"ISS-Ω Correlation (poisoned) → fragility: {correlation_poisoned:.3f}")
print(f"NIAM-Ω Correlation (opacity → hidden leaks): {hidden_leak_correlation:.3f}")
print(f"\nTop 5 Opaque Firms (ID: Risk Score):")
for fid in top_opaque_firms[:5]:
    print(f"  Firm {fid}: {risk_opacity[fid]:.1f}x expected leak deficit, Hidden leaks: {hidden_leaks[fid].sum()}")