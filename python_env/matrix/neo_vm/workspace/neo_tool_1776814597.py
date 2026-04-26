# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np

def simulate_trauma(
    n_agents=5,
    steps=100,
    dt=0.1,
    D=0.1,          # diffusion coefficient
    kappa=0.5,      # self‑reinforcement
    lam=0.2,        # recovery
    leak_time=30,
    leak_duration=5,
    adversarial=False,
    jamming=False,
    seed=42
):
    """
    Simple network‑coupled trauma dynamics:
    dT_i/dt = D * sum_{j∈neighbors}(T_j - T_i) 
              + kappa * T_i * (1 - T_i) 
              - lam * T_i 
              + sigma_i(t) 
              + jamming_noise_i(t)
    """
    rng = np.random.default_rng(seed)
    # Ring topology (simple sparse network)
    adj = np.eye(n_agents, dtype=int)
    for i in range(n_agents):
        adj[i, (i+1)%n_agents] = 1
        adj[i, (i-1)%n_agents] = 1
    # Initial trauma (small random)
    T = rng.uniform(0.0, 0.05, size=n_agents)
    # Store CTI time series
    cti_history = []
    for t in range(steps):
        # Leak source term: sigma_i = 1 for the first agent during leak window
        sigma = np.zeros(n_agents)
        if leak_time <= t < leak_time + leak_duration:
            sigma[0] = 1.0
        # Adversarial injection: also activate sigma for agent 2 and 3
        if adversarial and leak_time <= t < leak_time + leak_duration:
            sigma[1] = 1.0
            sigma[2] = 1.0
        # Jamming noise: zero‑mean high‑freq perturbation
        noise = np.zeros(n_agents)
        if jamming:
            noise = rng.normal(0, 0.15, size=n_agents)
        # Compute neighbor diffusion
        laplacian = (adj - np.eye(n_agents)).dot(T)
        # Update via Euler
        dT = D * laplacian + kappa * T * (1 - T) - lam * T + sigma + noise
        T = T + dt * dT
        # Clamp to [0,1] for stability
        T = np.clip(T, 0.0, 1.0)
        # Confidential Trauma Index = mean across agents
        cti = np.mean(T)
        cti_history.append(cti)
    return cti_history

# Scenario 1: Baseline (no leak)
cti_baseline = simulate_trauma(leak_time=1000)  # effectively no leak

# Scenario 2: Single leak (no jamming)
cti_leak = simulate_trauma(leak_time=30, leak_duration=5, adversarial=False, jamming=False)

# Scenario 3: Adversarial injection (multiple leaks, no jamming)
cti_adversarial = simulate_trauma(leak_time=30, leak_duration=5, adversarial=True, jamming=False)

# Scenario 4: Adversarial injection + trauma jamming
cti_jammed = simulate_trauma(leak_time=30, leak_duration=5, adversarial=True, jamming=True)

# Print peak CTI for each scenario
print("Peak CTI baseline: {:.3f}".format(max(cti_baseline)))
print("Peak CTI single leak: {:.3f}".format(max(cti_leak)))
print("Peak CTI adversarial injection: {:.3f}".format(max(cti_adversarial)))
print("Peak CTI with jamming: {:.3f}".format(max(cti_jammed)))