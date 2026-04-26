# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np

# ──────────────────────────────────────────────────────────────────────────────
# Classical Cognitive Control (C³) Simulation
# ──────────────────────────────────────────────────────────────────────────────
np.random.seed(0)
dt = 0.01
T = 100.0
t = np.arange(0, T, dt)
N = len(t)

# System parameters (double‑well potential)
lam = 1.0          # shape of potential
x0 = 1.0           # well minima
sigma = 0.5        # subconscious noise amplitude
k = 2.0            # conscious feedback gain

# Control threshold (selector aggressiveness)
threshold_high = 2.0   # "ignoring" regime
threshold_low  = 0.5   # "engaged" regime

def control_action(x, thr):
    """Selector: returns feedback if |x|<thr, otherwise zero (ignore)."""
    return -k * x if np.abs(x) < thr else 0.0

# ──────────────────────────────────────────────────────────────────────────────
# Run 1: High threshold → conscious ignoring (black‑hole)
# ──────────────────────────────────────────────────────────────────────────────
x1 = np.zeros(N)
ctrl1 = np.zeros(N)
noise = sigma * np.random.randn(N)

for i in range(1, N):
    ctrl1[i-1] = control_action(x1[i-1], threshold_high)
    dVdx = lam * x1[i-1] * (x1[i-1]**2 - x0**2)
    dxdt = -dVdx + noise[i-1] + ctrl1[i-1]
    x1[i] = x1[i-1] + dxdt * dt

# Cross‑correlation ≈ COD
cod_blackhole = np.corrcoef(noise[:-1], ctrl1[:-1])[0, 1]
print("COD (black‑hole/ignoring):", cod_blackhole)

# ──────────────────────────────────────────────────────────────────────────────
# Run 2: Annealed threshold → gradual engagement (stabilization)
# ──────────────────────────────────────────────────────────────────────────────
x2 = np.zeros(N)
ctrl2 = np.zeros(N)
thr_schedule = np.linspace(threshold_high, threshold_low, N)

for i in range(1, N):
    ctrl2[i-1] = control_action(x2[i-1], thr_schedule[i-1])
    dVdx = lam * x2[i-1] * (x2[i-1]**2 - x0**2)
    dxdt = -dVdx + noise[i-1] + ctrl2[i-1]
    x2[i] = x2[i-1] + dxdt * dt

cod_stabilized = np.corrcoef(noise[:-1], ctrl2[:-1])[0, 1]
print("COD (annealed/stabilized):", cod_stabilized)

# ──────────────────────────────────────────────────────────────────────────────
# Dimensional Inconsistency Demo
# ──────────────────────────────────────────────────────────────────────────────
# Stiffness invariant ξ_N is claimed to have units of time:
xi_N_seconds = 1.0   # seconds
# Yet it is also claimed to equal ∂Φ_N/∂ψ, which is dimensionless:
dPhi_dpsi = 0.5      # dimensionless
# The equation xi_N = dPhi_dpsi is dimensionally impossible:
print("Dimensional mismatch: xi_N (s) = dΦ/dψ (dimensionless) →",
      xi_N_seconds, "vs", dPhi_dpsi)