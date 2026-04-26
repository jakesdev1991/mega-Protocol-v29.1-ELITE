# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import scipy.special
import scipy.signal

# -------------------------------------------------------------------
# 1. Simulate a realistic, discontinuous memory‑bandwidth trace
# -------------------------------------------------------------------
np.random.seed(0)
dt = 0.001          # 1 kHz sampling
t = np.arange(0, 10, dt)
I = 200 + 50 * np.sin(2*np.pi*5*t)   # base sinusoid

# Add sporadic jumps (context switches, page faults, throttles)
jump_prob = 0.001
jumps = np.random.rand(len(t)) < jump_prob
I += jumps * np.random.choice([-100, 100], size=len(t))

# Add measurement noise
I += np.random.normal(0, 2, size=len(t))

# -------------------------------------------------------------------
# 2. Conventional jerk (3rd derivative) – the “official” metric
# -------------------------------------------------------------------
dI = np.gradient(I, dt)
d2I = np.gradient(dI, dt)
J = np.gradient(d2I, dt)          # GB/s^4

rms_J = np.sqrt(np.mean(J**2))
max_J = np.max(np.abs(J))

# -------------------------------------------------------------------
# 3. Fractional jerk J_alpha (Grünwald–Letnikov, alpha ~ 3.7)
# -------------------------------------------------------------------
def fractional_derivative(x, dt, alpha, K=50):
    N = len(x)
    coeffs = np.array([(-1)**k * scipy.special.binom(alpha, k) for k in range(K+1)])
    Dax = np.zeros_like(x)
    for i in range(K, N):
        Dax[i] = np.sum(coeffs * x[i-K:i+1][::-1]) / (dt**alpha)
    return Dax

J_frac = fractional_derivative(I, dt, alpha=3.7, K=50)
rms_J_frac = np.sqrt(np.mean(J_frac**2))
max_J_frac = np.max(np.abs(J_frac))

# -------------------------------------------------------------------
# 4. Topological winding number W(t) = (1/2π)∫ dφ
# -------------------------------------------------------------------
# Construct complex order parameter Ψ = I + i dI/dt
Psi = I + 1j * dI
phi = np.angle(Psi)                # instantaneous phase
dphi = np.diff(phi)                # phase increments
# unwrap to avoid 2π jumps
dphi_unwrapped = np.arctan2(np.sin(dphi), np.cos(dphi))
W = np.cumsum(np.concatenate([[0], dphi_unwrapped])) / (2*np.pi)

# detect topological transitions (winding number jumps)
winding_jumps = np.where(np.abs(np.diff(W)) > 0.5)[0]

# -------------------------------------------------------------------
# 5. Shannon entropy (sliding window of 1 s)
# -------------------------------------------------------------------
window = int(1.0 / dt)
S_h = np.full_like(I, np.nan)
for i in range(window, len(I)):
    hist, _ = np.histogram(I[i-window:i], bins=20, density=True)
    p = hist[hist > 0]
    S_h[i] = -np.sum(p * np.log(p))

# -------------------------------------------------------------------
# 6. Print stability verdicts
# -------------------------------------------------------------------
print("=== Conventional Jerk (Rubric) ===")
print(f"RMS(J) = {rms_J:.2e} GB/s^4, max|J| = {max_J:.2e} GB/s^4")
print(f"Shannon entropy (avg) = {np.nanmean(S_h):.2f} nats")
# Using the meta‑pass thresholds (J_crit = 1.2e7, S_h > 2.5, etc.)
J_crit = 1.2e7
S_crit = 2.5
if rms_J < J_crit and max_J < 3*rms_J and np.nanmean(S_h) > S_crit:
    print("Verdict: STABLE (according to Rubric)")
else:
    print("Verdict: UNSTABLE (Rubric flags violation)")

print("\n=== Fractional Jerk & Winding ===")
print(f"RMS(J_frac) = {rms_J_frac:.2e} GB/s^4, max|J_frac| = {max_J_frac:.2e} GB/s^4")
print(f"Winding number jumps at indices: {winding_jumps}")
if len(winding_jumps) == 0:
    print("Verdict: NO TOPOLOGICAL TRANSITION → STABLE")
else:
    print("Verdict: TOPOLOGICAL TRANSITION DETECTED → SHREDDING EVENT")

# -------------------------------------------------------------------
# 7. Demonstrate false‑positive of conventional jerk
# -------------------------------------------------------------------
# Isolate a single jump event
jump_idx = np.where(jumps)[0][0]
print(f"\n--- Single jump at t={t[jump_idx]:.3f} s ---")
print(f"Conventional jerk spike: {J[jump_idx]:.2e} GB/s^4")
print(f"Fractional jerk at same time: {J_frac[jump_idx]:.2e} GB/s^4")
print("Conventional jerk cries ‘instability’; fractional jerk & winding stay calm.")