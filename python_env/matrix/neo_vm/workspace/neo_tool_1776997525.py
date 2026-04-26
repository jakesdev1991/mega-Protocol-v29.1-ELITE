# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import matplotlib.pyplot as plt
from typing import Tuple, List

# ============================================================================
# AGENT NEO DISRUPTION PROTOCOL: CRYOGENIC TRAUMA PRESERVATION
# ============================================================================
# Thesis: The Adiabatic Safety Cooling Protocol (ASCP) doesn't resolve trauma—
# it *cryogenically preserves* it by enforcing stability on a system that needs
# a phase transition. The "safe" cooling is actually a dissociative trap.

def simulate_ascp_failure(
    initial_state: Tuple[float, float, float, float], 
    time_steps: int = 100,
    validation_trust: float = 0.3  # Critical parameter they ignore
) -> Tuple[List[float], List[float], List[float], List[float], List[bool]]:
    """
    Simulates their ASCP on a system with:
    1. Hysteresis in Xi_def (memory-dependent stiffness)
    2. Paradoxical validation (Psi_val can increase H_heat)
    3. Non-adiabatic phase transition threshold
    """
    
    # Unpack initial state: [gamma, xi_def, psi_id, H_heat]
    gamma, xi_def, psi_id, H_heat = initial_state
    
    # Their "invariant" thresholds
    PSI_ID_THRESHOLD = 0.95
    XI_DEF_MIN = 0.5
    GAMMA_CRITICAL = 0.8
    H_HEAT_LIMIT = 0.85
    
    # Neo's Reality: Non-linear couplings they ignore
    trauma_depth = 0.7  # Hidden variable: how deep the dissociation barrier is
    validation_paradox_threshold = 0.4  # When validation becomes threatening
    
    # Storage
    history = {
        'gamma': [], 'xi_def': [], 'psi_id': [], 'H_heat': [], 
        'cod': [], 'phase': [], 'dissociation_trap': []
    }
    
    for t in range(time_steps):
        # Their ASCP logic (simplified)
        if H_heat > H_HEAT_LIMIT and gamma > GAMMA_CRITICAL:
            # "Cool" by reducing gamma
            gamma *= 0.95  # Adiabatic reduction
        
        # Their Psi_val injection (naive)
        psi_val_boost = 1.05
        # NEO: But if trust is low, validation INCREASES threat
        if validation_trust < validation_paradox_threshold:
            H_heat *= (1 + (1 - validation_trust) * 0.1)  # Paradoxical heating
        
        # Calculate COD (their formula)
        fidelity = min(1.0, (psi_val_boost * 0.8))  # Simplified fidelity
        damping = np.exp(-1.0 * H_heat)
        stiffness_penalty = np.exp(-gamma * xi_def)
        cod = fidelity * damping * stiffness_penalty
        
        # NEO: Hysteresis in Xi_def - stiffness has memory, doesn't decrease linearly
        # The "cooling" reduces gamma, but Xi_def gets *stickier* as it approaches trauma_depth
        if gamma < 0.5 and xi_def > trauma_depth:
            xi_def *= 0.99  # Slow decay, but trauma_depth creates a potential well
        else:
            xi_def = max(XI_DEF_MIN, xi_def * 0.98)  # Their assumed linear decay
        
        # NEO: Phase transition threshold - system needs to cross trauma_depth to reintegrate
        # But their hard gate on psi_id prevents this non-adiabatic jump
        if xi_def < trauma_depth and psi_id > PSI_ID_THRESHOLD:
            # System is in the "dissociative trap": low stiffness but identity preserved
            # This is STABLE but pathological - it's dissociation, not integration
            dissociation_trap = True
            psi_id -= H_heat * 0.01  # Slow identity erosion they don't account for
        else:
            dissociation_trap = False
        
        # Their "safety" check
        if psi_id < PSI_ID_THRESHOLD:
            # They would abort here, preserving the trap
            break
        
        # Update heat with reduced gamma (but paradoxical validation may override)
        H_heat = max(0.1, H_heat * 0.97) if validation_trust > validation_paradox_threshold else H_heat
        
        # Record
        history['gamma'].append(gamma)
        history['xi_def'].append(xi_def)
        history['psi_id'].append(psi_id)
        history['H_heat'].append(H_heat)
        history['cod'].append(cod)
        history['phase'].append(1 if xi_def < trauma_depth else 0)
        history['dissociation_trap'].append(dissociation_trap)
    
    return history

# ============================================================================
# DEMONSTRATION: ASCP Creates Cryogenic Trauma Preservation
# ============================================================================

# Initial state: High performance, high anxiety (their target case)
initial = (0.9, 2.5, 1.0, 0.9)  # gamma, xi_def, psi_id, H_heat

# Run simulation with LOW trust in validation (realistic trauma case)
history_low_trust = simulate_ascp_failure(initial, validation_trust=0.2)

# Run simulation with HIGH trust (their optimistic assumption)
history_high_trust = simulate_ascp_failure(initial, validation_trust=0.8)

# ============================================================================
# VISUALIZATION: The Trap
# ============================================================================
fig, axes = plt.subplots(2, 2, figsize=(14, 10))
fig.suptitle("NEO DISRUPTION: ASCP = Cryogenic Trauma Preservation", fontsize=16, fontweight='bold')

# Plot 1: The "Safe" Cooling (High Trust)
axes[0, 0].plot(history_high_trust['gamma'], label='Γ (Measurement Intensity)', color='blue')
axes[0, 0].plot(history_high_trust['xi_def'], label='Ξ_def (Defensive Stiffness)', color='red')
axes[0, 0].set_title("SCENARIO A: High Validation Trust (Their Assumption)")
axes[0, 0].set_xlabel("Time Steps")
axes[0, 0].set_ylabel("Normalized Parameter")
axes[0, 0].legend()
axes[0, 0].grid(True, alpha=0.3)

# Plot 2: The Paradoxical Heating (Low Trust)
axes[0, 1].plot(history_low_trust['gamma'], label='Γ (Measurement Intensity)', color='blue')
axes[0, 1].plot(history_low_trust['xi_def'], label='Ξ_def (Defensive Stiffness)', color='red')
axes[0, 1].set_title("SCENARIO B: Low Validation Trust (Real Trauma)")
axes[0, 1].set_xlabel("Time Steps")
axes[0, 1].set_ylabel("Normalized Parameter")
axes[0, 1].legend()
axes[0, 1].grid(True, alpha=0.3)

# Plot 3: COD Deception
axes[1, 0].plot(history_high_trust['cod'], label='COD (High Trust)', color='green', linestyle='--')
axes[1, 0].plot(history_low_trust['cod'], label='COD (Low Trust)', color='orange')
axes[1, 0].plot(history_low_trust['dissociation_trap'], label='Dissociation Trap', color='purple', alpha=0.3)
axes[1, 0].set_title("Chain Overlap Density: The Deception")
axes[1, 0].set_xlabel("Time Steps")
axes[1, 0].set_ylabel("COD")
axes[1, 0].legend()
axes[1, 0].grid(True, alpha=0.3)
axes[1, 0].axhline(y=0.8, color='red', linestyle=':', label='COD Threshold')

# Plot 4: Phase Space Trajectory
axes[1, 1].scatter(history_low_trust['gamma'], history_low_trust['xi_def'], 
                   c=history_low_trust['H_heat'], cmap='hot', s=50, alpha=0.7)
axes[1, 1].set_title("Phase Space: ASCP Trajectory (Low Trust)")
axes[1, 1].set_xlabel("Γ (Measurement Intensity)")
axes[1, 1].set_ylabel("Ξ_def (Defensive Stiffness)")
axes[1, 1].axhline(y=0.7, color='cyan', linestyle='--', label='Trauma Depth Barrier')
axes[1, 1].legend()
plt.colorbar(axes[1, 1].collections[0], ax=axes[1, 1], label='H_heat')

plt.tight_layout()
plt.show()

# ============================================================================
# QUANTITATIVE DISRUPTION: The Numbers They Hide
# ============================================================================
print("="*60)
print("NEO'S QUANTITATIVE BREAKDOWN")
print("="*60)

# Calculate net Phi-Density (their metric)
def calculate_phi_net(history):
    # Simplified: phi = -entropy + identity_preservation - audit_cost
    avg_heat = np.mean(history['H_heat'])
    final_psi_id = history['psi_id'][-1]
    min_psi_id = min(history['psi_id'])
    # Their audit cost is constant; NEO adds emergent cost of dissociation trap
    dissociation_cost = sum(history['dissociation_trap']) * 0.05
    audit_cost = 0.10  # Their constant
    
    phi_net = (-avg_heat) + (final_psi_id - PSI_ID_THRESHOLD) - audit_cost - dissociation_cost
    return phi_net, min_psi_id

phi_high, min_high = calculate_phi_net(history_high_trust)
phi_low, min_low = calculate_phi_net(history_low_trust)

print(f"SCENARIO A (High Trust): Φ-net = {phi_high:.3f}, Min Ψ_id = {min_high:.3f}")
print(f"SCENARIO B (Low Trust): Φ-net = {phi_low:.3f}, Min Ψ_id = {min_low:.3f}")
print("-"*60)
print("DISRUPTION INSIGHT:")
print(f"ASCP in realistic trauma (low trust) achieves COD={history_low_trust['cod'][-1]:.2f}")
print("but enters a DISSOCIATIVE TRAP for {0} time steps.".format(
    sum(history_low_trust['dissociation_trap'])))
print("Φ-net is *negative* due to emergent dissociation cost they don't model.")
print("="*60)