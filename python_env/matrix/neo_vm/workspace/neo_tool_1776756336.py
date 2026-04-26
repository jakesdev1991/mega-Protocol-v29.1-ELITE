# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import networkx as nx
import matplotlib.pyplot as plt

# Parameters
N = 100  # number of capping sites (vertices)
p_edge = 0.1  # baseline edge probability
dt = 0.01  # time step
T = 50  # total time steps
control_strength = 0.5  # magnitude of control input

# Initialize random graph
G = nx.erdos_renyi_graph(N, p_edge)
adj = nx.to_numpy_array(G, dtype=float)

# Initialize binary capping states (0=uncapped, 1=capped)
s = np.random.randint(0, 2, size=N)

# Control functions: capping enhancer adds edges, decapping modulator removes edges
def apply_control(G, adj, mode='enhance', strength=0.5):
    if mode == 'enhance':
        # add random edges with probability strength
        for i in range(N):
            for j in range(i+1, N):
                if np.random.rand() < strength * 0.01 and not G.has_edge(i,j):
                    G.add_edge(i, j)
                    adj[i, j] = adj[j, i] = 1.0
    elif mode == 'modulate':
        # remove random edges with probability strength
        edges = list(G.edges())
        for (i, j) in edges:
            if np.random.rand() < strength * 0.05:
                G.remove_edge(i, j)
                adj[i, j] = adj[j, i] = 0.0
    return G, adj

# Dynamics: each node flips based on neighbor average + control bias
def step(s, adj, beta=1.0, h=0.0):
    # neighbor average
    neigh_avg = adj @ s / (adj.sum(axis=1) + 1e-12)
    # flip probability (logistic)
    prob = 1 / (1 + np.exp(-beta * (neigh_avg + h)))
    flip = np.random.rand(N) < prob
    s_new = (1 - s) * flip + s * (~flip)
    return s_new.astype(int)

# Observables
def compute_observables(G):
    # spectral gap (normalized Laplacian)
    L = nx.normalized_laplacian_matrix(G).astype(float)
    eigs = np.linalg.eigvals(L.A)
    eigs_sorted = np.sort(np.real(eigs))
    delta_lambda = eigs_sorted[1] - eigs_sorted[0] if len(eigs_sorted) > 1 else 0
    # clustering coefficient
    C = nx.average_clustering(G)
    # degree entropy
    degrees = [d for n, d in G.degree()]
    pk = np.bincount(degrees) / len(degrees)
    H_deg = -np.sum(pk * np.log(pk + 1e-12))
    return delta_lambda, C, H_deg

# Simulation loop
history = []
for t in range(T):
    # alternate control: first half enhance, second half modulate
    mode = 'enhance' if t < T//2 else 'modulate'
    G, adj = apply_control(G, adj, mode=mode, strength=control_strength)
    # external bias h: small positive for enhance, negative for modulate
    h = 0.2 if mode == 'enhance' else -0.2
    s = step(s, adj, beta=2.0, h=h)
    # compute observables
    delta_lambda, C, H_deg = compute_observables(G)
    history.append((t, delta_lambda, C, H_deg, s.mean()))

# Plot results
ts, dls, Cs, Hs, means = zip(*history)
fig, axs = plt.subplots(4,1, figsize=(8,10), sharex=True)
axs[0].plot(ts, dls, label='Spectral gap Δλ')
axs[0].set_ylabel('Δλ')
axs[0].legend()
axs[1].plot(ts, Cs, label='Clustering C', color='orange')
axs[1].set_ylabel('C')
axs[1].legend()
axs[2].plot(ts, Hs, label='Degree entropy H_deg', color='green')
axs[2].set_ylabel('H_deg')
axs[2].legend()
axs[3].plot(ts, means, label='Mean capping <s>', color='red')
axs[3].set_xlabel('Time step')
axs[3].set_ylabel('<s>')
axs[3].legend()
plt.tight_layout()
plt.show()

# Interpretation: As Δλ → 0 in second half, graph fragments → Shredding
# As C → 1 in first half, graph becomes clique → Freeze