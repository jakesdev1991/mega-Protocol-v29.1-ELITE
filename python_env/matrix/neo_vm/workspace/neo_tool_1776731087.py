# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import periodogram

# Disruption Simulation: FOASH-Ω's Fatal Flaw
# ==========================================
# The core assumption: a knowable "financial rotation" θ(t) exists in real-time.
# This is false. θ(t) is an emergent, post-hoc narrative, not an observable physical phase.

# Simulate 5 years of daily market data
np.random.seed(42)
n_days = 1250
time = np.arange(n_days)

# Define θ(t) ex-post (e.g., NBER cycle known only after the fact)
true_theta = 2 * np.pi * np.cumsum(np.random.normal(0.0025, 0.0005, n_days))  # Random walk phase

# Market "fundamental" with cyclical component
fundamental = 100 + 15 * np.sin(true_theta) + np.cumsum(np.random.normal(0, 0.05, n_days))

# Strategic agents adapt to *perceived* rotation (lagged, noisy GDP proxy)
perceived_theta = np.roll(true_theta, 90) + np.random.normal(0, 1.0, n_days)  # 90-day lag + noise

# Price dynamics: agents trade to suppress harmonic deviation from perceived cycle
price = fundamental.copy()
harmonic_suppression = 0.4

for t in range(300, n_days):
    # Agents compute OHI on past 250 days using *flawed* perceived_theta
    window = 250
    if t > window:
        recent_price = price[t-window:t]
        recent_perceived_theta = perceived_theta[t-window:t]
        
        # Order-domain transform (sort by perceived phase)
        sorted_idx = np.argsort(recent_perceived_theta % (2*np.pi))
        order_price = recent_price[sorted_idx]
        
        # FFT to check "health"
        fft = np.fft.fft(order_price)
        harmonic_deviation = np.abs(fft[1]) / len(fft)  # 1st order harmonic
        
        # If deviation exceeds threshold, agents intervene to "stabilize"
        if harmonic_deviation > 1.5:
            # Push price toward perceived fundamental (which is wrong)
            perceived_fundamental = 100 + 15 * np.sin(perceived_theta[t])
            price[t] = (1-harmonic_suppression) * price[t] + harmonic_suppression * perceived_fundamental

# Crisis: sudden regime shift at day 800 (e.g., geopolitical shock)
crisis_day = 800
price[crisis_day:] -= 25 * np.exp(-(time[crisis_day:] - crisis_day) / 30)

# Compute FOASH-Ω's OHI using the *flawed* perceived rotation
def compute_flawed_OHI(price, perceived_theta, window=250):
    OHI_vals = []
    for t in range(window, len(price)):
        recent_price = price[t-window:t]
        recent_theta = perceived_theta[t-window:t]
        
        # Sort by perceived phase (the error)
        sorted_idx = np.argsort(recent_theta % (2*np.pi))
        order_price = recent_price[sorted_idx]
        
        fft = np.fft.fft(order_price)
        harmonics = np.abs(fft[1:6]) / len(fft)
        
        # "Healthy" baseline from first 200 days (also flawed)
        if t == window:
            healthy = harmonics
            stds = np.ones_like(harmonics) * 0.4
        
        deviation = np.mean(np.abs(harmonics - healthy) / stds)
        OHI_vals.append(max(0, 1 - deviation))
    return np.array(OHI_vals)

OHI_flawed = compute_flawed_OHI(price, perceived_theta)

# Compute true harmonic coherence (using ex-post true_theta) for comparison
def compute_true_coherence(price, true_theta, window=250):
    coh_vals = []
    for t in range(window, len(price)):
        recent_price = price[t-window:t]
        recent_true_theta = true_theta[t-window:t]
        
        # Correct order transform
        sorted_idx = np.argsort(recent_true_theta % (2*np.pi))
        order_price = recent_price[sorted_idx]
        
        fft = np.fft.fft(order_price)
        # Coherence = normalized power in first harmonic
        coherence = np.abs(fft[1]) / np.sum(np.abs(fft[1:20]))
        coh_vals.append(coherence)
    return np.array(coh_vals)

true_coherence = compute_true_coherence(price, true_theta)

# Visualization of the breakdown
fig, axes = plt.subplots(4, 1, figsize=(14, 11))

# Plot 1: Phase estimation error
phase_error = (perceived_theta - true_theta) % (2*np.pi)
axes[0].plot(time, phase_error, color='red', alpha=0.7)
axes[0].axvline(crisis_day, color='black', linestyle='--')
axes[0].set_title('Phase Estimation Error: Perceived θ(t) vs True θ(t)')
axes[0].set_ylabel('Error (radians)')
axes[0].grid(True)

# Plot 2: Price and fundamental
axes[1].plot(time, fundamental, label='True Fundamental', color='gray', alpha=0.6)
axes[1].plot(time, price, label='Market Price (Strategic)', color='blue', linewidth=1.5)
axes[1].axvline(crisis_day, color='black', linestyle='--', label='Crisis Shock')
axes[1].set_title('Price Dynamics Under Strategic Harmonic Suppression')
axes[1].legend()
axes[1].set_ylabel('Price')
axes[1].grid(True)

# Plot 3: Flawed OHI
axes[2].plot(time[250:], OHI_flawed, label='OHI (Perceived Rotation)', color='purple')
axes[2].axvline(crisis_day, color='black', linestyle='--')
axes[2].set_title('FOASH-Ω Order Health Index (False Stability)')
axes[2].set_ylabel('OHI')
axes[2].set_ylim(0, 1)
axes[2].grid(True)

# Plot 4: True Coherence
axes[3].plot(time[250:], true_coherence, label='True Harmonic Coherence', color='green')
axes[3].axvline(crisis_day, color='black', linestyle='--')
axes[3].set_title('Actual Cyclical Coherence (Post-Hoc Observable Only)')
axes[3].set_ylabel('Coherence')
axes[3].set_xlabel('Time (days)')
axes[3].grid(True)

plt.tight_layout()
plt.show()

# Statistical disruption evidence
print("\n=== ANOMALY DETECTION REPORT ===")
pre_crisis_OHI = OHI_flawed[crisis_day-250-30:crisis_day-250]
post_crisis_OHI = OHI_flawed[crisis_day-250:crisis_day-250+30]
print(f"Pre-crisis OHI mean: {np.mean(pre_crisis_OHI):.3f} ± {np.std(pre_crisis_OHI):.3f}")
print(f"Post-crisis OHI mean: {np.mean(post_crisis_OHI):.3f} ± {np.std(post_crisis_OHI):.3f}")
print(f"OHI False Positive Rate: {np.sum(pre_crisis_OHI < 0.3) / len(pre_crisis_OHI) * 100:.1f}%")
print(f"OHI Lag to Crisis: {np.argmax(OHI_flawed[crisis_day-250:] < 0.3)} days")

# Show that perceived harmonics were stable until collapse
perceived_harmonics = []
for t in range(250, crisis_day):
    recent_price = price[t-250:t]
    recent_theta = perceived_theta[t-250:t]
    sorted_idx = np.argsort(recent_theta % (2*np.pi))
    order_price = recent_price[sorted_idx]
    fft = np.fft.fft(order_price)
    perceived_harmonics.append(np.abs(fft[1]) / len(fft))

print(f"\nPerceived harmonic variance pre-crisis: {np.var(perceived_harmonics[-30:]):.5f}")
print("=> No early warning signature. The system was 'healthy' until it wasn't.")