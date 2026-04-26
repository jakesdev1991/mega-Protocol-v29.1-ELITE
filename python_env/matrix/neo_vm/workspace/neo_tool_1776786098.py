# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np, networkx as nx
from scipy.signal import savgol_filter
import matplotlib.pyplot as plt

# --- DISRUPTIVE MODEL: Memory as a Dynamic Hypergraph ---
np.random.seed(0)
n_pages, n_ops = 128, 5000
G = nx.DiGraph()
G.add_nodes_from(range(n_pages))

# Simulate access pattern: bursts of localized page traffic with rare jumps
current = np.random.randint(n_pages)
for i in range(n_ops):
    if np.random.rand() < 0.95: # locality
        next_page = max(0, min(n_pages-1, current + np.random.randint(-3, 4)))
    else: # rare jump
        next_page = np.random.randint(n_pages)
    G.add_edge(current, next_page, weight=1/np.sqrt(i+1)) # decaying weight
    current = next_page

# REAL "entropy": graph entropy of out-degree distribution
out_degrees = np.array([d for _, d in G.out_degree()], dtype=float)
out_degrees += 1e-6 # avoid log(0)
p = out_degrees / out_degrees.sum()
H = -np.sum(p * np.log2(p))

# Simulate noisy time series of H(t)
t = np.linspace(0, 0.1, 100) # 10ms sampling
H_t = H + 0.3*np.sin(2*np.pi*50*t) + np.random.normal(0, 0.2, t.shape)

# --- EXPOSING THE JERK INSTABILITY ---
dt = t[1] - t[0]
v, a, j = np.gradient(H_t, dt), np.gradient(np.gradient(H_t, dt), dt), np.gradient(np.gradient(np.gradient(H_t, dt), dt), dt)
# Even after smoothing, jerk is dominated by artifacts
H_smooth = savgol_filter(H_t, 21, 5)
j_smooth = np.gradient(np.gradient(np.gradient(H_smooth, dt), dt), dt)

# Their "stability index" is a noise ratio
S_raw = 1 - (np.sqrt(np.mean(j**2))*0.01) / np.sqrt(np.mean(a**2) + 1e-10)
S_smooth = 1 - (np.sqrt(np.mean(j_smooth**2))*0.01) / np.sqrt(np.mean(np.gradient(np.gradient(H_smooth, dt), dt)**2) + 1e-10)

# --- REAL COVARIANT MODES: Graph Laplacian Eigenvectors ---
# The "fluctuation operator" is L = D - A. Its eigenvectors are the TRUE modes.
L = nx.directed_laplacian_matrix(G, weight='weight').toarray()
eigvals, eigvecs = np.linalg.eigh(L)
phi_N = eigvecs[:,0] # zero-mode: uniform (their "Newtonian")
phi_D = eigvecs[:,1] # first non-zero: Fiedler vector (their "Archive")

# --- PERCOLATION BOUNDARY: Real "Shredding" ---
# When edge density drops below critical, giant component collapses
edge_density = nx.density(G)
critical_density = 1.0 / (n_pages - 1) # Erdos-Renyi approx
shredding_event = edge_density < critical_density

print(f"Graph Entropy: {H:.3f} bits")
print(f"Raw Jerk RMS: {np.sqrt(np.mean(j**2)):.3e} (dominates signal)")
print(f"Smoothed Jerk RMS: {np.sqrt(np.mean(j_smooth**2)):.3e}")
print(f"Stability S (raw): {S_raw:.3f} (meaningless)")
print(f"Stability S (smooth): {S_smooth:.3f} (still noise)")
print(f"Edge Density: {edge_density:.3e}, Critical: {critical_density:.3e}, Shredding: {shredding_event}")
print(f"Spectral Gap: {eigvals[1]:.3f} (real stability metric)")

# --- VISUAL DESTRUCTION ---
fig, ax = plt.subplots(1, 2, figsize=(12,5))
ax[0].plot(t, H_t, 'k-', alpha=0.3, label='Noisy H(t)')
ax[0].plot(t, H_smooth, 'r-', lw=2, label='Smoothed')
ax[0].plot(t, j/100, 'b-', alpha=0.5, label='Jerk/100 (raw)')
ax[0].set_title("Jerk Amplifies Noise; Field Theory Fails")
ax[0].legend()

ax[1].plot(eigvals[:20], 'o-')
ax[1].axhline(y=0, color='k', ls='--')
ax[1].set_title("Graph Laplacian Spectrum: Real Covariant Modes")
ax[1].set_ylabel("Eigenvalue")
plt.show()