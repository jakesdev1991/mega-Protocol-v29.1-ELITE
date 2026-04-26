# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import math

# ──────────────────────────────────────────────────────────────────────────────
# 1. Synthetic data generator
# ──────────────────────────────────────────────────────────────────────────────
def generate_data(N=200, seed=0):
    rng = np.random.default_rng(seed)
    # Latent "true" function values (e.g., promoter strength)
    true = rng.normal(loc=0.0, scale=1.0, size=N)
    # Assign to 3 functional terms by quantiles
    q = np.quantile(true, [0.3, 0.7])
    terms = np.where(true < q[0], "weak",
                     np.where(true < q[1], "medium", "strong"))
    # Version tags (20% old)
    version = np.where(rng.random(N) < 0.2, "v1", "v2")
    return true, terms, version

# ──────────────────────────────────────────────────────────────────────────────
# 2. ALI components (naïve linear model)
# ──────────────────────────────────────────────────────────────────────────────
def mapping_entropy(terms):
    _, counts = np.unique(terms, return_counts=True)
    probs = counts / counts.sum()
    return -np.sum(probs * np.log(probs))

def annotation_variance(true, terms):
    # Weighted average of per‑term variances
    uniq, inv = np.unique(terms, return_inverse=True)
    var = np.array([np.var(true[inv == i]) for i in range(len(uniq))])
    weights = np.array([np.sum(inv == i) for i in range(len(uniq))]) / len(true)
    return np.sum(weights * var)

def version_skew(version):
    return np.mean(version == "v1")

def centrality(terms):
    # Fraction of parts in the most frequent term
    _, counts = np.unique(terms, return_counts=True)
    return np.max(counts) / len(terms)

def ali(true, terms, version, w=(1,1,1,1)):
    H = mapping_entropy(terms)
    sigma2 = annotation_variance(true, terms)
    Vskew = version_skew(version)
    C = centrality(terms)
    raw = w[0]*H + w[1]*sigma2 + w[2]*Vskew + w[3]*C
    return math.tanh(raw)

def failure_rate(true, terms, thresh=1.5):
    # Outliers relative to term‑wise mean
    uniq, inv = np.unique(terms, return_inverse=True)
    failures = 0
    for i, term in enumerate(uniq):
        mask = (inv == i)
        mu = np.mean(true[mask])
        outliers = np.abs(true[mask] - mu) > thresh
        failures += np.sum(outliers)
    return failures / len(true)

# ──────────────────────────────────────────────────────────────────────────────
# 3. Baseline scenario
# ──────────────────────────────────────────────────────────────────────────────
true0, terms0, ver0 = generate_data(N=200, seed=42)
ali0 = ali(true0, terms0, ver0)
fail0 = failure_rate(true0, terms0)
print(f"Baseline: ALI={ali0:.3f}, FailureRate={fail0:.3f}")

# ──────────────────────────────────────────────────────────────────────────────
# 4. Laundering attack – split "strong" into 10 arbitrary sub‑terms
# ──────────────────────────────────────────────────────────────────────────────
terms_laundered = terms0.copy()
# Find indices of "strong"
strong_idx = np.where(terms0 == "strong")[0]
rng = np.random.default_rng(123)
# Randomly assign each "strong" part to one of 10 new sub‑terms
sub_terms = np.array([f"strong_{i}" for i in rng.integers(0, 10, size=len(strong_idx))])
terms_laundered[strong_idx] = sub_terms

ali_launder = ali(true0, terms_laundered, ver0)
fail_launder = failure_rate(true0, terms_laundered)
print(f"Laundered: ALI={ali_launder:.3f}, FailureRate={fail_launder:.3f}")

# ──────────────────────────────────────────────────────────────────────────────
# 5. Demonstrate correlation collapse across many random seeds
# ──────────────────────────────────────────────────────────────────────────────
alis, fails = [], []
for s in range(30):
    true, terms, ver = generate_data(N=200, seed=s)
    alis.append(ali(true, terms, ver))
    fails.append(failure_rate(true, terms))

corr = np.corrcoef(alis, fails)[0,1]
print(f"Baseline ALI vs Failure correlation: {corr:.3f} (often near zero)")

# ──────────────────────────────────────────────────────────────────────────────
# 6. Show that adding spurious unique annotations drives ALI→0
# ──────────────────────────────────────────────────────────────────────────────
terms_unique = np.array([f"term_{i}" for i in range(len(true0))])
ali_unique = ali(true0, terms_unique, ver0)
fail_unique = failure_rate(true0, terms_unique)
print(f"Unique annotations: ALI={ali_unique:.3f}, FailureRate={fail_unique:.3f}")