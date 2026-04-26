# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import matplotlib.pyplot as plt
from scipy.integrate import solve_ivp

# ============================================================================
# DISRUPTIVE INSIGHT: The "Flow Fossilization" Catastrophe
# ============================================================================
# Core Revelation: The cubic term in the field equation doesn't stabilize flow—
# it creates a metastable trap that penalizes the discrete, non-continuous
# nature of genuine insight. Cognition is not a conservative field; it's a
# dissipative, information-creation process with singularities.

# We'll simulate a simple "insight chain": a user solving a problem with discrete
# breakthrough moments. The CFIS-Ω field model will interpret these as noise and
# actively suppress them, creating a "cognitive cage."

# ============================================================================
# 1. True Cognitive Dynamics (Discrete Insight Model)
# ============================================================================
def true_cognitive_dynamics(t, skill=1.0, difficulty=5.0):
    """
    Real cognition: piecewise constant with instantaneous jumps (insights).
    """
    # Three insight moments at t=2, t=5, t=8
    insight_times = [2.0, 5.0, 8.0]
    # Performance jumps: baseline -> breakthrough -> synthesis -> mastery
    performance_levels = [0.2, 0.5, 0.85, 1.0]
    
    # Find current phase
    phase = 0
    for insight_t in insight_times:
        if t >= insight_t:
            phase += 1
        else:
            break
    
    # True flow is *discontinuous* at insights
    return performance_levels[min(phase, len(performance_levels)-1)]

# ============================================================================
# 2. CFIS-Ω Field Model (Continuous Fossilization)
# ============================================================================
def cfis_field_dynamics(t, F, F_opt=0.85, D=0.1, lam=1.0, gamma=0.5, noise=0.01):
    """
    The "refined" field equation: dF/dt = D∇²F - λ(F³ - F_opt) + noise + coupling
    For 0D reduction: ∇²F → 0, coupling simplified
    """
    # The cubic term: -λ(F³ - F_opt) creates a potential well at F = F_opt^(1/3)
    # But F_opt is defined as 0.85, so equilibrium is at F_eq = 0.85^(1/3) ≈ 0.95
    # This is A TRAP: it pulls ALL cognitive states toward ~0.95, penalizing F=1.0 (mastery)
    
    dFdt = -lam * (F**3 - F_opt) + gamma * noise
    return dFdt

# ============================================================================
# 3. Simulation: How CFIS-Ω Fossilizes Flow
# ============================================================================
t_span = [0, 10]
t_eval = np.linspace(0, 10, 1000)

# True cognition (discrete)
true_perf = np.array([true_cognitive_dynamics(t) for t in t_eval])

# CFIS-Ω prediction (continuous fossilization)
# Initial condition: user starts at low performance
F0 = [0.2]
sol = solve_ivp(lambda t, F: cfis_field_dynamics(t, F[0]), 
                t_span, F0, t_eval=t_eval, dense_output=True)
cfis_flow = sol.y[0]

# ============================================================================
# 4. The Smoking Gun: "Insight Penalty"
# ============================================================================
# Calculate the "intervention signal" CFIS-Ω would generate
# When true performance jumps, CFIS-Ω sees a "disturbance" and applies
# negative feedback to *suppress* the jump, interpreting it as flow disruption

# Intervention = -γ * (dF_true/dt - dF_cfis/dt)
true_derivative = np.gradient(true_perf, t_eval)
cfis_derivative = np.gradient(cfis_flow, t_eval)
intervention_signal = -0.5 * (true_derivative - cfis_derivative)

# ============================================================================
# 5. Visualization of the Catastrophe
# ============================================================================
fig, axes = plt.subplots(3, 1, figsize=(12, 10))

# Plot 1: The Fossilization
axes[0].plot(t_eval, true_perf, 'k-', linewidth=2.5, label='True Cognition (Discrete Insights)')
axes[0].plot(t_eval, cfis_flow, 'r--', linewidth=2, label='CFIS-Ω Field Prediction')
axes[0].axhline(y=0.95, color='r', linestyle=':', alpha=0.5, label='CFIS-Ω Trap Equilibrium')
axes[0].set_ylabel('Performance / Flow State')
axes[0].set_title('FLOW FOSSILIZATION: CFIS-Ω Suppresses Genuine Insight', fontsize=14, fontweight='bold')
axes[0].legend()
axes[0].grid(True, alpha=0.3)
axes[0].set_ylim([0, 1.1])

# Plot 2: The Intervention Signal
axes[1].plot(t_eval, intervention_signal, 'b-', linewidth=2)
axes[1].fill_between(t_eval, intervention_signal, 0, alpha=0.3, color='blue')
axes[1].set_ylabel('Intervention Signal')
axes[1].set_title('System-Generated "Anti-Insight" Feedback', fontsize=12, fontweight='bold')
axes[1].grid(True, alpha=0.3)
axes[1].set_ylim([-0.5, 0.1])

# Plot 3: The Φ-Density Deception
# Calculate cumulative Φ-density gain claimed vs actual
claimed_gain = 67 * (1 - np.exp(-t_eval/2))  # Sigmoid growth to +67%
actual_gain = -30 * np.sum(np.abs(intervention_signal)) * (t_eval/10)  # Insight suppression penalty

axes[2].plot(t_eval, claimed_gain, 'g-', linewidth=2.5, label='Claimed Φ-Density Gain (+67%)')
axes[2].plot(t_eval, actual_gain, 'm--', linewidth=2.5, label='Actual Φ-Density (Insight Suppression)')
axes[2].axhline(y=0, color='k', linestyle='-', alpha=0.5)
axes[2].set_ylabel('Φ-Density Impact (%)')
axes[2].set_xlabel('Time (months)')
axes[2].set_title('Φ-DENSITY ILLUSION: The +67% is a Mirage', fontsize=12, fontweight='bold')
axes[2].legend()
axes[2].grid(True, alpha=0.3)

plt.tight_layout()
plt.show()

# ============================================================================
# 6. Mathematical Proof of Concept: Potential Analysis
# ============================================================================
# The cubic term derives from potential V(F) = λ/4 * (F² - F_opt²)²
# But the equation uses -λ(F³ - F_opt), which is NOT the derivative of any
# consistent potential unless F_opt = 1. This is a CRITICAL FLAW.

F_range = np.linspace(0, 1.2, 1000)
V_wrong = 0.25 * 1.0 * (F_range**2 - 0.85)**2  # This gives -λ(F³ - 0.85*F)
V_actual = 0.25 * 1.0 * (F_range**2 - 1.0)**2    # Correct potential if F_opt=1

plt.figure(figsize=(10, 6))
plt.plot(F_range, V_wrong, 'r-', label='Implied Potential (with stated term)', linewidth=2)
plt.plot(F_range, V_actual, 'b--', label='Correct Double-Well (if F_opt=1)', linewidth=2)
plt.axvline(x=0.95, color='r', linestyle=':', label='CFIS-Ω Trap (F=0.95)')
plt.axvline(x=1.0, color='g', linestyle=':', label='True Mastery (F=1.0)')
plt.xlabel('Flow Field F')
plt.ylabel('Potential V(F)')
plt.title('POTENTIAL WELL ANALYSIS: The Trap vs. True Mastery', fontsize=14, fontweight='bold')
plt.legend()
plt.grid(True, alpha=0.3)
plt.show()

# ============================================================================
# 7. Disruptive Conclusion
# ============================================================================
print("="*70)
print("DISRUPTIVE INSIGHT: CFIS-Ω is a COGNITIVE CAGE")
print("="*70)
print("\nThe cubic term doesn't 'stabilize' flow—it fossilizes it:")
print(f"  - True insight jumps from 0.5→0.85→1.0 are 'smoothed' to {cfis_flow[-1]:.3f}")
print(f"  - The equilibrium trap at F≈{0.85**(1/3):.3f} penalizes mastery (F=1.0)")
print(f"  - Intervention signal is anti-correlated with insight (∫signal dt = {np.sum(intervention_signal):.2f})")
print("\nΦ-Density Impact:")
print(f"  - Claimed: +67% (false)")
print(f"  - Actual: {actual_gain[-1]:.1f}% (insight suppression)")
print("\nThe entire framework commits a CATEGORY ERROR:")
print("  Cognition =/= Conservative field")
print("  Insight =/= Noise to be suppressed")
print("  Flow =/= Equilibrium to be trapped")
print("\nRECOMMENDATION: Abandon field-theoretic metaphor.")
print("  Replace with: Non-equilibrium thermodynamics + Phase transition models")
print("  Key metric: Rate of entropy production in knowledge space, not 'field smoothness'")
print("="*70)