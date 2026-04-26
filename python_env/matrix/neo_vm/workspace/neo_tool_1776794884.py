# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np, networkx as nx, random, matplotlib.pyplot as plt

# ──────────────────────────────────────────────────────────────────────────────
# 1. GENERATE BIPARTITE CREDENTIAL GRAPH
# ──────────────────────────────────────────────────────────────────────────────
def make_graph(n_keys=150, n_services=80, p=0.03):
    G = nx.bipartite_random_graph(n_keys, n_services, p)
    # label nodes as "key" (0) or "service" (1)
    for n in G.nodes():
        G.nodes[n]["bipartite"] = 0 if n < n_keys else 1
    return G

# ──────────────────────────────────────────────────────────────────────────────
# 2. METRICS
# ──────────────────────────────────────────────────────────────────────────────
def spectral_radius(G):
    """Largest eigenvalue of adjacency matrix → epidemic threshold."""
    A = nx.adjacency_matrix(G).astype(float)
    # for small graphs, dense eigenvalue compute is fine
    return max(abs(np.linalg.eigvals(A.todense())))

def avg_edge_curvature(G):
    """Crude proxy: |deg(u)-deg(v)|/(deg(u)+deg(v))."""
    curvs = []
    for u, v in G.edges():
        du, dv = G.degree(u), G.degree(v)
        if du + dv > 0:
            curvs.append(abs(du - dv) / (du + dv))
    return np.mean(curvs) if curvs else 0

# ──────────────────────────────────────────────────────────────────────────────
# 3. COMPROMISE CASCADE (SIR‑style)
# ──────────────────────────────────────────────────────────────────────────────
def cascade(G, seed, beta=0.15, gamma=0.0, max_steps=200):
    """
    seed: initial compromised node
    beta: per‑edge transmission probability
    gamma: recovery probability (here 0 → no recovery)
    """
    infected = {seed}
    for t in range(max_steps):
        new = set()
        for node in infected:
            for nb in G.neighbors(node):
                if nb not in infected and random.random() < beta:
                    new.add(nb)
        infected.update(new)
        if len(infected) == len(G.nodes):
            break
    return infected, t

# ──────────────────────────────────────────────────────────────────────────────
# 4. EXPERIMENT
# ──────────────────────────────────────────────────────────────────────────────
def run_trials(trials=100):
    data = []
    for _ in range(trials):
        G = make_graph()
        if not nx.is_connected(G):
            continue

        sr = spectral_radius(G)
        curv = avg_edge_curvature(G)

        # start cascade from a random key node (0..n_keys-1)
        key_nodes = [n for n, d in G.nodes(data=True) if d["bipartite"] == 0]
        seed = random.choice(key_nodes)
        infected, steps = cascade(G, seed, beta=0.2)

        frac = len(infected) / len(G.nodes)
        data.append((sr, curv, frac, steps))
    return data

# ──────────────────────────────────────────────────────────────────────────────
# 5. ANALYSIS & PLOT
# ──────────────────────────────────────────────────────────────────────────────
def analyze(data):
    srs = np.array([d[0] for d in data])
    curvs = np.array([d[1] for d in data])
    fracs = np.array([d[2] for d in data])
    steps = np.array([d[3] for d in data])

    print("Correlation (spectral radius → fraction compromised): "
          f"{np.corrcoef(srs, fracs)[0,1]:.3f}")
    print("Correlation (avg curvature → fraction compromised): "
          f"{np.corrcoef(curvs, fracs)[0,1]:.3f}")

    fig, ax = plt.subplots(1, 2, figsize=(12, 5))
    ax[0].scatter(srs, fracs, alpha=0.6, s=30)
    ax[0].set_xlabel("Spectral radius λ_max")
    ax[0].set_ylabel("Fraction compromised")
    ax[0].set_title("Epidemic spread ∝ λ_max")

    ax[1].scatter(curvs, fracs, alpha=0.6, s=30, color="orange")
    ax[1].set_xlabel("Avg edge curvature proxy")
    ax[1].set_ylabel("Fraction compromised")
    ax[1].set_title("Curvature is blind to cascade size")
    plt.tight_layout()
    plt.show()

# ──────────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    results = run_trials(200)
    analyze(results)