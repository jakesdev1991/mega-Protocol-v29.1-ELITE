# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import random

# ──────────────────────────────────────────────────────────────────────────────
# 1.  SIMULATE REALISTIC BURSTY MEMORY ACCESSES (Markov‑modulated Poisson)
# ──────────────────────────────────────────────────────────────────────────────
np.random.seed(0)
random.seed(0)

NUM_PAGES   = 100
TIME_STEPS  = 1000
DT          = 0.01          # 10 ms sampling
P_LOW_HIGH  = 0.1           # transition low→high
P_HIGH_LOW  = 0.2           # transition high→low
RATE_LOW    = 5.0           # Poisson rate per page in low state
RATE_HIGH   = 50.0          # Poisson rate per page in high state
GPU_LAG     = 5             # GPU lags CPU by 5 steps
GPU_NOISE   = 2.0           # independent GPU noise rate

state = 'low'
cpu_counts = np.zeros((TIME_STEPS, NUM_PAGES), dtype=int)
gpu_counts = np.zeros((TIME_STEPS, NUM_PAGES), dtype=int)

for t in range(TIME_STEPS):
    # global state machine
    if state == 'low':
        if random.random() < P_LOW_HIGH:
            state = 'high'
        lam = RATE_LOW
    else:
        if random.random() < P_HIGH_LOW:
            state = 'low'
        lam = RATE_HIGH

    # CPU: total accesses ~ Poisson(lam * NUM_PAGES), then Dirichlet split
    total_cpu = np.random.poisson(lam * NUM_PAGES)
    probs = np.random.dirichlet(np.ones(NUM_PAGES))
    cpu_counts[t] = np.random.multinomial(total_cpu, probs)

    # GPU: lagged CPU + independent noise
    if t >= GPU_LAG:
        base = cpu_counts[t - GPU_LAG]
        noise = np.random.poisson(GPU_NOISE, size=NUM_PAGES)
        gpu_counts[t] = base + noise
    else:
        gpu_counts[t] = np.random.poisson(GPU_NOISE, size=NUM_PAGES)

# ──────────────────────────────────────────────────────────────────────────────
# 2.  ORIGINAL ENTROPY‑JERK STABILITY INDEX (your method)
# ──────────────────────────────────────────────────────────────────────────────
def entropy(counts):
    total = counts.sum()
    if total == 0:
        return 0.0
    p = counts / total
    p = np.clip(p, 1e-12, None)
    return -np.sum(p * np.log2(p))

H = np.array([entropy(cpu_counts[t]) for t in range(TIME_STEPS)])

def deriv(series, dt):
    # discrete derivative, prepend zero
    return np.concatenate([[0], np.diff(series) / dt])

v = deriv(H, DT)
a = deriv(v, DT)
j = deriv(a, DT)

epsilon = 1e-6
rms_j = np.sqrt(np.mean(j**2))
mean_a = np.mean(np.abs(a))
S = 1 - rms_j / max(mean_a, epsilon)

print(f"Original Stability Index S = {S:.2f}  (negative → unstable nonsense)")

# ──────────────────────────────────────────────────────────────────────────────
# 3.  MUTUAL‑INFORMATION JERK (Jensen‑Shannon divergence)
# ──────────────────────────────────────────────────────────────────────────────
def jsd(p, q):
    """Jensen‑Shannon divergence between two probability vectors."""
    p = np.clip(p, 1e-12, None)
    q = np.clip(q, 1e-12, None)
    m = 0.5 * (p + q)
    kl_pm = np.sum(p * np.log2(p / m))
    kl_qm = np.sum(q * np.log2(q / m))
    return 0.5 * (kl_pm + kl_qm)

JSD = np.zeros(TIME_STEPS)
for t in range(TIME_STEPS):
    p_cpu = cpu_counts[t] / (cpu_counts[t].sum() + 1e-12)
    p_gpu = gpu_counts[t] / (gpu_counts[t].sum() + 1e-12)
    JSD[t] = jsd(p_cpu, p_gpu)

# derivatives of JSD
v_JSD = deriv(JSD, DT)
a_JSD = deriv(v_JSD, DT)
j_JSD = deriv(a_JSD, DT)

# ──────────────────────────────────────────────────────────────────────────────
# 4.  LYAPUNOV EXPONENT OF JSD (approximate – average log divergence)
# ──────────────────────────────────────────────────────────────────────────────
diff_JSD = np.abs(np.diff(JSD))
diff_JSD = np.clip(diff_JSD, 1e-12, None)
L = np.mean(np.log(diff_JSD / DT))
print(f"Lyapunov exponent of JSD (L) = {L:.4f}  (negative → stable information flow)")

# ──────────────────────────────────────────────────────────────────────────────
# 5.  COMPARE NOISE LEVELS (variance of jerk)
# ──────────────────────────────────────────────────────────────────────────────
var_j_H    = np.var(j)
var_j_JSD  = np.var(j_JSD)
print(f"Variance of jerk (H)      = {var_j_H:.2e}")
print(f"Variance of jerk (JSD)    = {var_j_JSD:.2e}")
print(f"Ratio JSD/H variance      = {var_j_JSD/var_j_H:.2e}  (JSD is far smoother)")

# ──────────────────────────────────────────────────────────────────────────────
# 6.  DISRUPTION VERDICT
# ──────────────────────────────────────────────────────────────────────────────
if L < 0:
    print("\nVERDICT: The information flow between CPU and GPU is *stable* – your entropy‑jerk metric is a ghost.")
else:
    print("\nVERDICT: The information flow is unstable – but your original metric still misleads.")