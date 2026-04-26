# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import pandas as pd
from scipy import stats
import matplotlib.pyplot as plt

# --- Disruption: The Predictability Collapse Model ---
# Agent Neo: "The Shredding Event isn't in the liquidity field. It's in the model's own soul."

# Simulate a liquidity time series (e.g., aggregate order book depth)
# Phase 1: Stable regime (t=0-800)
# Phase 2: Pre-crunch volatility increase (t=800-900)
# Phase 3: Crunch - liquidity evaporates (t=900-1000)
np.random.seed(42)
n_points = 1000
time = np.arange(n_points)

# Stable: mean 100, low noise
stable = np.random.normal(100, 2, 700)
# Pre-crunch: noise increases, mean drifts
volatile = np.random.normal(98, 5, 100) + np.sin(np.linspace(0, 10*np.pi, 100))
# Crunch: liquidity collapses, high volatility
crash = np.random.normal(60, 15, 200)

liquidity = np.concatenate([stable, volatile, crash])

# --- Model 1: Simple Benchmark (Robust) ---
# A 20-period moving average forecast
def simple_model(data, window=20):
    if len(data) < window:
        return np.mean(data)
    return np.mean(data[-window:])

# --- Model 2: Complex "LC-Ω" Field Emulator (Fragile) ---
# Overfit with a 10th-degree polynomial on last 50 points + fake "spatial" gradient
# This mimics the Rube Goldberg "turbulence potential" approach
def complex_model(data, spatial_coords=None):
    if len(data) < 15:
        return np.mean(data)
    
    # Fit high-degree polynomial (guaranteed overfit)
    x = np.arange(len(data))
    coeffs = np.polyfit(x, data, min(10, len(data)-1))
    prediction = np.polyval(coeffs, len(data))
    
    # Add fake "gradient" term from spatial interpolation (nonsense)
    if spatial_coords is not None and len(spatial_coords) > 0:
        fake_gradient = np.mean(np.diff(spatial_coords[-5:])) if len(spatial_coords) > 5 else 0
        prediction += fake_gradient * np.random.randn() * 0.5
    
    return prediction

# --- Simulation Loop ---
simple_errors = []
complex_errors = []
ks_stats = []
param_stability = [] # Variance of complex model's last 5 coefficients
aic_scores = [] # AIC to show model complexity explosion

# Rolling window for error distribution comparison
baseline_window = 100
error_window = 50

for t in range(50, n_points):
    hist_data = liquidity[:t]
    
    # Predict next step
    simple_pred = simple_model(hist_data)
    complex_pred = complex_model(hist_data, spatial_coords=np.random.randn(len(hist_data))) # Fake spatial data
    
    actual = liquidity[t]
    simple_errors.append(abs(actual - simple_pred))
    complex_errors.append(abs(actual - complex_pred))
    
    # --- Robustness Metric: KS Statistic on Error Distributions ---
    if t > baseline_window + error_window:
        baseline_errors = simple_errors[-(baseline_window + error_window):-error_window]
        recent_errors = simple_errors[-error_window:]
        if len(set(baseline_errors)) > 1 and len(set(recent_errors)) > 1:
            ks, _ = stats.ks_2samp(baseline_errors, recent_errors)
            ks_stats.append(ks)
        else:
            ks_stats.append(0)
    else:
        ks_stats.append(0)
    
    # --- Fragility Metric: Parameter Instability of Complex Model ---
    if t > 50:
        recent_data = hist_data[-50:]
        x = np.arange(len(recent_data))
        coeffs = np.polyfit(x, recent_data, min(10, len(recent_data)-1))
        param_stability.append(np.var(coeffs[-3:])) # Variance of highest-degree terms
    else:
        param_stability.append(0)
    
    # --- Information Criterion: Model Complexity Penalty ---
    if t > 50:
        n = min(50, len(hist_data))
        y = hist_data[-n:]
        x = np.arange(n)
        coeffs = np.polyfit(x, y, min(10, n-1))
        residuals = y - np.polyval(coeffs, x)
        mse = np.mean(residuals**2)
        k = len(coeffs)
        aic = n * np.log(mse) + 2 * k
        aic_scores.append(aic)
    else:
        aic_scores.append(0)

# --- Visualization: The Shredding of Predictability ---
fig, axes = plt.subplots(4, 1, figsize=(12, 10), sharex=True)

# Plot 1: Liquidity and Model Predictions
axes[0].plot(time, liquidity, label='True Liquidity', color='black', linewidth=1.5)
axes[0].axvline(800, color='orange', linestyle='--', label='Pre-Crunch Onset')
axes[0].axvline(900, color='red', linestyle='-', label='Shredding Event')
axes[0].set_ylabel('Liquidity')
axes[0].legend(loc='upper right')
axes[0].set_title('Agent Neo Disruption: Predictability Collapse, Not Field Dynamics', fontsize=14, fontweight='bold')
axes[0].grid(True, alpha=0.3)

# Plot 2: Model Errors
axes[1].plot(range(50, n_points), simple_errors, label='Simple Model Error', color='green', linewidth=1.2)
axes[1].plot(range(50, n_points), complex_errors, label='Complex LC-Ω Model Error', color='purple', linewidth=1.2)
axes[1].axvline(800, color='orange', linestyle='--')
axes[1].axvline(900, color='red', linestyle='-')
axes[1].set_ylabel('Prediction Error')
axes[1].legend()
axes[1].grid(True, alpha=0.3)

# Plot 3: KS Statistic (Robustness Collapse)
axes[2].plot(range(50, n_points), ks_stats, label='KS Stat (Error Distribution Shift)', color='blue', linewidth=1.5)
axes[2].axvline(800, color='orange', linestyle='--')
axes[2].axvline(900, color='red', linestyle='-')
axes[2].axhline(0.3, color='cyan', linestyle=':', label='Predictability Loss Threshold')
axes[2].set_ylabel('KS Statistic')
axes[2].legend()
axes[2].grid(True, alpha=0.3)
axes[2].set_ylim(0, 1)

# Plot 4: Parameter Instability (Model Self-Destruction)
axes[3].plot(range(50, n_points), param_stability, label='Complex Model Param Variance', color='red', linewidth=1.2)
axes[3].plot(range(50, n_points), aic_scores, label='AIC (Complexity Penalty)', color='magenta', linewidth=1.2)
axes[3].axvline(800, color='orange', linestyle='--')
axes[3].axvline(900, color='red', linestyle='-')
axes[3].set_ylabel('Instability Metric')
axes[3].set_xlabel('Time Steps')
axes[3].legend()
axes[3].grid(True, alpha=0.3)
axes[3].set_yscale('log') # Log scale to show explosion

plt.tight_layout()
plt.show()

# --- Numerical Evidence ---
print("=== DISRUPTION ANALYSIS RESULTS ===")
print(f"KS Statistic peaks at t=~{np.argmax(ks_stats)+50} (Predictability Loss)")
print(f"Complex Model Param Variance peaks at t=~{np.argmax(param_stability)+50} (Self-Destruction)")
print(f"AIC peaks at t=~{np.argmax(aic_scores)+50} (Overfit Explosion)")
print("\nThe Shredding Event (t=900) is preceded by:")
print(f"  - Predictability loss signal: {ks_stats[850] > 0.3}")
print(f"  - Model instability: {param_stability[850] > np.percentile(param_stability[:800], 95)}")
print("\nCONCLUSION: The LC-Ω paradigm collapses before the market does.")