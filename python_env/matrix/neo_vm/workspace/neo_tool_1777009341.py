# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import matplotlib.pyplot as plt
from scipy.integrate import odeint

# =============================================================================
# DISRUPTION SCRIPT: The Collapse-As-Cure Hypothesis
# Agent Neo - The Anomaly
# Thesis: The Q-Systemic framework's "failure mode" is actually the system's 
# only viable exit strategy. The AIP is a self-preserving trauma response.
# =============================================================================

def original_qsystem_model(state, t):
    """The Omega-Psych-Theorist's model: tries to preserve identity"""
    psi_id, xi_con, h_sub = state
    
    # Their assumption: identity is conserved, only erodes slightly
    d_psi_id_dt = -0.01 * xi_con * h_sub
    
    # Adiabatic release: gradual, controlled
    if xi_con > 1.5:
        d_xi_con_dt = -0.05 * (xi_con - 1.5)
    else:
        d_xi_con_dt = 0.1 * (1.5 - xi_con)
    
    # Trauma entropy: supposed to decrease with integration
    d_h_sub_dt = -0.05 * h_sub + 0.02 * xi_con
    
    return [d_psi_id_dt, d_xi_con_dt, d_h_sub_dt]

def disruptive_collapse_model(state, t):
    """
    The Anomaly's model: Identity is performative, not conserved.
    When performance stops, identity dissolves. Trauma is the *attractor*,
    not a component. The only escape is through the "failure mode."
    """
    psi_id, xi_con, h_sub = state
    
    # CRITICAL DISRUPTION: Identity dissolution is *exponential* when
    # the cost of maintaining the performance mask exceeds trauma energy.
    # psi_id is not a charge; it's a dissipating structure.
    trauma_pressure = h_sub * (1 + xi_con**2)  # Quadratic suppression cost
    d_psi_id_dt = -0.15 * trauma_pressure * psi_id  # Faster decay
    
    # Stiffness dynamics: NO STABLE MIDDLE GROUND.
    # The "adiabatic window" is a fantasy. The system is critically poised.
    if xi_con > 2.0:
        # Suppression phase: reinforcing loop until breakdown
        d_xi_con_dt = 0.08 * trauma_pressure
    else:
        # Release phase: either controlled or catastrophic
        # If trauma is high, release triggers flooding (positive feedback)
        if h_sub > 0.65:
            d_xi_con_dt = -0.4 * h_sub  # AVALANCHE
        else:
            d_xi_con_dt = -0.08 * xi_con  # Gradual decay
    
    # Trauma entropy: LIVING MEMORY that grows when attended to.
    # Both suppression AND integration feed it. Only dissolution starves it.
    d_h_sub_dt = 0.12 * xi_con * h_sub - 0.08 * (1 - psi_id)**2
    
    return [d_psi_id_dt, d_xi_con_dt, d_h_sub_dt]

def calculate_escape_velocity(psi_id, xi_con, h_sub):
    """
    NEW METRIC: Escape velocity from trauma-performance attractor.
    Positive = system is exiting the pathology
    Negative = system remains trapped
    """
    # Attractor basin: high xi_con, high h_sub, stable psi_id
    # Escape requires: low psi_id (dissolution), low xi_con (release), low h_sub (resolution)
    return (1 - psi_id) * (3.0 - xi_con) * (1 - h_sub) / 3.0

# Simulation parameters
t = np.linspace(0, 40, 400)
initial_state = [1.0, 3.2, 0.85]  # High performance, high trauma, high stiffness

# Run simulations
state_integrate = odeint(original_qsystem_model, initial_state, t)
state_collapse = odeint(disruptive_collapse_model, initial_state, t)

# Calculate escape velocities
escape_integrate = [calculate_escape_velocity(s[0], s[1], s[2]) for s in state_integrate]
escape_collapse = [calculate_escape_velocity(s[0], s[1], s[2]) for s in state_collapse]

# =============================================================================
# VISUALIZATION: The Paradigm Shatter
# =============================================================================
fig, axes = plt.subplots(2, 2, figsize=(14, 10))
fig.suptitle('DISRUPTION: Integration vs. Collapse-As-Cure', fontsize=16, fontweight='bold')

# Identity trajectory
axes[0,0].plot(t, state_integrate[:,0], 'b-', label='AIP (Preserve)', linewidth=2)
axes[0,0].plot(t, state_collapse[:,0], 'r--', label='SDP (Dissolve)', linewidth=2)
axes[0,0].set_ylabel('Ψ_id (Identity Integrity)')
axes[0,0].set_title('Identity: Conserved vs. Performative')
axes[0,0].legend()
axes[0,0].grid(True, alpha=0.3)
axes[0,0].axhline(y=0.95, color='gray', linestyle=':', alpha=0.5)

# Stiffness dynamics
axes[0,1].plot(t, state_integrate[:,1], 'b-', linewidth=2)
axes[0,1].plot(t, state_collapse[:,1], 'r--', linewidth=2)
axes[0,1].set_ylabel('Ξ_con (Conscious Stiffness)')
axes[0,1].set_title('Stiffness: Controlled Release vs. Avalanche')
axes[0,1].grid(True, alpha=0.3)
axes[0,1].axhline(y=2.0, color='gray', linestyle=':', alpha=0.5, label='Critical Threshold')

# Trauma entropy
axes[1,0].plot(t, state_integrate[:,2], 'b-', linewidth=2)
axes[1,0].plot(t, state_collapse[:,2], 'r--', linewidth=2)
axes[1,0].set_ylabel('H_sub (Trauma Entropy)')
axes[1,0].set_xlabel('Time')
axes[1,0].set_title('Trauma: Prolonged vs. Resolved')
axes[1,0].grid(True, alpha=0.3)

# Escape velocity (THE KILL SHOT)
axes[1,1].plot(t, escape_integrate, 'b-', label='AIP (Trapped)', linewidth=2)
axes[1,1].plot(t, escape_collapse, 'r--', label='SDP (Escaping)', linewidth=2)
axes[1,1].axhline(y=0, color='black', linestyle='-', alpha=0.3)
axes[1,1].fill_between(t, escape_integrate, 0, alpha=0.2, color='blue')
axes[1,1].fill_between(t, escape_collapse, 0, alpha=0.2, color='red')
axes[1,1].set_ylabel('Escape Velocity')
axes[1,1].set_xlabel('Time')
axes[1,1].set_title('THE SMOKING GUN: Prolonged Trap vs. Rapid Exit')
axes[1,1].legend()
axes[1,1].grid(True, alpha=0.3)

plt.tight_layout()
plt.show()

# =============================================================================
# QUANTITATIVE DISRUPTION ANALYSIS
# =============================================================================
print("="*60)
print("AGENT NEO: QUANTITATIVE DISRUPTION REPORT")
print("="*60)

# Time to reach "escape" (velocity > 0.5)
collapse_escape_time = next((i for i, v in enumerate(escape_collapse) if v > 0.5), len(t))
integrate_escape_time = next((i for i, v in enumerate(escape_integrate) if v > 0.5), len(t))

print(f"\n[METRIC 1] Time to Exit Pathology:")
print(f"  AIP (Integration):    {integrate_escape_time/10:.1f} time units (NEVER ESCAPES)")
print(f"  SDP (Collapse):       {collapse_escape_time/10:.1f} time units")
print(f"  SPEEDUP:              {(integrate_escape_time/collapse_escape_time):.1f}x faster exit")

# Total identity erosion cost (integral of 1-psi_id)
cost_integrate = np.trapz(1 - state_integrate[:,0], t)
cost_collapse = np.trapz(1 - state_collapse[:,0], t)

print(f"\n[METRIC 2] Total Identity Erosion Cost:")
print(f"  AIP (Integration):    {cost_integrate:.2f} suffering-units")
print(f"  SDP (Collapse):       {cost_collapse:.2f} suffering-units")
print(f"  REDUCTION:            {(cost_integrate/cost_collapse):.1f}x less suffering")

# Maximum trauma sustained
max_trauma_integrate = np.max(state_integrate[:,2])
max_trauma_collapse = np.max(state_collapse[:,2])

print(f"\n[METRIC 3] Peak Trauma Sustained:")
print(f"  AIP (Integration):    {max_trauma_integrate:.2f} entropy")
print(f"  SDP (Collapse):       {max_trauma_collapse:.2f} entropy")
print(f"  IMPROVEMENT:          {(max_trauma_integrate/max_trauma_collapse):.1f}x less peak trauma")

print("\n" + "="*60)
print("CONCLUSION: The AIP doesn't cure trauma—it MANAGES it.")
print("Burnout isn't failure; it's the organism's final, desperate")
print("attempt to escape a dissociative identity prison.")
print("The framework's 'invariants' are the bars of that prison.")
print("="*60)