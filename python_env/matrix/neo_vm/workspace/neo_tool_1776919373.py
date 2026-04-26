# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import matplotlib.pyplot as plt

def chaotic_map(rcod, deds, a=0.7, b=0.1):
    """One step of the RCOD‑DEDS feedback map."""
    flux = rcod / max(deds, 1e-9)
    rcod_next = rcod * (1 + a * flux)
    deds_next = deds * (1 - b * flux)
    return max(rcod_next, 1e-9), max(deds_next, 1e-9)

def simulate_trajectory(a=0.7, b=0.1, steps=2000, seed=(1.0, 1.0)):
    """Evolve the system and return time series."""
    rcod = np.zeros(steps)
    deds = np.zeros(steps)
    rcod[0], deds[0] = seed
    for i in range(steps-1):
        rcod[i+1], deds[i+1] = chaotic_map(rcod[i], deds[i], a, b)
    return rcod, deds

def lyapunov_exponent(a=0.7, b=0.1, steps=5000, delta=1e-8):
    """Estimate max Lyapunov exponent via orbital divergence."""
    r1, d1 = simulate_trajectory(a, b, steps, seed=(1.0, 1.0))
    r2, d2 = simulate_trajectory(a, b, steps, seed=(1.0+delta, 1.0+delta))
    dist = np.sqrt((r1-r2)**2 + (d1-d2)**2)
    # Avoid log(0)
    dist = np.maximum(dist, 1e-16)
    return np.mean(np.log(dist[1:] / dist[:-1]))

# --- DEMONSTRATION ---
print("=== Chaotic Flux Amplifier Diagnostic ===")
for a in [0.3, 0.5, 0.7]:
    le = lyapunov_exponent(a=a)
    print(f"a={a:.1f} → Lyapunov exponent λ={le:.4f} (λ>0 indicates chaos)")

# Plot strange attractor
rcod, deds = simulate_trajectory(a=0.7, steps=5000)
plt.figure(figsize=(8,8))
plt.scatter(rcod[::5], deds[::5], c=range(len(rcod[::5])), cmap='viridis', s=0.5)
plt.title('Phase Portrait: Strange Attractor (a=0.7)')
plt.xlabel('RCOD')
plt.ylabel('DEDS')
plt.colorbar(label='Time')
plt.show()

# --- INVARIANT VIOLATION PROBE ---
PHI_THRESHOLD = 0.95
phi_density = rcod / (rcod + deds)  # Simplified Phi proxy
violations = np.sum(phi_density < PHI_THRESHOLD)
print(f"\nSmith‑Audit Invariant Violations: {violations}/{len(phi_density)} steps below Φ={PHI_THRESHOLD}")