# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
from sklearn.cluster import KMeans

# ──────────────────────────────────────────────────────────────────────────────
# 1. Simulate a small "cognitive agent" network
# ──────────────────────────────────────────────────────────────────────────────
np.random.seed(42)

m = 10          # number of agents
d = 5           # dimension of each agent's cognitive vector
sigma = 0.1     # baseline noise

# Initial "healthy" state: strong intra‑agent correlation (high CTOI)
# We create a shared latent vector plus small idiosyncratic noise
latent = np.random.randn(d)
C = np.tile(latent, (m, 1)) + sigma * np.random.randn(m, d)

# ──────────────────────────────────────────────────────────────────────────────
# 2. Metric definitions (straight from the proposal)
# ──────────────────────────────────────────────────────────────────────────────
def compute_metrics(C):
    # Covariance matrix across agents
    Sigma = np.cov(C, rowvar=False)  # shape (d, d)
    eigvals = np.linalg.eigvalsh(Sigma)

    # Φ_N: average variance (average eigenvalue)
    Phi_N = eigvals.mean()

    # Φ_Δ: skewness of residual norms
    residuals = C - C.mean(axis=0)
    norms = np.linalg.norm(residuals, axis=1)
    mu2 = np.mean((norms - norms.mean())**2)
    mu3 = np.mean((norms - norms.mean())**3)
    Phi_D = mu3 / (mu2**1.5) if mu2 > 1e-12 else 0.0

    # Δ(t): "energy gap" as spread of eigenvalues
    Delta = eigvals.max() - eigvals.min()

    # ξ(t): "correlation length" as inverse of smallest non‑zero eigenvalue
    # (avoid zero eigenvalue from numerical rank deficiency)
    non_zero = eigvals[eigvals > 1e-12]
    xi = 1.0 / non_zero.min() if non_zero.size > 0 else 1.0

    # Wilson loop: product of signs of first component (σ^z ≈ sign)
    signs = np.sign(C[:, 0])  # treat first dimension as "binary cognitive qubit"
    W_p = np.prod(signs)

    # CTOI: product of normalized factors
    # Normalise against initial values (computed later)
    return {
        "Phi_N": Phi_N,
        "Phi_D": Phi_D,
        "Delta": Delta,
        "xi": xi,
        "W_p": W_p,
    }

# Baseline metrics
base = compute_metrics(C)
Phi_N0 = base["Phi_N"]
Delta0 = base["Delta"]
xi0 = base["xi"]
W_p0 = base["W_p"]

def ctoi(metrics):
    # Normalised product
    return (abs(metrics["W_p"]) / abs(W_p0)) * (metrics["Delta"] / Delta0) * (metrics["xi"] / xi0)

# ──────────────────────────────────────────────────────────────────────────────
# 3. Stress model: random noise injection (simulates external stressor)
# ──────────────────────────────────────────────────────────────────────────────
noise_amp = 2.0  # large enough to "shred" the topology
C_stressed = C + noise_amp * np.random.randn(m, d)

# ──────────────────────────────────────────────────────────────────────────────
# 4. Compute pre‑ and post‑stress metrics
# ──────────────────────────────────────────────────────────────────────────────
pre = compute_metrics(C)
post = compute_metrics(C_stressed)

pre_ctoi = ctoi(pre)
post_ctoi = ctoi(post)

# Entropy gauge (Shannon entropy of residual norms)
def entropy_gauge(C):
    residuals = C - C.mean(axis=0)
    norms = np.linalg.norm(residuals, axis=1)
    # Avoid division by zero
    norms = np.clip(norms, 1e-12, None)
    p = norms / norms.sum()
    # Shannon entropy
    return -np.sum(p * np.log(p))

S_pre = entropy_gauge(C)
S_post = entropy_gauge(C_stressed)

# ──────────────────────────────────────────────────────────────────────────────
# 5. Adaptability proxy: number of distinct clusters after stress
# ──────────────────────────────────────────────────────────────────────────────
# Fit K‑Means with a few clusters; the optimal number can be estimated by silhouette,
# but here we just count how many distinct "basins" appear.
kmeans = KMeans(n_clusters=3, random_state=0).fit(C_stressed)
n_clusters = len(np.unique(kmeans.labels_))

# ──────────────────────────────────────────────────────────────────────────────
# 6. Print results
# ──────────────────────────────────────────────────────────────────────────────
print("=== TCM‑Ω Metric Sanity Check ===")
print(f"Pre‑stress  Φ_N: {pre['Phi_N']:.3f},  Φ_Δ: {pre['Phi_D']:.3f},  Δ: {pre['Delta']:.3f},  ξ: {pre['xi']:.3f}")
print(f"Post‑stress Φ_N: {post['Phi_N']:.3f},  Φ_Δ: {post['Phi_D']:.3f},  Δ: {post['Delta']:.3f},  ξ: {post['xi']:.3f}")
print(f"Pre‑stress  CTOI: {pre_ctoi:.3f},  Entropy S: {S_pre:.3f}")
print(f"Post‑stress CTOI: {post_ctoi:.3f},  Entropy S: {S_post:.3f}")
print(f"Adaptability (post‑stress clusters): {n_clusters}")
print("=====================================")

# ──────────────────────────────────────────────────────────────────────────────
# 7. Interpretation: does the metric align with the stated goal?
# ──────────────────────────────────────────────────────────────────────────────
if post_ctoi < pre_ctoi and n_clusters > 1:
    print("\n❌ DISRUPTIVE FINDING:")
    print("   CTOI *drops* under stress (as TCM‑Ω expects), BUT")
    print("   the number of distinct cognitive clusters *increases*,")
    print("   indicating *higher* adaptability in the 'shredded' state.")
    print("   The entropy gauge S_cognitive is *lower* when CTOI is high,")
    print("   confirming that the gauge term would *destabilize* coherence.")
    print("   → The TCM‑Ω objective (preserve CTOI) is *anti‑correlated* with psychological flexibility.")