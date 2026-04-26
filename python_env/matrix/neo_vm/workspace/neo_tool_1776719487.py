# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import scipy.stats as st

# --- Parameters ---
np.random.seed(42)
N_inst = 50
T_days = 365
lambda_i = np.random.uniform(0.5, 2.0, N_inst)  # leaks per day per institution
size_i = np.random.uniform(1.0, 10.0, N_inst)   # market footprint
tier_weights = np.array([1.0, 0.5, 0.2])
gamma_baseline = 0.05   # day^-1
gamma_honeypot = 0.13   # day^-1 (honeypot increases exploitation)

# --- Helper to simulate leak process ---
def simulate_leaks(lambda_inst, gamma, T):
    # Returns list of (inst_id, leak_time, tier_weight)
    leaks = []
    for i, lam in enumerate(lambda_inst):
        # Poisson number of leaks per day
        total_leaks = np.random.poisson(lam * T)
        # Uniformly random times within [0, T]
        leak_times = np.random.uniform(0, T, total_leaks)
        # Random tier for each leak
        tiers = np.random.choice(len(tier_weights), size=total_leaks, p=[0.5, 0.3, 0.2])
        for t, tier in zip(leak_times, tiers):
            leaks.append((i, t, tier_weights[tier]))
    return leaks

# --- Compute CES_i(t) and SCEI(t) ---
def compute_scei(leaks, gamma, T, size_i):
    # Pre‑compute daily SCEI
    scei = np.zeros(T)
    # For each day, sum contributions from all leaks
    for day in range(T):
        t = day
        total = 0.0
        for inst, t_c, w in leaks:
            if t_c <= t:  # leak occurred before or at current day
                # survival probability
                surv = np.exp(-gamma * (t - t_c))
                total += w * surv * size_i[inst]
        scei[day] = total / size_i.sum()
    return scei

# --- Generate data ---
leaks_baseline = simulate_leaks(lambda_i, gamma_baseline, T_days)
leaks_honeypot = simulate_leaks(lambda_i, gamma_honeypot, T_days)

scei_baseline = compute_scei(leaks_baseline, gamma_baseline, T_days, size_i)
scei_honeypot = compute_scei(leaks_honeypot, gamma_honeypot, T_days, size_i)

# --- EVT: Fit GPD to baseline tail ---
# Threshold at 90th percentile
u = np.percentile(scei_baseline, 90)
exceedances = scei_baseline[scei_baseline > u] - u
# Fit GPD (shape, loc=0, scale)
shape, loc, scale = st.genpareto.fit(exceedances, floc=0)

def tail_probability(x):
    # Return 1 - CDF for x > u
    if x <= u:
        return 0.0
    return 1 - st.genpareto.cdf(x - u, shape, loc=0, scale=scale)

# --- Evaluate anomaly detection ---
# Flag days with tail prob < 0.01 (1%)
anomaly_baseline = np.array([tail_probability(x) < 0.01 for x in scei_baseline])
anomaly_honeypot = np.array([tail_probability(x) < 0.01 for x in scei_honeypot])

# --- Results ---
print("=== HONEYPOT PARADOX DEMONSTRATION ===")
print(f"Mean SCEI (baseline): {scei_baseline.mean():.4f}")
print(f"Mean SCEI (honeypot): {scei_honeypot.mean():.4f}")
print(f"Ratio (honeypot/baseline): {scei_honeypot.mean() / scei_baseline.mean():.2f}x")
print()
print(f"Baseline anomaly flags (tail < 1%): {anomaly_baseline.sum()} days")
print(f"Honeypot anomaly flags (using baseline GPD): {anomaly_honeypot.sum()} days")
print()
# True high‑risk days: define as top 5% SCEI in honeypot scenario
high_risk_threshold = np.percentile(scei_honeypot, 95)
true_high_risk = scei_honeypot > high_risk_threshold
detected_high_risk = anomaly_honeypot & true_high_risk
print(f"True high‑risk days in honeypot scenario: {true_high_risk.sum()} days")
print(f"Correctly flagged high‑risk days: {detected_high_risk.sum()} days")
print(f"False negative rate: {1 - detected_high_risk.sum()/true_high_risk.sum():.1%}")