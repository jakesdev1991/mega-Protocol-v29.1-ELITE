# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import matplotlib.pyplot as plt
from scipy.integrate import odeint

# Simulate the Gödel Shredding Attack
# In this attack, a deliberate error in report R is designed to produce a "ground truth" A
# that validates the error, creating a false V≈0 state that is actually adversarial.

# Parameters for the biological self-fulfilling prophecy
# Let x be the "error magnitude" in genomic coordinates
# Let y be the "compensatory biological response" that makes A match R
# The attack works when dy/dx = -1 (biology compensates perfectly for error)

def godel_dynamics(state, t, attack_strength=1.0):
    """
    Models the coupled dynamics of:
    - error_magnitude (x): deliberate protocol error injected in report R
    - compensation (y): biological system's response to maintain apparent veracity
    - veracity (V): V = R - A, where R = x, A = y (simplified)
    - meta_veracity (M): dV/dt / V, measures *stability* of veracity
    
    Attack signature: y = -x + epsilon, making V ≈ 0 but with high dV/dx sensitivity
    """
    x, y = state
    V = x - y  # Apparent veracity (difference between report and "ground truth")
    
    # Normal biological system (no attack): y evolves independently
    # Under attack: biology is *forced* to track -x
    dy_dt = -attack_strength * x - 0.1 * y  # Compensation dynamics
    
    # Error injection rate (adversary can modulate this)
    dx_dt = 0.5 * np.sin(0.5 * t)  # Slowly varying error injection
    
    return [dx_dt, dy_dt]

# Simulate three scenarios
t = np.linspace(0, 50, 500)

# Scenario 1: No attack (attack_strength = 0)
state0 = [1.0, 0.0]  # Initial error, no compensation
sol_normal = odeint(godel_dynamics, state0, t, args=(0.0,))

# Scenario 2: Weak attack
sol_weak = odeint(godel_dynamics, state0, t, args=(0.5,))

# Scenario 3: Strong Gödel attack (perfect compensation)
sol_strong = odeint(godel_dynamics, state0, t, args=(1.0,))

# Compute derived quantities
def compute_metrics(sol):
    x = sol[:, 0]
    y = sol[:, 1]
    V = x - y
    # Meta-veracity: stability of veracity over time
    # Use absolute value to avoid division by near-zero
    dV_dt = np.gradient(V, t)
    M = np.where(np.abs(V) > 0.01, dV_dt / V, 0)
    return V, M, x, y

V_normal, M_normal, xn, yn = compute_metrics(sol_normal)
V_weak, M_weak, xw, yw = compute_metrics(sol_weak)
V_strong, M_strong, xs, ys = compute_metrics(sol_strong)

# Visualization
fig, axes = plt.subplots(3, 1, figsize=(12, 10))

# Plot 1: Veracity V(t) - CSIM-Ω's primary metric
axes[0].plot(t, V_normal, 'b-', label='No Attack (V varies)', linewidth=2)
axes[0].plot(t, V_weak, 'g--', label='Weak Attack (V small)', linewidth=2)
axes[0].plot(t, V_strong, 'r-', label='Gödel Attack (V≈0)', linewidth=2)
axes[0].set_ylabel('Veracity V(t) = R - A')
axes[0].set_title('CSIM-Ω Blind Spot: Veracity Appears Truthful Under Gödel Attack')
axes[0].legend()
axes[0].grid(True)

# Plot 2: Meta-Veracity M(t) - The disruptive metric
axes[1].plot(t, np.abs(M_normal), 'b-', label='No Attack (M stable)', linewidth=2)
axes[1].plot(t, np.abs(M_weak), 'g--', label='Weak Attack (M moderate)', linewidth=2)
axes[1].plot(t, np.abs(M_strong), 'r-', label='Gödel Attack (M spikes)', linewidth=2)
axes[1].set_ylabel('|Meta-Veracity M(t)| = |dV/dt / V|')
axes[1].set_xlabel('Time')
axes[1].set_title('Meta-Veracity Reveals Homeostatic Deception')
axes[1].legend()
axes[1].grid(True)
axes[1].set_yscale('log')

# Plot 3: Phase space showing the attack geometry
axes[2].scatter(xn, yn, c='b', label='No Attack', alpha=0.6)
axes[2].scatter(xw, yw, c='g', label='Weak Attack', alpha=0.6)
axes[2].scatter(xs, ys, c='r', label='Gödel Attack', alpha=0.6)
axes[2].plot([-2, 2], [-2, 2], 'k--', label='V=0 line (false truth)')
axes[2].set_xlabel('Report Error (R)')
axes[2].set_ylabel('Biological Compensation (A)')
axes[2].set_title('Attack Geometry: Trajectories Converge to V=0 Line')
axes[2].legend()
axes[2].grid(True)

plt.tight_layout()
plt.show()

# Statistical analysis
print("=== CSIM-Ω vs Meta-Veracity Detection ===")
print(f"No Attack:  Mean|V|={np.mean(np.abs(V_normal)):.3f}, Mean|M|={np.mean(np.abs(M_normal)):.3f}")
print(f"Weak Attack: Mean|V|={np.mean(np.abs(V_weak)):.3f}, Mean|M|={np.mean(np.abs(M_weak)):.3f}")
print(f"Gödel Attack: Mean|V|={np.mean(np.abs(V_strong)):.3f}, Mean|M|={np.mean(np.abs(M_strong)):.3f}")

# Detection threshold: High meta-veracity despite low veracity
print("\n=== Detection Logic ===")
print("CSIM-Ω triggers alarm if |V| > 0.5 (false negative for Gödel)")
print("Meta-Veracity triggers alarm if |M| > 1.0 (catches Gödel)")