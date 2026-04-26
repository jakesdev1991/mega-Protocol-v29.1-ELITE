# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
#!/usr/bin/env python3
"""
Omega Protocol validation for Informational Jerk monitoring in Linux HSA.
Checks:
  - Correctness of the third‑derivative stencil.
  - Shannon entropy computation.
  - Savitzky‑Golay smoothing.
  - RMS Jerk and its derivative.
  - Omega‑field invariants (Phi_N, Phi_Delta, psi).
  - Conditional entropy constraint (S_gap >= ln2).
  - Hard constraints: RMS_J <= 0.025, Phi_N >= 0.7, S_gap >= ln2.
"""

import numpy as np
from scipy.signal import savgol_filter

# ----------------------------------------------------------------------
# Helper functions
# ----------------------------------------------------------------------
def shannon_entropy(probs):
    """Compute Shannon entropy (bits) from a probability vector."""
    # Avoid log2(0) by masking zeros
    mask = probs > 0
    return -np.sum(probs[mask] * np.log2(probs[mask]))

def conditional_entropy(joint):
    """
    Compute S_gap = - Σ p(device,type) * log2(p(type|device)).
    joint: 2x2 array [[p(C,read), p(C,write)], [p(G,read), p(G,write)]]
    """
    device_marginal = joint.sum(axis=1)          # p(C), p(G)
    # Avoid division by zero
    with np.errstate(divide='ignore', invalid='ignore'):
        cond = joint / device_marginal[:, None]  # p(type|device)
    cond = np.where(device_marginal[:, None] == 0, 0, cond)
    S_gap = -np.sum(joint * np.log2(cond + 1e-12))  # add tiny to avoid log2(0)
    return S_gap

def third_derivative_stencil(signal, dt=1e-3):
    """
    Central‑difference approximation of the third derivative.
    Returns array same length as signal (edges set to NaN).
    """
    n = len(signal)
    j = np.full(n, np.nan)
    # indices i where i-2 and i+2 are valid
    for i in range(2, n-2):
        j[i] = (-signal[i-2] + 2*signal[i-1] - 2*signal[i+1] + signal[i+2]) / (2 * dt**3)
    return j

def rms_jerk(jerk, window_samples):
    """Root‑mean‑square jerk over a sliding window (returns same length, NaN at start)."""
    n = len(jerk)
    rms = np.full(n, np.nan)
    for i in range(window_samples-1, n):
        rms[i] = np.sqrt(np.nanmean(jerk[i-window_samples+1:i+1]**2))
    return rms

# ----------------------------------------------------------------------
# Synthetic data generation (replace with real histograms if available)
# ----------------------------------------------------------------------
np.random.seed(42)
n_samples = 800_000          # a bit more than 10 min to have edges
dt = 1e-3                    # 1 ms sampling

# Simulate raw histograms (256 blocks) for CPU and GPU
n_blocks = 256
# CPU histogram: slowly varying mean + noise
cpu_raw = np.random.poisson(lam=100, size=(n_samples, n_blocks)).astype(float)
# GPU histogram: slightly higher mean, opposite trend
gpu_raw = np.random.poisson(lam=120, size=(n_samples, n_blocks)).astype(float)

# Normalise to probabilities at each time step
cpu_prob = cpu_raw / cpu_raw.sum(axis=1, keepdims=True)
gpu_prob = gpu_raw / gpu_raw.sum(axis=1, keepdims=True)

# ----------------------------------------------------------------------
# Entropy and smoothing
# ----------------------------------------------------------------------
I_cpu = np.apply_along_axis(shannon_entropy, 1, cpu_prob)
I_gpu = np.apply_along_axis(shannon_entropy, 1, gpu_prob)
I_total = I_cpu + I_gpu

# Savitzky‑Golay smoothing (window=11, order=3)
window_sg = 11
order_sg = 3
I_smooth = savgol_filter(I_total, window_length=window_sg, polyorder=order_sg, mode='interp')

# ----------------------------------------------------------------------
# Jerk, RMS Jerk, and its derivative
# ----------------------------------------------------------------------
jerk = third_derivative_stencil(I_smooth, dt)
N_window = 600_000               # 10 min @1 ms
rmsJ = rms_jerk(jerk, N_window)
# derivative of RMS_J (using gradient, ignoring NaNs)
drmsJ_dt = np.gradient(rmsJ, dt, edge_order=2)
drmsJ_dt[np.isnan(rmsJ)] = np.nan

# ----------------------------------------------------------------------
# Omega‑field quantities
# ----------------------------------------------------------------------
Phi_N = (I_cpu + I_gpu) / np.sqrt(2)
Phi_Delta = (I_cpu - I_gpu) / np.sqrt(2)

# Effective potential matching the Lagrangian potential term:
# V_eff = 0.5*m^2*(Phi_N^2 + Phi_Delta^2) + (lambda/4)*Phi_N*Phi_Delta^2
# Choose arbitrary but dimensionally consistent parameters:
kappa = 1.0          # [T^{-3/2}]
m = 1.0              # [T^{-1/2}]
lam = 1.0            # [T^{-1}]
V_eff = 0.5 * m**2 * (Phi_N**2 + Phi_Delta**2) + (lam/4) * Phi_N * Phi_Delta**2

# Hessian of V_eff w.r.t (Phi_N, Phi_Delta) – analytic:
# d2V/dPhiN^2 = m^2
# d2V/dPhiD^2 = m^2 + (lam/2)*Phi_N
# d2V/dPhiNdPhiD = (lam/2)*Phi_Delta
h11 = np.full_like(Phi_N, m**2)
h22 = m**2 + (lam/2) * Phi_N
h12 = (lam/2) * Phi_Delta
# Eigenvalues of 2x2 symmetric matrix:
disc = np.sqrt(((h11 - h22)/2)**2 + h12**2)
eval1 = (h11 + h22)/2 + disc
eval2 = (h11 + h22)/2 - disc
m_eff = np.sqrt(np.abs(eval1 * eval2))
psi = np.log(m_eff)   # m0 = 1 for scaling

# ----------------------------------------------------------------------
# Conditional entropy (S_gap)
# ----------------------------------------------------------------------
# Build a dummy joint distribution of (device, access_type)
# Assume read/write probabilities vary slowly.
p_read = 0.6 + 0.1 * np.sin(2*np.pi*np.arange(n_samples)/n_samples)
p_write = 1.0 - p_read
# Split between CPU and GPU according to their relative activity
cpu_weight = I_cpu / (I_cpu + I_gpu + 1e-12)
gpu_weight = 1.0 - cpu_weight

joint = np.zeros((n_samples, 2, 2))  # [time, device(0=C,1=G), type(0=read,1=write)]
joint[:,0,0] = cpu_weight * p_read   # CPU, read
joint[:,0,1] = cpu_weight * p_write  # CPU, write
joint[:,1,0] = gpu_weight * p_read   # GPU, read
joint[:,1,1] = gpu_weight * p_write  # GPU, write

# Normalise just in case
joint /= joint.sum(axis=(1,2), keepdims=True)

S_gap = np.apply_along_axis(lambda x: conditional_entropy(x), 1, joint)

# ----------------------------------------------------------------------
# Validation checks
# ----------------------------------------------------------------------
def assert_close(a, b, tol=1e-6, name=""):
    if not np.allclose(a, b, rtol=tol, atol=tol):
        raise AssertionError(f"{name} mismatch: {a} vs {b}")

# 1. Jerk stencil sanity check on a cubic polynomial f(t)=t^3 -> f'''=6
t = np.arange(-5, 6) * dt
f = t**3
jerk_exact = np.full_like(f, 6.0)
jerk_est = third_derivative_stencil(f, dt)
# ignore edges where stencil undefined
valid = ~np.isnan(jerk_est)
assert_close(jerk_est[valid], jerk_exact[valid], tol=1e-12, name="Jerk stencil")

# 2. Entropy non‑negative
assert np.all(I_cpu >= -1e-12) and np.all(I_gpu >= -1e-12), "Entropy negative"
assert np.all(I_total >= -1e-12), "Total entropy negative"

# 3. Smoothed signal finite
assert np.all(np.isfinite(I_smooth)), "Savitzky‑Golay produced non‑finite values"

# 4. RMS Jerk threshold
rms_now = rmsJ[-1]  # latest sample
assert rms_now <= 0.025 + 1e-9, f"RMS_J exceeds threshold: {rms_now}"

# 5. Phi_N constraint
phi_N_now = Phi_N[-1]
assert phi_N_now >= 0.7 - 1e-9, f"Phi_N below lower bound: {phi_N_now}"

# 6. S_gap constraint (diversity)
s_gap_now = S_gap[-1]
assert s_gap_now >= np.log2(2) - 1e-9, f"S_gap below ln2: {s_gap_now}"

# 7. Jerk derivative sign (just report)
drms_now = drmsJ_dt[-1]
print(f"[VALIDATION] RMS_J(t) = {rms_now:.6f} bits·s⁻³")
print(f"[VALIDATION] d(RMS_J)/dt = {drms_now:.6e} bits·s⁻⁴")
print(f"[VALIDATION] Phi_N = {phi_N_now:.3f} bits")
print(f"[VALIDATION] Phi_Delta = {Phi_Delta[-1]:.3f} bits")
print(f"[VALIDATION] psi = {psi[-1]:.3f}")
print(f"[VALIDATION] S_gap = {s_gap_now:.3f} bits (ln2 = {np.log2(2):.3f})")
print("[VALIDATION] All Omega Protocol hard constraints satisfied.")

# ----------------------------------------------------------------------
# Optional: detect a potential violation and suggest control
# ----------------------------------------------------------------------
if drms_now > 0 and rms_now > 0.02 * 0.025:  # arbitrary early‑warning heuristic
    print("[ACTION] Positive jerk derivative with rising RMS_J → consider work‑stealing rebalance.")
else:
    print("[ACTION] No immediate control action required.")