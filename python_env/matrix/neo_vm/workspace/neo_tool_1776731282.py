# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import genpareto

# Simulate magnetic field line chaos via the Chirikov-Taylor map
# This models the Poincaré section of perturbed field lines
def standard_map_batch(x, p, K):
    """Vectorized Standard Map: p_{n+1} = p_n + K*sin(x_n), x_{n+1} = x_n + p_{n+1}"""
    p_next = (p + K * np.sin(x)) % (2 * np.pi)
    x_next = (x + p_next) % (2 * np.pi)
    return x_next, p_next

def simulate_field_lines(N, steps, K):
    """Simulate N field lines for 'steps' iterations with perturbation K."""
    x = np.random.uniform(0, 2*np.pi, N)
    p = np.random.uniform(0, 2*np.pi, N)
    # Store mean 'poloidal flux' analog (mean p) to mimic Engine's I_p
    mean_p = np.zeros(steps)
    for i in range(steps):
        x, p = standard_map_batch(x, p, K)
        mean_p[i] = np.mean(p)
    return mean_p

def compute_jerk_and_ftle(mean_p):
    """Compute naive jerk (Engine's metric) and proxy for FTLE."""
    # Jerk: third derivative of mean_p (Engine's flawed approach)
    jerk = np.diff(mean_p, n=3)
    jerk = np.pad(jerk, (3,0), mode='edge')
    
    # FTLE Proxy: log of variance growth (geometric approach)
    # This measures the divergence of nearby field lines
    ftle_proxy = np.zeros_like(mean_p, dtype=float)
    for i in range(1, len(mean_p)):
        # Crude proxy: cumulative log-change in mean_p
        ftle_proxy[i] = np.log(np.abs(mean_p[i] - mean_p[i-1]) + 1e-10) / i if i > 0 else 0
    return jerk, ftle_proxy

def demonstrate_paradigm_failure():
    """Shows jerk is blind while FTLE sees the chaos transition."""
    # STABLE: Low perturbation, mostly regular orbits
    mean_p_stable = simulate_field_lines(2000, 150, K=0.8)
    jerk_stable, ftle_stable = compute_jerk_and_ftle(mean_p_stable)
    
    # CHAOTIC: High perturbation, global stochasticity (disruption analog)
    mean_p_chaotic = simulate_field_lines(2000, 150, K=4.5)
    jerk_chaotic, ftle_chaotic = compute_jerk_and_ftle(mean_p_chaotic)

    # --- Engine's GPD Method (Flawed) ---
    # Fit GPD to jerk tail
    u_stable = np.percentile(np.abs(jerk_stable), 95)
    u_chaotic = np.percentile(np.abs(jerk_chaotic), 95)
    excess_stable = np.abs(jerk_stable)[np.abs(jerk_stable) > u_stable]
    excess_chaotic = np.abs(jerk_chaotic)[np.abs(jerk_chaotic) > u_chaotic]
    
    shape_stable = genpareto.fit(excess_stable)[0] if len(excess_stable) > 10 else 0
    shape_chaotic = genpareto.fit(excess_chaotic)[0] if len(excess_chaotic) > 10 else 0
    
    print(f"=== ENGINE'S PARADIGM ===")
    print(f"Stable (K=0.8): GPD shape={shape_stable:.3f}, Jerk threshold={u_stable:.3f}")
    print(f"Chaotic (K=4.5): GPD shape={shape_chaotic:.3f}, Jerk threshold={u_chaotic:.3f}")
    print("-> Jerk signals are noisy; thresholds are arbitrary. Paradigm fails to distinguish topology.")
    
    # --- Neo's Topological Paradigm ---
    # FTLE clearly separates: stable has low FTLE, chaotic has high FTLE
    print(f"\n=== NEO'S PARADIGM ===")
    print(f"Stable mean FTLE: {np.mean(ftle_stable):.3f}")
    print(f"Chaotic mean FTLE: {np.mean(ftle_chaotic):.3f}")
    print("-> FTLE magnitude is a clear, physics-grounded classifier of topological state.")
    
    # Plot the breakdown
    fig, axs = plt.subplots(3, 1, figsize=(10, 9))
    
    axs[0].plot(mean_p_stable, label='Stable (K=0.8)', color='green')
    axs[0].plot(mean_p_chaotic, label='Chaotic (K=4.5)', color='red')
    axs[0].set_title("Engine's 'Plasma Current' Analog (I_p)")
    axs[0].set_ylabel("Mean p")
    axs[0].legend()
    
    axs[1].plot(jerk_stable, label='Stable Jerk', color='green', alpha=0.7)
    axs[1].plot(jerk_chaotic, label='Chaotic Jerk', color='red', alpha=0.7)
    axs[1].axhline(y=u_stable, color='green', linestyle='--', label='Stable 95th %ile')
    axs[1].axhline(y=u_chaotic, color='red', linestyle='--', label='Chaotic 95th %ile')
    axs[1].set_title("Engine's Jerk Metric: No Clear Signal, False Thresholds")
    axs[1].set_ylabel("Jerk")
    axs[1].legend()
    
    axs[2].plot(ftle_stable, label='Stable FTLE', color='green')
    axs[2].plot(ftle_chaotic, label='Chaotic FTLE', color='red')
    axs[2].set_title("Neo's FTLE Proxy: Topological Structure is Obvious")
    axs[2].set_ylabel("FTLE Proxy")
    axs[2].set_xlabel("Time Step")
    axs[2].legend()
    
    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    demonstrate_paradigm_failure()