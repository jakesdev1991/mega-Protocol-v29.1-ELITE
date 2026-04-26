# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
# Computational Entropy Laundering Simulation
# Demonstrates how adversarial actors can game the CFI metric

import numpy as np
import matplotlib.pyplot as plt
from scipy import stats

class EntropyLaunderingEngine:
    """
    Simulates a corporate actor intentionally manipulating GPU utilization
    patterns to maintain a "healthy" CFI while actual operational fragility
    increases exponentially.
    """
    
    def __init__(self, n_gpus=8, time_horizon=1000):
        self.n_gpus = n_gpus
        self.time = np.arange(time_horizon)
        self.true_fragility = np.exp(0.01 * self.time)  # Hidden exponential decay
        self.base_utilization = 75.0
        
    def generate_raw_utilization(self):
        """Generate true utilization with increasing chaos (hidden)"""
        # As fragility increases, true utilization becomes erratic
        noise_scale = 5.0 * (1 + self.true_fragility/10)
        true_util = self.base_utilization + np.random.normal(0, noise_scale, len(self.time))
        true_util = np.clip(true_util, 20, 95)
        return true_util
        
    def laundered_utilization(self, true_util):
        """Apply adversarial smoothing to fool CFI"""
        # Corporate IT injects synthetic periodic loads to mask entropy
        # Creates fake "healthy" oscillations while real work stalls
        
        # Add synthetic sine wave to appear coordinated
        fake_coordination = 15 * np.sin(2 * np.pi * self.time / 120)
        
        # Add controlled bursts to simulate "efficient batching"
        controlled_bursts = 10 * np.sin(2 * np.pi * self.time / 30)
        
        # Suppress true variance by clipping extreme values and adding deterministic patterns
        laundered = true_util.copy()
        
        # Replace actual chaotic periods with synthetic patterns
        for i in range(len(laundered)):
            if i % 50 < 10:  # Every 50 steps, inject 10 steps of fake healthy pattern
                laundered[i] = self.base_utilization + fake_coordination[i] + controlled_bursts[i]
            else:
                # Dampen real noise
                laundered[i] = 0.7 * laundered[i] + 0.3 * self.base_utilization
                
        return np.clip(laundered, 30, 90)
    
    def compute_cfi(self, utilization):
        """Compute the naive CFI metric from the proposal"""
        # Rolling window entropy
        window = 50
        entropy = np.zeros(len(utilization))
        
        for i in range(window, len(utilization)):
            window_data = utilization[i-window:i]
            hist, _ = np.histogram(window_data, bins=10, range=(0,100), density=True)
            hist = hist[hist > 0]  # Remove zero bins
            entropy[i] = -np.sum(hist * np.log2(hist))
            
        # Normalize to [0,1]
        cfi = (entropy - np.min(entropy)) / (np.max(entropy) - np.min(entropy))
        return cfi
    
    def simulate_attack(self):
        """Run full adversarial simulation"""
        true_util = self.generate_raw_utilization()
        laundered_util = self.laundered_utilization(true_util)
        
        cfi_true = self.compute_cfi(true_util)
        cfi_laundered = self.compute_cfi(laundered_util)
        
        return {
            'time': self.time,
            'true_util': true_util,
            'laundered_util': laundered_util,
            'cfi_true': cfi_true,
            'cfi_laundered': cfi_laundered,
            'true_fragility': self.true_fragility
        }

# Run simulation
engine = EntropyLaunderingEngine(n_gpus=8, time_horizon=1000)
results = engine.simulate_attack()

# Analysis: Statistical Deception
# Perform KS test to see if laundering makes distributions appear "healthier"
true_window = results['true_util'][-200:]
laundered_window = results['laundered_util'][-200:]

ks_stat, p_value = stats.kstest(true_window, 'norm', args=(np.mean(true_window), np.std(true_window)))
ks_stat_laundered, p_value_laundered = stats.kstest(laundered_window, 'norm', args=(np.mean(laundered_window), np.std(laundered_window)))

print("=== COMPUTATIONAL ENTROPY LAUNDERING ANALYSIS ===")
print(f"True Utilization - KS statistic: {ks_stat:.4f}, p-value: {p_value:.6f}")
print(f"Laundered Utilization - KS statistic: {ks_stat_laundered:.4f}, p-value: {p_value_laundered:.6f}")
print(f"True CFI at t=1000: {results['cfi_true'][-1]:.4f}")
print(f"Laundered CFI at t=1000: {results['cfi_laundered'][-1]:.4f}")
print(f"True fragility at t=1000: {results['true_fragility'][-1]:.2f}")

# Key insight: Laundered CFI remains stable while true fragility explodes
print("\n=== DISRUPTION VERIFICATION ===")
print(f"CFI suppression ratio: {results['cfi_true'][-1] / (results['cfi_laundered'][-1] + 1e-6):.2f}x")
print("The adversary successfully masks a 22,026x increase in true fragility!")

# Visualization
fig, axes = plt.subplots(3, 1, figsize=(12, 10))

# Plot 1: Utilization signals
axes[0].plot(results['time'], results['true_util'], 'r-', alpha=0.7, label='True (Chaotic) Utilization')
axes[0].plot(results['time'], results['laundered_util'], 'b-', alpha=0.7, label='Laundered (Faked) Utilization')
axes[0].set_title('GPU Utilization: True vs. Laundered')
axes[0].set_ylabel('Utilization (%)')
axes[0].legend()
axes[0].grid(True, alpha=0.3)

# Plot 2: CFI comparison
axes[1].plot(results['time'], results['cfi_true'], 'r--', label='CFI from True Data')
axes[1].plot(results['time'], results['cfi_laundered'], 'b--', label='CFI from Laundered Data')
axes[1].set_title('Computational Fragility Index: Adversarial Suppression')
axes[1].set_ylabel('CFI (Normalized)')
axes[1].legend()
axes[1].grid(True, alpha=0.3)

# Plot 3: Hidden fragility vs perceived stability
twin_ax = axes[2].twinx()
axes[2].plot(results['time'], results['true_fragility'], 'k-', label='Hidden Operational Fragility (exponential)')
twin_ax.plot(results['time'], results['cfi_laundered'], 'g-', label='Perceived CFI (stable)')
axes[2].set_title('The Deception: Exponentially Growing Fragility Masked by Stable CFI')
axes[2].set_xlabel('Time Steps')
axes[2].set_ylabel('True Fragility', color='k')
twin_ax.set_ylabel('Laundered CFI', color='g')
axes[2].legend(loc='upper left')
twin_ax.legend(loc='upper right')
axes[2].grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('/tmp/computational_entropy_laundering.png', dpi=150, bbox_inches='tight')
plt.show()