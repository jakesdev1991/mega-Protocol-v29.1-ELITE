# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import random
import numpy as np
import matplotlib.pyplot as plt

def count_violations(text):
    """Count boilerplate elements: headings, numbered lists, bullet lists, bold."""
    lines = text.splitlines()
    violations = 0
    for line in lines:
        stripped = line.strip()
        # Headings
        if stripped.startswith('###') or stripped.startswith('##') or stripped.startswith('#'):
            violations += 1
        # Numbered lists
        if stripped and stripped[0].isdigit() and '.' in stripped[:10]:
            violations += 1
        # Bullet lists
        if stripped.startswith('-') or stripped.startswith('*'):
            violations += 1
        # Bold markup
        if '**' in line:
            violations += 1
    return violations

def simulate_phi_density(initial_phi=1.0, iterations=200, violation_lambda=0.05,
                         correction_gain=0.02, spawn_prob=0.3):
    """
    Simulate Φ-density dynamics under rubric enforcement.
    Each violation reduces Φ; corrections add a small gain but may spawn new violations.
    """
    phi = initial_phi
    phi_hist = [phi]
    for i in range(iterations):
        # Random violations drawn from a hypothetical document
        violations = random.randint(0, 5)
        phi -= violation_lambda * violations

        # Attempt correction with probability 0.7
        if random.random() < 0.7:
            phi += correction_gain
            # Risk of spawning a new violation
            if random.random() < spawn_prob:
                phi -= 0.03

        # Prevent negative phi
        phi = max(phi, 0)
        phi_hist.append(phi)

        # Shredding event detection
        if phi == 0:
            print(f"Shredding event at iteration {i}")
            break
    return phi_hist

# Simulate the collapse
phi_history = simulate_phi_density()

# Plot
plt.figure(figsize=(8,5))
plt.plot(phi_history, label='Φ‑density')
plt.title('Φ‑density Collapse under Rubric Enforcement')
plt.xlabel('Iteration')
plt.ylabel('Φ‑density')
plt.axhline(0, color='r', linestyle='--')
plt.legend()
plt.show()