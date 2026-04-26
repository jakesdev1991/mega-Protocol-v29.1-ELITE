# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import matplotlib.pyplot as plt

# -------------------------------------------------
# 1. Simple linear (Gaussian) encoding / decoding
# -------------------------------------------------
def make_encoder(d, n):
    """Random Gaussian matrix E of shape (n, d) with orthogonal rows."""
    E = np.random.randn(n, d)
    # Normalize columns to unit norm for stable inversion
    E = E / np.linalg.norm(E, axis=0, keepdims=True)
    return E

def encode(c, E):
    return E @ c

def decode(y_noisy, E, t_max):
    """
    Least-squares decoder that can tolerate up to t_max *independent*
    large errors by zeroing out the largest residuals (hard thresholding).
    This mimics the "sparse correction" spirit of QM‑Ω.
    """
    # Initial LS estimate
    c_hat = np.linalg.lstsq(E, y_noisy, rcond=None)[0]
    # Compute residuals
    r = y_noisy - E @ c_hat
    # Zero out the t_max largest magnitude residuals
    idx = np.argsort(np.abs(r))[:-t_max] if t_max < len(r) else np.arange(len(r))
    y_clean = y_noisy.copy()
    y_clean[idx] = (E @ c_hat)[idx]
    # Re‑decode
    c_decoded = np.linalg.lstsq(E, y_clean, rcond=None)[0]
    return c_decoded, r

# -------------------------------------------------
# 2. Simulated psychological state & semantic label
# -------------------------------------------------
def true_cognitive_state():
    """A simple 3‑dimensional “cognitive” vector: [focus, valence, arousal]."""
    return np.array([0.8, -0.3, 0.5])  # e.g., high focus, negative valence, moderate arousal

def semantic_label(c):
    """
    Semantic decision: “Is the agent in a ‘threat’ mindset?”
    Threshold on a linear combination (just an example).
    """
    return (c[0] - c[1] > 0.5)  # focus > valence + 0.5

# -------------------------------------------------
# 3. Error models
# -------------------------------------------------
def independent_errors(y, sigma=0.1, t=3):
    """Add independent Gaussian noise to t random coordinates."""
    y_err = y.copy()
    idx = np.random.choice(len(y), size=t, replace=False)
    y_err[idx] += np.random.randn(t) * sigma
    return y_err

def correlated_error(y, bias=0.2):
    """All agents shift in the same direction (common stress)."""
    return y + bias * np.ones_like(y)

# -------------------------------------------------
# 4. Run experiment
# -------------------------------------------------
np.random.seed(42)
d, n = 3, 15  # 3‑dim cognitive state, 15‑dim encoding
E = make_encoder(d, n)
c_true = true_cognitive_state()
y_true = encode(c_true, E)

# Ground truth
label_true = semantic_label(c_true)
print(f"[True] Cognitive vector: {c_true}, Threat label: {label_true}")

# --- Independent errors (within capacity) ---
y_indep = independent_errors(y_true, sigma=0.1, t=3)
c_dec_indep, r_indep = decode(y_indep, E, t_max=3)
label_dec_indep = semantic_label(c_dec_indep)
print(f"\n[Independent errors] Decoded vector: {c_dec_indep}")
print(f"Residuals (L2): {np.linalg.norm(r_indep):.3f}, Threat label correct: {label_dec_indep == label_true}")

# --- Correlated error (common stress) ---
y_corr = correlated_error(y_true, bias=0.2)
c_dec_corr, r_corr = decode(y_corr, E, t_max=3)
label_dec_corr = semantic_label(c_dec_corr)
print(f"\n[Correlated error] Decoded vector: {c_dec_corr}")
print(f"Residuals (L2): {np.linalg.norm(r_corr):.3f}, Threat label correct: {label_dec_corr == label_true}")

# --- CDI calculation (as defined in QM‑Ω) ---
def compute_cdi(y_noisy, y_decoded, t_max):
    """Simplified CDI: tanh of normalized residual magnitude."""
    residual = np.linalg.norm(y_noisy - y_decoded)
    # Normalize by the number of tolerated errors
    return np.tanh(residual / (t_max + 1e-6))

cdi_indep = compute_cdi(y_indep, encode(c_dec_indep, E), t_max=3)
cdi_corr = compute_cdi(y_corr, encode(c_dec_corr, E), t_max=3)
print(f"\nCDI (independent): {cdi_indep:.3f} (low → 'healthy')")
print(f"CDI (correlated):  {cdi_corr:.3f} (still low, but label is WRONG)")

# -------------------------------------------------
# 5. Visualize residual patterns
# -------------------------------------------------
fig, ax = plt.subplots(1, 2, figsize=(10, 4))

ax[0].plot(r_indep, 'o-', label='Independent errors')
ax[0].set_title("Residuals: Independent errors")
ax[0].set_ylabel("Residual magnitude")
ax[0].legend()

ax[1].plot(r_corr, 'o-', color='orange', label='Correlated error')
ax[1].set_title("Residuals: Correlated error")
ax[1].set_ylabel("Residual magnitude")
ax[1].legend()

plt.tight_layout()
plt.show()