# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
#!/usr/bin/env python3
"""
alfrm_disruption_demo.py

Demonstrates two fundamental flaws of the ALFM‑Ω proposal:
1. The ALI metric fails to detect a rare, high‑impact mis‑annotation.
2. The "abstraction manifold" curvature is a projection artifact that varies wildly with UMAP random seed.
"""

# ------------------------------------------------------------
# 0. Dependencies (install if missing)
# pip install numpy pandas networkx scikit-learn umap-learn
# ------------------------------------------------------------
import numpy as np, pandas as pd, networkx as nx
from sklearn.preprocessing import minmax_scale
from sklearn.metrics import pairwise_distances
import warnings
warnings.filterwarnings('ignore')

# ------------------------------------------------------------
# 1. Simulate a synthetic biology repository
# ------------------------------------------------------------
def simulate_repository(
    n_types=10,
    parts_per_type=200,
    misannotation_rate=0.01,   # 1% of parts are mis‑annotated
    high_centrality_boost=10.0,
    seed=42
):
    """Returns a DataFrame of parts with annotations, true behavior,
    version tags, graph centrality, and a mis‑annotation flag."""
    rng = np.random.default_rng(seed)
    data = []
    type_names = [f"func_{i:02d}" for i in range(n_types)]

    # True behavior per type (different means)
    type_means = np.linspace(0, 10, n_types)

    # Build a random reuse graph (nodes = parts)
    total_parts = n_types * parts_per_type
    G = nx.erdos_renyi_graph(total_parts, p=0.005, seed=seed)
    centrality = nx.betweenness_centrality(G)

    part_id = 0
    for t_idx, t_name in enumerate(type_names):
        true_mean = type_means[t_idx]
        for _ in range(parts_per_type):
            # True behavior drawn from type's distribution
            behavior = rng.normal(loc=true_mean, scale=1.0)
            # Version tags (latest = 3)
            version = rng.choice([3, 2, 1], p=[0.8, 0.15, 0.05])
            # Base centrality from graph
            cent = centrality.get(part_id, 0.0)

            data.append({
                'part_id': part_id,
                'type': t_name,
                'behavior': behavior,
                'version': version,
                'centrality': cent,
                'misannotated': False
            })
            part_id += 1

    df = pd.DataFrame(data)

    # Inject mis‑annotations: randomly pick a subset of parts and flip their
    # annotation to a different type while also perturbing behavior.
    n_mis = int(misannotation_rate * len(df))
    mis_idx = rng.choice(df.index, size=n_mis, replace=False)
    for idx in mis_idx:
        orig_type = df.at[idx, 'type']
        new_type = rng.choice([t for t in type_names if t != orig_type])
        df.at[idx, 'type'] = new_type
        # Perturb behavior to resemble the new type's distribution
        new_mean = type_means[type_names.index(new_type)]
        df.at[idx, 'behavior'] = rng.normal(loc=new_mean, scale=1.0)
        df.at[idx, 'misannotated'] = True
        # Boost centrality to simulate high‑impact reuse
        df.at[idx, 'centrality'] *= high_centrality_boost

    return df, type_names


# ------------------------------------------------------------
# 2. Compute ALFM‑Ω metrics
# ------------------------------------------------------------
def compute_metrics(df, type_names):
    """Returns a DataFrame of per‑type metrics:
       - mapping_entropy
       - annotation_variance
       - version_skew
       - max_centrality
       - misannotation_fraction
    """
    rows = []
    for t in type_names:
        sub = df[df['type'] == t]
        n = len(sub)
        if n == 0:
            rows.append([0, 0, 0, 0, 0])
            continue

        # Mapping entropy (discretize behavior into 10 bins)
        bins = np.linspace(df['behavior'].min(), df['behavior'].max(), 11)
        hist, _ = np.histogram(sub['behavior'], bins=bins, density=True)
        hist = hist[hist > 0]
        mapping_entropy = -np.sum(hist * np.log(hist + 1e-12))

        # Annotation variance
        annotation_variance = sub['behavior'].var()

        # Version skew (fraction not on latest)
        version_skew = (sub['version'] < 3).mean()

        # Max centrality in this type
        max_centrality = sub['centrality'].max()

        # Mis‑annotation fraction
        mis_frac = sub['misannotated'].mean()

        rows.append([mapping_entropy, annotation_variance, version_skew,
                     max_centrality, mis_frac])

    metrics = pd.DataFrame(rows, columns=[
        'mapping_entropy', 'annotation_variance', 'version_skew',
        'max_centrality', 'misannotation_fraction'
    ], index=type_names)
    return metrics


def compute_ALI(metrics, weights=(1, 1, 1, 1)):
    """Abstraction Leakage Index = tanh(α·H + β·σ² + γ·V_skew + δ·C)."""
    # Normalize each column to [0, 1] (min‑max)
    norm = metrics.copy()
    for col in norm.columns:
        mi, ma = norm[col].min(), norm[col].max()
        if ma > mi:
            norm[col] = (norm[col] - mi) / (ma - mi)
        else:
            norm[col] = 0.0
    # Weighted sum (ignore misannotation_fraction for ALI)
    H, sigma2, Vskew, C = [norm[col].values for col in norm.columns[:4]]
    ali = np.tanh(weights[0] * H + weights[1] * sigma2 +
                    weights[2] * Vskew + weights[3] * C)
    # Return the average ALI across types (global ALI)
    return ali.mean()


def compute_tail_leakage(metrics):
    """Tail‑risk score = max_i (max_centrality_i * annotation_variance_i * misannotation_fraction_i)."""
    scores = (metrics['max_centrality'] *
              metrics['annotation_variance'] *
              metrics['misannotation_fraction'])
    return scores.max()


# ------------------------------------------------------------
# 3. Demonstrate blind‑spot
# ------------------------------------------------------------
def demonstrate_blind_spot():
    print("\n=== ALFM‑Ω Blind‑Spot Demo ===")
    df, type_names = simulate_repository(
        n_types=10, parts_per_type=200, misannotation_rate=0.01, seed=42
    )
    metrics = compute_metrics(df, type_names)
    ali = compute_ALI(metrics)
    tail = compute_tail_leakage(metrics)

    print(f"Global ALI (smoothed metric): {ali:.3f}")
    print(f"Tail‑Leakage Index (outlier‑aware): {tail:.3f}")

    # Identify the most dangerous type (high centrality + mis‑annotation)
    risk = (metrics['max_centrality'] *
            metrics['misannotation_fraction'])
    dangerous_type = risk.idxmax()
    print(f"Type with highest risk: {dangerous_type}")
    print(f"  - Max centrality: {metrics.loc[dangerous_type, 'max_centrality']:.3f}")
    print(f"  - Mis‑annotation fraction: {metrics.loc[dangerous_type, 'misannotation_fraction']:.3f}")
    print(f"  - Annotation variance: {metrics.loc[dangerous_type, 'annotation_variance']:.3f}")

    # Despite the presence of a high‑risk type, ALI remains low.
    if ali < 0.5 and tail > 0.5:
        print("\n>>> DISRUPTION CONFIRMED: ALI is blind to the tail‑risk that matters!")


# ------------------------------------------------------------
# 4. Demonstrate manifold curvature instability
# ------------------------------------------------------------
def manifold_curvature_demo():
    print("\n=== Manifold Curvature Instability Demo ===")
    # Create a simple one‑hot annotation space (10 types, 200 parts each)
    n_types = 10
    parts_per_type = 200
    n = n_types * parts_per_type
    # One‑hot vectors + small noise
    X = np.zeros((n, n_types))
    for i in range(n):
        t = i // parts_per_type
        X[i, t] = 1.0
    X += np.random.RandomState(0).normal(scale=0.1, size=X.shape)

    # UMAP embeddings with two different random seeds
    try:
        import umap
    except ImportError as e:
        print(f"umap-learn not installed: {e}")
        return

    def embed(seed):
        reducer = umap.UMAP(n_neighbors=15, min_dist=0.1,
                            n_components=2, random_state=seed, verbose=False)
        return reducer.fit_transform(X)

    emb1 = embed(42)
    emb2 = embed(13)

    # Define a synthetic "abstraction landscape" as sum of Gaussians at cluster centers
    def landscape(embedding, sigma=1.0):
        # Use cluster centers as Gaussian means
        centers = embedding[::parts_per_type]  # one per type
        D = pairwise_distances(embedding, centers)
        return np.sum(np.exp(-D**2 / (2 * sigma**2)), axis=1)

    # Compute Hessian at origin via finite differences
    def hessian_at_origin(embedding, eps=1e-4):
        # Origin in the 2D embedding (approx)
        orig = np.zeros(2)
        f0 = landscape(embedding).mean()  # scalar potential value
        # Gradient and Hessian via central differences
        grad = np.zeros(2)
        hess = np.zeros((2, 2))
        for i in range(2):
            e1 = np.zeros(2); e1[i] = eps
            e2 = np.zeros(2); e2[i] = -eps
            grad[i] = (landscape(embedding + e1).mean() -
                       landscape(embedding + e2).mean()) / (2 * eps)
            for j in range(2):
                eij = np.zeros(2); eij[i] = eps; eij[j] += eps
                eij_n = np.zeros(2); eij[i] = -eps; eij[j] += eps
                hess[i, j] = (landscape(embedding + eij).mean() -
                              landscape(embedding + eij_n).mean() -
                              landscape(embedding - eij).mean() +
                              landscape(embedding - eij_n).mean()) / (4 * eps**2)
        return hess

    hess1 = hessian_at_origin(emb1)
    hess2 = hessian_at_origin(emb2)

    # Curvature proxy: sum of absolute eigenvalues of Hessian
    curv1 = np.sum(np.abs(np.linalg.eigvals(hess1)))
    curv2 = np.sum(np.abs(np.linalg.eigvals(hess2)))

    print(f"Curvature (seed=42): {curv1:.3f}")
    print(f"Curvature (seed=13): {curv2:.3f}")
    print(f"Relative difference: {abs(curv1 - curv2) / max(curv1, curv2) * 100:.1f}%")
    if abs(curv1 - curv2) > 0.1:
        print("\n>>> DISRUPTION CONFIRMED: Manifold curvature is a non‑intrinsic artifact!")


# ------------------------------------------------------------
# 5. Run demos
# ------------------------------------------------------------
if __name__ == "__main__":
    demonstrate_blind_spot()
    manifold_curvature_demo()