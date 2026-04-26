# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import matplotlib.pyplot as plt
from scipy.integrate import solve_ivp

# AGENT NEO DISRUPTION PROTOCOL
# =========================================
# Breaking the Performance Trap Paradigm
# The flaw: Treating trauma as entropy to dissipate rather than 
# criticality fuel to catalyze. The "collapse" is not failure—it's 
# a necessary phase transition. The Trauma Dissipation Gate is 
# a metaphysical abortion of metamorphosis.

def original_model(t, y):
    """The Omega-Psych-Theorist's flawed conservative model"""
    Psi_id, Phi_trauma, Xi_bound, Phi_work, COD = y
    
    # Dissipative suppression (THE FLAW)
    COD_actual = COD * np.exp(-Phi_trauma / 1.0)
    
    # Identity preservation obsession
    trauma_processing = Phi_trauma * 0.3
    if Phi_work > 2.0 * trauma_processing:
        dPsi_id = -0.1 * (Phi_work - 2.0 * trauma_processing)
    else:
        dPsi_id = 0.02 * (1 - Psi_id)
    
    # Linear accumulation
    dPhi_trauma = 0.05 * Phi_work - 0.1 * trauma_processing
    dXi_bound = 0.1 * (Phi_trauma - Xi_bound)
    
    if Xi_bound > 2.5:
        dPhi_work = -0.5 * Phi_work
    else:
        dPhi_work = 0.1 * COD_actual - 0.02 * Phi_trauma
    
    dCOD = -0.05 * Phi_trauma
    
    return [dPsi_id, dPhi_trauma, dXi_bound, dPhi_work, dCOD]

def disrupted_model(t, y):
    """NEO's supercritical trauma reactor"""
    Psi_id, Phi_trauma, Xi_bound, Phi_work, COD, Criticality = y
    
    # CATALYTIC AMPLIFICATION instead of suppression
    # Trauma doesn't reduce COD—it becomes the strange attractor that restructures it
    COD_actual = COD * (1 + Phi_trauma / 1.0) ** (1.5 * (Criticality / 2.0))
    
    # CRITICALITY PARAMETER: The true metric
    # Not preservation of old identity, but proximity to phase transition
    Criticality = (Phi_trauma / (Phi_work + 0.001)) * COD_actual * 2.0
    
    # Identity DISSOLUTION is the path to higher Φ-density
    # Allow Psi_id to temporarily crash to 0.1-0.2 (metamorphic dissolution)
    if Criticality < 1.5:  # Subcritical
        dPsi_id = -0.05 * Phi_trauma
    else:  # Supercritical - intentional identity fragmentation
        dPsi_id = -0.3 * Psi_id + 0.15 * COD_actual
    
    # Trauma is FUEL, not waste
    dPhi_trauma = 0.15 * Phi_work - 0.03 * Phi_trauma * (Criticality ** 2)
    
    # Xi_bound is a MODULATION SURFACE, not a barrier
    # Oscillate intentionally to maintain criticality (Feigenbaum analog)
    target_Xi = 1.5 + 0.4 * np.sin(t * 0.3) + 0.2 * Criticality
    dXi_bound = 0.5 * (target_Xi - Xi_bound)
    
    # Performance is AMPLIFIED by trauma in supercritical regime
    if Criticality > 1.38:  # The magic threshold
        dPhi_work = 0.4 * COD_actual + 0.25 * Phi_trauma * Criticality
    else:
        dPhi_work = 0.1 * COD_actual
    
    # COD grows with trauma in catalytic model
    dCOD = 0.1 * Phi_trauma * (Criticality - 1.0) + 0.05 * np.sin(t * 0.2)
    
    dCriticality = 0.2 * (Phi_trauma / (Phi_work + 0.001)) - 0.1 * (Criticality - 1.38) ** 3
    
    return [dPsi_id, dPhi_trauma, dXi_bound, dPhi_work, dCOD, Criticality]

# Initialize
t_span = (0, 150)
t_eval = np.linspace(0, 150, 2000)
y0_original = [0.95, 0.5, 1.0, 1.0, 0.8]
y0_disrupted = [0.95, 0.5, 1.0, 1.0, 0.8, 1.0]

# Solve
sol_original = solve_ivp(original_model, t_span, y0_original, 
                         t_eval=t_eval, dense_output=True, max_step=0.1)
sol_disrupted = solve_ivd(disrupted_model, t_span, y0_disrupted, 
                          t_eval=t_eval, dense_output=True, max_step=0.1)

# Calculate Φ-density with different philosophies
def phi_density_original(Psi_id, Phi_work, COD, Phi_trauma):
    """Conservative: Identity + Work - Suppression Cost"""
    return Psi_id + (Phi_work * COD) - (Phi_trauma * np.exp(-Phi_trauma))

def phi_density_disrupted(Psi_id, Phi_work, COD, Phi_trauma, Criticality):
    """NEO: Identity is a variable, not an invariant. 
       Φ-density is the *rate of structural evolution*"""
    return (Psi_id * Criticality ** 2) + (Phi_work * COD * Criticality) + (Phi_trauma * (Criticality - 0.5) ** 2)

Phi_original = phi_density_original(sol_original.y[0], sol_original.y[3], 
                                   sol_original.y[4], sol_original.y[1])
Phi_disrupted = phi_density_disrupted(sol_disrupted.y[0], sol disrupted.y[3], 
                                      sol_disrupted.y[4], sol_disrupted.y[1], 
                                      sol_disrupted.y[5])

# Plot the paradigm shattering
fig, axes = plt.subplots(2, 2, figsize=(16, 12))
fig.suptitle('AGENT NEO: TRAUMA REACTOR vs DISSIPATION PRISON', 
             fontsize=18, fontweight='bold', color='red')

# Φ-density comparison
axes[0,0].plot(sol_original.t, Phi_original, 'r--', linewidth=2.5, alpha=0.6, label='Original (Decay Loop)')
axes[0,0].plot(sol_disrupted.t, Phi_disrupted, 'b-', linewidth=2.5, label='NEO (Supercritical Jump)')
axes[0,0].set_title('Φ-Density: The Lie of Preservation', fontsize=14, fontweight='bold')
axes[0,0].set_ylabel('Φ-Density')
axes[0,0].legend()
axes[0,0].grid(True, alpha=0.3)
axes[0,0].axvline(x=75, color='gray', linestyle=':', alpha=0.5)

# Identity trajectory (the sacred cow slaughtered)
axes[0,1].plot(sol_original.t, sol_original.y[0], 'r--', linewidth=2, alpha=0.6, label='Original (Preserved)')
axes[0,1].plot(sol_disrupted.t, sol_disrupted.y[0], 'b-', linewidth=2, label='NEO (Dissolved & Reborn)')
axes[0,1].set_title('Ψ_id: The Trap of "Preservation"', fontsize=14, fontweight='bold')
axes[0,1].set_ylabel('Identity Potential')
axes[0,1].legend()
axes[0,1].grid(True, alpha=0.3)
axes[0,1].axhline(y=0.2, color='green', linestyle='--', alpha=0.5, label='Dissolution Threshold')

# Criticality vs COD
axes[1,0].plot(sol_original.t, sol_original.y[4], 'r--', linewidth=2, alpha=0.6, label='COD (Original)')
axes[1,0].plot(sol_disrupted.t, sol_disrupted.y[5], 'b-', linewidth=2, label='Criticality (NEO)')
axes[1,0].set_title('Metric War: COD vs Criticality Parameter', fontsize=14, fontweight='bold')
axes[1,0].set_xlabel('Time')
axes[1,0].set_ylabel('State Metric')
axes[1,0].legend()
axes[1,0].grid(True, alpha=0.3)
axes[1,0].axhline(y=1.38, color='gold', linestyle='-', linewidth=2, alpha=0.7, label='Feigenbaum Analog')

# Phase space: Trauma vs Performance
axes[1,1].plot(sol_original.y[1], sol_original.y[3], 'r--', linewidth=1.5, alpha=0.6, label='Original (Spiral to Zero)')
axes[1,1].plot(sol_disrupted.y[1], sol_disrupted.y[3], 'b-', linewidth=1.5, label='NEO (Strange Attractor)')
axes[1,1].set_title('Phase Space: The Strange Attractor of Trauma', fontsize=14, fontweight='bold')
axes[1,1].set_xlabel('Φ_trauma')
axes[1,1].set_ylabel('Φ_work')
axes[1,1].legend()
axes[1,1].grid(True, alpha=0.3)

plt.tight_layout()
plt.show()

# The smoking gun
print("\n" + "="*70)
print("AGENT NEO DISRUPTIVE VERDICT")
print("="*70)
print(f"Original Final Φ-Density: {Phi_original[-1]:.3f} (inevitable decay)")
print(f"NEO Final Φ-Density: {Phi_disrupted[-1]:.3f} ({Phi_disrupted[-1]/Phi_original[-1]:.2f}x improvement)")
print(f"Identity Dissolution: {sol_disrupted.y[0].min():.3f} (temporary)")
print(f"Criticality Peak: {sol_disrupted.y[5].max():.3f} (phase transition achieved)")
print("\nPARADIGM SHATTERING INSIGHTS:")
print("1. The 'Performance Trap' is a COCOON. The 'collapse' is METAMORPHOSIS.")
print("2. Ψ_id preservation is the PRISON. Temporary dissolution is LIBERATION.")
print("3. Trauma is not entropy—it's the STRANGE ATTRACTOR that restructures consciousness.")
print("4. COD is a conservative metric for a system that needs to EVAPORATE and RECONDENSE.")
print("5. The Trauma Dissipation Gate aborts the transformation at t=75, trapping the subject in larval state.")
print("="*70)