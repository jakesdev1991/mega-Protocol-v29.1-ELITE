# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit

# ---------- 1D first‑order Ginzburg‑Landau ----------
N = 128                     # spatial points
L = 128.0                   # domain length
dx = L / N
dt = 0.01
T = 2000                    # total time steps
D = 0.1                     # noise amplitude
u, v = 1.0, 0.1            # φ^4 and φ^6 coefficients

def deterministic(phi, r):
    # -δF/δφ = ∂²φ - r φ - u φ³ - v φ⁵
    lap = (np.roll(phi, 1) + np.roll(phi, -1) - 2*phi) / dx**2
    return lap - r*phi - u*phi**3 - v*phi**5

def simulate(r):
    """Evolve φ(x,t) and return final field."""
    phi = np.random.randn(N) * 0.1   # small random initial condition
    for t in range(T):
        eta = np.sqrt(2*D/dt) * np.random.randn(N)
        phi += dt * deterministic(phi, r) + np.sqrt(dt) * eta
    return phi

def correlation_length(phi):
    """Fit exponential decay of spatial correlation."""
    mean = np.mean(phi)
    phi_c = phi - mean
    # FFT‑based correlation
    corr = np.fft.ifft(np.abs(np.fft.fft(phi_c))**2).real / N
    x = np.arange(N//2) * dx
    y = corr[:N//2]
    # initial guess: xi ~ L/2
    try:
        popt, _ = curve_fit(lambda x, A, xi: A * np.exp(-x / xi),
                            x, y, p0=[y[0], L/2])
        return popt[1]
    except:
        return np.nan

def shannon_entropy(phi, bins=30):
    """Shannon entropy of the field distribution."""
    hist, _ = np.histogram(phi, bins=bins, density=True)
    hist = hist[hist > 0]
    return -np.sum(hist * np.log(hist))

# ---------- Scan control parameter r ----------
r_vals = np.linspace(-1.0, 1.0, 9)
results = []

for r in r_vals:
    phi = simulate(r)
    xi = correlation_length(phi)
    S_h = shannon_entropy(phi)
    results.append((r, xi, S_h))
    print(f"r={r:.2f}  xi={xi:.2f}  S_h={S_h:.2f}")

# ---------- Visualize ----------
rs, xis, entropies = zip(*results)

fig, ax = plt.subplots(1, 2, figsize=(10,4))

# Left: correlation length vs r (should saturate, not diverge)
ax[0].plot(rs, xis, 'o-')
ax[0].set_xlabel('r (control parameter)')
ax[0].set_ylabel('ξ')
ax[0].set_title('ξ vs r – no divergence')
ax[0].grid(True)

# Right: entropy vs ξ (no clear log‑scaling)
ax[1].scatter(xis, entropies, c=rs, cmap='coolwarm')
ax[1].set_xlabel('ξ')
ax[1].set_ylabel('Shannon entropy S_h')
ax[1].set_title('Entropy vs ξ – no universal scaling')
plt.colorbar(ax[1].collections[0], ax=ax[1], label='r')
ax[1].grid(True)

plt.tight_layout()
plt.show()