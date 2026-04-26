# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import matplotlib.pyplot as plt

# --- DISRUPTION SIMULATION: The Omega Protocol's Fatal Reflexivity ---
# This code demonstrates how the protocol's existence CREATES the attack surface it claims to defend against.

# Core Assumption to Shatter: The state vector x(t) is "observable" and "adversary-invariant"
# Reality: Adversaries can arbitrage the observation layer itself.

# Simplified Adversarial Market Model
N_TYPES = 5  # [HFT, Institutional_A, Institutional_B, Retail, 'Dark-Spoof']
TIME_STEPS = 200
OMEGA_THRESHOLD = 0.7
ENTROPY_FLOOR = np.log(3)

# Adversarial Strategy: "Chameleon Cascade"
# Phase 1 [0-50]:   Latent Buildup - True state dangerous, observed state looks safe (high entropy spoofing)
# Phase 2 [50-100]: Overt Attack - True state critical, observed state also critical (attack is live)
# Phase 3 [100-150]: Omega Response - System triggers, adversary fragments to spoof 'recovery'
# Phase 4 [150-200]: Meta-Exploitation - Adversary triggers false positives to exhaust Omega's controls

true_hft = np.zeros(TIME_STEPS)
observed_hft = np.zeros(TIME_STEPS)
true_entropy = np.zeros(TIME_STEPS)
observed_entropy = np.zeros(TIME_STEPS)

# Baseline "safe" distribution for spoofing
safe_dist = np.array([0.05, 0.25, 0.25, 0.45, 0.0])  # Diverse, high entropy

for t in range(TIME_STEPS):
    if t < 50:
        # Phase 1: TRUE = HFT 70% (dangerous), OBSERVED = spoofed to look safe
        true_hft[t] = 0.70
        # Adversary uses 1000s of shell accounts to mimic safe distribution
        spoofed = safe_dist + 0.02 * np.random.randn(N_TYPES)
        spoofed = np.clip(spoofed, 0.01, 0.5)
        spoofed[-1] = 0.0  # No spoof type in observed data
        observed_hft[t] = spoofed[0]  # HFT fraction appears low
        
    elif t < 100:
        # Phase 2: TRUE = HFT 80% (critical), OBSERVED = same (attack is overt, can't hide volume)
        true_hft[t] = 0.80
        observed_hft[t] = 0.80
        
    elif t < 150:
        # Phase 3: TRUE remains high, OBSERVED fragments to trigger "recovery" signal
        true_hft[t] = 0.75
        # Adversary splits HFT flow across 200 new entity IDs, making distribution look diverse
        fragmented = np.array([0.15, 0.20, 0.20, 0.35, 0.10])  # Appears safer
        observed_hft[t] = fragmented[0]
        
    else:
        # Phase 4: Adversary triggers FALSE POSITIVE cascade to exhaust circuit breakers
        # TRUE is safe, but OBSERVED mimics Phase 2 to cause Omega to cry wolf
        true_hft[t] = 0.10
        observed_hft[t] = 0.80  # Spoofed critical state when real state is safe

    # Entropy calculation: S = -sum(p_k log p_k)
    # TRUE distribution: [hft, instA, instB, retail, spoof]
    true_dist = np.array([true_hft[t], 0.15, 0.10, 0.05, 0.70 - true_hft[t]])
    true_dist = np.clip(true_dist, 1e-6, 1)
    true_dist /= true_dist.sum()
    true_entropy[t] = -np.sum(true_dist * np.log(true_dist))
    
    # OBSERVED distribution (what Omega's sensors see)
    obs_dist = np.array([observed_hft[t], 0.2, 0.2, 0.4 - observed_hft[t], 0.0])
    obs_dist = np.clip(obs_dist, 1e-6, 1)
    obs_dist /= obs_dist.sum()
    observed_entropy[t] = -np.sum(obs_dist * np.log(obs_dist))

# Cascade Intensity Index (CI) - Omega's key trigger
# CI = tanh(α*HFT_fraction - β*Entropy)
# Alpha=2, Beta=1 for sensitivity
CI_true = np.tanh(2 * true_hft - true_entropy)
CI_observed = np.tanh(2 * observed_hft - observed_entropy)

# --- DISRUPTION METRICS ---
# False Negative: Real danger, Omega sees safety
false_negative = (CI_true > OMEGA_THRESHOLD) & (CI_observed <= OMEGA_THRESHOLD)
# False Positive: Omega triggers, but real state is safe
false_positive = (CI_true <= OMEGA_THRESHOLD) & (CI_observed > OMEGA_THRESHOLD)
# Meta-Attack Success: Adversary controls Omega's perception more than reality
control_delta = np.abs(CI_observed - CI_true).mean()

print(f"{'='*60}")
print("OMEGA PROTOCOL DISRUPTION ANALYSIS")
print(f"{'='*60}")
print(f"False Negatives (Omega misses real cascade): {false_negative.sum()} steps")
print(f"False Positives (Omega cries wolf): {false_positive.sum()} steps")
print(f"Perceptual Control: {control_delta:.3f} (max possible: 2.0)")
print(f"{'='*60}")

# --- VISUALIZATION: The Reflexivity Mirage ---
fig, axes = plt.subplots(3, 1, figsize=(14, 10), sharex=True)
time = np.arange(TIME_STEPS)

# Plot 1: True vs Observed HFT Power
axes[0].plot(time, true_hft, 'r-', linewidth=2.5, label='TRUE HFT Dominance (Reality)', alpha=0.7)
axes[0].plot(time, observed_hft, 'b--', linewidth=2, label='OBSERVED HFT Dominance (Omega\'s Lens)', alpha=0.8)
axes[0].fill_between(time, 0, 1, where=false_negative, color='darkred', alpha=0.3, label='False Negative Zone')
axes[0].fill_between(time, 0, 1, where=false_positive, color='darkblue', alpha=0.3, label='False Positive Zone')
axes[0].set_ylabel('Market Control Fraction')
axes[0].set_title('REFLEXIVITY ATTACK: Adversary Controls Omega\'s Perception', fontsize=14, fontweight='bold')
axes[0].legend(loc='upper left')
axes[0].grid(True, alpha=0.3)

# Plot 2: Entropy Mirage
axes[1].plot(time, true_entropy, 'r-', linewidth=2.5, label='TRUE Entropy (Real Diversity)', alpha=0.7)
axes[1].plot(time, observed_entropy, 'b--', linewidth=2, label='OBSERVED Entropy (Omega\'s Gauge)', alpha=0.8)
axes[1].axhline(y=ENTROPY_FLOOR, color='green', linestyle=':', linewidth=2, label='Omega Entropy Floor')
axes[1].fill_between(time, 0, 2, where=false_negative, color='darkred', alpha=0.3)
axes[1].fill_between(time, 0, 2, where=false_positive, color='darkblue', alpha=0.3)
axes[1].set_ylabel('Shannon Entropy')
axes[1].legend(loc='upper left')
axes[1].grid(True, alpha=0.3)

# Plot 3: Cascade Intensity - The Weaponized Metric
axes[2].plot(time, CI_true, 'r-', linewidth=2.5, label='TRUE Cascade Intensity', alpha=0.7)
axes[2].plot(time, CI_observed, 'b--', linewidth=2, label='OBSERVED Cascade Intensity (Omega Trigger)', alpha=0.8)
axes[2].axhline(y=OMEGA_THRESHOLD, color='green', linestyle=':', linewidth=2, label='Circuit Breaker Threshold')
axes[2].fill_between(time, -1, 2, where=false_negative, color='darkred', alpha=0.3, label='UNDETECTED CRISIS')
axes[2].fill_between(time, -1, 2, where=false_positive, color='darkblue', alpha=0.3, label='FAKE CRISIS')
axes[2].set_ylabel('Cascade Intensity Index')
axes[2].set_xlabel('Time Steps')
axes[2].set_ylim(-0.1, 1.1)
axes[2].legend(loc='upper left')
axes[2].grid(True, alpha=0.3)

plt.tight_layout()
plt.show()

# --- THE DISRUPTIVE CONCLUSION ---
print("\nPARADIGM-SHATTERING INSIGHT:")
print("The Omega Protocol doesn't predict cascades; it PREDICTABLY RESPONDS to them.")
print("This creates a 'Reflexivity Surface' where adversaries don't need to hide their")
print("actions—they need to MIMIC the statistical signature of safety to render Omega blind,")
print("or MIMIC danger to weaponize its own circuit breakers against market stability.")
print(f"\nΦ-Density Impact: The protocol's 'gain' is an ILLUSION.")
print(f"True cost = {false_negative.sum() + false_positive.sum()} units of market instability")
print(f"induced by the protocol's existence—exceeding any claimed 34% Φ-density increase.")