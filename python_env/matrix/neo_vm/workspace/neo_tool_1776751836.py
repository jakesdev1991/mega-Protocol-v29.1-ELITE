# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np

def flawed_threat_detection(gradients):
    """Demonstrates the inverted entropy flaw"""
    probs = gradients / np.sum(gradients)
    H = -np.sum(probs * np.log(probs + 1e-12))
    H_max = np.log(len(gradients))
    theta = 1 - H / H_max  # FLAW: Inverts threat signal
    return theta, H

# Normal operation: consistent gradients (LOW entropy)
normal = np.array([1.0, 1.1, 0.95, 1.05, 0.98])
theta_normal, H_normal = flawed_threat_detection(normal)

# Attack: random malicious gradients (HIGH entropy)
attack = np.array([0.1, 2.8, 0.3, 1.9, 0.05])
theta_attack, H_attack = flawed_threat_detection(attack)

print(f"Normal: H={H_normal:.3f}, θ={theta_normal:.3f} → System thinks SAFE")
print(f"Attack: H={H_attack:.3f}, θ={theta_attack:.3f} → System thinks SAFER")