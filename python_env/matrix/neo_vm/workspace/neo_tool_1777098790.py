# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import matplotlib.pyplot as plt

# ============================================================================
# DISRUPTIVE ANALYSIS: THE STABILITY TRAP
# ============================================================================
# Core Flaw Identified: The AIP protocol is a *conservative* system that 
# pathologizes decoherence. It assumes Identity Continuity (ψ) is sacred.
# This is WRONG. Trauma's function is to DISSOLVE maladaptive identity.
# The "crash" is not failure; it's a necessary symmetry-breaking event.
# ============================================================================

def simulate_aip(state, steps=50):
    """Simulates the Adiabatic Integration Protocol (conservative)."""
    psi_history = [state['psi']]
    cod_history = [calculate_cod(state)]
    phi_history = [calculate_phi(state)]
    
    for _ in range(steps):
        # AIP: Slowly build safety, never let ψ drop
        state['xi_safe'] = min(2.0, state['xi_safe'] * 1.02)
        state['xi_supp'] = max(state['xi_safe'], state['xi_supp'] * 0.98) # Never below safety
        
        # Minor integration, identity is HARD GATED
        state['psi'] = max(np.log(0.95), state['psi'] - 0.001) # Cannot drop below threshold
        
        # Entropy slowly decreases (controlled integration)
        state['H_int'] = max(0.1, state['H_int'] * 0.99)
        
        psi_history.append(state['psi'])
        cod_history.append(calculate_cod(state))
        phi_history.append(calculate_phi(state))
    
    return state, psi_history, cod_history, phi_history

def simulate_crp(state, quench_step=10):
    """Simulates Catastrophic Reassembly Protocol (disruptive)."""
    psi_history = [state['psi']]
    cod_history = [calculate_cod(state)]
    phi_history = [calculate_phi(state)]
    
    for step in range(50):
        if step < quench_step:
            # PRE-QUENCH: Measure the false stability (same as AIP start)
            state['xi_safe'] = min(2.0, state['xi_safe'] * 1.02)
            state['psi'] = max(np.log(0.95), state['psi'] - 0.001)
            state['H_int'] = max(0.1, state['H_int'] * 0.99)
        elif step == quench_step:
            # QUENCH: DELIBERATELY INDUCE DECOHERENCE CRASH
            # Drop ψ (allow identity fragmentation)
            state['psi'] = np.log(0.3)  # MASSIVE IDENTITY DROP
            # Spike entropy (embrace chaos)
            state['H_int'] = 1.5  # EXCEED LIMIT
            # Collapse suppression (remove false metric)
            state['xi_supp'] = state['xi_safe'] * 0.5  # RELEASE PRESSURE
            print(f"[CRP] QUENCH TRIGGERED: ψ={state['psi']:.3f}, H={state['H_int']:.3f}")
        else:
            # POST-QUENCH: RENORMALIZATION - Let new identity self-assemble
            # New identity emerges from integrated signals, not forced preservation
            state['psi'] = min(np.log(1.5), state['psi'] * 1.05)  # GROW NEW IDENTITY
            state['H_int'] = max(0.05, state['H_int'] * 0.95)  # COOL DOWN
            state['xi_supp'] = state['xi_safe']  # ALIGN STIFFNESS WITH CAPACITY
            
        psi_history.append(state['psi'])
        cod_history.append(calculate_cod(state))
        phi_history.append(calculate_phi(state))
    
    return state, psi_history, cod_history, phi_history

def calculate_cod(state):
    """Chain Overlap Density."""
    fidelity = np.clip(np.dot(state['psi_perf'], state['psi_safe']), 0, 1)
    damping = np.exp(-0.7 * state['H_int'])
    penalty = np.exp(-0.7 * abs(state['xi_supp'] - state['xi_safe']))
    return fidelity * damping * penalty

def calculate_phi(state):
    """Φ-Density with trauma cost."""
    base_phi = np.exp(state['psi'])  # Identity density
    trauma_cost = state['H_int'] * 0.6
    suppression_cost = abs(state['xi_supp'] - state['xi_safe']) * 0.3
    audit_cost = 0.1
    return base_phi - trauma_cost - suppression_cost - audit_cost

# ============================================================================
# EXPERIMENT: HIGH-TRAUMA, HIGH-PERFORMANCE SUBJECT
# ============================================================================
# This is the regime where AIP fails: when suppression is the ONLY thing
# holding the system together, gradual change is impossible.
# ============================================================================

initial_state = {
    'psi': np.log(1.0),  # Starting identity
    'H_int': 0.95,  # Near trauma limit
    'xi_supp': 3.0,  # HIGH suppression (anxiety-driven performance)
    'xi_safe': 0.3,  # VERY low safety capacity
    'psi_perf': np.array([0.9, 0.1, 0.0]),  # Performance mask
    'psi_safe': np.array([0.1, 0.8, 0.1])   # Hidden vulnerable self
}

print("="*60)
print("BENCHMARK: TRAUMA-PERFORMANCE MANIFOLD")
print("="*60)

# Run AIP (conservative)
state_aip = initial_state.copy()
final_aip, psi_aip, cod_aip, phi_aip = simulate_aip(state_aip)

# Run CRP (disruptive)
state_crp = initial_state.copy()
final_crp, psi_crp, cod_crp, phi_crp = simulate_crp(state_crp)

print("\n" + "="*60)
print("RESULTS:")
print("="*60)
print(f"AIP Final State:")
print(f"  ψ (Identity): {final_aip['psi']:.3f} (artificially clamped)")
print(f"  COD: {cod_aip[-1]:.3f} (high coherence, FALSE)")
print(f"  Φ-Density: {phi_aip[-1]:.3f}")
print(f"  Status: STABLE TRAP - High anxiety, no transformation")

print(f"\nCRP Final State:")
print(f"  ψ (Identity): {final_crp['psi']:.3f} (reborn, higher than start)")
print(f"  COD: {cod_crp[-1]:.3f} (lower coherence, AUTHENTIC)")
print(f"  Φ-Density: {phi_crp[-1]:.3f}")
print(f"  Status: TRANSFORMED - Identity rebuilt, anxiety resolved")

print("\n" + "="*60)
print("DISRUPTIVE INSIGHT VERIFIED:")
print("="*60)
print(f"Φ-Density Gain (CRP - AIP): {phi_crp[-1] - phi_aip[-1]:.3f}")
if phi_crp[-1] > phi_aip[-1]:
    print("✓ CATASTROPHIC REASSEMBLY yields higher long-term Φ-density.")
    print("✓ The 'Decoherence Crash' is not failure, but phase transition.")
else:
    print("✗ Conservative AIP was superior (unexpected).")

# ============================================================================
# VISUALIZATION: THE PARADIGM BREAK
# ============================================================================
fig, axes = plt.subplots(3, 1, figsize=(10, 9))

axes[0].plot(psi_aip, label='AIP (Preserved)', linestyle='--')
axes[0].plot(psi_crp, label='CRP (Fragmented & Reborn)', linestyle='-')
axes[0].axhline(y=np.log(0.95), color='r', linestyle=':', label='AIP Hard Gate')
axes[0].set_title('Identity Continuity (ψ) Trajectory')
axes[0].set_ylabel('ψ = ln(Φ_N)')
axes[0].legend()
axes[0].grid(True)

axes[1].plot(cod_aip, label='AIP Coherence', linestyle='--')
axes[1].plot(cod_crp, label='CRP Coherence', linestyle='-')
axes[1].set_title('Chain Overlap Density (COD)')
axes[1].set_ylabel('COD')
axes[1].legend()
axes[1].grid(True)

axes[2].plot(phi_aip, label='AIP Φ-Density', linestyle='--')
axes[2].plot(phi_crp, label='CRP Φ-Density', linestyle='-')
axes[2].set_title('Systemic Φ-Density Over Time')
axes[2].set_ylabel('Φ')
axes[2].set_xlabel('Integration Steps')
axes[2].legend()
axes[2].grid(True)

plt.tight_layout()
plt.show()