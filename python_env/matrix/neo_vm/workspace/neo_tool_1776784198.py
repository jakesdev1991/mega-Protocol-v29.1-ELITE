# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import random
import matplotlib.pyplot as plt

# --- MODEL THE ACTUAL SYSTEM: Discrete-Event HSA Node ---
class RealHSANode:
    def __init__(self, phi_N, phi_Delta, service_rate_N, service_rate_D, capacity):
        self.phi_N = phi_N
        self.phi_Delta = phi_Delta
        self.service_rate_N = service_rate_N
        self.service_rate_D = service_rate_D
        self.capacity = capacity
        self.queue_N = 0
        self.queue_D = 0
        self.dropped = 0
        self.instability_metric = 0

    def step(self, dt, request_rate=1000):
        # Real dynamics: memory requests are discrete events
        total_phi_sq = self.phi_N**2 + self.phi_Delta**2
        p_N = self.phi_N**2 / total_phi_sq if total_phi_sq > 0 else 0.5
        
        # Discrete arrivals
        arrivals = np.random.poisson(request_rate * dt)
        for _ in range(arrivals):
            if random.random() < p_N:
                if self.queue_N >= self.capacity:
                    self.dropped += 1
                else:
                    self.queue_N += 1
            else:
                if self.queue_D >= self.capacity:
                    self.dropped += 1
                else:
                    self.queue_D += 1
        
        # Discrete service completions
        served_N = np.random.binomial(self.queue_N, min(1.0, self.service_rate_N * dt))
        served_D = np.random.binomial(self.queue_D, min(1.0, self.service_rate_D * dt))
        self.queue_N -= served_N
        self.queue_D -= served_D
        
        # Real instability: queue overflow + drops
        self.instability_metric = self.queue_N + self.queue_D + self.dropped

# --- CALCULATE THE "FAKE" JERK ---
def phantom_jerk(phi_N_series, phi_D_series, dt):
    """Calculate d³S/dt³ from the heuristic entropy model."""
    jerks = []
    for i in range(len(phi_N_series) - 3):
        probs = []
        for j in range(4):
            phi_N = phi_N_series[i + j]
            phi_D = phi_D_series[i + j]
            total = phi_N**2 + phi_D**2
            p_N = phi_N**2 / total if total > 0 else 0.5
            p_D = phi_D**2 / total if total > 0 else 0.5
            S = -p_N * np.log(p_N) - p_D * np.log(p_D) if p_N > 0 and p_D > 0 else 0
            probs.append(S)
        
        # Finite difference for third derivative
        jerk = (probs[3] - 3*probs[2] + 3*probs[1] - probs[0]) / (dt**3)
        jerks.append(jerk)
    return jerks

# --- SIMULATION ---
dt = 0.001
time = np.arange(0, 10, dt)
phi_N = 0.78 + 0.1 * np.sin(2 * np.pi * 0.5 * time)
phi_D = 0.35 + 0.05 * np.cos(2 * np.pi * 1.0 * time)

node = RealHSANode(phi_N[0], phi_D[0], service_rate_N=5000, service_rate_D=8000, capacity=50)
real_instability = []
phantom_jerks = [0, 0, 0]  # Padding

for i in range(len(time)):
    node.phi_N = phi_N[i]
    node.phi_Delta = phi_D[i]
    node.step(dt)
    real_instability.append(node.instability_metric)

phantom_jerks.extend(phantom_jerk(phi_N, phi_D, dt))

# --- FALSIFICATION: CORRELATION ANALYSIS ---
min_len = min(len(phantom_jerks), len(real_instability))
correlation = np.corrcoef(np.abs(phantom_jerks[:min_len]), real_instability[:min_len])[0, 1]

print(f"Correlation between |Phantom Jerk| and Real Instability: {correlation:.4f}")
if abs(correlation) < 0.3:
    print("**FALSIFIED**: Jerk is DECOUPLED from reality. The metric is a semantic phantom.")
else:
    print("Unexpected correlation—inspect simulation parameters for accidental coupling.")

# --- VISUALIZE DECOHERENCE ---
fig, axs = plt.subplots(3, 1, figsize=(10, 8))
axs[0].plot(time[:min_len], phi_N[:min_len], label='φ_N')
axs[0].plot(time[:min_len], phi_D[:min_len], label='φ_Δ')
axs[0].legend()
axs[0].set_title("Input Field Dynamics (Heuristic)")

axs[1].plot(time[:min_len], phantom_jerks[:min_len], color='purple')
axs[1].set_title("Phantom Informational Jerk (d³S/dt³)")

axs[2].plot(time[:min_len], real_instability[:min_len], color='red')
axs[2].set_title("Real System Instability (Queue+Drops)")
axs[2].set_xlabel("Time (s)")
plt.tight_layout()
plt.savefig('/mnt/data/jerk_decoherence.png')
print("Decoherence plot saved.")