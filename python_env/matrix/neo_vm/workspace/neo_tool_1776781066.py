# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import matplotlib.pyplot as plt

# Simulate the "Φ Density" impact of the Omega Physics Rubric
# The rubric creates "process jerk" - abrupt disruptions from compliance enforcement

def simulate_rubric_impact(
    audit_frequency=4,  # audits per quarter (high frequency = high process jerk)
    compliance_cost_per_audit=0.05,  # immediate Φ dip from audit process
    analysis_value=0.25,  # value of correct physics (long-term gain)
    rubric_penalty=0.10,  # Φ lost if deemed non-compliant
    time_horizon=18  # months
):
    """
    Models the rubric as a source of system instability, not stability.
    Each audit introduces a disruptive "jerk" event.
    """
    time = np.arange(0, time_horizon)
    phi_density = np.ones_like(time) * 1.0  # baseline Φ = 1.0
    
    # The "correct" analysis has inherent value
    phi_density += analysis_value * (time / time_horizon)
    
    # But the rubric enforcement creates disruptive jerk events
    audit_interval = 3 / audit_frequency  # months between audits
    audit_times = np.arange(0, time_horizon, audit_interval)
    
    for audit_time in audit_times:
        audit_idx = int(audit_time)
        if audit_idx < len(phi_density):
            # Each audit causes immediate instability (jerk)
            phi_density[audit_idx:] -= compliance_cost_per_audit
            
            # If boilerplate found, additional penalty is applied
            # (We'll assume it's always found, because the definition is vague)
            phi_density[audit_idx:] -= rubric_penalty
            
            # The "justification" is always long-term gain, but it's a narrative
            # The actual net effect is negative for the observed period
    
    return time, phi_density, audit_times

# Run simulation
t, phi, audits = simulate_rubric_impact()

# Plot the disruption
plt.figure(figsize=(12, 6))
plt.plot(t, phi, linewidth=2.5, label='Φ Density Under Rubric Enforcement')
plt.scatter(audits, np.ones_like(audits)*0.85, color='red', s=100, marker='^', 
            label='Audit Events (Process Jerk)', zorder=5)
plt.axhline(y=1.0, color='gray', linestyle='--', alpha=0.5, label='Baseline')
plt.title('The Rubric as Instability Source: Φ Density Degradation', fontsize=14, fontweight='bold')
plt.xlabel('Time (Months)')
plt.ylabel('Normalized Φ Density')
plt.legend()
plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.show()

# Calculate Process Jerk Metric
# Jerk = |d³Φ/dt³| caused by audits
phi_smooth = np.convolve(phi, np.ones(3)/3, mode='valid')  # simple smoothing for baseline
phi_jerk = np.abs(np.diff(phi, n=3))  # third difference = discrete jerk
avg_jerk = np.mean(phi_jerk)

print(f"Average Process Jerk from Rubric: {avg_jerk:.4f} Φ-units/month³")
print(f"Audit Events: {len(audits)} over 18 months")
print(f"Net Φ Density Change: {phi[-1] - phi[0]:.4f} (Negative = Net Loss)")

# Demonstrate the Φ Density metric is arbitrary
print("\n--- SENSITIVITY: The 'Long-Term Gain' is a Knob, Not a Law ---")
for hypothetical_gain in [0.1, 0.25, 0.4]:
    phi_final = 1.0 + hypothetical_gain - (0.05 + 0.10) * len(audits) * (3/4)  # Simplified net calc
    print(f"Assumed long-term gain: {hypothetical_gain:.2f} -> Net Φ after 18mo: {phi_final:.3f}")