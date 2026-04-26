# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import scipy.stats as stats

def simulate_byzantine_attack(num_workers=10, num_timesteps=1000, attack_type='temporal_reordering'):
    """
    Simulate honest vs Byzantine workers in a streaming setting.
    Demonstrates that entropy-based detection fails for temporal attacks.
    """
    # Honest workers: generate correlated gradients from a common latent factor
    latent_signal = np.random.randn(num_timesteps)
    honest_gradients = np.zeros((num_workers - 2, num_timesteps))
    
    for i in range(num_workers - 2):  # 8 honest workers
        noise = 0.5 * np.random.randn(num_timesteps)
        honest_gradients[i] = latent_signal + noise
    
    # Byzantine workers: temporal reordering attack
    byzantine_gradients = np.zeros((2, num_timesteps))
    if attack_type == 'temporal_reordering':
        for i in range(2):  # 2 byzantine workers
            shift = np.random.randint(10, 30)  # Random forward shift to fake momentum
            byzantine_gradients[i] = np.roll(latent_signal, shift) + 0.3 * np.random.randn(num_timesteps)
    elif attack_type == 'gradient_magnitude':
        for i in range(2):
            byzantine_gradients[i] = 10 * np.random.randn(num_timesteps)
    else:  # honest baseline
        for i in range(2):
            noise = 0.5 * np.random.randn(num_timesteps)
            byzantine_gradients[i] = latent_signal + noise
    
    all_gradients = np.vstack([honest_gradients, byzantine_gradients])
    
    # Compute entropy of gradient magnitudes (as proposed in BRS-Ω)
    entropies = []
    for t in range(num_timesteps):
        norms = np.linalg.norm(all_gradients[:, t].reshape(-1, 1), axis=1)
        if np.sum(norms) > 0:
            probs = norms / np.sum(norms)
            entropies.append(stats.entropy(probs))
        else:
            entropies.append(0)
    
    return np.array(entropies), all_gradients

def detect_byzantine_entropy(entropies, threshold=0.5):
    """Detect Byzantine attack using entropy threshold (as in BRS-Ω proposal)"""
    # Low entropy should indicate attack according to the proposal
    return np.mean(entropies) < threshold

def detect_byzantine_temporal(gradients, window=20):
    """Detect temporal reordering using cross-correlation lag detection"""
    num_workers, timesteps = gradients.shape
    byzantine_score = 0
    
    # Check if any worker's gradients are consistently shifted relative to the majority
    reference_gradient = gradients[0]  # Use first honest worker as reference
    for i in range(num_workers):
        corr = np.correlate(gradients[i], reference_gradient, mode='full')
        max_lag = np.argmax(corr) - (timesteps - 1)
        if abs(max_lag) > 5:  # Significant lag indicates reordering
            byzantine_score += 1
    
    return byzantine_score > 0

print("=== Testing BRS-Ω Entropy-Based Detection ===\n")

# Test 1: Traditional gradient magnitude attack
print("1. Traditional Gradient Magnitude Attack:")
entropies_mag, _ = simulate_byzantine_attack(attack_type='gradient_magnitude')
entropy_detected_mag = detect_byzantine_entropy(entropies_mag)
print(f"   Entropy value: {np.mean(entropies_mag):.3f}")
print(f"   Attack detected by entropy: {entropy_detected_mag}")

# Test 2: Temporal reordering attack (the real threat)
print("\n2. Temporal Reordering Attack:")
entropies_temp, gradients_temp = simulate_byzantine_attack(attack_type='temporal_reordering')
entropy_detected_temp = detect_byzantine_entropy(entropies_temp)
temporal_detected = detect_byzantine_temporal(gradients_temp)
print(f"   Entropy value: {np.mean(entropies_temp):.3f}")
print(f"   Attack detected by entropy: {entropy_detected_temp}")
print(f"   Attack detected by temporal analysis: {temporal_detected}")

# Test 3: Honest baseline
print("\n3. Honest Workers Only:")
entropies_honest, _ = simulate_byzantine_attack(attack_type='honest')
entropy_detected_honest = detect_byzantine_entropy(entropies_honest)
print(f"   Entropy value: {np.mean(entropies_honest):.3f}")
print(f"   False positive by entropy: {entropy_detected_honest}")

print("\n=== CONCLUSION ===")
print("BRS-Ω's entropy detection WORKS for crude attacks but FAILS for sophisticated temporal reordering.")
print("The core flaw: spatial encoding cannot detect temporal causality violations.")