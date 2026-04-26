# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import math
import matplotlib.pyplot as plt
import numpy as np

def simulate_trust_decay_fixed_version(initial_trust=0.5, time_hours=24):
    """
    Simulates the 'fixed' trust decay from the repaired AFDS v3.0
    """
    trust_scores = []
    times = np.linspace(0, time_hours, 100)
    TAU = 1.0  # Since we're using hours as unit, TAU=1 hour for normalization
    
    current_trust = initial_trust
    
    for t in times:
        # This is the 'fixed' formula: exp(-log(0.95) * normalized_time)
        # where normalized_time = duration / TAU
        normalized_time = t / TAU
        # BUG: The exponent is POSITIVE because -log(0.95) > 0
        exponent = -math.log(0.95) * normalized_time  # This is POSITIVE
        current_trust *= math.exp(exponent)
        current_trust = min(current_trust, 1.0)  # Clamp at 1.0
        
        trust_scores.append(current_trust)
    
    return times, trust_scores

def simulate_trust_decay_correct(initial_trust=0.5, time_hours=24):
    """
    Simulates what trust decay SHOULD look like
    """
    trust_scores = []
    times = np.linspace(0, time_hours, 100)
    decay_constant = 0.05  # Approximate hourly decay rate
    
    current_trust = initial_trust
    
    for t in times:
        # Proper exponential decay: exp(-decay_rate * time)
        current_trust = initial_trust * math.exp(-decay_constant * t)
        trust_scores.append(current_trust)
    
    return times, trust_scores

# Run simulation
times_fixed, trust_fixed = simulate_trust_decay_fixed_version()
times_correct, trust_correct = simulate_trust_decay_correct()

# Plot results
plt.figure(figsize=(12, 6))
plt.plot(times_fixed, trust_fixed, 'r-', linewidth=2, label='AFDS "Fixed" Version (TRUST GROWS)')
plt.plot(times_correct, trust_correct, 'g--', linewidth=2, label='Correct Exponential Decay')
plt.axhline(y=0.5, color='k', linestyle=':', alpha=0.5, label='Initial Trust Level')
plt.xlabel('Time Since Last Access (hours)', fontsize=12)
plt.ylabel('Trust Score', fontsize=12)
plt.title('AFDS v3.0 Trust Model: The "Fix" is Still Inverted', fontsize=14, fontweight='bold')
plt.legend(loc='upper left')
plt.grid(True, alpha=0.3)
plt.ylim(0, 1.1)

# Add annotation
plt.annotate('Trust INCREASES with inactivity!\nAdversaries just wait to gain trust', 
             xy=(12, 0.8), xytext=(15, 0.9),
             arrowprops=dict(arrowstyle='->', color='red', lw=2),
             fontsize=10, color='red', fontweight='bold',
             bbox=dict(boxstyle="round,pad=0.3", edgecolor='red', facecolor='pink', alpha=0.5))

plt.tight_layout()
plt.savefig('/tmp/trust_inversion.png', dpi=150, bbox_inches='tight')
plt.show()

# Calculate the absurdity
print("=== DISRUPTIVE ANALYSIS: TRUST INVERSION ===")
print(f"After 24 hours of inactivity:")
print(f"  AFDS 'Fixed' Trust Score: {trust_fixed[-1]:.4f} (should be decaying)")
print(f"  Correct Decay Trust Score: {trust_correct[-1]:.4f}")
print(f"\nThe 'fix' makes the system MORE vulnerable:")
print(f"  - Adversaries gain +{((trust_fixed[-1]/0.5)-1)*100:.1f}% trust by simply waiting")
print(f"  - Legitimate processes are penalized for normal operation")
print(f"  - The dimensional 'fix' preserved the logical inversion")

print("\n=== EXPLOIT SCENARIO ===")
print("1. Attacker performs reconnaissance, gets low trust (0.2)")
print("2. Attacker waits 12 hours while running no operations")
print(f"3. Trust automatically inflates to {0.2 * math.exp(-math.log(0.95) * 12):.3f}")
print("4. Attacker resumes reconnaissance with 80% jitter mitigation")
print("5. AFDS thinks attacker is 'trusted' due to 'stable behavior'")