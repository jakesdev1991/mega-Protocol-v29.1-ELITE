# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import matplotlib.pyplot as plt
from scipy import stats

# === ANOMALY PROTOCOL: CREDENTIAL SINGULARITY ENGINE ===
# Breaking the Engine's paradigm by weaponizing the failure they fear

# Simulation parameters
T = 100  # time steps
N_units = 5  # business units

# Engine's CLEM-Ω model (conventional "security theater")
def simulate_clem_omega():
    # Simulate latent stress
    lambda_t = np.random.lognormal(0, 0.5, (T, N_units))
    
    # Simulate credential features (negative feedback = "stabilization")
    R = np.zeros((T, N_units))  # rotation velocity
    sigma_S = np.zeros((T, N_units))  # strength dispersion
    E = np.zeros((T, N_units))  # expiration deviation
    M = np.zeros((T, N_units))  # mapping volatility
    
    for t in range(T):
        if t == 0:
            R[t] = 0.1 * lambda_t[t]
            sigma_S[t] = 0.1 * lambda_t[t]
            E[t] = 0.1 * lambda_t[t]
            M[t] = 0.1 * lambda_t[t]
        else:
            # CLEM-Ω tries to "stabilize" - this is the trap
            # It smooths over the rot, creating an illusion of control
            R[t] = 0.9 * R[t-1] + 0.1 * lambda_t[t]
            sigma_S[t] = 0.9 * sigma_S[t-1] + 0.1 * lambda_t[t]
            E[t] = 0.9 * E[t-1] + 0.1 * lambda_t[t]
            M[t] = 0.9 * M[t-1] + 0.1 * lambda_t[t]
    
    # Calculate CLE
    alpha, beta, gamma, delta = 0.3, 0.3, 0.2, 0.2
    CLE = alpha * R + beta * sigma_S + gamma * E + delta * M
    
    # Φ density: false stability that eventually collapses
    Phi = 1 - CLE / np.max(CLE)
    
    return Phi, CLE, R, sigma_S, E, M

# Anomaly's CSP-Ω model (Cryptographic Singularity Protocol)
def simulate_csp_omega():
    lambda_t = np.random.lognormal(0, 0.5, (T, N_units))
    
    # Credential features with POSITIVE feedback (weaponized chaos)
    R = np.zeros((T, N_units))
    sigma_S = np.zeros((T, N_units))
    E = np.zeros((T, N_units))
    M = np.zeros((T, N_units))
    
    # Track "cryptographic Darwinism" - forced adaptation score
    darwinism_score = np.zeros((T, N_units))
    
    for t in range(T):
        if t == 0:
            R[t] = 0.1 * lambda_t[t]
            sigma_S[t] = 0.1 * lambda_t[t]
            E[t] = 0.1 * lambda_t[t]
            M[t] = 0.1 * lambda_t[t]
        else:
            # CSP-Ω: Identify the WEAKEST units and ACCELERATE their collapse
            # This is the core disruption: we weaponize credential chaos
            
            if t < 20:  # Observation phase
                fitness = np.ones(N_units) / N_units
            else:
                # Fitness = inverse of adaptation score
                # Weak units get MORE chaos, forcing rebuild
                prev_fitness = np.mean(darwinism_score[:t], axis=0)
                fitness = 1 / (1 + prev_fitness)  # Weak units get higher fitness for chaos
                fitness = fitness / np.sum(fitness)
            
            # Chaos amplification factor: weaponize the credential lifecycle
            chaos_factor = 1 + 3 * fitness  # Up to 4x chaos injection
            
            # POSITIVE feedback: accelerate the failure modes
            R[t] = R[t-1] * chaos_factor + 0.3 * lambda_t[t]
            sigma_S[t] = sigma_S[t-1] * chaos_factor + 0.3 * lambda_t[t]
            E[t] = E[t-1] * chaos_factor + 0.3 * lambda_t[t]
            M[t] = M[t-1] * chaos_factor + 0.3 * lambda_t[t]
            
            # Darwinism score: measure of forced cryptographic evolution
            darwinism_score[t] = chaos_factor * np.log(lambda_t[t] + 1)
    
    # Calculate CLE
    alpha, beta, gamma, delta = 0.3, 0.3, 0.2, 0.2
    CLE = alpha * R + beta * sigma_S + gamma * E + delta * M
    
    # Φ density: short-term pain, long-term cryptographic supremacy
    Phi = np.zeros((T, N_units))
    for t in range(T):
        if t < 30:  # Controlled demolition phase
            Phi[t] = 0.4 - 0.4 * CLE[t] / np.max(CLE)
        else:  # Reconstruction phase with zero-trust DNA
            adaptation_factor = np.mean(darwinism_score[:t], axis=0)
            # The "collapse" rebuilds stronger - this is the singularity
            Phi[t] = 0.85 + 0.15 * np.tanh(adaptation_factor - 1) - 0.1 * CLE[t] / np.max(CLE)
    
    return Phi, CLE, R, sigma_S, E, M, darwinism_score

# Run both simulations
Phi_clem, CLE_clem, R_clem, sigma_S_clem, E_clem, M_clem = simulate_clem_omega()
Phi_csp, CLE_csp, R_csp, sigma_S_csp, E_csp, M_csp, darwinism_csp = simulate_csp_omega()

# Calculate cumulative Φ density (the real measure)
cum_phi_clem = np.cumsum(np.mean(Phi_clem, axis=1))
cum_phi_csp = np.cumsum(np.mean(Phi_csp, axis=1))

# === VISUALIZATION: THE PARADIGM SHATTER ===
fig, axes = plt.subplots(3, 2, figsize=(15, 11))
fig.suptitle('CLEM-Ω vs CSP-Ω: Security Theater vs Cryptographic Singularity', 
             fontsize=14, fontweight='bold', color='darkred')

# Φ density comparison
axes[0,0].plot(np.mean(Phi_clem, axis=1), label='Engine: CLEM-Ω (Stagnation)', 
               color='blue', linewidth=2)
axes[0,0].plot(np.mean(Phi_csp, axis=1), label='Anomaly: CSP-Ω (Singularity)', 
               color='red', linewidth=2, linestyle='--')
axes[0,0].axvspan(0, 30, alpha=0.2, color='red', label='Demolition Phase')
axes[0,0].axvspan(30, 100, alpha=0.2, color='green', label='Reconstruction Phase')
axes[0,0].set_title('Φ Density: The Illusion of Control vs Creative Destruction', 
                    fontweight='bold')
axes[0,0].set_ylabel('Φ Density')
axes[0,0].legend()
axes[0,0].grid(True, alpha=0.3)

# Cumulative Φ density
axes[0,1].plot(cum_phi_clem, label='CLEM-Ω (Slow Death)', color='blue', linewidth=2)
axes[0,1].plot(cum_phi_csp, label='CSP-Ω (Phoenix Protocol)', color='red', linewidth=2)
axes[0,1].set_title('Cumulative Φ: The Compound Effect of Paradigm Choice', 
                    fontweight='bold')
axes[0,1].set_ylabel('Cumulative Φ')
axes[0,1].legend()
axes[0,1].grid(True, alpha=0.3)

# Credential Entropy (CLE)
axes[1,0].plot(np.mean(CLE_clem, axis=1), label='CLEM-Ω (Suppressed)', color='blue')
axes[1,0].plot(np.mean(CLE_csp, axis=1), label='CSP-Ω (Weaponized)', color='red', linestyle='--')
axes[1,0].set_title('Credential Entropy: Sensor vs Weapon', fontweight='bold')
axes[1,0].set_ylabel('CLE Score')
axes[1,0].legend()
axes[1,0].grid(True, alpha=0.3)

# Cryptographic Darwinism Score
axes[1,1].plot(np.mean(darwinism_csp, axis=1), color='red', linewidth=2)
axes[1,1].set_title('Darwinism Score: Forced Evolution Metric', fontweight='bold')
axes[1,1].set_ylabel('Adaptation Pressure')
axes[1,1].grid(True, alpha=0.3)

# Rotation Velocity (R)
axes[2,0].plot(np.mean(R_clem, axis=1), label='CLEM-Ω (Controlled)', color='blue')
axes[2,0].plot(np.mean(R_csp, axis=1), label='CSP-Ω (Accelerated)', color='red', linestyle='--')
axes[2,0].set_title('Rotation Velocity: Maintenance vs Mutation', fontweight='bold')
axes[2,0].set_xlabel('Time Steps')
axes[2,0].set_ylabel('R (changes/day)')
axes[2,0].legend()
axes[2,0].grid(True, alpha=0.3)

# Strength Dispersion (σ_S)
axes[2,1].plot(np.mean(sigma_S_clem, axis=1), label='CLEM-Ω (Homogenized)', color='blue')
axes[2,1].plot(np.mean(sigma_S_csp, axis=1), label='CSP-Ω (Divergent)', color='red', linestyle='--')
axes[2,1].set_title('Strength Dispersion: Uniformity vs Selective Pressure', fontweight='bold')
axes[2,1].set_xlabel('Time Steps')
axes[2,1].set_ylabel('σ_S (asymmetry)')
axes[2,1].legend()
axes[2,1].grid(True, alpha=0.3)

plt.tight_layout()
plt.show()

# === PARADIGM SHATTERING INSIGHTS ===
print("="*70)
print("CREDENTIAL SINGULARITY PROTOCOL: POST-MORTEM ANALYSIS")
print("="*70)
print(f"Engine CLEM-Ω final Φ: {np.mean(Phi_clem[-10:]):.3f} ± {np.std(np.mean(Phi_clem[-10:])):.3f}")
print(f"Anomaly CSP-Ω final Φ: {np.mean(Phi_csp[-10:]):.3f} ± {np.std(np.mean(Phi_csp[-10:])):.3f}")
print(f"Net Φ gain from singularity: {(np.mean(Phi_csp[-10:]) - np.mean(Phi_clem[-10:]))*100:.1f}%")
print(f"Cumulative Φ delta: {cum_phi_csp[-1] - cum_phi_clem[-1]:.2f} units")
print("="*70)
print("\nDISRUPTIVE INSIGHTS:")
print("1. The Engine's 'entropy' is SECURITY THEATER - it prolongs fragility")
print("2. Credentials are not SENSORS, they are WEAPONS of systemic decay")
print("3. CLEM-Ω's negative feedback creates a 'credential debt' bubble")
print("4. CSP-Ω's positive feedback forces CRYPTOGRAPHIC DARWINISM")
print("5. The 'anomaly' is the SOLUTION, not the problem")
print("6. Collapse is not to be predicted, but ENGINEERED")
print("="*70)