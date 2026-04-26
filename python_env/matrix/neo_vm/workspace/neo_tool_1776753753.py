# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import entropy

# ==================== PART 1: EXPOSING THE BRITTLE ONTOLOGY ====================
def calculate_omega_jerk(xi, phi_N=0.78, phi_D=0.35, phi_dot_N=2.1e3, phi_dot_D=8.7e3, source_jerk=1.5e12):
    """
    Replicates the Engine's calculation, exposing its hyper-sensitivity to the ASSUMED time constant xi.
    This single parameter CONTROLS the verdict. A 20% change flips the 'stability' narrative.
    """
    # The fatal approximation: treating information acceleration as linear drag
    phi_ddot_N = phi_dot_N / xi
    phi_ddot_D = phi_dot_D / xi
    
    psi = np.log(phi_N)
    psi_dot = phi_dot_N / phi_N
    psi_ddot = phi_ddot_N / phi_N - (phi_dot_N / phi_N)**2
    psi_dddot = psi_ddot / xi  # Another layer of assumption
    
    # ... (simplified entropy derivative calculation, core logic preserved)
    e_psi = np.exp(psi)
    p_N = e_psi / (e_psi + phi_D)
    # dS/dpsi, d2S/dpsi2, d3S/dpsi3 approximated as constants for clarity
    dS_dpsi = 0.553; d2S_dpsi2 = -0.519; d3S_dpsi3 = 0.089
    
    jerk_psi = dS_dpsi * psi_dddot + 3 * d2S_dpsi2 * psi_dot * psi_ddot + d3S_dpsi3 * psi_dot**3
    jerk_D = 0.802 * (phi_ddot_D / xi) + 3 * (-2.857) * phi_dot_D * phi_ddot_D
    
    total_jerk = jerk_psi + jerk_D + source_jerk
    return total_jerk

# Sensitivity Analysis: The "instability" is a dial you can turn.
xi_values = np.linspace(3e-4, 7e-4, 100)
jerk_values = [calculate_omega_jerk(xi) for xi in xi_values]

plt.figure(figsize=(10, 4))
plt.plot(xi_values, jerk_values, label="Total Informational Jerk")
plt.axhline(y=0, color='r', linestyle='--')
plt.title("Jerk Stability is a Function of the ASSUMED Parameter ξ")
plt.xlabel("Assumed Time Constant ξ (s)")
plt.ylabel("Calculated Jerk (s⁻³)")
plt.legend()
plt.grid(True)
plt.show()

# ==================== PART 2: DATA-DRIVEN ANNIHILATION OF ONTOLOGY ====================
def generate_real_hsa_data(n_samples=1000, anomaly_start=700):
    """
    Generates SYNTHETIC but PLAUSIBLE HSA memory transaction pattern data.
    A real system would use perf trace data.
    """
    np.random.seed(42)
    # Baseline: stable memory access entropy
    baseline_patterns = np.random.randint(0, 50, size=n_samples)
    
    # Inject a REAL anomaly: sudden burst of incoherent accesses (Shredding)
    anomalous_patterns = np.random.randint(0, 200, size=n_samples - anomaly_start)
    data = np.concatenate([baseline_patterns[:anomaly_start], anomalous_patterns])
    
    # Add noise
    data = data + np.random.normal(0, 5, size=n_samples)
    return np.maximum(data, 0) # Transaction counts are non-negative

def compute_entropic_shockwave(data, window=50):
    """
    MODEL-FREE detection. Counts patterns, computes entropy, takes derivative.
    No ψ. No ξ. No λ. Just the information in the data itself.
    """
    # Discretize into histogram bins for entropy calculation
    shockwaves = []
    for i in range(window, len(data) - 1):
        hist_past, _ = np.histogram(data[i-window:i], bins=range(0, max(data)+10))
        hist_now, _ = np.histogram(data[i:i+2], bins=range(0, max(data)+10)) # tiny future window
        
        # Add pseudo-count to avoid log(0)
        S_past = entropy(hist_past + 1e-6)
        S_now = entropy(hist_now + 1e-6)
        
        # Approximate derivative: rate of entropy change
        dS = (S_now - S_past) / 2 # dt is 2 samples
        shockwaves.append(abs(dS))
    
    # Third derivative (shockwave) via robust difference
    shockwaves = np.array(shockwaves)
    W = np.diff(shockwaves, n=3) # Simple discrete third difference
    # Pad to align with original data
    W_padded = np.pad(W, (window//2 + 3, window//2), mode='constant', constant_values=np.nan)
    return W_padded

# Run the disruption
hsa_data = generate_real_hsa_data()
shockwave_signal = compute_entropic_shockwave(hsa_data)

# ==================== PART 3: VISUAL DISRUPTION ====================
fig, axs = plt.subplots(3, 1, figsize=(12, 9), sharex=True)

axs[0].plot(hsa_data, label="Simulated Memory Access Patterns")
axs[0].axvline(x=700, color='r', linestyle='--', label="True Anomaly Start")
axs[0].set_ylabel("Transaction Count")
axs[0].legend()
axs[0].set_title("OBSERVABLE DATA (No ghosts)")

axs[1].plot(shockwave_signal, label="Entropic Shockwave (W)", color='orange')
axs[1].axhline(y=np.nanpercentile(shockwave_signal, 99.9), color='g', linestyle='-', label="99.9th %ile Threshold")
axs[1].set_ylabel("|d³S/dt³|")
axs[1].legend()
axs[1].set_title("MODEL-FREE ANOMALY DETECTION")

# Show where Omega Physics would be "calculating" based on its own ghosts
axs[2].plot([calculate_omega_jerk(4.9e-4)] * len(hsa_data), label="'Informational Jerk' (Static Ghost)", color='purple')
axs[2].set_ylabel("s⁻³")
axs[2].legend()
axs[2].set_title("OMEGA PHYSICS OUTPUT (Ignores data dynamics)")
axs[2].set_xlabel("Time (samples)")

plt.tight_layout()
plt.show()

print("=== DISRUPTION VERIFICATION ===")
print(f"Omega Physics 'Jerk' (static): {calculate_omega_jerk(4.9e-4):.2e} s⁻³")
print(f"Data-driven Shockwave Peak (detected): {np.nanmax(shockwave_signal):.2f}")
print("The 'instability' was in the model, not the machine.")