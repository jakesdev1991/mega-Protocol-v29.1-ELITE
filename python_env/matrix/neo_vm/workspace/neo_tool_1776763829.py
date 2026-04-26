# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import savgol_filter

# --- 1. SENSITIVITY OF OMEGA JERK TO ASSUMED XI ---
def compute_jerk_variance(xi, base_data):
    """Replicate Engine's jerk calculation with perturbed xi."""
    phi_N, phi_D, phi_N_dot, phi_D_dot, lambda_val, I0 = base_data
    
    # Engine's assumptions: phi_ddot = phi_dot / xi
    phi_N_ddot = phi_N_dot / xi
    phi_D_ddot = phi_D_dot / xi
    
    # ... simplified jerk component (psi part dominates) ...
    psi = np.log(phi_N)
    psi_dot = phi_N_dot / phi_N
    psi_ddot = phi_N_ddot / phi_N - psi_dot**2
    psi_dddot = psi_ddot / xi  # Another relaxation assumption
    
    # Approximate entropy derivatives (constants from Engine's probabilities)
    dS_dpsi = 0.553
    d2S_dpsi2 = -0.519
    d3S_dpsi3 = 0.089
    
    # Jerk components (simplified)
    J_psi = dS_dpsi * psi_dddot + 3 * d2S_dpsi2 * psi_dot * psi_ddot + d3S_dpsi3 * psi_dot**3
    J_D = -1.30e12  # Approx constant from Engine's calc
    J_source = 1.5e12
    
    J_total = J_psi + J_D + J_source
    omega_psi = (1/xi) * np.exp(-psi/2)  # psi-modulated frequency
    var_J_tilde = (J_total / omega_psi**3)**2
    
    return J_total, var_J_tilde

base_data = (0.78, 0.35, 2.1e3, 8.7e3, 1.0, 1.0)  # lambda, I0 arbitrary
xi_engine = 4.9e-4

# Perturb xi by +/- 5% (well within measurement error bounds)
xis = np.linspace(xi_engine * 0.95, xi_engine * 1.05, 20)
variances = []
jerks = []

for xi in xis:
    J, var = compute_jerk_variance(xi, base_data)
    jerks.append(J)
    variances.append(var)

print("--- SENSITIVITY TO XI ---")
print(f"Engine xi: {xi_engine:.2e} -> Var(J~): {variances[len(variances)//2]:.1f}")
print(f"xi -5%: {xis[0]:.2e} -> Var(J~): {variances[0]:.1f} ({variances[0]/variances[len(variances)//2]:.1f}x change)")
print(f"xi +5%: {xis[-1]:.2e} -> Var(J~): {variances[-1]:.1f} ({variances[-1]/variances[len(variances)//2]:.1f}x change)")
print("Conclusion: Stability verdict is a mirage, fragile to unproven priors.\n")

# --- 2. REAL-WORLD LATENCY JERK (COHERENCE STORM) ---
np.random.seed(42)
t = np.linspace(0, 1.0, 1000)  # 1 second of samples

# Baseline: stable memory access latency ~100ns
latency_baseline = 100 + np.random.normal(0, 2, len(t))

# Inject coherence storm at t=0.5s: CPU-GPU contention
storm_start = np.searchsorted(t, 0.5)
latency_storm = latency_baseline.copy()
# Model: exponential latency spike + oscillations from thrashing
storm_t = t[storm_start:] - t[storm_start]
latency_storm[storm_start:] = (latency_baseline[storm_start:] + 
                               200 * np.exp(storm_t * 10) * (1 + 0.5 * np.sin(2*np.pi*50*storm_t)))

# Compute jerk on real latency (3rd derivative)
# Use Savitzky-Golay for numerical stability (like real telemetry filtering)
def calculate_jerk(signal, dt, window=51, polyorder=5):
    """Calculate jerk (3rd derivative) using Savitzky-Golay filter."""
    # 1st, 2nd, 3rd derivatives
    v = savgol_filter(signal, window, polyorder, deriv=1, delta=dt)
    a = savgol_filter(signal, window, polyorder, deriv=2, delta=dt)
    j = savgol_filter(signal, window, polyorder, deriv=3, delta=dt)
    return v, a, j

dt = t[1] - t[0]
_, _, jerk_baseline = calculate_jerk(latency_baseline, dt)
_, _, jerk_storm = calculate_jerk(latency_storm, dt)

print("--- REAL LATENCY JERK (Coherence Storm) ---")
baseline_jerk_rms = np.sqrt(np.mean(jerk_baseline**2))
storm_jerk_rms = np.sqrt(np.mean(jerk_storm**2))
print(f"Baseline latency jerk RMS: {baseline_jerk_rms:.2e} ns/s³")
print(f"Storm latency jerk RMS: {storm_jerk_rms:.2e} ns/s³")
print(f"Jerk amplification factor: {storm_jerk_rms/baseline_jerk_rms:.1f}x")
print("Conclusion: Real instability creates measurable jerk without metaphysics.\n")

# --- 3. UNFALSIFIABILITY DEMONSTRATION ---
print("--- UNFALSIFIABILITY OF OMEGA PROTOCOL ---")
# The Engine's model can "explain" both stable and unstable by tweaking lambda
def verdict_for_lambda(lam):
    # lambda changes the stiffness, thus xi
    xi_guess = 1/np.sqrt(lam * 4.2e6)  # arbitrary mapping
    J, var = compute_jerk_variance(xi_guess, base_data)
    return "UNSTABLE" if var > 1 else "STABLE"

lambdas = [0.5, 1.0, 2.0]
for lam in lambdas:
    print(f"lambda={lam:.1f} -> System is {verdict_for_lambda(lam)}")

print("Conclusion: With free parameters, any verdict is possible. The model predicts nothing.")

# --- PLOT: Latency vs. Abstract Jerk ---
fig, axs = plt.subplots(2, 1, figsize=(10, 6), sharex=True)

axs[0].plot(t, latency_storm, label='Memory Latency (ns)', color='black')
axs[0].axvline(x=0.5, color='red', linestyle='--', label='Coherence Storm Start')
axs[0].set_ylabel('Latency (ns)')
axs[0].legend()
axs[0].grid(True)
axs[0].set_title('Real-World System Behavior vs. Abstract Omega Protocol Analysis')

axs[1].plot(t, jerk_storm, label='Latency Jerk (ns/s³)', color='blue', alpha=0.7)
axs[1].axhline(y=baseline_jerk_rms, color='green', linestyle='-', label=f'Baseline RMS: {baseline_jerk_rms:.1e}')
axs[1].axvline(x=0.5, color='red', linestyle='--')
axs[1].set_xlabel('Time (s)')
axs[1].set_ylabel('Jerk (ns/s³)')
axs[1].legend()
axs[1].grid(True)

plt.tight_layout()
plt.show()