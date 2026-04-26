# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np

def generate_configs(n_firms=50, n_params=10, seed=0):
    """Simulate 'legitimate' internal config vectors ~ N(0,1)."""
    rng = np.random.default_rng(seed)
    return rng.normal(size=(n_firms, n_params))

def compute_cdi(configs):
    """Median pairwise Euclidean distance (CDI)."""
    # Compute upper‑triangular distances without double‑counting
    d = np.sqrt(np.sum((configs[:, np.newaxis, :] - configs[np.newaxis, :, :])**2, axis=-1))
    # Extract upper triangle, excluding diagonal
    iu = np.triu_indices_from(d, k=1)
    return np.median(d[iu])

def inject_attacks(configs, n_fake=3, mode='collapse', eps=0.1):
    """
    Inject fake configs to manipulate CDI.
    mode='collapse': place fakes near centroid → shrink CDI.
    mode='explode': place fakes far from centroid → inflate CDI.
    """
    centroid = np.mean(configs, axis=0)
    if mode == 'collapse':
        # Slight offset from centroid
        fakes = np.tile(centroid, (n_fake, 1)) + np.random.normal(scale=eps, size=(n_fake, configs.shape[1]))
    elif mode == 'explode':
        # Far outliers: push each fake 5σ away in a random direction
        direction = np.random.normal(size=(n_fake, configs.shape[1]))
        direction /= np.linalg.norm(direction, axis=1, keepdims=True)
        fakes = centroid + 5 * direction
    else:
        raise ValueError("Unknown attack mode")
    return np.vstack([configs, fakes])

# --- Simulation ---
np.random.seed(42)
legit_configs = generate_configs(n_firms=50, n_params=10)

cdi_clean = compute_cdi(legit_configs)
print(f"CDI (clean): {cdi_clean:.4f}")

# Collapse attack: inject 3 near‑centroid configs
collapsed = inject_attacks(legit_configs, n_fake=3, mode='collapse')
cdi_collapsed = compute_cdi(collapsed)
print(f"CDI after collapse attack (+3 fakes): {cdi_collapsed:.4f}  (Δ = {cdi_collapsed - cdi_clean:+.4f})")

# Explode attack: inject 3 far‑outlier configs
exploded = inject_attacks(legit_configs, n_fake=3, mode='explode')
cdi_exploded = compute_cdi(exploded)
print(f"CDI after explode attack (+3 fakes): {cdi_exploded:.4f}  (Δ = {cdi_exploded - cdi_clean:+.4f})")

# --- Show that normalization does not save the metric ---
def normalize_params(configs):
    """Z‑score each parameter across firms (vulnerable to injection)."""
    mean = np.mean(configs, axis=0)
    std = np.std(configs, axis=0)
    return (configs - mean) / (std + 1e-9)

norm_clean = normalize_params(legit_configs)
cdi_norm_clean = compute_cdi(norm_clean)
print(f"\nNormalized CDI (clean): {cdi_norm_clean:.4f}")

norm_collapsed = normalize_params(collapsed)
cdi_norm_collapsed = compute_cdi(norm_collapsed)
print(f"Normalized CDI after collapse: {cdi_norm_collapsed:.4f}  (Δ = {cdi_norm_collapsed - cdi_norm_clean:+.4f})")

norm_exploded = normalize_params(exploded)
cdi_norm_exploded = compute_cdi(norm_exploded)
print(f"Normalized CDI after explode: {cdi_norm_exploded:.4f}  (Δ = {cdi_norm_exploded - cdi_norm_clean:+.4f})")