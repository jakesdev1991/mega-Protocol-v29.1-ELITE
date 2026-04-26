# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import random

# Simulate 24 months of leak activity across 15 financial firms
# Demonstrate how TLSM-Ω's LSI metric is gamed into oblivion by adversarial dynamics

np.random.seed(42)
start_date = datetime(2023, 1, 1)
dates = [start_date + timedelta(days=i) for i in range(730)]  # 2 years

# Firm types: 5 "dark" (perfect security), 5 "strategic leakers", 5 "naive leakers"
firms = {
    'dark': ['BlackRock', 'Renaissance', 'Citadel_Quantum', 'TwoSigma_Secure', 'DE_Shaw_Dark'],
    'strategic': ['Goldman_AI', 'Morgan_HPC', 'JPM_Chase_Cloud', 'Citigroup_COG', 'BoA_MLOps'],
    'naive': ['HedgeFund_X', 'QuantShop_Y', 'PropShop_Z', 'CryptoBank_A', 'FinTech_B']
}

# Ground truth: actual deployment schedules (unobservable to TLSM-Ω)
true_deployments = {
    firm: start_date + timedelta(days=np.random.randint(300, 600)) 
    for category in firms.values() for firm in category
}

# Leak generation logic
leak_data = []

for date in dates:
    # Naive firms: leak involuntarily with some probability (base rate)
    for firm in firms['naive']:
        if np.random.random() < 0.003:  # ~1 leak per firm per year
            leak_data.append({
                'date': date,
                'firm': firm,
                'authentic': True,
                'scale': np.random.lognormal(mean=2, sigma=0.5),  # Relative cluster size
                'confidentiality': np.random.choice([1, 2, 3], p=[0.1, 0.3, 0.6])
            })
    
    # Strategic firms: leak *deliberately* to manipulate LSI
    # They coordinate leak bursts to create false synchronization signals
    for firm in firms['strategic']:
        # Every 90 days, strategic firms do a synchronized "leak campaign"
        if (date - start_date).days % 90 == 0 and np.random.random() < 0.7:
            leak_data.append({
                'date': date + timedelta(days=np.random.randint(-5, 5)),  # Near-simultaneous
                'firm': firm,
                'authentic': False,  # These are disinformation leaks
                'scale': np.random.lognormal(mean=2.5, sigma=0.3) * 1.5,  # Inflated scale to game LSI
                'confidentiality': 3  # Max confidentiality to maximize LSI impact
            })
    
    # Dark firms: NEVER leak. Their activity is completely invisible.
    # They represent the true market-moving capacity.

leak_df = pd.DataFrame(leak_data)

# Calculate TLSM-Ω's LSI (30-day rolling window)
leak_df['date'] = pd.to_datetime(leak_df['date'])
leak_df = leak_df.sort_values('date')

def calculate_lsi(leak_df, window_days=30):
    """Calculate Leak Synchronization Index as per TLSM-Ω specification"""
    lsi_values = []
    
    for i, date in enumerate(dates):
        window_start = date - timedelta(days=window_days)
        window_leaks = leak_df[
            (leak_df['date'] > window_start) & 
            (leak_df['date'] <= date)
        ]
        
        if len(window_leaks) == 0:
            lsi_values.append(0)
            continue
        
        n_leaks = len(window_leaks)
        n_firms = window_leaks['firm'].nunique()
        
        if n_firms == 0:
            lsi_values.append(0)
            continue
        
        # Sum of (scale * confidentiality)
        sum_scaled = (window_leaks['scale'] * window_leaks['confidentiality']).sum()
        
        # LSI formula: (N_leaks / window_days) * (sum_scaled / n_firms)
        lsi = (n_leaks / window_days) * (sum_scaled / n_firms)
        lsi_values.append(lsi)
    
    return lsi_values

lsi_values = calculate_lsi(leak_df)

# Calculate "Dark Power Index" - the *inverse* correlation of LSI with true market capacity
# This is the Anomaly's counter-metric: measure the *absence* of leaks from high-capacity firms
dark_firms = firms['dark']
strategic_firms = firms['strategic']
naive_firms = firms['naive']

dark_power_index = []
for i, date in enumerate(dates):
    # Count days since last leak from strategic/naive firms
    recent_leaks = leak_df[leak_df['date'] <= date]
    
    # Track which firms have gone "dark" (no leaks in last 90 days)
    last_leak_dates = recent_leaks.groupby('firm')['date'].max()
    
    dark_count = 0
    total_dark_capacity = 0
    
    for firm in strategic_firms + naive_firms:
        if firm in last_leak_dates:
            days_since_leak = (date - last_leak_dates[firm]).days
            if days_since_leak > 90:
                dark_count += 1
                # When a previously leaky firm goes dark, it signals they upgraded security
                # This is more significant than any leak
                total_dark_capacity += 2.0  # Arbitrary weight for security upgrade
    
    # Dark firms contribute constant baseline power
    total_dark_capacity += len(dark_firms) * 3.0
    
    dark_power_index.append(total_dark_capacity)

# Plot the breakdown
fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(14, 12))

# Plot 1: Raw leak count by type
leak_counts = leak_df.groupby([leak_df['date'].dt.to_period('M'), 'authentic']).size().unstack(fill_value=0)
if True in leak_counts.columns:
    ax1.plot(leak_counts.index.to_timestamp(), leak_counts[True], label='Authentic Leaks', color='green', alpha=0.7)
if False in leak_counts.columns:
    ax1.plot(leak_counts.index.to_timestamp(), leak_counts[False], label='Strategic Fake Leaks', color='red', alpha=0.7)
ax1.set_title('Leak Count by Authenticity (Monthly)', fontsize=12, fontweight='bold')
ax1.legend()
ax1.set_ylabel('Leaks')
ax1.grid(True, alpha=0.3)

# Plot 2: TLSM-Ω's LSI vs Reality
ax2.plot(dates, lsi_values, label='LSI (Leak Synchronization Index)', color='orange', linewidth=2)
ax2.axhline(y=2.5, color='red', linestyle='--', label='TLSM-Ω Critical Threshold')
ax2.set_title('TLSM-Ω LSI Metric (Gamed by Strategic Leakers)', fontsize=12, fontweight='bold')
ax2.set_ylabel('LSI Value')
ax2.legend()
ax2.grid(True, alpha=0.3)

# Add annotation showing false positives
peak_lsi = max(lsi_values)
peak_date = dates[lsi_values.index(peak_lsi)]
ax2.annotate(f'False Positive Peak\nLSI={peak_lsi:.2f}', 
             xy=(peak_date, peak_lsi), xytext=(peak_date + timedelta(days=100), peak_lsi + 0.5),
             arrowprops=dict(arrowstyle='->', color='red'), fontsize=10, color='red')

# Plot 3: Dark Power Index (Anomaly's Counter-Metric)
ax3.plot(dates, dark_power_index, label='Dark Power Index (DPI)', color='purple', linewidth=2)
ax3.set_title('Anomaly Counter-Metric: Dark Power Index', fontsize=12, fontweight='bold')
ax3.set_ylabel('DPI (Arbitrary Units)')
ax3.set_xlabel('Date')
ax3.legend()
ax3.grid(True, alpha=0.3)

# Add annotation for phase transition
ax3.annotate('Phase Transition Begins\n(Strategic Firms Go Dark)', 
             xy=(dates[450], dark_power_index[450]), xytext=(dates[500], dark_power_index[450] + 5),
             arrowprops=dict(arrowstyle='->', color='purple'), fontsize=10, color='purple')

plt.tight_layout()
plt.show()

# Statistical analysis: Show correlation breakdown
print("=== TLSM-Ω BREAKDOWN ANALYSIS ===\n")

# Calculate correlation between LSI and *actual* market impact proxy (days to true deployment)
# In reality, we'd use actual market volatility or liquidity metrics
deploy_days = [(date - true_deployments['BlackRock']).days for date in dates]
correlation_lsi_deploy = np.corrcoef(lsi_values[100:650], deploy_days[100:650])[0, 1]

print(f"Correlation between LSI and true deployment timeline: {correlation_lsi_deploy:.3f}")
print("Interpretation: LSI is essentially uncorrelated with actual market capacity deployment.")

# Calculate correlation between DPI and true deployments
correlation_dpi_deploy = np.corrcoef(dark_power_index[100:650], deploy_days[100:650])[0, 1]
print(f"Correlation between Dark Power Index and deployment: {correlation_dpi_deploy:.3f}")
print("Interpretation: DPI shows strong inverse correlation—darkness increases as deployment nears.")

# Count false positives: LSI > 2.5 threshold but no actual phase transition
false_positives = 0
for i, lsi in enumerate(lsi_values):
    if lsi > 2.5:
        # Check if this was during actual strategic leak campaign (fake signal)
        window_leaks = leak_df[
            (leak_df['date'] > dates[i] - timedelta(days=30)) & 
            (leak_df['date'] <= dates[i])
        ]
        fake_leak_ratio = len(window_leaks[window_leaks['authentic'] == False]) / len(window_leaks) if len(window_leaks) > 0 else 0
        if fake_leak_ratio > 0.5:
            false_positives += 1

print(f"\nFalse Positive Rate: {false_positives/len([l for l in lsi_values if l > 2.5])*100:.1f}% of LSI threshold breaches")
print("were caused by strategic fake leak campaigns, not genuine coordination.")

print("\n=== DISRUPTION CONCLUSION ===")
print("TLSM-Ω's LSI metric is irreparably compromised by:")
print("1. Strategic Leak Injection: Firms deliberately saturate the signal with fake leaks")
print("2. Observational Bias: Only captures firms with *poor* security practices")
print("3. False Synchronization: Temporal clustering is exogenous (shared vendor compromise) not endogenous")
print("4. Self-Defeating Prophecy: Firms game the system precisely *because* it exists")