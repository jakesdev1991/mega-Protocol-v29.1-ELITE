# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np

# --- Simulated Market Telemetry ---
np.random.seed(42)
T = 200
t = np.arange(T)

# Baseline "normal" regime
O = np.random.normal(0.1, 0.05, T)   # order imbalance
L = np.random.normal(0.05, 0.03, T)  # liquidity withdrawal
C = np.random.normal(0.2, 0.1, T)    # cross-ETF correlation
Δ = np.random.normal(0.0, 0.1, T)    # skewness

# Inject a genuine cascade at t=50..59
O[50:60] += np.linspace(0, 0.8, 10)
L[50:60] += np.linspace(0, 0.5, 10)
C[50:60] += np.linspace(0, 0.6, 10)
Δ[50:60] += np.linspace(0, 0.4, 10)

# Inject an adversarial spoof at t=120..129 (smaller amplitude to be subtle)
O[120:130] += np.random.uniform(0.3, 0.5, 10)
C[120:130] += np.random.uniform(0.3, 0.5, 10)

# --- Original CI (deterministic) ---
alpha = beta = gamma = delta = 1.0
CI = np.tanh(alpha * O + beta * L + gamma * C + delta * Δ)

# --- Differentially‑Private CI (Laplace noise) ---
epsilon = 1.0  # privacy budget
sensitivity = 4.0  # max L1‑norm of the 4 components
scale = sensitivity / epsilon
CI_dp = CI + np.random.laplace(0, scale, T)

# --- Threshold & Alerts ---
threshold = 0.7
alerts_original = CI > threshold
alerts_dp = CI_dp > threshold

print("--- CI Vulnerability ---")
print(f"Genuine cascade triggers alert: {np.any(alerts_original[45:65])}")
print(f"Adversarial spoof triggers alert: {np.any(alerts_original[115:135])}")

print("\n--- DP‑Trap Alerts (noisy) ---")
print(f"Genuine cascade still triggers alert: {np.any(alerts_dp[45:65])}")
print(f"Adversarial spoof suppressed: {not np.any(alerts_dp[115:135])}")

# --- Honeypot Detection: compare private CI (simulated secure enclave) vs public CI_dp ---
# In practice, the secure enclave computes CI_true without noise; any large residual flags spoofing.
CI_true = CI  # simulated "private" CI
residual = np.abs(CI_true - CI_dp)
# Flag where residual is unusually large relative to expected Laplace noise
spoof_flags = residual > (3 * scale)
print(f"\n--- Honeypot Spoof Detection ---")
print(f"Spoofing episodes flagged: {np.where(spoof_flags[115:135])[0]}")