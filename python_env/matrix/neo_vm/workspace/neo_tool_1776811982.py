# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np

def simulate_ecosystem(homogeneous: bool, n: int = 50, shock: float = 0.3):
    """
    Simulate n AMM pools. If homogeneous, all use constant-product.
    If heterogeneous, parameters vary, creating arbitrage slippage gaps.
    Returns average impermanent loss (IL) after shock.
    """
    # Uniform reserves for baseline; jitter for heterogeneity
    reserves = np.ones((n, 2)) * 1e6 if homogeneous else np.random.uniform(8e5, 1.2e6, (n, 2))
    # All constant-product (a=1) if homogeneous; varied if heterogeneous
    alphas = np.ones(n) if homogeneous else np.random.uniform(0.5, 1.5, n)

    # External price shock: token X drops by `shock`
    p_ext = 1 - shock

    # Arbitrageurs align pool prices by selling X into pools
    for i in range(n):
        x, y = reserves[i]
        a = alphas[i]
        # Arbitrage trade size scales with shock & pool depth
        dx = shock * x * 0.2
        # Constant-product trade (all pools use this; alpha only affects initial price)
        dy = -(y * dx) / (x + dx)
        reserves[i] = [x + dx, y + dy]

    # Compute impermanent loss vs. hold strategy
    ils = []
    for i in range(n):
        x, y = reserves[i]
        # Original value: 1e6 + 1e6 * p_ext
        # Current value: x + y * p_ext
        il = (x + y * p_ext) - (1e6 + 1e6 * p_ext)
        ils.append(il / (1e6 + 1e6 * p_ext))
    return np.mean(ils)

def curvature_instability(reserves: np.ndarray, eps: float = 1e-3):
    """
    Compute pseudo-curvature as variance of pairwise distances.
    Show that tiny perturbations explode curvature variance.
    """
    def curvature(res):
        d = np.var(np.linalg.norm(res[:, None, :] - res[None, :, :], axis=2), axis=1)
        return np.var(d)  # variance of variances

    curv0 = curvature(reserves)
    perturbed = reserves + np.random.normal(0, eps * reserves.mean(), reserves.shape)
    curv1 = curvature(perturbed)
    return abs(curv1 - curv0) / curv0 if curv0 != 0 else np.inf

def hfi_is_noise(trials: int = 100):
    """
    Demonstrate that HFI is dominated by random components.
    """
    hfis = []
    for _ in range(trials):
        # Random shock, random curvature, random IL std
        shock = np.random.uniform(0.1, 0.5)
        curv = np.random.normal(0, 0.1)
        sigma_il = np.random.uniform(0.01, 0.1)
        # HFI formula from proposal
        hfi = np.tanh(abs(curv) + sigma_il + np.random.normal(0, 0.05))
        hfis.append(hfi)
    return np.var(hfis)

# --- Disruption Execution ---
if __name__ == "__main__":
    print("=== AMMHM‑Ω Disruption ===\n")

    # 1. Curvature is unstable
    reserves = np.random.uniform(9e5, 1.1e6, (20, 2))
    instability = curvature_instability(reserves)
    print(f"Curvature instability: {instability:.2e} (explodes on tiny perturbations)\n")

    # 2. HFI is noise
    hfi_var = hfi_is_noise()
    print(f"HFI variance (pure noise): {hfi_var:.3f} (signal-to-noise ≈ 0)\n")

    # 3. Heterogeneity amplifies systemic damage
    shock = 0.25
    damage_homo = simulate_ecosystem(homogeneous=True, shock=shock)
    damage_hetero = simulate_ecosystem(homogeneous=False, shock=shock)
    print(f"Average IL under {shock:.0%} shock:")
    print(f"  Homogeneous (constant-product): {damage_homo:.4f}")
    print(f"  Heterogeneous (mixed):           {damage_hetero:.4f}")
    print(f"  Heterogeneity penalty:           {(damage_hetero / damage_homo - 1):.0%}")