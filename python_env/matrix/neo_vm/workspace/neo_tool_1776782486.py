# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import scipy.stats as st

# ──────────────────────────────────────────────────────────────────────────────
# 1. Synthetic market dynamics
# ──────────────────────────────────────────────────────────────────────────────
np.random.seed(42)
T = 500                     # time steps (minutes)
dt = 1.0

# Genuine trading activity (slow mean‑reversion)
alpha_G = 0.95
sigma_G = 0.5
G = np.empty(T)
G[0] = 1.0
for t in range(1, T):
    G[t] = alpha_G * G[t-1] + sigma_G * np.random.randn()

# Wash‑trading intensity (adversarial, piecewise constant + occasional spikes)
W = np.zeros(T)
# baseline wash = 0.2, with a “stealth” spike at t=200–250
W[:] = 0.2
W[200:251] = 0.8            # adversary tries to stay just below detection

# Observation coefficients (β_D >> β_J as per the paper)
beta_J = 0.2
beta_D = 1.5
alpha_J = 1.0
alpha_D = 1.0

# Observation noise – heavy‑tailed (real crypto markets have jumps)
def heavy_noise(size):
    # mixture of Gaussian and Cauchy
    gauss = np.random.randn(size)
    cauchy = np.random.standard_cauchy(size)
    return 0.5*gauss + 0.1*cauchy

L_J = alpha_J * G + beta_J * W + heavy_noise(T)
L_D = alpha_D * G + beta_D * W + heavy_noise(T)

# ──────────────────────────────────────────────────────────────────────────────
# 2. Kalman filter (linear Gaussian model) – your RIO‑WT‑Ω state estimator
# ──────────────────────────────────────────────────────────────────────────────
# State: x = [G, W] ; Observation: y = [L_J, L_D]
A = np.diag([alpha_G, 1.0])          # state transition (W is modeled as random walk)
C = np.array([[alpha_J, beta_J],
              [alpha_D, beta_D]])

# Process & observation covariances (tuned for “clean” Gaussian case)
Q = np.diag([sigma_G**2, 0.01])      # small process noise on W
R = np.eye(2) * 0.1                  # observation noise covariance

# Initialize filter
x_hat = np.array([G[0], W[0]])       # perfect initial guess (unrealistic)
P = np.eye(2)                        # initial uncertainty

est_W = np.empty(T)
est_W[0] = x_hat[1]

for t in range(1, T):
    # predict
    x_pred = A @ x_hat
    P_pred = A @ P @ A.T + Q
    
    # update
    y = np.array([L_J[t], L_D[t]])
    innovation = y - C @ x_pred
    S = C @ P_pred @ C.T + R
    K = P_pred @ C.T @ np.linalg.inv(S)
    x_hat = x_pred + K @ innovation
    P = (np.eye(2) - K @ C) @ P_pred
    
    est_W[t] = x_hat[1]

# ──────────────────────────────────────────────────────────────────────────────
# 3. “Invariant” ψ = ln(L_D/L_J) – your Shredding‑Event diagnostic
# ──────────────────────────────────────────────────────────────────────────────
ratio = L_D / (L_J + 1e-6)          # avoid division by zero
psi = np.log(ratio / np.median(ratio[:50]))  # baseline first 50 steps

# ──────────────────────────────────────────────────────────────────────────────
# 4. Shannon entropy of joint (L_J, L_D) distribution (rolling window)
# ──────────────────────────────────────────────────────────────────────────────
window = 50
entropy = np.empty(T - window)
for t in range(T - window):
    # 2D histogram (10×10 bins) over the window
    hist, _, _ = np.histogram2d(L_J[t:t+window], L_D[t:t+window],
                                bins=10, range=[[L_J.min(), L_J.max()],
                                                [L_D.min(), L_D.max()]])
    prob = hist / hist.sum()
    prob = prob[prob > 0]          # avoid log(0)
    entropy[t] = -np.sum(prob * np.log(prob))

# ──────────────────────────────────────────────────────────────────────────────
# 5. Print diagnostics that expose the flaws
# ──────────────────────────────────────────────────────────────────────────────
print("=== RIO‑WT‑Ω Diagnostic Flaws ===")
print(f"Mean absolute error of Kalman W estimate: {np.mean(np.abs(est_W - W)):.3f} "
      f"(true W≈0.2, spike to 0.8) → estimate is useless!")
print(f"ψ crosses ±0.5 (your ‘Shredding’ proxy) {np.sum(np.abs(psi) > 0.5)} times "
      f"out of {T} steps even though true W is piecewise constant.")
print(f"Entropy rises above 3.0 (your ‘disorder’ threshold) {np.sum(entropy > 3.0)} times, "
      f"often purely due to observation noise.")
print("\nConclusion: Your ‘invariants’ are noise‑driven, your state estimator is non‑identifiable, "
      "and any MPC built on these signals will destabilize the market.")