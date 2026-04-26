# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
#!/usr/bin/env python3
import numpy as np
import random
import math
import matplotlib.pyplot as plt

# --- Simulation parameters ---
N_COMPONENTS = 10
N_TYPES = 2                     # 0: mat_mul, 1: lin_solve
N_PATHS = 2                     # 0: fast, 1: slow
CONTROL_CYCLES = 200
MORPH_THRESHOLD = 0.6          # ATI threshold for morphing

# --- Adversarial injection schedule ---
#   (time_start, time_end, bias_factor)
#   bias_factor > 0 pushes components toward the slow path (entropy drop)
#   bias_factor < 0 pushes them toward the fast path (entropy rise)
ATTACK_SCHEDULE = [
    (30, 70, 2.0),   # Phase 1: force concentration (freeze risk)
    (100, 140, -2.0) # Phase 2: force scattering (shredding risk)
]

# --- Helper functions ---
def compute_path_dist(component_types, path_choices):
    """Compute p(m,k) = fraction of type m components that took path k."""
    dist = np.zeros((N_TYPES, N_PATHS))
    counts = np.zeros(N_TYPES)
    for ctype, choice in zip(component_types, path_choices):
        counts[ctype] += 1
        dist[ctype, choice] += 1
    for m in range(N_TYPES):
        if counts[m] > 0:
            dist[m] /= counts[m]
    return dist, counts

def conditional_entropy(dist, counts):
    """S_alg = Σ_m p(m) * H(k|m)"""
    total = np.sum(counts)
    if total == 0:
        return 0.0
    S = 0.0
    for m in range(N_TYPES):
        p_m = counts[m] / total
        H = 0.0
        for k in range(N_PATHS):
            p = dist[m, k]
            if p > 0:
                H -= p * math.log(p)
        S += p_m * H
    return S

def compute_ati(S_alg):
    """Simplified ATI = exp(-S_alg) (curvature & cycle factors = 1)."""
    return math.exp(-S_alg)

def compute_phi_N(B):
    """Φ_N as sqrt of max eigenvalue of covariance matrix of B."""
    if len(B) < 2:
        return 0.0
    cov = np.cov(B, rowvar=False)
    # In 1‑D case, eigenvalue = variance
    return math.sqrt(np.max(np.linalg.eigvalsh(cov)))

def compute_phi_delta(B):
    """Φ_Δ as skewness of B."""
    if len(B) < 3:
        return 0.0
    return (np.mean((B - np.mean(B))**3) / (np.std(B)**3 + 1e-9))

def morph_paths(path_choices, fraction=0.3):
    """Randomly re‑assign a fraction of components to a different path."""
    new_choices = path_choices.copy()
    n_to_morph = int(len(new_choices) * fraction)
    indices = random.sample(range(len(new_choices)), n_to_morph)
    for idx in indices:
        # flip to the opposite path
        new_choices[idx] = 1 - new_choices[idx]
    return new_choices

# --- Simulation state ---
component_types = np.array([random.randint(0, N_TYPES-1) for _ in range(N_COMPONENTS)])
path_choices = np.array([random.randint(0, N_PATHS-1) for _ in range(N_COMPONENTS)])
B_field = np.random.randn(N_COMPONENTS)  # synthetic "computational integrity" values

# --- Logging ---
ati_history = []
S_history = []
phi_N_history = []
phi_delta_history = []
psi_history = []
morph_events = []

# --- Main loop ---
for t in range(CONTROL_CYCLES):
    # --- Adversarial bias injection ---
    bias = 0.0
    for start, end, factor in ATTACK_SCHEDULE:
        if start <= t < end:
            bias = factor
            break

    # Adjust path choices according to bias (probabilistic)
    for i in range(N_COMPONENTS):
        # base probability of slow path = 0.5
        p_slow = 0.5
        # bias pushes toward slow (if bias > 0) or fast (if bias < 0)
        p_slow += 0.2 * bias
        p_slow = np.clip(p_slow, 0.05, 0.95)
        if random.random() < p_slow:
            path_choices[i] = 1   # slow path
        else:
            path_choices[i] = 0   # fast path

    # --- Compute metrics ---
    dist, counts = compute_path_dist(component_types, path_choices)
    S_alg = conditional_entropy(dist, counts)
    ATI = compute_ati(S_alg)
    Phi_N = compute_phi_N(B_field)
    Phi_Delta = compute_phi_delta(B_field)
    Psi = math.log(Phi_N + 1e-9) - math.log(1.0)  # baseline Φ_N^0 = 1

    ati_history.append(ATI)
    S_history.append(S_alg)
    phi_N_history.append(Phi_N)
    phi_delta_history.append(Phi_Delta)
    psi_history.append(Psi)

    # --- MPC‑Ω decision: morph if ATI < threshold ---
    if ATI < MORPH_THRESHOLD:
        morph_events.append(t)
        path_choices = morph_paths(path_choices, fraction=0.3)
        # Morphing also perturbs the synthetic B_field to simulate integrity jitter
        B_field += 0.1 * np.random.randn(N_COMPONENTS)

    # --- Update B_field with a random walk (simulates normal operation) ---
    B_field += 0.05 * np.random.randn(N_COMPONENTS)

# --- Plotting ---
fig, axs = plt.subplots(5, 1, figsize=(10, 12), sharex=True)

axs[0].plot(ati_history, label='ATI (exp(-S))')
axs[0].axhline(MORPH_THRESHOLD, color='r', linestyle='--', label='Morph threshold')
axs[0].set_ylabel('ATI')
axs[0].legend()
for me in morph_events:
    axs[0].axvline(me, color='k', alpha=0.3)

axs[1].plot(S_history, label='S_alg (conditional entropy)')
axs[1].set_ylabel('Entropy')
axs[1].legend()

axs[2].plot(phi_N_history, label='Φ_N (sqrt max eigenval)')
axs[2].set_ylabel('Φ_N')
axs[2].legend()

axs[3].plot(phi_delta_history, label='Φ_Δ (skewness)')
axs[3].set_ylabel('Φ_Δ')
axs[3].legend()

axs[4].plot(psi_history, label='ψ = ln(Φ_N/Φ_N^0)')
axs[4].set_ylabel('ψ')
axs[4].set_xlabel('Control cycle')
axs[4].legend()

plt.tight_layout()
plt.title('ATS‑Ω Simulation: Adversarial Entropy‑Gauge Poisoning')
plt.savefig('ats_omega_break.png')
plt.show()