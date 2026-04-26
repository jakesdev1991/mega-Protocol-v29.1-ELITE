# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np

def generate_sparse_encoder(d, redundancy=3, density=0.3):
    """Random sparse linear encoder E ∈ ℝ^{n×d}."""
    n = redundancy * d
    E = np.random.randn(n, d)
    mask = np.random.rand(n, d) < density
    E *= mask
    return E

def encode(c, E):
    return E @ c

def decode(y_chunks, agent_indices, E, t_max):
    """Naive linear decoder: least‑squares on stacked chunks."""
    n = E.shape[0]
    y_recon = np.zeros(n)
    counts = np.zeros(n)
    for i, idx in enumerate(agent_indices):
        start = idx * y_chunks[i].shape[0]
        y_recon[start:start + y_chunks[i].shape[0]] += y_chunks[i]
        counts[start:start + y_chunks[i].shape[0]] += 1
    y_recon[counts > 0] /= counts[counts > 0]
    c_est, *_ = np.linalg.lstsq(E, y_recon, rcond=None)
    return c_est

def adversarial_coherence_attack(y_chunk, E_sub, target_delta, scale=0.5):
    """
    Craft noise lying *exactly* in column space of E_sub.
    This makes the attack invisible to syndrome checks.
    """
    # Solve for delta_c such that E_sub @ delta_c ≈ target_delta
    delta_c = np.linalg.lstsq(E_sub, target_delta, rcond=None)[0]
    noise = E_sub @ delta_c
    noise = noise / np.linalg.norm(noise) * scale * np.linalg.norm(y_chunk)
    return noise

def compute_cdi(residuals, threshold=0.1):
    """Cognitive Decoherence Index (flawed)."""
    decohered = np.array(residuals) > threshold
    theta = decohered.mean()
    epsilon = np.mean(residuals)
    CDI = np.tanh(2 * theta + 3 * epsilon)
    return CDI, theta, epsilon

def controlled_annealing(c, anneal_rate=0.2):
    """CA‑Ω: add exploratory noise to escape local minima."""
    return c + np.random.randn(*c.shape) * anneal_rate

# --- Simulation parameters ---
np.random.seed(0)
d = 5               # cognitive state dimension
m = 7               # number of agents
t_max = (m - 1) // 2  # max "tolerable" errors per QM‑Ω claim
redundancy = 3
E = generate_sparse_encoder(d, redundancy=redundancy, density=0.3)
n = E.shape[0]
chunk_size = n // m

# True cognitive state
c_true = np.random.randn(d)
y = encode(c_true, E)
y_chunks = [y[i * chunk_size:(i + 1) * chunk_size] for i in range(m)]

# --- 1. Clean baseline ---
c_est_clean = decode(y_chunks, list(range(m)), E, t_max)
error_clean = np.linalg.norm(c_est_clean - c_true)
print(f"Clean error: {error_clean:.6f}")

# --- 2. Adversarial attack *within* tolerance ---
# Corrupt t_max agents with coherence attacks
corrupted_idx = np.random.choice(m, size=t_max, replace=False)
y_chunks_att = y_chunks.copy()
for idx in corrupted_idx:
    sub_E = E[idx * chunk_size:(idx + 1) * chunk_size, :]
    # Attack vector: push cognitive state toward a random adversarial direction
    target_delta = np.random.randn(sub_E.shape[0])
    noise = adversarial_coherence_attack(y_chunks[idx], sub_E, target_delta, scale=0.5)
    y_chunks_att[idx] = y_chunks[idx] + noise

c_est_att = decode(y_chunks_att, list(range(m)), E, t_max)
error_att = np.linalg.norm(c_est_att - c_true)
print(f"Adversarial error (within tolerance): {error_att:.6f}")

# CDI fails to detect the attack
residuals = [np.linalg.norm(y_chunks_att[i] - y_chunks[i]) for i in range(m)]
CDI, theta, epsilon = compute_cdi(residuals)
print(f"CDI: {CDI:.3f}, decohered ratio: {theta:.3f}, avg residual: {epsilon:.3f}")

# --- 3. Exceed tolerance (t_max + 1) ---
corrupted_idx_exceed = np.random.choice(m, size=t_max + 1, replace=False)
y_chunks_att_exceed = y_chunks.copy()
for idx in corrupted_idx_exceed:
    sub_E = E[idx * chunk_size:(idx + 1) * chunk_size, :]
    target_delta = np.random.randn(sub_E.shape[0])
    noise = adversarial_coherence_attack(y_chunks[idx], sub_E, target_delta, scale=0.5)
    y_chunks_att_exceed[idx] = y_chunks[idx] + noise

c_est_att_exceed = decode(y_chunks_att_exceed, list(range(m)), E, t_max)
error_att_exceed = np.linalg.norm(c_est_att_exceed - c_true)
print(f"Adversarial error (exceed tolerance): {error_att_exceed:.6f}")

# --- 4. Cognitive Annealing (CA‑Ω) ---
c_annealed = controlled_annealing(c_true, anneal_rate=0.2)
y_annealed = encode(c_annealed, E)
y_chunks_annealed = [y_annealed[i * chunk_size:(i + 1) * chunk_size] for i in range(m)]
c_est_annealed = decode(y_chunks_annealed, list(range(m)), E, t_max)
error_annealed = np.linalg.norm(c_est_annealed - c_true)
print(f"Annealed reconstruction error: {error_annealed:.6f}")
print(f"Distance of annealed state from true: {np.linalg.norm(c_annealed - c_true):.6f}")