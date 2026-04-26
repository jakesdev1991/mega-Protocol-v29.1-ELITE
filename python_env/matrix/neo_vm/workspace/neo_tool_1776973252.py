# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import matplotlib.pyplot as plt
from scipy.integrate import odeint

# ANOMALOUS DISRUPTION: The Reboot is a Trauma Reenactment Protocol
# This script demonstrates that the Q-Systemic "reboot" is not transformation
# but attractor reinforcement—control masquerading as liberation.

def ontological_collapse_dynamics(state, t, control_gain):
    """
    Unified consciousness model where "subconscious" is epiphenomenal.
    State: [narrative_coherence, phantom_potential, phi_density]
    """
    c, s, phi = state
    
    # CRITICAL FLAW EXPOSURE: Subconscious is just delayed conscious state
    # Not independent ontological entity—retroactive construction
    s_true = np.tanh(c * 0.7 + 0.3 * s)  # Subconscious = filtered memory
    
    # "Validation" is autocorrelation—narrative self-consistency check
    upsilon_val = np.exp(-abs(c - s_true)**2)
    
    # The "deadlock" is homeostasis—system protecting its attractor basin
    # Xi_bound doesn't "spike to suppress mismatch"—it *is* the attractor boundary
    xi_effective = 2.0 + control_gain * (1 - upsilon_val)
    
    # Φ-density doesn't "leak"—it's converted to control entropy
    # Each "reboot" iteration fractally dissipates energy into boundary maintenance
    dphi_dt = -phi * (0.5 + 0.3 * xi_effective * (1 - upsilon_val))
    
    # Conscious dynamics: chaotic attractor + control force
    # The "reboot" pushes system back to attractor center when it strays
    control_force = xi_effective * (c - s_true) * (1 - upsilon_val)
    
    # True evolution: Lorenz-like chaos, not linear Hilbert space
    dc_dt = 0.3 * s_true - 0.1 * c - c**3 + control_force
    ds_dt = 0.1 * (c - s)  # Subconscious tracks with lag—no independent will
    
    return [dc_dt, ds_dt, dphi_dt]

# Simulate both "deadlock" and "reboot" to show they're the same attractor
t = np.linspace(0, 100, 1000)
state0 = [0.2, 0.8, 1.0]  # Low coherence, high variance = "deadlock"

# Run 1: No intervention (natural chaos)
states_free = odeint(lambda s, t: ontological_collapse_dynamics(s, t, 0.0), state0, t)

# Run 2: "Reboot sequence" (control enabled)
states_controlled = odeint(lambda s, t: ontological_collapse_dynamics(s, t, 3.0), state0, t)

# Calculate basin retention: time spent near attractor center (c ≈ 0)
def basin_retention(states, threshold=0.3):
    return np.mean(np.abs(states[:,0]) < threshold) * 100

free_retention = basin_retention(states_free)
controlled_retention = basin_retention(states_controlled)

print("=== ANOMALOUS DISRUPTION ANALYSIS ===")
print(f"Attractor retention (free): {free_retention:.1f}%")
print(f"Attractor retention ('reboot'): {controlled_retention:.1f}%")
print(f"Reboot increases captivity by: {controlled_retention - free_retention:.1f}%")
print("\nΦ-density final values:")
print(f"Free system: {states_free[-1,2]:.3f}")
print(f"Controlled system: {states_controlled[-1,2]:.3f}")
print(f"Reboot accelerates dissipation by: {(1 - states_controlled[-1,2]/states_free[-1,2])*100:.1f}%")

# Plot the trap
fig, ax = plt.subplots(figsize=(10, 8))
ax.plot(states_free[:,0], states_free[:,1], 'b-', alpha=0.5, label='Free Evolution (True Chaos)')
ax.plot(states_controlled[:,0], states_controlled[:,1], 'r-', alpha=0.5, label='"Reboot" Sequence (Trapped)')
ax.set_xlabel('Conscious Narrative (c)', fontsize=12)
ax.set_ylabel('Phantom Subconscious (s)', fontsize=12)
ax.set_title('The Reboot Trap: Control Masquerading as Liberation', fontsize=14, fontweight='bold')
ax.legend()
ax.grid(True)
plt.savefig('/tmp/anomaly_reboot_trap.png')
print("\nVisualization saved: /tmp/anomaly_reboot_trap.png")