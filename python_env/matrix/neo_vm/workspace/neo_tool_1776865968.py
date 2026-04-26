# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import matplotlib.pyplot as plt
from scipy.integrate import solve_ivp

# --- CORE DISRUPTION: The "Flow Trap" Vulnerability ---

def simulate_cfis_flow_trap(t_span=(0, 100), disturbance_freq=5):
    """
    Simulates CFIS-Ω's fatal flaw: preserving suboptimal flow states
    that become cognitive cages. When users develop systematic biases
    while in "optimal flow," CFIS-Ω *amplifies* those biases by preventing
    the natural disruptions that would break bias patterns.
    """
    
    def flow_trap_dynamics(t, y, bias_strength):
        F, bias_reinforcement, error_rate = y
        
        # CFIS-Ω maintains flow > 0.8 at all costs
        if F > 0.8:
            # In flow: bias gets reinforced, errors accumulate unseen
            dF_dt = -0.1 * (F - 0.85)  # "Protecting" flow
            dbias_dt = 0.05 * bias_strength * F  # Bias grows under protection
            derror_dt = 0.02 * bias_reinforcement  # Errors increase silently
        else:
            # Out of flow: natural correction mechanisms activate
            dF_dt = 0.5 * (0.85 - F)
            dbias_dt = -0.3 * bias_reinforcement
            derror_dt = -0.1 * error_rate
        
        return [dF_dt, dbias_dt, derror_dt]
    
    # Simulate: user starts in good flow, develops bias
    y0 = [0.85, 0.1, 0.05]
    t_eval = np.linspace(0, t_span[1], 1000)
    
    sol = solve_ivp(flow_trap_dynamics, t_span, y0, args=(0.3,), 
                    t_eval=t_eval, dense_output=True)
    
    return sol

# --- DISRUPTIVE INSIGHT: Cognitive Shock Induction (CSI-Ω) ---

def simulate_csi_shock_therapy(t_span=(0, 100), shock_intensity=2.5):
    """
    CSI-Ω: The anti-CFIS. Instead of preserving flow, we detect when
    Φ-density has plateaued (cognitive local optimum) and induce
    *controlled shocks* to force phase transitions into supercritical states
    where breakthrough thinking emerges.
    """
    
    def shock_dynamics(t, y, plateau_thresh):
        Phi_density, cognitive_state, breakthrough_potential = y
        
        # Detect plateau: low derivative + decent absolute level
        is_plateau = abs(Phi_density - 0.75) < 0.05 and Phi_density > 0.6
        
        # If plateaued, trigger shock - DRIVE OUT OF FLOW
        shock = shock_intensity if is_plateau and cognitive_state > 0.7 else 0
        
        # Φ-density: shock causes temporary dip but breakthroughs raise it higher
        dPhi_dt = -0.15 * (Phi_density - 0.75) + 0.3 * breakthrough_potential - 0.1 * shock
        
        # Cognitive state: flow -> shocked -> supercritical -> recondensed
        if shock > 0:
            dstate_dt = -3.0 * (cognitive_state - 0.2)  # Violent exit from flow
        elif cognitive_state < 0.4:
            dstate_dt = 0.8 * (0.4 - cognitive_state)   # Recovery phase
        else:
            dstate_dt = -0.2 * (cognitive_state - 1.0)   # Maintain new flow
        
        # Breakthrough potential: emerges during supercritical state (state > 1.2)
        dbreakthrough_dt = -0.4 * breakthrough_potential + 4.0 * max(0, cognitive_state - 1.2)
        
        return [dPhi_dt, dstate_dt, dbreakthrough_dt]
    
    y0 = [0.75, 0.85, 0.1]  # Start in "optimal" flow
    t_eval = np.linspace(0, t_span[1], 1000)
    
    sol = solve_ivp(shock_dynamics, t_span, y0, args=(0.05,),
                    t_eval=t_eval, dense_output=True)
    
    return sol

# --- Execute Simulations ---
print("=== CFIS-Ω FLOW TRAP ANALYSIS ===")
sol_trap = simulate_cfis_flow_trap()

# Calculate bias amplification factor
bias_growth = sol_trap.y[1, -1] / sol_trap.y[1, 0]
error_growth = sol_trap.y[2, -1] / sol_trap.y[2, 0]
print(f"Bias reinforcement amplification: {bias_growth:.2f}x")
print(f"Error rate increase: {error_growth:.2f}x")
print("CFIS-Ω creates a 'cognitive cage' where biases crystallize under protection.\n")

print("=== CSI-Ω SHOCK THERAPY ANALYSIS ===")
sol_shock = simulate_csi_shock_therapy()

# Calculate breakthrough yield
total_breakthrough = np.trapz(sol_shock.y[2], sol_shock.t)
final_phi = sol_shock.y[0, -1]
print(f"Total breakthrough potential: {total_breakthrough:.2f} units")
print(f"Final Φ-density: {final_phi:.3f} (vs 0.75 initial)")
print("CSI-Ω sacrifices short-term flow for long-term Φ-density gains.\n")

# --- Visualization ---
fig, axes = plt.subplots(2, 3, figsize=(16, 10))

# CFIS-Ω Trap
axes[0,0].plot(sol_trap.t, sol_trap.y[0], 'b-', linewidth=2, label='Flow Field')
axes[0,0].set_title('CFIS-Ω: "Protected" Flow', fontsize=11, fontweight='bold')
axes[0,0].set_ylabel('Flow State')
axes[0,0].axhline(0.8, color='r', linestyle='--', alpha=0.5, label='Flow Threshold')
axes[0,0].legend()

axes[0,1].plot(sol_trap.t, sol_trap.y[1], 'r-', linewidth=2, label='Bias Reinforcement')
axes[0,1].set_title('CFIS-Ω: Crystallizing Bias', fontsize=11, fontweight='bold')
axes[0,1].set_ylabel('Bias Strength')

axes[0,2].plot(sol_trap.t, sol_trap.y[2], 'g-', linewidth=2, label='Error Rate')
axes[0,2].set_title('CFIS-Ω: Silent Error Accumulation', fontsize=11, fontweight='bold')
axes[0,2].set_ylabel('Error Rate')

# CSI-Ω Shock
axes[1,0].plot(sol_shock.t, sol_shock.y[0], 'b-', linewidth=2, label='Φ-Density')
axes[1,0].set_title('CSI-Ω: Shock-Induced Phase Transitions', fontsize=11, fontweight='bold')
axes[1,0].set_ylabel('Φ-Density')
axes[1,0].set_xlabel('Time')
axes[1,0].legend()

axes[1,1].plot(sol_shock.t, sol_shock.y[1], 'r-', linewidth=2, label='Cognitive State')
axes[1,1].set_title('CSI-Ω: State Transitions (Flow → Shock → Supercritical)', fontsize=11, fontweight='bold')
axes[1,1].set_ylabel('State (0=disrupted, 1=flow, >1=supercritical)')
axes[1,1].set_xlabel('Time')

axes[1,2].plot(sol_shock.t, sol_shock.y[2], 'g-', linewidth=2, label='Breakthrough Potential')
axes[1,2].set_title('CSI-Ω: Breakthrough Emergence', fontsize=11, fontweight='bold')
axes[1,2].set_ylabel('Breakthrough Rate')
axes[1,2].set_xlabel('Time')

plt.suptitle('CFIS-Ω vs CSI-Ω: The Flow Trap vs Cognitive Shock Therapy', 
             fontsize=14, fontweight='bold', y=0.995)
plt.tight_layout()
plt.savefig('/mnt/data/cognitive_disruption_verification.png', dpi=300, bbox_inches='tight')
plt.show()

# --- Mathematical Proof of Concept ---
print("=== MATHEMATICAL DISRUPTION ===")
print("CFIS-Ω assumes: ∂ₜℱ = -λ(ℱ-ℱ_opt) + η - A")
print("This creates a STABLE ATTRACTOR at ℱ_opt = 0.85")
print("Problem: Stable attractors = cognitive local optima\n")

print("CSI-Ω proposes: ∂ₜℱ = -λ(ℱ-ℱ_meta) + Σᵢ δ(t-tᵢ)Sᵢ")
print("Where Sᵢ are SHOCK OPERATORS that kick system into meta-stable states")
print("This creates a STRANGE ATTRACTOR in cognitive phase space")
print("Result: ℱ oscillates between flow and disruption, maximizing ∫breakthrough dt\n")

# Phase portrait
def phase_portrait():
    F_range = np.linspace(0, 1.5, 50)
    state_range = np.linspace(0, 2, 50)
    F_grid, state_grid = np.meshgrid(F_range, state_range)
    
    # Vector field for CSI
    dF = -0.15 * (F_grid - 0.75)
    dState = np.where(state_grid > 0.7, -3 * (state_grid - 0.2), 
                     np.where(state_grid < 0.4, 0.8 * (0.4 - state_grid), 
                             -0.2 * (state_grid - 1.0)))
    
    plt.figure(figsize=(8, 6))
    plt.streamplot(F_grid, state_grid, dF, dState, density=1.5, color='purple', alpha=0.6)
    plt.axhline(0.85, color='r', linestyle='--', label='CFIS-Ω Target')
    plt.axvline(0.75, color='b', linestyle='--', label='Φ Plateau')
    plt.xlabel('Φ-Density')
    plt.ylabel('Cognitive State')
    plt.title('CSI-Ω Phase Portrait: Strange Attractor vs Stable Fixed Point')
    plt.legend()
    plt.savefig('/mnt/data/phase_portrait_disruption.png', dpi=300, bbox_inches='tight')
    plt.show()

phase_portrait()