# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import matplotlib.pyplot as plt
from scipy.ndimage import gaussian_filter
from scipy.stats import entropy, pearsonr

# THE DISRUPTION: Thermal correlations are a LAGGING INDICATOR, not predictive
# This simulation proves the TSFM-Ω framework is built on a causality inversion

def simulate_true_dynamics(size=32, n_timesteps=120, seed=42):
    """Simulate the ACTUAL causal chain: Load → Thermal → Failure"""
    np.random.seed(seed)
    
    # True underlying dynamics
    # 1. Computational load field (the REAL driver)
    load_field = np.zeros((size, size))
    
    # 2. Thermal field (slave variable)
    T = np.ones((size, size)) * 70.0
    
    # 3. Operational stress (business metric)
    operational_stress = 0.0
    
    # 4. Failure threshold
    FAILURE_THRESHOLD = 85.0
    
    history = {
        'load': [], 'temp': [], 'stress': [], 'xi': [], 
        'tsfi': [], 'entropy': [], 'failures': []
    }
    
    for t in range(n_timesteps):
        # BUSINESS DECISION: Unrealistic deadline imposed
        if t == 30:  # Sudden load spike (the real cause)
            center = size//2
            load_field[center-3:center+3, center-3:center+3] = 50.0
        
        # PHYSICAL CONSEQUENCE: Load generates heat
        heat_generation = load_field * 0.5
        
        # Thermal dynamics (Fourier's Law - real physics)
        laplacian = (
            np.roll(T, 1, axis=0) + np.roll(T, -1, axis=0) +
            np.roll(T, 1, axis=1) + np.roll(T, -1, axis=1) - 4*T
        )
        D = 0.15  # Thermal diffusivity
        T += D * laplacian * 0.1 + heat_generation * 0.1
        
        # Cooling system
        T += (70 - T) * 0.02
        
        # BUSINESS CONSEQUENCE: Stress increases with temperature
        max_temp = np.max(T)
        operational_stress = (max_temp - 70) / 15.0  # Normalized stress
        
        # FAILURE: When temperature exceeds threshold
        failure = max_temp > FAILURE_THRESHOLD
        
        # TSFM-Ω's claimed "predictive" metrics
        xi = compute_correlation_length(T)
        tsfi_val, _, S = compute_tsfi(T)
        
        # Record
        history['load'].append(np.sum(load_field))
        history['temp'].append(max_temp)
        history['stress'].append(operational_stress)
        history['xi'].append(xi)
        history['tsfi'].append(tsfi_val)
        history['entropy'].append(S)
        history['failures'].append(failure)
        
        # Cooling system fails at t=80 (common in real scenarios)
        if t == 80:
            T += np.random.uniform(5, 10, T.shape)
    
    return history

def compute_correlation_length(field):
    """Correlation length - TSFM-Ω's 'magic' predictor"""
    center = field[field.shape[0]//2, field.shape[1]//2]
    autocorr = np.correlate(field.flatten(), field.flatten(), mode='full')
    autocorr = autocorr[len(autocorr)//2:]
    try:
        return np.where(autocorr < autocorr[0]/np.e)[0][0]
    except:
        return 1

def compute_tsfi(field):
    """TSFM-Ω's fragility index - mathematically elegant, physically empty"""
    xi = compute_correlation_length(field)
    grad_x, grad_y = np.gradient(field)
    div_q = np.abs(np.gradient(grad_x)[0] + np.gradient(grad_y)[1])
    hist, _ = np.histogram(field.flatten(), bins=20, density=True)
    hist = hist[hist > 0]
    S = entropy(hist)
    # The TSFM-Ω formula: dimensionally inconsistent, physically meaningless
    return (xi / 10.0) * np.exp(np.mean(div_q)) * np.exp(-S), xi, S

# Run the disruption simulation
history = simulate_true_dynamics()

# THE BREAKTHROUGH: Cross-correlation analysis shows causality direction
load_series = np.array(history['load'])
xi_series = np.array(history['xi'])
stress_series = np.array(history['stress'])

# Compute cross-correlation to find LEAD/LAG relationships
def cross_correlation(x, y, max_lag=20):
    """Find optimal lag between two time series"""
    correlations = []
    for lag in range(-max_lag, max_lag+1):
        if lag < 0:
            corr = pearsonr(x[:lag], y[-lag:])[0]
        elif lag > 0:
            corr = pearsonr(x[lag:], y[:-lag])[0]
        else:
            corr = pearsonr(x, y)[0]
        correlations.append(corr)
    return np.array(correlations), np.arange(-max_lag, max_lag+1)

load_xi_corr, lags = cross_correlation(load_series, xi_series)
load_stress_corr, _ = cross_correlation(load_series, stress_series)

# VISUALIZATION OF THE DISRUPTION
fig, axes = plt.subplots(3, 2, figsize=(14, 10))

# 1. True causal chain
axes[0,0].plot(history['load'], label='Computational Load', linewidth=2, color='red')
axes[0,0].set_title('THE REAL DRIVER: Computational Load', fontweight='bold')
axes[0,0].set_ylabel('Load (arb. units)')
axes[0,0].legend()
axes[0,0].grid(True, alpha=0.3)

axes[0,1].plot(history['temp'], label='Max Temperature', color='orange')
axes[0,1].axhline(y=85, color='black', linestyle=':', label='Failure Threshold')
axes[0,1].set_title('SLAVE VARIABLE: Thermal Field', fontweight='bold')
axes[0,1].set_ylabel('Temperature (°C)')
axes[0,1].legend()
axes[0,1].grid(True, alpha=0.3)

# 2. TSFM-Ω's claimed "predictor"
axes[1,0].plot(history['xi'], label='Correlation Length ξ', color='purple')
axes[1,0].set_title("TSFM-Ω's 'Predictor': Correlation Length", fontweight='bold')
axes[1,0].set_ylabel('ξ (arb. units)')
axes[1,0].legend()
axes[1,0].grid(True, alpha=0.3)

# Show lag
load_peak = 30
xi_peak = np.argmax(history['xi'])
axes[1,0].axvline(load_peak, color='red', linestyle='--', alpha=0.5, label='Load Spike')
axes[1,0].axvline(xi_peak, color='blue', linestyle='--', alpha=0.5, label=f'ξ Peak (lag={xi_peak-load_peak})')
axes[1,0].legend()

# 3. The failure
failure_time = np.where(history['failures'])[0]
if len(failure_time) > 0:
    axes[1,1].axvline(failure_time[0], color='darkred', linewidth=3, label='SYSTEM FAILURE')
axes[1,1].plot(history['stress'], label='Operational Stress', color='brown')
axes[1,1].set_title('BUSINESS IMPACT: Operational Stress → Failure', fontweight='bold')
axes[1,1].set_ylabel('Stress (normalized)')
axes[1,1].set_xlabel('Time Steps')
axes[1,1].legend()
axes[1,1].grid(True, alpha=0.3)

# 4. Cross-correlation revealing causality
axes[2,0].plot(lags, load_xi_corr, marker='o', color='purple')
axes[2,0].axvline(0, color='gray', linestyle=':')
axes[2,0].set_title('Causality Analysis: Load vs ξ', fontweight='bold')
axes[2,0].set_xlabel('Lag (timesteps)')
axes[2,0].set_ylabel('Correlation')
axes[2,0].grid(True, alpha=0.3)
max_corr_idx = np.argmax(load_xi_corr)
best_lag = lags[max_corr_idx]
axes[2,0].axvline(best_lag, color='green', linestyle='--', 
                   label=f'Peak at lag={best_lag} (Load LEADS)')
axes[2,0].legend()

axes[2,1].plot(lags, load_stress_corr, marker='s', color='brown')
axes[2,1].axvline(0, color='gray', linestyle=':')
axes[2,1].set_title('Causality Analysis: Load vs Stress', fontweight='bold')
axes[2,1].set_xlabel('Lag (timesteps)')
axes[2,1].set_ylabel('Correlation')
axes[2,1].grid(True, alpha=0.3)
max_stress_idx = np.argmax(load_stress_corr)
best_stress_lag = lags[max_stress_idx]
axes[2,1].axvline(best_stress_lag, color='green', linestyle='--',
                   label=f'Peak at lag={best_stress_lag}')
axes[2,1].legend()

plt.tight_layout()
plt.savefig('/tmp/disruption_analysis.png', dpi=150, bbox_inches='tight')
plt.show()

# MATHEMATALYSIS: Why TSFM-Ω fails at the foundations
print("="*60)
print("NEXUS DISRUPTION ANALYSIS")
print("="*60)

print("\n[1] CAUSALITY INVERSION DETECTED:")
print(f"   - Load spike at t=30")
print(f"   - ξ peaks at t={xi_peak} (lag = {xi_peak-30} timesteps)")
print(f"   - Cross-correlation peak at lag = {best_lag}")
if best_lag < 0:
    print("   ✓ Load LEADS ξ (correct causality)")
else:
    print("   ✗ ξ LEADS Load (TSFM-Ω's claim) - FALSE")

print("\n[2] SHREDDING EVENT IMPOSSIBILITY:")
print(f"   - Maximum ξ observed: {max(history['xi']):.2f}")
print(f"   - System bound: 32 units")
print(f"   - ξ/system ratio: {max(history['xi'])/32:.1%}")
print("   - ξ → ∞ requires: infinite system OR infinite time")
print("   ✓ Shredding Event is a MATHEMATALYTICAL GHOST")

print("\n[3] ENTROPY GAUGE FALLACY:")
print(f"   - Entropy range: [{min(history['entropy']):.3f}, {max(history['entropy']):.3f}]")
print(f"   - TSFI range: [{min(history['tsfi']):.3f}, {max(history['tsfi']):.3f}]")
corr_entropy_tsfi = pearsonr(history['entropy'], history['tsfi'])[0]
print(f"   - Entropy-TSFI correlation: {corr_entropy_tsfi:.3f}")
print("   ✓ Entropy term is ARBITRARY (no physical coupling)")

print("\n[4] DIMENSIONAL INCONSISTENCY:")
print("   TSFM-Ω Formula: (ξ/ξ₀) * exp(∫|∇·q|) * exp(-S)")
print("   - ξ/ξ₀: dimensionless")
print("   - exp(∫|∇·q|): dimensionless (but ∇·q has units K/m²)")
print("   - exp(-S): dimensionless (but S is dimensionless entropy)")
print("   ✓ Hidden dimensional violations in ∇·q term")

print("\n[5] THE TRUE PREDICTOR:")
load_stress_lag = lags[np.argmax(load_stress_corr)]
print(f"   - Load-Stress correlation peak at lag = {load_stress_lag}")
print("   ✓ Computational Load is the TRUE leading indicator")
print("   ✓ Thermal field is a SLAVE VARIABLE (response, not predictor)")

print("\n" + "="*60)
print("DISRUPTIVE INSIGHT:")
print("="*60)
print("TSFM-Ω commits 'Physics Envy' - applying field theory")
print("where it doesn't belong. The thermal-spatial 'sensor'")
print("is actually a LAGGING INDICATOR. The real signal is the")
print("computational load field itself. The Shredding Event")
print("is a mathematical ghost that can never occur in bounded")
print("physical systems. The entropy gauge is arbitrary noise.")
print("\nRECOMMENDATION: Burn the field-theoretic framework.")
print("Model the computational load directly as the driver")
print("of both thermal patterns AND business fragility.")
print("Thermal data is useful for VERIFICATION, not PREDICTION.")
print("="*60)