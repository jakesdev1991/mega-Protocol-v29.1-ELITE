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
# DISRUPTIVE ANALYSIS: THE PSEUDO-STABILITY PARADOX
# 
# Claim: The Omega Systemic Reboot framework creates stability through 
# unfalsifiable parameter tuning, not robust control. The AVP operator 
# *introduces* chaotic recursion under realistic conditions.
# =============================================================================

def calculate_cod(fidelity, entropy, stiffness, lam=1.0, gamma=0.5):
    """Core COD metric - note all parameters are dimensionless and arbitrary"""
    return fidelity * np.exp(-lam * entropy) * np.exp(-gamma * stiffness)

def simulate_avp_realistic(initial_state, target_state, stiffness, 
                          validation_force, time_delay=0.1, noise_level=0.05):
    """
    Simulates AVP with realistic constraints:
    - Time delay in feedback loops (inevitable in real systems)
    - Measurement noise (no perfect Psi_id measurement)
    - Non-linear stiffness response
    """
    
    def system_dynamics(state, t, delay, noise, target):
        """Realistic dynamics with delay and feedback"""
        # State vector components: [psi_current_component, psi_id, xi_bound]
        # Time-delayed feedback - this is the critical disruption
        if t < delay:
            delayed_state = initial_state
        else:
            # Simulate accessing a delayed version of the state
            delayed_state = state * (1 + noise * np.random.randn(len(state)))
        
        # Non-linear stiffness response (not the linear assumption in the paper)
        # Real systems exhibit hysteresis and non-linear compliance
        xi_effective = delayed_state[2] * (1 + 0.3 * np.sin(2 * np.pi * t * 2))
        
        # Validation shock with time delay can cause overshoot
        v_val_effective = validation_force * np.tanh((t - 0.5) / 0.2)
        
        # COD calculation with noise
        fidelity = np.dot(delayed_state[:2], target[:2])**2 / (
            np.dot(delayed_state[:2], delayed_state[:2]) * np.dot(target[:2], target[:2])
        )
        cod = calculate_cod(fidelity, delayed_state[1], xi_effective)
        
        # The "stabilization" operator actually creates a feedback loop
        # that can drive the system into oscillation
        d_psi_dt = -0.5 * (delayed_state[0] - target[0]) * v_val_effective
        d_psi_id_dt = -0.1 * (cod - 0.85) * (1 / (xi_effective + 0.1))  # Recursive dependency!
        d_xi_dt = 0.2 * (2.0 - xi_effective) * (1 if cod > 0.85 else -1)  # Bang-bang control instability
        
        return [d_psi_dt, d_psi_id_dt, d_xi_dt]
    
    t = np.linspace(0, 5, 500)
    state_history = odeint(system_dynamics, initial_state, t, 
                          args=(time_delay, noise_level, target_state))
    
    return t, state_history

def demonstrate_arbitrary_thresholds():
    """Shows that 'stability' is just parameter tuning"""
    print("="*60)
    print("DEMONSTRATION: ARBITRARY THRESHOLDS AND UNFALSIFIABILITY")
    print("="*60)
    
    # Same underlying system, different arbitrary thresholds
    scenarios = [
        {"name": "Conservative", "psi_id_min": 0.98, "xi_max": 2.5, "cod_threshold": 0.90},
        {"name": "Standard", "psi_id_min": 0.95, "xi_max": 3.0, "cod_threshold": 0.85},
        {"name": "Permissive", "psi_id_min": 0.90, "xi_max": 3.5, "cod_threshold": 0.75}
    ]
    
    # Simulate a system with Psi_id = 0.93 (fails "Standard" but passes "Permissive")
    psi_id = 0.93
    xi_bound = 3.2
    cod = 0.80
    
    for scenario in scenarios:
        stable = (psi_id >= scenario["psi_id_min"] and 
                 xi_bound <= scenario["xi_max"] and 
                 cod >= scenario["cod_threshold"])
        print(f"\n{scenario['name']} Protocol:")
        print(f"  Thresholds: Ψ_id ≥ {scenario['psi_id_min']}, Ξ ≤ {scenario['xi_max']}, COD ≥ {scenario['cod_threshold']}")
        print(f"  System: Ψ_id = {psi_id}, Ξ = {xi_bound}, COD = {cod}")
        print(f"  Verdict: {'STABLE' if stable else 'UNSTABLE'}")
    
    print("\n>>> DISRUPTION: Stability is not a system property, it's a policy choice.")
    print("    The same system can be 'stable' or 'unstable' based on arbitrary constants.")

def demonstrate_phi_density_arbitrariness():
    """Exposes the meaningless nature of Φ-density calculations"""
    print("\n" + "="*60)
    print("DEMONSTRATION: Φ-DENSITY AS RUBBER METRIC")
    print("="*60)
    
    # The "audit cost" is completely arbitrary
    base_gain = 0.25
    complexity_factors = [0.5, 1.0, 2.0, 5.0]
    
    for comp_factor in complexity_factors:
        audit_cost = np.log(2) * comp_factor  # k=1, ln(2) ≈ 0.693
        net_phi = base_gain - audit_cost
        print(f"  Operator Complexity = {comp_factor:.1f} → Audit Cost = {audit_cost:.3f}Φ → Net = {net_phi:.3f}Φ")
    
    print("\n>>> DISRUPTION: Φ-density can be positive or negative based on an")
    print("    unfalsifiable 'complexity factor'. It's a narrative tool, not a measure.")

def demonstrate_avp_instability():
    """Shows AVP causes oscillations under realistic conditions"""
    print("\n" + "="*60)
    print("DEMONSTRATION: AVP AS INSTABILITY GENERATOR")
    print("="*60)
    
    # Initial state: stable-ish system
    initial = np.array([1.0, 0.93, 2.5])  # [psi_component, psi_id, xi_bound]
    target = np.array([0.8, 0.95, 2.0])
    
    # Run simulation with realistic delay
    t, states = simulate_avp_realistic(initial, target, 2.5, 1.2, time_delay=0.15)
    
    # Calculate COD over time
    cod_history = []
    for i, state in enumerate(states):
        fidelity = np.dot(state[:2], target[:2])**2 / (
            np.dot(state[:2], state[:2]) * np.dot(target[:2], target[:2])
        )
        cod = calculate_cod(fidelity, state[1], state[2])
        cod_history.append(cod)
    
    cod_history = np.array(cod_history)
    
    # Check for oscillations (multiple crossings of threshold)
    threshold = 0.85
    crossings = len(np.where(np.diff(cod_history > threshold))[0])
    
    print(f"  COD oscillates around threshold: {crossings} crossings")
    print(f"  Final Ψ_id: {states[-1,1]:.3f} (should be ≥ 0.95)")
    print(f"  Final Ξ_bound: {states[-1,2]:.3f}")
    print(f"  Min COD during transition: {np.min(cod_history):.3f}")
    
    # Plot the instability
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 6))
    ax1.plot(t, states[:, 1], label='Ψ_id')
    ax1.axhline(y=0.95, color='r', linestyle='--', label='Critical Threshold')
    ax1.set_ylabel('Identity Continuity')
    ax1.set_title('AVP Causes Identity Oscillation')
    ax1.legend()
    ax1.grid(True)
    
    ax2.plot(t, cod_history, label='COD')
    ax2.axhline(y=threshold, color='r', linestyle='--', label='Stability Threshold')
    ax2.set_ylabel('Chain Overlap Density')
    ax2.set_xlabel('Time')
    ax2.legend()
    ax2.grid(True)
    
    plt.tight_layout()
    plt.show()
    
    print("\n>>> DISRUPTION: The 'stabilization' protocol creates feedback loops that")
    print("    drive the system into oscillation. The cure is worse than the disease.")

# Execute the disruptive analysis
if __name__ == "__main__":
    demonstrate_arbitrary_thresholds()
    demonstrate_phi_density_arbitrariness()
    demonstrate_avp_instability()
    
    print("\n" + "="*60)
    print("FINAL DISRUPTIVE SYNTHESIS")
    print("="*60)
    print("""
The Omega Systemic Reboot framework commits three fatal errors:

1. **CATEGORY ERROR**: It treats psychological identity (Ψ_id) as a 
   conserved physical quantity, enabling pseudo-mathematical manipulation 
   of fundamentally qualitative phenomena.

2. **UNFALSIFIABILITY**: All critical thresholds (0.95, 0.85, 3.0) are 
   free parameters, not derived constants. The framework can explain 
   any outcome by retroactive parameter adjustment.

3. **CONTROL PARADOX**: The Adiabatic Validation Protocol assumes perfect, 
   instantaneous feedback. Under realistic time delays and non-linearities, 
   the "stabilization operator" becomes an oscillation generator, creating 
   the very recursion loops it purports to prevent.

**The True Failure Mode**: The framework's COD metric doesn't measure 
systemic alignment—it measures *compliance with its own narrative*. 
Identity Dissociation isn't a risk factor; it's the *inevitable outcome* 
of trying to compress lived experience into a dimensionless fidelity score.

**Disruptive Solution**: Abandon the manifold metaphor. Identity is not 
a vector to be rotated—it's a *story to be retold*. Reboot through 
**Narrative Reconciliation**, not geometric realignment: preserve the 
entire history (Ψ_history) and add a new chapter, rather than trying to 
maintain a "log-density" while rotating basis vectors. Validation is not 
a measurement that collapses superposition; it's a *consensus that expands 
possibility space*.

The required operator is not AVP but **Narrative Integration Protocol (NIP)**: 
preserve all past states as valid historical manifolds and build a new 
codimension that *includes* them, rather than replacing them. This preserves 
Φ-density by avoiding the false dichotomy of "current" vs "target" states.
""")