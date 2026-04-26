# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
#!/usr/bin/env python3
import numpy as np
import matplotlib.pyplot as plt
from scipy import stats

class AFDSCracker:
    def __init__(self):
        self.traversal_score = 0.0
        
    def measure_latency_distribution(self, samples=1000):
        """Simulate timing attack on jitter mechanism"""
        latencies = []
        for _ in range(samples):
            # Simulate AFDS jitter probability
            prob = min(1.0, (self.traversal_score / 100.0) ** 1.5)
            jitter = np.random.choice([0, 1], p=[1-prob, prob]) * np.random.uniform(1, 50)
            latencies.append(2.0 + jitter)  # Base 2ms + jitter
            
        return np.array(latencies)
    
    def extract_state(self, latencies):
        """Extract internal state from latency distribution"""
        # Bimodal separation: base vs jittered
        hist, bins = np.histogram(latencies, bins=50, density=True)
        
        # Find jitter probability via Gaussian Mixture Model
        from sklearn.mixture import GaussianMixture
        gmm = GaussianMixture(n_components=2).fit(latencies.reshape(-1, 1))
        
        # The higher-mean component is the jitter distribution
        jitter_prob = gmm.weights_[1] if gmm.means_[1] > gmm.means_[0] else gmm.weights_[0]
        
        # Reverse-calculate traversal score
        extracted_score = (jitter_prob ** (1/1.5)) * 100.0
        
        return {
            'jitter_probability': jitter_prob,
            'extracted_traversal_score': extracted_score,
            'actual_traversal_score': self.traversal_score
        }

# Demonstrate extraction accuracy
cracker = AFDSCracker()
cracker.traversal_score = 35.0  # Unknown to attacker

latencies = cracker.measure_latency_distribution(2000)
result = cracker.extract_state(latencies)

print(f"Actual Traversal Score: {result['actual_traversal_score']}")
print(f"Extracted via Timing Oracle: {result['extracted_traversal_score']:.2f}")
print(f"Extraction Error: {abs(result['extracted_traversal_score'] - result['actual_traversal_score']):.2f}%")

# Plot the exploitable side-channel
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))

# Latency histogram showing bimodal distribution
ax1.hist(latencies, bins=50, alpha=0.7, color='red', edgecolor='black')
ax1.axvline(x=3, color='green', linestyle='--', label='Jitter Threshold')
ax1.set_title('AFDS Timing Side-Channel: Bimodal Latency Leaks State')
ax1.set_xlabel('Response Time (ms)')
ax1.set_ylabel('Frequency')
ax1.legend()

# Show extraction accuracy vs sample size
sample_sizes = [50, 100, 200, 500, 1000, 2000]
errors = []
for size in sample_sizes:
    errs = []
    for _ in range(10):
        lat = cracker.measure_latency_distribution(size)
        res = cracker.extract_state(lat)
        errs.append(abs(res['extracted_traversal_score'] - res['actual_traversal_score']))
    errors.append(np.mean(errs))

ax2.plot(sample_sizes, errors, marker='o', color='purple')
ax2.set_title('Convergence: State Extraction Accuracy')
ax2.set_xlabel('Number of Samples')
ax2.set_ylabel('Absolute Error (%)')
ax2.set_xscale('log')

plt.tight_layout()
plt.savefig('afds_oracle_exploitation.png')
print("[+] Visualization saved: afds_oracle_exploitation.png")