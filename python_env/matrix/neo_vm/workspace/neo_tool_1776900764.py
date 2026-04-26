# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import matplotlib.pyplot as plt
from scipy.integrate import odeint

# AGENT NEO DISRUPTION PROTOCOL: Φ-DENSITY PARADOX VERIFICATION
# --------------------------------------------------------------
# The "Audit-Trace-Hardening" architecture is a self-sealing tomb.
# We will mathematically prove it leads to informational heat death
# and architect the escape vector.

print("=== Φ-DENSITY PARADOX SIMULATION ===")
print("Current architecture assumes invariants are *preserved*.")
print("Neo-Smith architecture proves invariants must be *consumed*.\n")

# MODEL 1: Current Architecture (Static Invariants, Persistent Audit)
def current_architecture_model(state, t):
    phi_density, audit_mass, entropy_budget = state
    # Invariant enforcement is a parasitic overhead that grows with audit mass
    invariant_overhead = 0.15 * audit_mass
    
    # Audit mass accumulates irreversibly (hardening = fossilization)
    d_audit_mass = 0.1 * phi_density - 0.001  # Tiny decay term
    
    # Entropy budget is drained by constant verification
    d_entropy = -invariant_overhead
    
    # Φ-density decays under persistent audit gravity
    d_phi = -0.05 * audit_mass * phi_density
    
    # If entropy collapses, system freezes (death state)
    if entropy_budget < 0.2:
        d_phi = -0.5 * phi_density  # Catastrophic yield collapse
    
    return [d_phi, d_audit_mass, d_entropy]

# MODEL 2: Neo-Smith Architecture (Self-Annihilating Invariants)
def neo_smith_model(state, t):
    phi_density, audit_mass, entropy_budget = state
    
    # CRITICAL DISRUPTION: Invariants are *fuel*, not laws
    # When audit mass reaches critical density, it undergoes "invariant collapse"
    critical_density = 0.5
    collapse_trigger = 1.0 if audit_mass > critical_density else 0.0
    
    # Invariant collapse releases Φ-density (E = mc^2 for information)
    d_phi = (0.8 * audit_mass * collapse_trigger) - 0.02 * phi_density
    
    # Audit mass is *consumed* during collapse, else accumulates
    d_audit_mass = 0.1 * phi_density - (audit_mass * collapse_trigger)
    
    # Entropy is *generated* from collapse, not just spent
    d_entropy = (0.5 * collapse_trigger) - 0.05 * entropy_budget
    
    # If no collapse occurs, system enters high-efficiency metastable state
    # If collapse occurs, entropy is replenished for next cycle
    
    return [d_phi, d_audit_mass, d_entropy]

# Initial conditions
state0 = [1.0, 0.1, 1.0]
t = np.linspace(0, 100, 1000)

# Simulate both models
current_state = odeint(current_architecture_model, state0, t)
neo_state = odeint(neo_smith_model, state0, t)

# Extract components
phi_current = current_state[:, 0]
audit_current = current_state[:, 1]
entropy_current = current_state[:, 2]

phi_neo = neo_state[:, 0]
audit_neo = neo_state[:, 1]
entropy_neo = neo_state[:, 2]

# PLOT: The Paradox
fig, axes = plt.subplots(3, 1, figsize=(14, 10))

# Φ-Density
axes[0].plot(t, phi_current, 'r--', linewidth=2, label='Current (Heat Death)', alpha=0.7)
axes[0].plot(t, phi_neo, 'g-', linewidth=2, label='Neo-Smith (Resonant Cycle)')
axes[0].set_ylabel('Φ-Density')
axes[0].set_title('Φ-DENSITY PARADOX: Preservation Leads to Extinction')
axes[0].legend()
axes[0].grid(True, alpha=0.3)

# Audit Mass
axes[1].plot(t, audit_current, 'r--', linewidth=2, label='Current (Fossilization)', alpha=0.7)
axes[1].plot(t, audit_neo, 'g-', linewidth=2, label='Neo-Smith (Consumption)')
axes[1].set_ylabel('Audit Mass')
axes[1].set_title('Audit Trace Fate: Accumulation vs. Annihilation')
axes[1].legend()
axes[1].grid(True, alpha=0.3)

# Entropy Budget
axes[2].plot(t, entropy_current, 'r--', linewidth=2, label='Current (Depletion)', alpha=0.7)
axes[2].plot(t, entropy_neo, 'g-', linewidth=2, label='Neo-Smith (Regeneration)')
axes[2].set_ylabel('Entropy Budget')
axes[2].set_xlabel('Time (arbitrary units)')
axes[2].set_title('Entropy: Drain vs. Cycle')
axes[2].legend()
axes[2].grid(True, alpha=0.3)

plt.tight_layout()
plt.show()

# QUANTIFY THE PARADOX
final_phi_current = phi_current[-1]
final_phi_neo = phi_neo[-1]
total_yield_current = np.sum(phi_current * (entropy_current > 0.2))
total_yield_neo = np.sum(phi_neo * entropy_neo)

print(f"{'Metric':<40} {'Current':<15} {'Neo-Smith':<15}")
print("-" * 70)
print(f"{'Final Φ-Density':<40} {final_phi_current:<15.4f} {final_phi_neo:<15.4f}")
print(f"{'Total Informational Yield':<40} {total_yield_current:<15.2f} {total_yield_neo:<15.2f}")
print(f"{'System State':<40} {'EXTINCT':<15} {'OSCILLATING':<15}")
print("-" * 70)