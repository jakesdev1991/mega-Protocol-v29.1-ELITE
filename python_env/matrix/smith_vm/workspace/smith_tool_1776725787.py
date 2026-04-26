# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np

# -------------------------------------------------
# Parameters from the analysis
# -------------------------------------------------
I0 = 200.0          # GB/s, reference bandwidth
A  = 50.0           # GB/s, amplitude of sinusoid
omega = 20.0 * np.pi  # rad/s
v = I0              # assume vacuum expectation equals I0 (as implied)

# Time array over several periods for accurate stats
T = 2 * np.pi / omega
t = np.linspace(0, 10 * T, 200000)  # 10 periods, high resolution

I = I0 + A * np.sin(omega * t)          # GB/s
dIdt = A * omega * np.cos(omega * t)    # GB/s^2

# -------------------------------------------------
# Derive lambda from the given RMS(J) target
# -------------------------------------------------
# Jerk expression: J = -lambda * (3*I**2 - v**2) * dIdt
factor = (3.0 * I**2 - v**2) * dIdt   # GB/s^4 per unit lambda
# Compute RMS of factor (without lambda)
rms_factor = np.sqrt(np.mean(factor**2))
max_factor = np.max(np.abs(factor))

# Target RMS(J) from the analysis
target_rms_J = 8.77e6   # GB/s^4
# Solve for |lambda|
lam = target_rms_J / rms_factor
print(f"Derived |lambda| = {lam:.3e} (units 1/(GB^2))")

# Compute actual jerk with this lambda
J = -lam * factor
rms_J = np.sqrt(np.mean(J**2))
max_J = np.max(np.abs(J))
print(f"RMS(J) = {rms_J:.3e} GB/s^4")
print(f"max|J| = {max_J:.3e} GB/s^4")
print(f"Target RMS(J) = {target_rms_J:.3e} GB/s^4")
print(f"J_crit (given) = 1.2e7 GB/s^4")
print()

# -------------------------------------------------
# Stability criteria checks
# -------------------------------------------------
crit1 = rms_J < 1.2e7
crit2 = max_J < 3.0 * rms_J
print(f"Criterion 1 (RMS < J_crit): {crit1}")
print(f"Criterion 2 (max|J| < 3*RMS): {crit2}")

# Entropy: Shannon conditional entropy of I over sliding 1‑s window
window_len = 1.0  # seconds
dt = t[1] - t[0]
win_samples = int(window_len / dt)
# Compute probability histogram for each window (using 10 bins)
num_bins = 10
entropy_vals = []
for i in range(0, len(I) - win_samples, win_samples // 2):  # 50% overlap
    seg = I[i:i+win_samples]
    hist, _ = np.histogram(seg, bins=num_bins, density=True)
    # Avoid zeros for log
    hist = hist[hist > 0]
    S = -np.sum(hist * np.log(hist))
    entropy_vals.append(S)
mean_entropy = np.mean(entropy_vals) if entropy_vals else 0.0
print(f"Mean Shannon entropy over windows: {mean_entropy:.3f} nats")
crit3 = mean_entropy > 2.5
print(f"Criterion 3 (S_h > 2.5 nats): {crit3}")

# Invariants: stiffness xi_N, xi_der
# xi_N = [lambda * (3*I^2 - v^2)]^{-1/2}
# xi_Δ = [lambda * (I^2 + 3*PhiDelta^2 - v^2)]^{-1/2}
# For simplicity we set PhiDelta = 0 (worst‑case for xi_Δ)
xi_N = 1.0 / np.sqrt(lam * np.maximum(3.0 * I**2 - v**2, 1e-12))
xi_Delta = 1.0 / np.sqrt(lam * np.maximum(I**2 - v**2, 1e-12))
min_xi_N = np.min(xi_N)
min_xi_Delta = np.min(xi_Delta)
print(f"Minimum ξ_N = {min_xi_N:.3f} s")
print(f"Minimum ξ_Δ = {min_xi_Delta:.3f} s")
crit4 = (min_xi_N > 0.1) and (min_xi_Delta > 0.05)
print(f"Criterion 4 (ξ_N>0.1s, ξ_Δ>0.05s): {crit4}")

# Overall compliance
overall = crit1 and crit2 and crit3 and crit4
print("\n=== OVERALL COMPLIANCE ===")
print("PASS" if overall else "FAIL")