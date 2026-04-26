# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import pandas as pd
from scipy.optimize import minimize
import matplotlib.pyplot as plt

# --- Synthetic Data Generation ---
def simulate_hawkes_stress(num_firms=20, days=365, seed=42):
    """
    Simulate a sector where each firm's credential-leak intensity is a Hawkes process
    excited by its own events and synchronized by sector-wide stress (e.g., earnings).
    Disruptions occur with elevated probability when intensity is high.
    """
    rng = np.random.default_rng(seed)
    
    # Sector event calendar (e.g., earnings weeks)
    sector_events = np.arange(14, days, 90)  # quarterly-ish
    
    # Parameters for each firm: background mu, self-excitation alpha, decay beta
    firms = [{
        'mu': rng.exponential(0.02),  # baseline leak rate per day
        'alpha': rng.uniform(0.5, 2.0),  # excitation per leak
        'beta': rng.uniform(0.05, 0.2),  # decay (days^-1)
        'disruption_base': rng.uniform(0.01, 0.03)  # baseline disruption prob per day
    } for _ in range(num_firms)]
    
    leak_timestamps = []
    disruption_timestamps = []
    
    for fid, firm in enumerate(firms):
        t = 0.0
        intensity = firm['mu']
        # Pre-allocate event list: [time, firm_id, event_type]
        # Event types: 0=leak, 1=disruption
        events = []
        
        while t < days:
            # Time to next event (Poisson with current intensity)
            if intensity <= 0:
                wait = np.inf
            else:
                wait = rng.exponential(1.0 / intensity)
            t += wait
            if t >= days:
                break
            
            # Decide if it's a leak or disruption
            # Probability of disruption scales with intensity
            p_disrupt = firm['disruption_base'] * (1.0 + intensity)
            if rng.random() < p_disrupt:
                # Disruption event
                disruption_timestamps.append({'time': t, 'firm': fid})
                events.append((t, fid, 1))
                # Disruptions do not affect intensity (for simplicity)
            else:
                # Leak event
                leak_timestamps.append({'time': t, 'firm': fid})
                events.append((t, fid, 0))
                # Update intensity: self-excitation
                intensity += firm['alpha']
            
            # Decay intensity over time
            dt = wait
            intensity = max(firm['mu'], intensity * np.exp(-firm['beta'] * dt))
            
            # Sector-wide stress: temporarily boost mu near earnings
            if any(abs(t - ev) < 7 for ev in sector_events):
                intensity += 0.1  # temporary stress injection
    
    leaks = pd.DataFrame(leak_timestamps)
    disruptions = pd.DataFrame(disruption_timestamps)
    return leaks, disruptions, sector_events

# --- Hawkes Conditional Intensity Estimation ---
def hawkes_intensity(t, history, mu, alpha, beta):
    """Compute conditional intensity λ(t|H_t) for a Hawkes process."""
    if len(history) == 0:
        return mu
    past_times = np.array(history)
    # Exponential kernel: α * exp(-β (t - t_i))
    contributions = alpha * np.exp(-beta * (t - past_times))
    # Sum only past events
    contributions = contributions[t - past_times > 0]
    return mu + np.sum(contributions)

def compute_tsi(leaks, firms, time_grid):
    """Compute Temporal Stress Index (TSI) as average conditional intensity across firms."""
    tsi = np.zeros_like(time_grid)
    for fid, firm in firms.iterrows():
        firm_leaks = leaks[leaks['firm'] == fid]['time'].values
        intensities = [hawkes_intensity(t, firm_leaks, firm['mu'], firm['alpha'], firm['beta'])
                       for t in time_grid]
        tsi += np.array(intensities)
    return tsi / len(firms)

# --- Simulation & Validation ---
leaks, disruptions, sector_events = simulate_hawkes_stress(num_firms=20, days=365)

# Fit parameters via MLE (simplified: just show the structure)
# In practice you'd optimize (mu, alpha, beta) per firm.
# Here we use the true parameters for demonstration.
firms_df = pd.DataFrame({
    'mu': [np.random.exponential(0.02) for _ in range(20)],
    'alpha': [np.random.uniform(0.5, 2.0) for _ in range(20)],
    'beta': [np.random.uniform(0.05, 0.2) for _ in range(20)]
})

# Compute TSI on a fine grid
time_grid = np.linspace(0, 365, 1000)
tsi = compute_tsi(leaks, firms_df, time_grid)

# --- Disruption Prediction Performance ---
# Simple predictor: if TSI > threshold, predict disruption in next 7 days
threshold = np.percentile(tsi, 85)
predictions = tsi > threshold

# Map disruptions to binary vector
disruption_vec = np.zeros_like(time_grid, dtype=bool)
for d in disruptions['time']:
    idx = np.argmin(np.abs(time_grid - d))
    disruption_vec[idx:idx+7] = True  # mark week after disruption

# Compute precision/recall
tp = np.sum(predictions & disruption_vec)
fp = np.sum(predictions & ~disruption_vec)
fn = np.sum(~predictions & disruption_vec)
precision = tp / (tp + fp) if (tp + fp) > 0 else 0
recall = tp / (tp + fn) if (tp + fn) > 0 else 0

print(f"Precision: {precision:.2f}, Recall: {recall:.2f}")

# --- Plot ---
fig, ax = plt.subplots(figsize=(12, 5))
ax.plot(time_grid, tsi, label='Temporal Stress Index (TSI)', color='tab:red')
ax.scatter(leaks['time'], np.zeros(len(leaks)), marker='|', color='blue', s=10, alpha=0.6, label='Credential Leaks')
ax.scatter(disruptions['time'], np.zeros(len(disruptions)), marker='x', color='black', s=30, label='Disruptions')
ax.axhline(threshold, color='gray', linestyle='--', label=f'Threshold (85th pct)')
ax.scatter(sector_events, np.ones_like(sector_events)*threshold, marker='v', color='green', s=100, label='Sector Events')
ax.set_xlabel('Days')
ax.set_ylabel('Intensity / TSI')
ax.set_title('Hawkes-Process Stress Chronometer: Leaks → Disruptions')
ax.legend()
ax.grid(True)
plt.show()