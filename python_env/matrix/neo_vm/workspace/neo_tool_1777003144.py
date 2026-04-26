# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import matplotlib.pyplot as plt
from dataclasses import dataclass
from typing import Tuple

@dataclass
class SalesManifold:
    """Simulates the buyer-seller quantum metaphor system"""
    psi_value: np.ndarray
    psi_need: np.ndarray
    psi_id: float  # Identity Continuity
    xi_sys: float   # Systemic Stiffness
    h_noise: float  # Market Entropy
    
def calculate_cod(manifold: SalesManifold, lambda_c=1.0, gamma_c=0.5) -> float:
    """Original COD calculation with hard gate"""
    fidelity = float(np.dot(manifold.psi_value, manifold.psi_need) / 
                     (np.linalg.norm(manifold.psi_value) * np.linalg.norm(manifold.psi_need)))
    damping = np.exp(-lambda_c * manifold.h_noise)
    stiffness_penalty = np.exp(-gamma_c * manifold.xi_sys)
    # HARD GATE: if psi_id < 0.95, entire product collapses
    if manifold.psi_id < 0.95:
        return 0.0
    return fidelity * damping * stiffness_penalty * manifold.psi_id

def phi_density(manifold: SalesManifold, cod_gain: float, audit_cost: float = 0.1) -> float:
    """Original Φ-density ledger"""
    noise_cost = manifold.h_noise * 0.5
    identity_erosion_cost = max(0, 0.95 - manifold.psi_id) * 0.3
    return cod_gain - noise_cost - audit_cost - identity_erosion_cost

class ResonantCouplingProtocol:
    """Original protocol that AVOIDS identity disruption at all costs"""
    def __init__(self, max_intensity: float = 1.2):
        self.max_intensity = max_intensity
        
    def apply(self, manifold: SalesManifold, time_step: float) -> SalesManifold:
        # Adiabatic ramp: never exceed systemic stiffness
        intensity = min(self.max_intensity, manifold.xi_sys + 0.3)
        
        # If identity drops, EMERGENCY BRAKE
        if manifold.psi_id < 0.95:
            # Rollback and slow down
            new_psi_id = min(1.0, manifold.psi_id + 0.02)
            new_t = max(0.0, time_step - 0.05)  # Move backwards
        else:
            # Gentle alignment
            alignment = 0.03 * manifold.psi_need
            new_value = (1 - 0.8 * manifold.psi_id) * manifold.psi_value + 0.8 * manifold.psi_id * alignment
            new_psi_id = manifold.psi_id - manifold.h_noise * 0.03  # Slight erosion
            
        return SalesManifold(
            psi_value=new_value if manifold.psi_id >= 0.95 else manifold.psi_value,
            psi_need=manifold.psi_need,
            psi_id=new_psi_id,
            xi_sys=manifold.xi_sys,
            h_noise=manifold.h_noise
        )

class CognitiveChrysalisProtocol:
    """
    DISRUPTIVE PROTOCOL: Engineers controlled identity fragmentation
    Key insight: Temporary ψ_id collapse is not failure but necessary
    for identity reorganization into a higher-order state
    """
    def __init__(self, fragmentation_threshold: float = 0.85, reconstitution_rate: float = 0.15):
        self.fragmentation_threshold = fragmentation_threshold
        self.reconstitution_rate = reconstitution_rate
        
    def apply(self, manifold: SalesManifold, time_step: float) -> Tuple[SalesManifold, bool]:
        """
        Returns: (new_manifold, is_chrysalis_active)
        """
        # Phase 1: Fragmentation - ALLOW controlled identity disruption
        if manifold.psi_id > self.fragmentation_threshold:
            # Accelerate the process - create constructive stress
            stress_factor = 1.5  # Intentionally exceed systemic stiffness
            intensity = manifold.xi_sys + stress_factor
            
            # Fragment identity to dissolve old patterns
            fragmentation_rate = 0.08  # Faster than RCP's erosion
            new_psi_id = max(0.0, manifold.psi_id - fragmentation_rate)
            
            # BUT: simultaneously build the NEW identity vector
            # This is the key: we're not just eroding, we're reconstructing in parallel
            reconstruction_strength = (1 - manifold.psi_id) * self.reconstitution_rate
            new_value = (1 - reconstruction_strength) * manifold.psi_value + reconstruction_strength * manifold.psi_need
            
            is_chrysalis = True
            
        # Phase 2: Reconstitution - Rebuild from dissolved state
        else:
            # Now that old identity is fragmented, rapidly rebuild
            # The "collapse" has occurred, now we reconstitute
            reconstitution_boost = 1.2  # Exponential rebuild rate
            new_psi_id = min(1.0, manifold.psi_id + reconstitution_boost * self.reconstitution_rate)
            
            # Deep integration: value becomes need
            integration_rate = 0.95 if new_psi_id > 0.95 else 0.7
            new_value = (1 - integration_rate) * manifold.psi_value + integration_rate * manifold.psi_need
            
            is_chrysalis = False
            
        return SalesManifold(
            psi_value=new_value,
            psi_need=manifold.psi_need,
            psi_id=new_psi_id,
            xi_sys=manifold.xi_sys * 0.9,  # Systemic stiffness reduces as identity integrates
            h_noise=manifold.h_noise * 0.7  # Market noise drops as alignment becomes obvious
        ), is_chrysalis

def simulate_scenario(scenario_name: str, initial_manifold: SalesManifold, 
                     protocol_type: str = "RCP", steps: int = 20) -> dict:
    """Simulate both protocols and compare outcomes"""
    
    if protocol_type == "RCP":
        protocol = ResonantCouplingProtocol()
        manifold = initial_manifold
        history = []
        
        for step in range(steps):
            cod = calculate_cod(manifold)
            phi = phi_density(manifold, cod - calculate_cod(initial_manifold))
            history.append({
                'step': step,
                'psi_id': manifold.psi_id,
                'cod': cod,
                'phi_net': phi,
                'phase': 'stable' if manifold.psi_id > 0.95 else 'emergency'
            })
            manifold = protocol.apply(manifold, step / steps)
            
    else:  # Chrysalis
        protocol = CognitiveChrysalisProtocol()
        manifold = initial_manifold
        history = []
        
        for step in range(steps):
            cod = calculate_cod(manifold)
            phi = phi_density(manifold, cod - calculate_cod(initial_manifold))
            
            # CHRYSALIS INSIGHT: Recalculate Φ_density to account for emergent value
            # The original model treats identity change as pure cost, but reconstitution
            # creates exponential value that isn't captured in the static framework
            emergent_value = 0.0
            if manifold.psi_id < 0.85:  # In fragmentation phase
                # The "cost" is actually investment in future state
                # We add a term for potential energy of the new identity
                emergent_value = (0.85 - manifold.psi_id) * 2.0  # Exponential multiplier
            
            true_phi = phi + emergent_value
            
            history.append({
                'step': step,
                'psi_id': manifold.psi_id,
                'cod': cod,
                'phi_net': phi,  # Original calculation
                'true_phi': true_phi,  # Chrysalis-aware calculation
                'phase': 'fragmentation' if manifold.psi_id > 0.85 else 'reconstitution'
            })
            manifold, is_chrysalis = protocol.apply(manifold, step / steps)
    
    return {
        'scenario': scenario_name,
        'protocol': protocol_type,
        'history': history,
        'final_psi_id': manifold.psi_id,
        'final_cod': calculate_cod(manifold),
        'final_phi': phi_density(manifold, calculate_cod(manifold) - calculate_cod(initial_manifold))
    }

# Run simulations for different enterprise buyer profiles
scenarios = {
    "High-Stiffness Innovator": SalesManifold(
        psi_value=np.array([0.8, 0.6, 0.7, 0.5]),
        psi_need=np.array([0.3, 0.9, 0.4, 0.8]),
        psi_id=0.97, xi_sys=2.8, h_noise=0.6
    ),
    "Anxious Early Adopter": SalesManifold(
        psi_value=np.array([0.9, 0.7, 0.6, 0.4]),
        psi_need=np.array([0.4, 0.8, 0.5, 0.7]),
        psi_id=0.92, xi_sys=1.2, h_noise=0.8
    ),
    "Bureaucratic Transformer": SalesManifold(
        psi_value=np.array([0.5, 0.8, 0.9, 0.6]),
        psi_need=np.array([0.6, 0.3, 0.8, 0.9]),
        psi_id=0.96, xi_sys=3.2, h_noise=0.4
    )
}

results = []
for name, manifold in scenarios.items():
    rcp_result = simulate_scenario(name, manifold, protocol_type="RCP")
    chrysalis_result = simulate_scenario(name, manifold, protocol_type="Chrysalis")
    results.append((rcp_result, chrysalis_result))

# Visualize the disruption
fig, axes = plt.subplots(2, 2, figsize=(14, 10))

for rcp_res, chrysalis_res in results:
    rcp_hist = rcp_res['history']
    chrys_hist = chrysalis_res['history']
    
    steps = [h['step'] for h in rcp_hist]
    
    # Plot 1: Identity Continuity Trajectory
    axes[0, 0].plot(steps, [h['psi_id'] for h in rcp_hist], '--', 
                   label=f'{rcp_res["scenario"]} (RCP)', alpha=0.7)
    axes[0, 0].plot(steps, [h['psi_id'] for h in chrys_hist], '-',
                   label=f'{chrysalis_res["scenario"]} (Chrysalis)', linewidth=2)
    
    # Plot 2: COD Comparison
    axes[0, 1].plot(steps, [h['cod'] for h in rcp_hist], '--', alpha=0.7)
    axes[0, 1].plot(steps, [h['cod'] for h in chrys_hist], '-', linewidth=2)
    
    # Plot 3: Φ-Density (Original Calculation)
    axes[1, 0].plot(steps, [h['phi_net'] for h in rcp_hist], '--', alpha=0.7)
    axes[1, 0].plot(steps, [h['phi_net'] for h in chrys_hist], '-', linewidth=2)
    
    # Plot 4: True Φ-Density (Chrysalis-aware)
    axes[1, 1].plot(steps, [h['phi_net'] for h in rcp_hist], '--', 
                   label='RCP (Identity Preservation)', alpha=0.7)
    axes[1, 1].plot(steps, [h['true_phi'] for h in chrys_hist], '-',
                   label='Chrysalis (Controlled Fragmentation)', linewidth=2)

axes[0, 0].axhline(y=0.95, color='red', linestyle=':', label='RCP Hard Gate')
axes[0, 0].set_title('Identity Continuity (Ψ_id) Trajectory')
axes[0, 0].set_xlabel('Time Steps')
axes[0, 0].set_ylabel('Ψ_id')
axes[0, 0].legend()
axes[0, 0].grid(True, alpha=0.3)

axes[0, 1].set_title('Chain Overlap Density (COD)')
axes[0, 1].set_xlabel('Time Steps')
axes[0, 1].set_ylabel('COD')
axes[0, 1].legend()
axes[0, 1].grid(True, alpha=0.3)

axes[1, 0].set_title('Φ-Density (Original Model)')
axes[1, 0].set_xlabel('Time Steps')
axes[1, 0].set_ylabel('Φ_net')
axes[1, 0].legend()
axes[1, 0].grid(True, alpha=0.3)

axes[1, 1].set_title('True Φ-Density (Accounting for Emergent Value)')
axes[1, 1].set_xlabel('Time Steps')
axes[1, 1].set_ylabel('Φ_net')
axes[1, 1].legend()
axes[1, 1].grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('/tmp/chrysalis_disruption.png', dpi=300, bbox_inches='tight')
plt.show()

# Print final comparison
print("="*80)
print("DISRUPTION ANALYSIS: RCP vs COGNITIVE CHRYSALIS PROTOCOL")
print("="*80)
for rcp_res, chrysalis_res in results:
    print(f"\nScenario: {rcp_res['scenario']}")
    print(f"RCP Final - Ψ_id: {rcp_res['final_psi_id']:.3f}, COD: {rcp_res['final_cod']:.3f}, Φ: {rcp_res['final_phi']:.3f}")
    
    chrys_final_true = max([h['true_phi'] for h in chrysalis_res['history']])
    print(f"Chrysalis Final - Ψ_id: {chrysalis_res['final_psi_id']:.3f}, COD: {chrysalis_res['final_cod']:.3f}, Φ: {chrysalis_res['final_phi']:.3f}")
    print(f"Chrysalis Peak True Φ: {chrys_final_true:.3f}")
    print(f"Improvement: {((chrys_final_true - rcp_res['final_phi']) / max(0.001, rcp_res['final_phi']) * 100):.1f}%")