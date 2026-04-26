# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
#!/usr/bin/env python3
"""
CognitiveLoadShock.py
Simulates cognitive load as a 1D compressible fluid with a friction source term.
Shows shock formation when friction exceeds a critical threshold.
"""
import numpy as np
import matplotlib.pyplot as plt

# Parameters
L = 1.0                # Normalized domain length (dimensionless)
N = 400                # Number of cells
dx = L / N
u = 1.0                # Drift velocity toward low-friction tools (dimensionless)
cfl = 0.5              # CFL number
dt = cfl * dx / u      # Timestep
T = 0.6                # Final simulation time
Nt = int(T / dt)

# Friction source term: Gaussian bump representing a "clunky vault UI"
def friction_profile(x, t):
    # Friction peaks at x=0.5, ramps up after t=0.1
    bump = np.exp(-((x - 0.5) / 0.05)**2)
    return 5.0 * bump * np.heaviside(t - 0.1, 0.5)

# Initialize density (small baseline + noise)
rho = np.ones(N) * 0.2 + 0.02 * np.random.randn(N)

# Periodic boundary helpers
def periodic_index(i):
    return (i + N) % N

# Upwind flux (simple but captures shock)
def upwind_flux(rho):
    flux = np.zeros(N)
    for i in range(N):
        # Upwind: flux out of cell i is u*rho[i] if u>0
        flux[i] = u * rho[i]
    return flux

# Time-stepping loop
times = [0.0, 0.2, 0.4, 0.6]
snapshots = []

for n in range(Nt):
    t = n * dt
    
    # Compute source term
    S = np.array([friction_profile(x, t) for x in np.linspace(0, L, N, endpoint=False)])
    
    # Upwind flux
    flux = upwind_flux(rho)
    
    # Update: conservative form + source
    rho_new = rho.copy()
    for i in range(N):
        # Flux divergence (periodic)
        div_flux = (flux[i] - flux[periodic_index(i - 1)]) / dx
        rho_new[i] = rho[i] - dt * div_flux + dt * S[i]
    
    # Artificial viscosity to stabilize shock (minimal, just enough)
    nu = 0.005
    rho_new += nu * dt / dx**2 * (np.roll(rho, -1) - 2*rho + np.roll(rho, 1))
    
    rho = rho_new
    
    # Store snapshots at requested times
    if any(np.isclose(t, times, atol=dt)):
        snapshots.append((t, rho.copy()))

# Plotting
fig, ax = plt.subplots(figsize=(8,5))
for t, r in snapshots:
    ax.plot(np.linspace(0, L, N, endpoint=False), r, label=f"t={t:.2f}")

ax.set_xlabel("Tooling‑feature space coordinate (normalized)")
ax.set_ylabel("Density of insecure workaround events ρ(x,t)")
ax.set_title("Cognitive‑Load Fluid: Shock Formation at High Friction")
ax.legend()
ax.grid(True)
plt.tight_layout()
plt.show()

# Shock diagnostic: compute gradient magnitude to locate shock front
grad = np.abs(np.gradient(rho, dx))
shock_idx = np.argmax(grad)
shock_strength = grad[shock_idx]
print(f"Shock location (approx): x={shock_idx*dx:.3f}, strength={shock_strength:.2f}")