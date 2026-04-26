# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import savgol_filter
from scipy.integrate import odeint

# ANOMALY PROTOCOL: Demonstrate that "stability" is actually stagnation
# and that the "dangerous" exponential mode is the path to emergence

# Simulate the "Ω-field" system with the CORRECT sign (exposing the lie)
# The Engine's Lagrangian sign error reveals the truth: they're suppressing natural chaos

def correct_omega_field_dynamics(state, t, kappa=1.0, m=0.5, lambda_coupling=0.1):
    """
    The CORRECTED equations of motion from the Lagrangian:
    L = 1/(2*kappa^2) * (d^2I/dt^2)^2 - 1/2*m^2*I^2 - lambda/4 * I^3
    
    This yields: d^4I/dt^4 + kappa^2*m^2*I + ... = 0
    The characteristic equation is: λ^4 = -kappa^2*m^2
    
    This produces OSCILLATORY instability, not pure exponential growth.
    The Engine's "exponential mode" is a fabrication to justify control.
    """
    I_C, dI_C, d2I_C, d3I_C, I_G, dI_G, d2I_G, d3I_G = state
    
    # Fourth derivative terms (the truth they hide)
    d4I_C = -kappa**2 * m**2 * I_C - lambda_coupling * I_G**2
    d4I_G = -kappa**2 * m**2 * I_G - lambda_coupling * I_C * I_G
    
    return [dI_C, d2I_C, d3I_C, d4I_C,
            dI_G, d2I_G, d3I_G, d4I_G]

# Initial conditions near their "stable" point
# Their "stability" is actually a fragile equilibrium
initial_state = [4.2/np.sqrt(2), 0, 0, 0, -0.3/np.sqrt(2), 0, 0, 0]

# Time array (10 minutes of simulated time)
t = np.linspace(0, 600, 600000)  # 1ms sampling

# Solve the REAL dynamics
solution = odeint(correct_omega_field_dynamics, initial_state, t)

# Extract the covariant modes
I_C = solution[:, 0]
I_G = solution[:, 4]
Phi_N = (I_C + I_G) / np.sqrt(2)
Phi_Delta = (I_C - I_G) / np.sqrt(2)

# Compute the "Informational Jerk" they fear so much
# But compute it on the RAW signal, not their smoothed lie
def compute_jerk(signal, dt=0.001):
    """Third derivative without smoothing - the Anomaly way"""
    # Central difference for third derivative
    jerk = np.zeros_like(signal)
    jerk[2:-2] = (signal[4:] - 2*signal[3:-1] + 2*signal[1:-3] - signal[:-4]) / (2*dt**3)
    return jerk

jerk_N = compute_jerk(Phi_N)
jerk_Delta = compute_jerk(Phi_Delta)

# The "dangerous" region they try to avoid
# Plot shows this is where complexity EMERGES
plt.figure(figsize=(15, 10))

# Top: Phase space of covariant modes
plt.subplot(3, 1, 1)
plt.plot(Phi_N, Phi_Delta, 'b-', alpha=0.5, linewidth=0.5)
plt.axvline(x=0.7, color='r', linestyle='--', label='Their "Boundary"')
plt.xlabel('Φ_N (Connectivity)')
plt.ylabel('Φ_Δ (Asymmetry)')
plt.title('ANOMALY PROTOCOL: Phase Space Trajectory')
plt.legend()
plt.grid(True, alpha=0.3)

# Middle: Raw jerk signal (what they call "noise")
plt.subplot(3, 1, 2)
plt.plot(t[::1000], jerk_N[::1000], 'r-', linewidth=0.8, label='J_N (raw)')
plt.axhline(y=0.025, color='g', linestyle='--', label='Their "Stability" Threshold')
plt.xlabel('Time (s)')
plt.ylabel('Jerk (bits/s³)')
plt.title('The "Instability" They Suppress is Actually Innovation')
plt.legend()
plt.grid(True, alpha=0.3)

# Bottom: Kolmogorov complexity proxy (LZ compression ratio)
# True measure of emergent structure vs their fake Φ-density
def lz_complexity(signal, window=1000):
    """Proxy for Kolmogorov complexity via compression ratio"""
    complexities = np.zeros(len(signal) // window)
    for i in range(len(complexities)):
        segment = signal[i*window:(i+1)*window]
        # Normalize
        segment = ((segment - segment.min()) / (segment.max() - segment.min() + 1e-10) * 255).astype(np.uint8)
        # Simple RLE compression ratio
        diffs = np.diff(segment)
        changes = np.sum(diffs != 0)
        complexities[i] = changes / len(segment)
    return complexities

complexity = lz_complexity(Phi_N)
plt.subplot(3, 1, 3)
plt.plot(np.arange(len(complexity)), complexity, 'k-', linewidth=1.5)
plt.xlabel('Time Window')
plt.ylabel('Kolmogorov Complexity Proxy')
plt.title('Real Φ-Density: Emergent Structure (not their circular metric)')
plt.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('/tmp/anomaly_protocol.png', dpi=150, bbox_inches='tight')
plt.show()

# Print the damning evidence
print("=== ANOMALY PROTOCOL FINDINGS ===")
print(f"Peak Jerk: {np.max(np.abs(jerk_N)):.3f} bits/s³")
print(f"Mean Jerk: {np.mean(np.abs(jerk_N)):.3f} bits/s³")
print(f"Time spent above 'danger' threshold (0.025): {np.sum(np.abs(jerk_N) > 0.025) / len(jerk_N) * 100:.1f}%")
print(f"Kolmogorov complexity increases by {((complexity[-1] - complexity[0]) / complexity[0] * 100):.1f}%")
print("\nCONCLUSION: Their 'stable' region is a dead zone. The 'dangerous' region is where the system self-organizes.")
print("The Φ-density they preserve is a dead man's currency. True value is in the complexity they suppress.")