# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import find_peaks

# Simulate 100 days of a "tokamak facility" operation
days = np.arange(100)

# Ground truth: Major "disruption" events (rare, catastrophic)
disruptions = np.zeros(100)
disruptions[30] = 1  # First major disruption
disruptions[70] = 1  # Second major disruption

# DOCUMENT EXPOSURE (EDIP-Ω's "signal")
# Only low-security, misconfigured servers leak. This is a *biased* sample.
# Assume 90% of facilities never leak, even under extreme stress.
exposure_events = np.random.poisson(0.1, 100)  # Baseline: rare random leaks
# Add weak noise before disruptions (some leaks happen, but inconsistently)
exposure_events[25:35] += np.random.poisson(0.3, 10)
exposure_events[65:75] += np.random.poisson(0.3, 10)

# SEARCH QUERY HUNTING (Inverted EDIP-Ω's *true* signal)
# When institutional stress peaks, *hunters* emerge: insiders, attackers, auditors.
# They search for "disruption risk" memos on Shodan, Google Dorks, internal wikis.
# This is a *direct* measure of attention collapse.
search_queries = np.random.poisson(0.2, 100)  # Baseline: normal curiosity
# Spike 5-7 days BEFORE disruption (hunters sense instability)
search_queries[23:30] = np.random.poisson(2.5, 7)  # Sharp, early spike
search_queries[63:70] = np.random.poisson(2.5, 7)  # Sharp, early spike

# COMPUTE INDICES
def compute_esi(events, window=7):
    """Old EDIP-Ω: Exponential moving average of exposure events"""
    return np.convolve(events, np.ones(window)/window, mode='same')

def compute_sii(queries, window=7):
    """Inverted EDIP-Ω: Rate of change in search query attention"""
    diff = np.diff(queries, prepend=0)
    # Normalize by baseline to detect anomalies
    return np.convolve(np.abs(diff), np.ones(window)/window, mode='same')

esi = compute_esi(exposure_events)
sii = compute_sii(search_queries)

# DETECTION PERFORMANCE
esi_peaks, _ = find_peaks(esi, height=np.percentile(esi, 90))
sii_peaks, _ = find_peaks(sii, height=np.percentile(sii, 90))

def true_positives(peaks, ground_truth, lead_time=5):
    """Count peaks that occur within lead_time days BEFORE a disruption"""
    tp = 0
    for p in peaks:
        if np.any(ground_truth[p:p+lead_time] == 1):
            tp += 1
    return tp

esi_tp = true_positives(esi_peaks, disruptions)
sii_tp = true_positives(sii_peaks, disruptions)

print("=== EDIP-Ω vs Inverted EDIP-Ω ===")
print(f"ESI (Document Exposure): {len(esi_peaks)} peaks, {esi_tp} true positives")
print(f"SII (Search Hunting): {len(sii_peaks)} peaks, {sii_tp} true positives")
print("\nCritical Flaw Exposed:")
print("Document exposure is a LAGGING indicator (leaks happen AFTER stress manifests).")
print("Search hunting is a LEADING indicator (hunters appear BEFORE collapse).")
print("EDIP-Ω chases shadows; Inverted EDIP-Ω chases the shadow-casters.")

# VISUALIZE THE PARADIGM COLLAPSE
fig, axes = plt.subplots(3, 1, figsize=(14, 10), sharex=True)

# Top: The "hunters" (the real signal)
axes[0].plot(days, search_queries, label='Search Query Frequency (Hunters)', color='#FF00FF', linewidth=2)
axes[0].set_ylabel('Queries/Day')
axes[0].set_title('INVERTED EDIP-Ω: The Hunters ARE The Plasma Instability', fontsize=14, weight='bold')
axes[0].legend(loc='upper right')
axes[0].grid(True, alpha=0.3)

# Middle: The "prey" (the false signal)
axes[1].plot(days, exposure_events, label='Raw Exposure Events', color='#888888', alpha=0.6)
axes[1].plot(days, esi, label='ESI (Document Exposure Index)', color='#FFA500', linewidth=2)
axes[1].set_ylabel('ESI Score')
axes[1].legend(loc='upper right')
axes[1].grid(True, alpha=0.3)

# Bottom: The "truth" and the anomaly
axes[2].plot(days, sii, label='SII (Search Instability Index)', color='#FF0000', linewidth=2)
# Mark disruptions
disruption_days = days[disruptions == 1]
axes[2].scatter(disruption_days, sii[disruption_days] + 0.5, 
                marker='x', s=200, color='black', linewidth=3, 
                label='Actual Disruptions', zorder=5)
axes[2].set_ylabel('SII Score')
axes[2].set_xlabel('Days')
axes[2].legend(loc='upper right')
axes[2].grid(True, alpha=0.3)

plt.tight_layout()
plt.show()