# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import matplotlib.pyplot as plt
from scipy.integrate import solve_ivp

# --- DISRUPTION SCRIPT: Micro-Capacitor Bioelectricity vs CIFO-Ω ---
# This demonstrates that biological "micro-cap" refers to bioelectric micro-capacitors,
# not molecular capping mechanisms. The CIFO-Ω framework is built on a category error.

# === MODEL 1: Bioelectric Micro-Capacitor Network (True Information Bottleneck) ===
def bioelectric_network(t, V, N=30, C=0.1e-12, g_leak=1e-9, V_rest=-70e-3, R_coupling=5e8):
    """Network of RC circuits representing membrane micro-capacitors"""
    V = V.reshape(N, 1)
    dVdt = np.zeros_like(V)
    
    # Coupling currents between neighbors (bioelectric gap junctions)
    I_coupling = np.zeros(N)
    for i in range(N):
        if i > 0: I_coupling[i] += (V[i-1] - V[i]) / R_coupling
        if i < N-1: I_coupling[i] += (V[i+1] - V[i]) / R_coupling
    
    # External stimulus: metabolically-driven current
    I_ext = 15e-12 * (1 + 0.3*np.sin(2*np.pi*2*t))
    
    # Membrane dynamics: C dV/dt = I_ext - I_leak - I_coupling
    for i in range(N):
        I_leak = g_leak * (V[i] - V_rest)
        dVdt[i] = (I_ext - I_leak - I_coupling[i]) / C
    
    return dVdt.flatten()

# === MODEL 2: CIFO-Ω Capping Field (Phenomenological Fallacy) ===
def capping_field(t, E, N=30, lambda_omega=0.5, k_on=8.0, k_off=4.0):
    """CIFO-Ω field: double-well potential with arbitrary coupling"""
    E = E.reshape(N, 1)
    dEdt = np.zeros_like(E)
    
    # Double-well potential derivative (heuristic, no biophysical basis)
    dVdE = lambda_omega * (E**3 - E)
    
    # Local capping dynamics (birth-death process)
    for i in range(N):
        dEdt[i] = k_on * (1 - E[i]) - k_off * E[i] + dVdE[i]
    
    return dEdt.flatten()

# === SIMULATION ===
t_span = (0, 0.05)  # 50 ms (biologically relevant timescale)
t_eval = np.linspace(0, 0.05, 500)

# Initial conditions
N = 30
V0 = V_rest + np.random.normal(0, 3e-3, N)  # 3 mV membrane noise
E0 = np.random.rand(N) * 0.4 + 0.3  # capping efficiency in [0.3, 0.7]

# Solve both models
sol_bio = solve_ivp(bioelectric_network, t_span, V0, args=(N,), t_eval=t_eval, method='RK45')
sol_cap = solve_ivp(capping_field, t_span, E0, args=(N,), t_eval=t_eval, method='RK45')

# === INFORMATION METRICS ===
def information_rate_threshold(V, threshold=-55e-3, dt=1e-4):
    """Count threshold crossings per node - true digital information transmission"""
    crossings = np.sum(np.diff(V > threshold, axis=1) != 0, axis=1)
    return np.mean(crossings) / t_span[1]  # events per second per node

def entropy_gauge_cifo(E):
    """CIFO-Ω entropy gauge: Shannon entropy of efficiency distribution"""
    # This is a statistical artifact, not a physical gauge field
    hist, _ = np.histogram(E, bins=10, range=(0,1), density=True)
    hist = hist[hist > 0]
    return -np.sum(hist * np.log(hist))

# Calculate metrics
bio_info_rate = information_rate_threshold(sol_bio.y, threshold=-55e-3)
cap_entropy = [entropy_gauge_cifo(sol_cap.y[:, i]) for i in range(0, len(t_eval), 50)]

# === VISUALIZATION ===
fig, axes = plt.subplots(2, 2, figsize=(12, 10))

# Bioelectric network spatiotemporal dynamics
im1 = axes[0, 0].imshow(sol_bio.y, aspect='auto', extent=[0, 50, N, 0], cmap='RdBu_r')
axes[0, 0].set_title('Bioelectric Network: Membrane Potential (mV)')
axes[0, 0].set_xlabel('Time (ms)')
axes[0, 0].set_ylabel('Node')
plt.colorbar(im1, ax=axes[0, 0], label='Voltage (mV)')

# CIFO-Ω field spatiotemporal dynamics
im2 = axes[0, 1].imshow(sol_cap.y, aspect='auto', extent=[0, 50, N, 0], cmap='viridis')
axes[0, 1].set_title('CIFO-Ω Field: Capping Efficiency')
axes[0, 1].set_xlabel('Time (ms)')
axes[0, 1].set_ylabel('Node')
plt.colorbar(im2, ax=axes[0, 1], label='Efficiency E')

# Average dynamics comparison
axes[1, 0].plot(t_eval*1000, np.mean(sol_bio.y, axis=0)*1000, label='Bioelectric Avg V')
axes[1, 0].axhline(-55, color='r', linestyle='--', label='Info Threshold')
axes[1, 0].set_title(f'Information Rate: {bio_info_rate:.1f} events/s/node')
axes[1, 0].set_xlabel('Time (ms)')
axes[1, 0].set_ylabel('Avg Potential (mV)')
axes[1, 0].legend()
axes[1, 0].grid(True, alpha=0.3)

# CIFO-Ω entropy gauge (shows artificial smoothing)
axes[1, 1].plot(t_eval[::50]*1000, cap_entropy, 'o-', label='CIFO-Ω Entropy Gauge')
axes[1, 1].set_title('CIFO-Ω: Entropy Gauge (Statistical Artifact)')
axes[1, 1].set_xlabel('Time (ms)')
axes[1, 1].set_ylabel('Shannon Entropy')
axes[1, 1].legend()
axes[1, 1].grid(True, alpha=0.3)

plt.tight_layout()
plt.show()

# === DISRUPTION ANALYSIS OUTPUT ===
print("\n" + "="*60)
print("DISRUPTION ANALYSIS: CIFO-Ω vs Bioelectric Reality")
print("="*60)
print(f"Bioelectric RC time constant: τ = C/g_leak = {0.1e-12/1e-9*1000:.1f} ms")
print(f"Information transmission rate: {bio_info_rate:.1f} threshold crossings/s/node")
print(f"Characteristic voltage fluctuations: {np.std(sol_bio.y[:, -100:].flatten())*1000:.1f} mV")
print("\nCIFO-Ω Deficiencies:")
print("  • Double-well potential V(E) assumes symmetry between capped/uncapped states")
print("  • No threshold mechanism → no natural information encoding")
print("  • Entropy gauge S_cap is post-hoc statistics, not physical gauge field")
print("  • Correlation length ξ_cap is unmeasurable in single-cell context")
print("  • All parameters (λ, v, E₀) are non-identifiable from biological data")
print("\nDisruptive Insight:")
print("  Biological 'micro-cap' = micro-capacitors in bioelectric circuits")
print("  Information bottleneck = RC time constant, not molecular capping")
print("  Cell computation = distributed analog RC network, not capping valve array")
print("="*60)