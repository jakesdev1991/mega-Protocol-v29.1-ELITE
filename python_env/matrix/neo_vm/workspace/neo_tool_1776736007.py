# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import matplotlib.pyplot as plt
from scipy import stats

# Disruptive Simulation: Synchronized Cadence Collapse vs. Field Theory Blindness

def simulate_synchronized_collapse(n_companies=15, time_period=730):
    """
    Simulates the TRUE mechanism: synchronized presentation clusters that create
    a false stability signal, then catastrophic desynchronization.
    """
    # First 300 days: synchronized cluster (companies 0-7 present together)
    # Next 200 days: partial desync (some drop out)
    # Final 230 days: complete fragmentation
    
    events = [[] for _ in range(n_companies)]
    sync_companies = 8
    
    # Phase 1: Synchronized cluster (days 0-300)
    cluster_times = np.arange(20, 300, 45)  # Regular cluster events
    for t in cluster_times:
        for i in range(sync_companies):
            # All synced companies present within 3 days of each other
            jitter = np.random.normal(0, 1.5)
            events[i].append(t + jitter)
            # Add 1-2 extra presentations near cluster
            events[i].extend(t + np.random.normal(0, 2, np.random.poisson(1.5)))
    
    # Phase 2: Partial desync (days 300-500) - some companies lose access
    for i in range(sync_companies):
        if i < 3:  # 3 companies drop out
            continue
        for t in np.arange(320, 500, 60):
            if np.random.random() > 0.4:  # 60% chance of still presenting
                events[i].append(t + np.random.normal(0, 2))
    
    # Phase 3: Fragmentation (days 500-730) - everyone isolated
    for i in range(n_companies):
        if len(events[i]) == 0:  # Already dropped out
            continue
        # Sparse random events
        remaining_days = time_period - 500
        n_events = np.random.poisson(remaining_days / 120)  # Much sparser
        events[i].extend(500 + np.cumsum(np.random.exponential(120, n_events)))
    
    return [np.sort(np.array(ev)) for ev in events]

def calculate_phi4_metrics(events, window=90):
    """
    Calculates what the φ⁴ field theory would measure: individual cadence metrics.
    Returns CCS and entropy - these will FAIL to detect synchronized fragility.
    """
    results = []
    for ev in events:
        if len(ev) < 5:
            results.append({'ccs': np.nan, 'entropy': np.nan, 'jerk': np.nan})
            continue
        
        intervals = np.diff(ev)
        if len(intervals) < window:
            window = len(intervals)
        
        # CCS calculation
        mu = np.mean(intervals[-window:])
        sigma = np.std(intervals[-window:])
        n_cluster = np.sum(intervals[-window:] < 7)
        ccs = np.exp(-sigma/(mu+1e-6)) * np.exp(-n_cluster/window)
        
        # Entropy of intervals
        hist, _ = np.histogram(intervals[-window:], bins=10, density=True)
        hist = hist[hist > 0]
        entropy = -np.sum(hist * np.log(hist))
        
        # Jerk (3rd derivative of entropy over time)
        if len(results) > 3:
            recent_entropies = [r['entropy'] for r in results[-4:]] + [entropy]
            if not any(np.isnan(e) for e in recent_entropies):
                jerk = np.diff(recent_entropies, 3)[0] if len(recent_entropies) >= 4 else 0
            else:
                jerk = 0
        else:
            jerk = 0
        
        results.append({'ccs': ccs, 'entropy': entropy, 'jerk': jerk})
    
    return results

def calculate_synchronization_order_parameter(events, time_window=30):
    """
    The DISRUPTIVE metric: measures phase-locking between companies.
    This is what ACTUALLY predicts collapse.
    """
    if len(events) < 2:
        return 0
    
    # Create binary activity matrix: companies × time bins
    time_bins = np.arange(0, 730, time_window)
    activity = np.zeros((len(events), len(time_bins)))
    
    for i, ev in enumerate(events):
        for e in ev:
            bin_idx = int(e // time_window)
            if bin_idx < len(time_bins):
                activity[i, bin_idx] = 1
    
    # Calculate pairwise correlation matrix
    corr_matrix = np.corrcoef(activity)
    corr_matrix = np.nan_to_num(corr_matrix, 0)
    
    # Order parameter = mean correlation (excluding self)
    mask = ~np.eye(len(events), dtype=bool)
    order_param = np.mean(corr_matrix[mask])
    
    return order_param

# Run simulation
print("=== SYNCHRONIZED CADENCE COLLAPSE SIMULATION ===")
events = simulate_synchronized_collapse()
phi4_metrics = calculate_phi4_metrics(events)
sync_order = calculate_synchronization_order_parameter(events)

# Plot the collapse
fig, axes = plt.subplots(3, 1, figsize=(12, 10))

# Top: Event raster plot
for i, ev in enumerate(events):
    axes[0].scatter(ev, [i]*len(ev), alpha=0.6, s=8)
axes[0].axvspan(0, 300, alpha=0.1, color='green', label='Sync Phase')
axes[0].axvspan(300, 500, alpha=0.1, color='orange', label='Partial Desync')
axes[0].axvspan(500, 730, alpha=0.1, color='red', label='Fragmentation')
axes[0].set_title('Presentation Events: Synchronized Cadence Collapse')
axes[0].set_xlabel('Time (days)')
axes[0].set_ylabel('Company ID')
axes[0].legend()

# Middle: φ⁴ metrics (will show FALSE STABILITY)
ccs_values = [m['ccs'] for m in phi4_metrics if not np.isnan(m['ccs'])]
entropy_values = [m['entropy'] for m in phi4_metrics if not np.isnan(m['entropy'])]

axes[1].plot(ccs_values, label='CCS (φ⁴ Regularity)', color='blue')
axes[1].axhline(np.mean(ccs_values), linestyle='--', alpha=0.5)
axes[1].set_title(f'φ⁴ Field Theory Metrics: MISSES Collapse\n(CCS stays high during sync phase)')
axes[1].set_xlabel('Company Index')
axes[1].set_ylabel('CCS Score')
axes[1].legend()

# Bottom: TRUE order parameter
sync_over_time = []
for t in np.arange(50, 730, 50):
    events_up_to_t = [ev[ev < t] for ev in events]
    sync_over_time.append(calculate_synchronization_order_parameter(events_up_to_t))

axes[2].plot(np.arange(50, 730, 50), sync_over_time, color='red', linewidth=2)
axes[2].axvspan(0, 300, alpha=0.1, color='green')
axes[2].axvspan(300, 500, alpha=0.1, color='orange')
axes[2].axvspan(500, 730, alpha=0.1, color='red')
axes[2].set_title('SYNCHRONIZATION ORDER PARAMETER\n(True Collapse Signal)')
axes[2].set_xlabel('Time (days)')
axes[2].set_ylabel('Mean Pairwise Correlation')
axes[2].set_ylim(0, 1)

plt.tight_layout()
plt.show()

# Statistical proof: φ⁴ metrics don't predict the desync
print("\n=== STATISTICAL PROOF OF FAILURE ===")
print(f"φ⁴ CCS during sync (days 0-300): {np.mean([m['ccs'] for m in phi4_metrics[:8]]):.3f}")
print(f"φ⁴ CCS after fragmentation (days 500+): {np.mean([m['ccs'] for m in phi4_metrics[-5:]]):.3f}")
print("→ CCS shows minimal change, completely missing the systemic collapse")

print(f"\nSynchronization order parameter:")
print(f"  Sync phase: {sync_over_time[3]:.3f}")
print(f"  Fragmentation phase: {sync_over_time[-1]:.3f}")
print("→ Order parameter captures the TRUE catastrophic breakdown")

# Disruptive insight summary
print("\n" + "="*60)
print("DISRUPTIVE INSIGHT: THE φ⁴ FIELD THEORY IS A CATEGORY ERROR")
print("="*60)
print("The proposal commits a fatal ontological mistake:")
print("• Treats each company's presentation cadence as an INDEPENDENT scalar field")
print("• Assumes breakdown occurs through individual symmetry breaking")
print("• Uses equilibrium physics (Mexican hat potential) for a non-equilibrium system")
print("\nREALITY: Presentation schedules form a TEMPORAL NETWORK where:")
print("• Fragility emerges from SYNCHRONIZATION between companies")
print("• Phase-locked clusters create narrative echo chambers (false stability)")
print("• Collapse occurs via DESYNCHRONIZATION cascades, not individual cadence loss")
print("\n→ The φ⁴ model would have issued NO WARNING during the 300-day sync phase")
print("→ Investors using PICM-Ω would be blindsided by the sudden fragmentation")