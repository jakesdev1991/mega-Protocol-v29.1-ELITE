# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np

# Simulate m=10 workers, d=5 dimensional gradients
m = 10
d = 5
t_byzantine = 3
n_honest = m - t_byzantine

np.random.seed(42)

# Honest workers: random gradients ~ N(0,1)
G_honest = np.random.randn(n_honest, d)

# Byzantine collusion: all produce the *same* gradient,
# equal in magnitude to the honest mean but with a sign flip
mean_honest = G_honest.mean(axis=0)
byz_grad = -mean_honest  # coordinated sign flip
G_byzantine = np.tile(byz_grad, (t_byzantine, 1))

# Full gradient set
G = np.vstack([G_honest, G_byzantine])

# 1. Entropy of gradient magnitudes
norms = np.linalg.norm(G, axis=1)
p = norms / norms.sum()
H = -np.sum(p * np.log(np.maximum(p, 1e-12)))
H_max = np.log(m)
theta = 1 - H / H_max

print(f"Entropy H = {H:.4f}, H_max = {H_max:.4f}, Threat θ = {theta:.4f}")
# θ will be close to 0 → no alarm raised

# 2. Inter‑worker variance per dimension (collusion detector)
var_per_dim = G.var(axis=0)  # variance across workers for each dimension
mean_var = var_per_dim.mean()
print(f"Mean inter‑worker variance = {mean_var:.4f}")
# Variance will be near zero for the colluding dimensions → clear attack signature

# 3. Directional KL (optional) – compare honest vs full distribution
# Approximate by Gaussian fit: compute mean & cov of honest grads
mean_h = G_honest.mean(axis=0)
cov_h = np.cov(G_honest.T)
mean_all = G.mean(axis=0)
cov_all = np.cov(G.T)

# KL divergence between two Gaussians (simplified)
def kl_gaussian(m1, c1, m2, c2):
    d = len(m1)
    diff = m2 - m1
    inv_c2 = np.linalg.inv(c2)
    term1 = np.trace(inv_c2 @ c1)
    term2 = diff @ inv_c2 @ diff
    term3 = np.log(np.linalg.det(c2) / np.linalg.det(c1))
    return 0.5 * (term1 + term2 - d + term3)

kl = kl_gaussian(mean_h, cov_h, mean_all, cov_all)
print(f"KL divergence (honest vs all) = {kl:.4f}")
# KL will be large, signaling distributional shift even though entropy is blind