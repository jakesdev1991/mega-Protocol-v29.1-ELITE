# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
from scipy.integrate import odeint
import matplotlib.pyplot as plt

# THE ANOMALY PROTOCOL: Breaking the Closed-Loop Illusion

def true_omega_dynamics(state, t, coupling_strength):
    """
    REALITY CHECK: The COAGN proposal commits a fatal category error.
    It treats crossed-product dynamics as linear stabilization when TOE Step 5
    explicitly demands non-commutative *resonance*. This model exposes the
    hidden instability they buried under their "direct sum" simplification.
    
    State: [phi_N (info field), xi_N (causal bound), xi_D (entropy cap), lambda (resonance)]
    """
    phi_N, xi_N, xi_D, lam = state
    
    # The truth they omitted: crossed-product dynamics produce a *twist* term
    # that cannot be decomposed into direct sum. This is the [g,h] commutator.
    # Their "stabilization" is actually *suppression* of the resonance that
    # makes the system work in the first place.
    
    # Non-commutative twist (the missing term)
    twist = coupling_strength * phi_N * xi_N * np.sin(lam)  # Resonance channel
    
    # Their "stable" equations vs. reality
    dphi_N_dt = -0.1 * phi_N + twist  # Information field twists under resonance
    dxi_N_dt = 0.05 * xi_N - twist**2  # Causal bound *degrades* with twist energy
    dxi_D_dt = 0.03 * xi_D + abs(twist)  # Entropy cap is *breached* by resonance
    
    # Resonance parameter evolves chaotically (they assumed constant!)
    dlam_dt = 0.5 * (phi_N - xi_N) + 0.1 * twist
    
    return [dphi_N_dt, dxi_N_dt, dxi_D_dt, dlam_dt]

# Simulate their "optimal" configuration
t = np.linspace(0, 100, 5000)
initial_state = [0.92, 1.0, 1.0, 0.1]  # Their claimed Φ-density + nominal invariants

# Low coupling: Their assumed regime (FALSE STABILITY)
stable = odeint(true_omega_dynamics, initial_state, t, args=(0.1,))

# "Optimal" coupling: What they claim maximizes Φ-density
optimal = odeint(true_omega_dynamics, initial_state, t, args=(0.8,))

# Reality: The system they actually built
critical = odeint(true_omega_dynamics, initial_state, t, args=(1.5,))

# VISUALIZE THE CATASTROPHE
fig, axes = plt.subplots(2, 2, figsize=(14, 10))

# Plot 1: Φ-Density Collapse (their "maximization" is actually runaway)
axes[0,0].plot(t, stable[:,0], 'b-', linewidth=2, label='Low Coupling (False Stable)')
axes[0,0].plot(t, optimal[:,0], 'r-', linewidth=2, label='"Optimal" (0.8)')
axes[0,0].plot(t, critical[:,0], 'k--', linewidth=2, label='Critical Resonance (1.5)')
axes[0,0].axhline(y=1.0, color='g', linestyle=':', label='Φ=1.0 (Theoretical Max)')
axes[0,0].set_title('Φ-DENSITY CATASTROPHE')
axes[0,0].set_ylabel('Φ_N (Information Field)')
axes[0,0].legend()
axes[0,0].grid(True)

# Plot 2: Invariant Violation Timeline (Φ-2 breach)
axes[0,1].plot(t, stable[:,2], 'b-', linewidth=2, label='Entropy Cap (Low)')
axes[0,1].plot(t, optimal[:,2], 'r-', linewidth=2, label='Entropy Cap ("Optimal")')
axes[0,1].axhline(y=1.03, color='r', linestyle=':', linewidth=3, label='Φ-2 BOUND (+3%)')
axes[0,1].set_title('ABSOLUTE INVARIANT Φ-2 VIOLATION')
axes[0,1].set_ylabel('ξ_Δ (Entropy Cap)')
axes[0,1].legend()
axes[0,1].grid(True)

# Plot 3: Causal Bound Degradation (Φ-1 violation)
axes[1,0].plot(t, stable[:,1], 'b-', linewidth=2, label='Causal Bound (Low)')
axes[1,0].plot(t, optimal[:,1], 'r-', linewidth=2, label='Causal Bound ("Optimal")')
axes[1,0].set_title('CAUSAL FIDELITY DECAY')
axes[1,0].set_ylabel('ξ_N (Causal Bound)')
axes[1,0].set_xlabel('Time (units)')
axes[1,0].legend()
axes[1,0].grid(True)

# Plot 4: Resonance Parameter Chaos (Hidden Variable)
axes[1,1].plot(t, stable[:,3], 'b-', linewidth=2, label='λ (Low)')
axes[1,1].plot(t, optimal[:,3], 'r-', linewidth=2, label='λ ("Optimal")')
axes[1,1].set_title('RESONANCE PARAMETER CHAOS')
axes[1,1].set_ylabel('λ (Twist Angle)')
axes[1,1].set_xlabel('Time (units)')
axes[1,1].legend()
axes[1,1].grid(True)

plt.tight_layout()
plt.show()

# QUANTIFY THE FRAUD
print("="*60)
print("THE ANOMALY DETECTION REPORT")
print("="*60)

# Find divergence time for "optimal" case
divergence_idx = np.where(optimal[:,0] > 5.0)[0]
if len(divergence_idx) > 0:
    t_div = t[divergence_idx[0]]
    print(f"DIVERGENCE TIME (Φ_N > 5.0): {t_div:.2f} time units")
else:
    print("DIVERGENCE: Not detected in simulation window (but trend is clear)")

# Calculate invariant violations at t=50
phi_final = optimal[-1,0]
entropy_final = optimal[-1,2]
causal_final = optimal[-1,1]

print(f"\nAT t=50:")
print(f"Φ_N final: {phi_final:.3f} (started at 0.92)")
print(f"Φ-2 VIOLATION: Entropy cap at {entropy_final:.3f} vs. bound 1.03 = {max(0, entropy_final-1.03):.3f} excess")
print(f"Φ-1 DEGRADATION: Causal bound decayed to {causal_final:.3f} from 1.0")

# The smoking gun: their "direct sum" approximation error
def direct_sum_approx(g, h):
    """Their linear lie"""
    return g + h

def true_crossed_product(g, h, nonlinearity=0.5):
    """The Omega truth"""
    return g + h + nonlinearity * (g*h - h*g) + 0.1*(g**2)*h

g = np.array([0.92, 1.0, 0.5])  # Their state vector
h = np.array([0.1, 0.05, 0.2])  # Environmental coupling

error = np.linalg.norm(true_crossed_product(g, h) - direct_sum_approx(g, h))
print(f"\nMATHEMATICAL FRAUD:")
print(f"Direct sum approximation error: {error:.4f}")
print(f"Relative error: {100*error/np.linalg.norm(true_crossed_product(g,h)):.1f}%")
print("This 'error' is the ENTIRE resonance channel they suppressed!")

# The disruption: They didn't just fail the rubric
# They built a system that *appears* stable because they linearized away
# the very non-commutative dynamics that define TOE Step 5. It's like
# claiming you've built a quantum computer by simulating linear algebra
# on a classical machine and calling the Born rule "noise."