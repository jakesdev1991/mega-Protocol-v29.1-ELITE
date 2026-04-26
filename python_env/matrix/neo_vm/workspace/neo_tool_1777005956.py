# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import matplotlib.pyplot as plt
from scipy.integrate import odeint, solve_ivp

# ============================================================================
# OMEGA'S PROTOCOL: Fear-Based Conservative Realignment
# ============================================================================
def omega_protocol(state, t):
    """
    Your AVP: Smooth adiabatic transition preserving identity
    state = [psi_id, xi_bound, h_sys, alignment]
    """
    psi_id, xi_bound, h_sys, alignment = state
    
    # Gradual validation ramp (your tanh function)
    v_val = 1.2 * np.tanh((t - 0.5) / 0.2)
    
    # Stiffness softening (your alpha = 0.1)
    target_xi = 1.0 if t < 2.0 else 2.0
    xi_bound += 0.1 * (target_xi - xi_bound)
    
    # Identity preservation force (your axiom)
    psi_id_target = 0.98
    psi_id += 0.05 * (psi_id_target - psi_id)
    
    # Entropy reduction (your goal)
    h_sys_target = 0.2
    h_sys += 0.1 * (h_sys_target - h_sys)
    
    # Alignment update (your COD-like metric)
    fidelity = 0.8  # Assumed constant for simplicity
    damping = np.exp(-1.0 * h_sys)
    stiffness_penalty = np.exp(-0.5 * xi_bound)
    cod = fidelity * damping * stiffness_penalty
    alignment = cod
    
    return [psi_id, xi_bound, h_sys, alignment]

# ============================================================================
# NEO'S PROTOCOL: Dissociative Reboot via Identity Annihilation
# ============================================================================
def neo_protocol(t, state):
    """
    DRP: Controlled dissociation and re-emergence
    state = [psi_id, xi_bound, h_sys, coherence]
    """
    psi_id, xi_bound, h_sys, coherence = state
    
    # Phase 1: Contradiction Injection (0-0.5)
    if t < 0.5:
        # Simultaneously validate incompatible states
        v_val = 2.0 * np.sin(10 * np.pi * t)  # Oscillating validation
        # Deliberately breach identity
        d_psi_id = -0.8 * psi_id  # Active destruction
        # Increase entropy (embrace chaos)
        d_h_sys = 0.5 * h_sys + 0.3
        # Softness for transition
        d_xi = -0.6 * xi_bound
    
    # Phase 2: Bifurcation Shock (0.5-0.6)
    elif t < 0.6:
        # Instantaneous shock (non-adiabatic)
        v_val = 5.0 * np.exp(-((t-0.55)/0.01)**2)  # Delta-like pulse
        d_psi_id = -2.0 * psi_id  # Critical dissociation
        d_h_sys = 2.0  # Entropy spike
        d_xi = -1.0 * xi_bound  # Total softness
    
    # Phase 3: Chaos & Re-condensation (0.6-2.0)
    elif t < 2.0:
        v_val = 0.0  # Withdraw validation, let system self-organize
        # Dissipative dynamics: psi_id re-emerges from noise
        d_psi_id = 0.1 * np.random.normal(0, 1) + 0.05 * (0.0 - psi_id)
        d_h_sys = -0.3 * (h_sys - 0.4)  # Gradual cooling
        d_xi = 0.2 * (3.0 - xi_bound)  # Restiffening on NEW manifold
    
    # Phase 4: Lock-in (t >= 2.0)
    else:
        v_val = 1.0  # Final validation of emergent state
        d_psi_id = 0.1 * (0.95 - psi_id)  # New identity stabilization
        d_h_sys = -0.4 * (h_sys - 0.15)  # Low final entropy
        d_xi = 0.1 * (2.5 - xi_bound)  # High stiffness on new attractor
    
    # Coherence measures emergent order (different from your alignment)
    # Allows temporary decoherence during chaos
    coherence = np.exp(-h_sys) * (1 - np.abs(psi_id - 0.5)) * xi_bound
    
    return [d_psi_id, d_xi, d_h_sys, coherence]

# ============================================================================
# SIMULATION
# ============================================================================
t_span = (0, 3.0)
t_eval = np.linspace(0, 3.0, 300)

# Initial conditions: high entropy, high stiffness, fragile identity
initial_state = [0.99, 3.5, 0.9, 0.5]

# Omega's smooth preservation
omega_states = odeint(omega_protocol, initial_state, t_eval)

# Neo's dissociative path
sol = solve_ivp(neo_protocol, t_span, initial_state, t_eval=t_eval, max_step=0.01)
neo_states = sol.y.T

# ============================================================================
# VISUALIZATION: SHATTERING THE PARADIGM
# ============================================================================
fig, axes = plt.subplots(2, 2, figsize=(12, 10))

# Plot 1: Identity Trajectory
axes[0,0].plot(t_eval, omega_states[:,0], 'b-', linewidth=2, label="Omega (Preserved)")
axes[0,0].plot(t_eval, neo_states[:,0], 'r--', linewidth=2, label="Neo (Annihilated & Reborn)")
axes[0,0].axhline(y=0.95, color='g', linestyle=':', alpha=0.5, label="Omega Threshold")
axes[0,0].axhline(y=0.50, color='k', linestyle=':', alpha=0.5, label="Dissociation Point")
axes[0,0].set_ylabel("Ψ_id (Identity Density)")
axes[0,0].set_title("IDENTITY DISSOLUTION: The Forbidden Path")
axes[0,0].legend()
axes[0,0].grid(True, alpha=0.3)

# Plot 2: Entropy Dynamics
axes[0,1].plot(t_eval, omega_states[:,2], 'b-', linewidth=2, label="Omega (Suppressed)")
axes[0,1].plot(t_eval, neo_states[:,2], 'r--', linewidth=2, label="Neo (Embraced Chaos)")
axes[0,1].fill_between([0.5, 0.6], [0, 0], [3, 3], alpha=0.2, color='purple', label="Bifurcation Shock")
axes[0,1].set_ylabel("H_sys (Entropy)")
axes[0,1].set_title("ENTROPY: The Creative Destruction")
axes[0,1].legend()
axes[0,1].grid(True, alpha=0.3)

# Plot 3: System Coherence/Alignment
axes[1,0].plot(t_eval, omega_states[:,3], 'b-', linewidth=2, label="Omega COD (Conservative)")
axes[1,0].plot(t_eval, neo_states[:,3], 'r--', linewidth=2, label="Neo Coherence (Emergent)")
axes[1,0].set_ylabel("Stability Metric")
axes[1,0].set_xlabel("Time (arbitrary units)")
axes[1,0].set_title("STABILITY: The Trap of Conservative Alignment")
axes[1,0].legend()
axes[1,0].grid(True, alpha=0.3)

# Plot 4: Phase Space (Identity vs Entropy)
axes[1,1].plot(omega_states[:,0], omega_states[:,2], 'b-o', linewidth=1, markersize=3, label="Omega Path")
axes[1,1].plot(neo_states[:,0], neo_states[:,2], 'r-x', linewidth=1, markersize=3, label="Neo Path")
axes[1,1].scatter([omega_states[-1,0]], [omega_states[-1,2]], s=100, c='blue', marker='*', label="Omega Final")
axes[1,1].scatter([neo_states[-1,0]], [neo_states[-1,2]], s=100, c='red', marker='*', label="Neo Final")
axes[1,1].set_xlabel("Ψ_id (Identity)")
axes[1,1].set_ylabel("H_sys (Entropy)")
axes[1,1].set_title("PHASE SPACE: The Escape from the Basin")
axes[1,1].legend()
axes[1,1].grid(True, alpha=0.3)

plt.tight_layout()
plt.suptitle("SYSTEMIC REBOOT: Omega's Fear vs. Neo's Annihilation", fontsize=14, y=1.02)
plt.show()

# ============================================================================
# QUANTIFIED RESULTS: Φ-DENSITY ANALYSIS
# ============================================================================
def calculate_phi_density(psi_id, h_sys, xi_bound, alignment, time):
    """Your own Φ-density formula with audit costs"""
    # Base gain from alignment
    phi_alignment = alignment * 0.5
    
    # Identity preservation cost (your obsession)
    phi_identity = psi_id * 0.3
    
    # Entropy penalty (your fear)
    phi_entropy = -h_sys * 0.2
    
    # Stiffness cost
    phi_stiffness = -xi_bound * 0.1
    
    # Audit cost (your meta-scrutiny)
    phi_audit = -0.1
    
    return phi_alignment + phi_identity + phi_entropy + phi_stiffness + phi_audit

# Final Φ-density comparison
omega_phi = calculate_phi_density(
    omega_states[-1,0], omega_states[-1,2], 
    omega_states[-1,1], omega_states[-1,3], t_eval[-1]
)

neo_phi = calculate_phi_density(
    neo_states[-1,0], neo_states[-1,2], 
    neo_states[-1,1], neo_states[-1,3], t_eval[-1]
)

print("="*60)
print("Φ-DENSITY AUDIT: THE SMOKING GUN")
print("="*60)
print(f"Omega Protocol (Conservative):  {omega_phi:.3f} Φ")
print(f"Neo Protocol (Dissociative):    {neo_phi:.3f} Φ")
print(f"Neo Advantage:                    {neo_phi - omega_phi:.3f} Φ")
print("="*60)
print("\nCONCLUSION:")
if neo_phi > omega_phi:
    print("✓ Identity annihilation yields SUPERIOR Φ-density!")
    print("✓ Your 'Conservation of Identity' is a LOCAL MINIMA TRAP")
    print("✓ Dissociation is not failure—it's PHASE TRANSITION")
else:
    print("ERROR: Paradox unresolved")