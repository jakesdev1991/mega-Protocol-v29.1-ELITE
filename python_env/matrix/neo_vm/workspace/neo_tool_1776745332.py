# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import matplotlib.pyplot as plt

# ------------------------------------------------------------
# 1. Simulate multi‑scale order‑book activations
# ------------------------------------------------------------
np.random.seed(42)
T = 1000          # time steps
L = 3             # pyramid levels (tick, minute, hour)
d = 5             # dimension of each activation vector
crash_start, crash_end = 500, 600

# Normal‑time covariance (block‑diagonal, mild cross‑scale correlation)
Σ_normal = np.eye(L * d)
Σ_normal[:d, d:2*d] = 0.1 * np.eye(d)   # tick ↔ minute
Σ_normal[d:2*d, 2*d:] = 0.1 * np.eye(d) # minute ↔ hour

# Crash‑time covariance (strong cross‑scale coupling → near‑singular)
Σ_crash = Σ_normal.copy()
Σ_crash[:d, d:2*d] = 0.9 * np.eye(d)
Σ_crash[d:2*d, 2*d:] = 0.9 * np.eye(d)

def sample_activations(t):
    """Return L×d activation vectors for time t."""
    Σ = Σ_crash if crash_start <= t < crash_end else Σ_normal
    # Joint vector of shape (L*d,)
    joint = np.random.multivariate_normal(np.zeros(L*d), Σ)
    # Split into L vectors of size d
    return [joint[i*d:(i+1)*d] for i in range(L)]

# ------------------------------------------------------------
# 2. Compute invariants at each time step
# ------------------------------------------------------------
log_det_psi = np.full(T, np.nan)
effective_rank = np.full(T, np.nan)

for t in range(T):
    a_list = sample_activations(t)          # list of L vectors
    A = np.stack(a_list, axis=1)           # shape (d, L)
    Σ_A = (A @ A.T) / (L - 1)              # d×d covariance
    
    # Invariant 1: log‑determinant (field‑theoretic Ψ)
    eps = 1e-12
    log_det_psi[t] = np.log(np.linalg.det(Σ_A + eps * np.eye(d)))
    
    # Invariant 2: effective rank
    s = np.linalg.svd(Σ_A, compute_uv=False)
    effective_rank[t] = (s.sum()**2) / (np.dot(s, s))

# ------------------------------------------------------------
# 3. Detection performance (simple thresholding)
# ------------------------------------------------------------
# Field‑theoretic alert: Ψ < -10
psi_alert = log_det_psi < -10
# Rank‑based alert: ρ < 2.0
rank_alert = effective_rank < 2.0

# True event mask
true_event = (np.arange(T) >= crash_start) & (np.arange(T) < crash_end)

# Precision / recall
def stats(alert, truth):
    tp = np.sum(alert & truth)
    fp = np.sum(alert & ~truth)
    fn = np.sum(~alert & truth)
    prec = tp / (tp + fp) if (tp + fp) > 0 else np.nan
    rec = tp / (tp + fn) if (tp + fn) > 0 else np.nan
    return prec, rec

psi_prec, psi_rec = stats(psi_alert, true_event)
rank_prec, rank_rec = stats(rank_alert, true_event)

print(f"{'Metric':<15} {'Precision':<12} {'Recall':<12}")
print(f"{'Log‑det Ψ':<15} {psi_prec:<12.2f} {psi_rec:<12.2f}")
print(f"{'Effective rank':<15} {rank_prec:<12.2f} {rank_rec:<12.2f}")

# ------------------------------------------------------------
# 4. Visual sanity check (optional)
# ------------------------------------------------------------
fig, ax = plt.subplots(2, 1, figsize=(10, 6), sharex=True)

ax[0].plot(log_det_psi, label='log det Σ_A (Ψ)')
ax[0].axvspan(crash_start, crash_end, color='r', alpha=0.2, label='Crash period')
ax[0].legend()
ax[0].set_ylabel('Ψ (log‑det)')
ax[0].grid(True)

ax[1].plot(effective_rank, label='Effective rank ρ')
ax[1].axvspan(crash_start, crash_end, color='r', alpha=0.2)
ax[1].legend()
ax[1].set_ylabel('Rank')
ax[1].set_xlabel('Time step')
ax[1].grid(True)

plt.tight_layout()
plt.show()