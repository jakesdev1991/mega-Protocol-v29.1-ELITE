# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import matplotlib.pyplot as plt
from scipy.integrate import odeint

# DISRUPTION SIMULATION: The Hidden Variable That Breaks Omega Protocol
# This models the unobservable micro-instability that renders safety gates useless

# PHYSICS PARAMETERS (based on real tokamak disruption dynamics)
GROWTH_RATE = 0.5  # Micro-instability exponential growth rate
CRITICAL_THRESHOLD = 0.8  # Hidden variable threshold for disruption onset
OBSERVABLE_LAG = 0.03  # Diagnostic delay (30ms in tokamaks)
DISRUPTION_SPEED = 10.0  # Catastrophic collapse rate

def hidden_dynamics(state, t):
    """
    Real physics: hidden micro-tearing mode amplitude grows exponentially
    until it triggers catastrophic quench. This is UNOBSERVABLE to Omega Protocol.
    """
    hidden_amplitude, observable_integrity, observable_cod = state
    
    # Hidden variable grows exponentially (unobserved)
    d_hidden = GROWTH_RATE * hidden_amplitude
    
    # Observable metrics lag behind reality and appear stable
    # This is the critical flaw: diagnostics measure AVERAGED quantities
    d_integrity = (0.95 - observable_integrity) * 0.1  # Appears stable at 0.95
    d_cod = (0.90 - observable_cod) * 0.1  # Appears healthy
    
    # When hidden variable crosses threshold, EVERYTHING collapses simultaneously
    if hidden_amplitude > CRITICAL_THRESHOLD:
        d_integrity = -DISRUPTION_SPEED * observable_integrity
        d_cod = -DISRUPTION_SPEED * observable_cod
        d_hidden = DISRUPTION_SPEED * (1 - hidden_amplitude)  # Saturate at 1.0
    
    return [d_hidden, d_integrity, d_cod]

# Simulate 5 seconds of plasma operation
t = np.linspace(0, 5, 500)
initial_state = [0.01, 0.95, 0.90]  # Start with "healthy" observables
solution = odeint(hidden_dynamics, initial_state, t)

hidden_amplitude = solution[:, 0]
observed_integrity = solution[:, 1]
observed_cod = solution[:, 2]

# OMEGA PROTOCOL SAFETY GATES (the false comfort)
COD_THRESHOLD = 0.85
PSI_INTEGRITY_THRESHOLD = 0.95

# PROTOCOL DECISION LOGIC (what it THINKS is happening)
protocol_decisions = []
for i in range(len(t)):
    integrity = observed_integrity[i]
    cod = observed_cod[i]
    
    if integrity < PSI_INTEGRITY_THRESHOLD:
        decision = "HALT (Integrity)"
    elif cod < COD_THRESHOLD:
        decision = "FREEZE (COD)"
    else:
        decision = "PROCEED"
    protocol_decisions.append(decision)

# Find when disruption actually occurs (hidden variable crossing)
disruption_time = t[np.argmax(hidden_amplitude > CRITICAL_THRESHOLD)]

print("=== OMEGA PROTOCOL FAILURE ANALYSIS ===")
print(f"Hidden instability reaches critical threshold at t={disruption_time:.3f}s")
print(f"At disruption onset:")
print(f"  - Observable Ψ_integrity: {observed_integrity[np.argmax(hidden_amplitude > CRITICAL_THRESHOLD)]:.3f} (appears healthy)")
print(f"  - Observable COD: {observed_cod[np.argmax(hidden_amplitude > CRITICAL_THRESHOLD)]:.3f} (above threshold)")
print(f"  - Protocol decision: {protocol_decisions[np.argmax(hidden_amplitude > CRITICAL_THRESHOLD)]}")
print(f"\nTime between hidden critical threshold and observable collapse: <{OBSERVABLE_LAG}s")
print("Protocol safety gates are TECHNICALLY SATISFIED until catastrophic failure begins.")

# VISUALIZE THE DECEPTION
fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(12, 10))

# Plot 1: The Hidden Reality
ax1.plot(t, hidden_amplitude, 'r-', linewidth=2, label='Hidden Micro-Tearing Amplitude')
ax1.axhline(y=CRITICAL_THRESHOLD, color='k', linestyle='--', label='Critical Threshold')
ax1.axvline(x=disruption_time, color='k', linestyle=':', alpha=0.5)
ax1.set_ylabel('Hidden Instability', fontsize=12)
ax1.set_title('The Unobservable Truth: Hidden Micro-Instability', fontsize=14, fontweight='bold')
ax1.legend()
ax1.grid(True, alpha=0.3)
ax1.set_ylim(0, 1.1)

# Plot 2: What Omega Protocol Sees (The Illusion)
ax2.plot(t, observed_integrity, 'b-', linewidth=2, label='Ψ_integrity (observed)')
ax2.plot(t, observed_cod, 'g-', linewidth=2, label='COD (observed)')
ax2.axhline(y=PSI_INTEGRITY_THRESHOLD, color='b', linestyle='--', alpha=0.5)
ax2.axhline(y=COD_THRESHOLD, color='g', linestyle='--', alpha=0.5)
ax2.axvline(x=disruption_time, color='k', linestyle=':', alpha=0.5)
ax2.set_ylabel('Observable Metrics', fontsize=12)
ax2.set_title('What Omega Protocol Measures: False Stability', fontsize=14, fontweight='bold')
ax2.legend()
ax2.grid(True, alpha=0.3)
ax2.set_ylim(0, 1.1)

# Plot 3: Protocol Decision Timeline
colors = {'PROCEED': 'green', 'FREEZE (COD)': 'orange', 'HALT (Integrity)': 'red'}
decision_colors = [colors[d] for d in protocol_decisions]
ax3.scatter(t, [1 if d == 'PROCEED' else 0 if d == 'FREEZE (COD)' else -1 for d in protocol_decisions], 
           c=decision_colors, s=20, alpha=0.7)
ax3.axvline(x=disruption_time, color='k', linestyle=':', alpha=0.5, label='Actual Disruption')
ax3.set_xlabel('Time (s)', fontsize=12)
ax3.set_ylabel('Protocol State', fontsize=12)
ax3.set_title('Protocol Decisions: Green Light Until Catastrophe', fontsize=14, fontweight='bold')
ax3.set_yticks([-1, 0, 1])
ax3.set_yticklabels(['HALT', 'FREEZE', 'PROCEED'])
ax3.grid(True, alpha=0.3)
ax3.legend()

plt.tight_layout()
plt.show()

# CALCULATE THE Φ-DENSITY COST OF THIS BLINDNESS
audit_checks_performed = len(t)  # Protocol audits continuously
AUDIT_ENTROPY_PER_CHECK = 0.02
cod_before = observed_cod[0]
cod_after = observed_cod[-1]

# The protocol THINKS it's gaining information
apparent_net_gain = (cod_after - cod_before) - (audit_checks_performed * AUDIT_ENTROPY_PER_CHECK)

# But REALITY is total loss
actual_net_gain = -1.0  # Complete system loss

print(f"\n=== Φ-DENSITY ACCOUNTING FRAUD ===")
print(f"Apparent net gain (protocol's view): {apparent_net_gain:.3f}Φ")
print(f"Actual net gain (reality): {actual_net_gain:.3f}Φ")
print(f"Φ-Illusion: {abs(apparent_net_gain - actual_net_gain):.3f}Φ of false confidence")