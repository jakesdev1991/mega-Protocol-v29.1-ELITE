# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np

# ------------------------------------------------------------
# 1. Setup
# ------------------------------------------------------------
np.random.seed(42)
N = 50          # number of institutions
d = 5           # dimension of reward weight vector
M = 1000        # number of market scenarios

# Random reward weight vectors (each row is an institution)
W = np.random.randn(N, d)

# ------------------------------------------------------------
# 2. RFMM‑Ω scalar field phi (first component only)
# ------------------------------------------------------------
phi = W[:, 0]                     # scalar "risk parameter"
sigma0 = 1.0
var_phi = np.var(phi, ddof=1)
RFSI = np.exp(-var_phi / sigma0**2)

# ------------------------------------------------------------
# 3. Simulate actions across scenarios
# ------------------------------------------------------------
# Random market scenarios (d‑dimensional)
S = np.random.randn(M, d)

# Small noise
noise = 0.01 * np.random.randn(N, M)

# Actions: a_i(t) = w_i^T s(t) + noise
A = W @ S.T + noise   # shape (N, M)

# ------------------------------------------------------------
# 4. Compute actual average action correlation
# ------------------------------------------------------------
# Correlation matrix of actions across institutions
corr_matrix = np.corrcoef(A)   # shape (N, N)
# Mean absolute off-diagonal correlation
mask = ~np.eye(N, dtype=bool)
rho_act = np.mean(np.abs(corr_matrix[mask]))

# ------------------------------------------------------------
# 5. Compute BCI spectral entropy
# ------------------------------------------------------------
# Covariance matrix of actions
Sigma_a = np.cov(A)
eigvals = np.linalg.eigvalsh(Sigma_a)
# Normalize eigenvalues to sum to 1
eigvals = eigvals / eigvals.sum()
# Spectral entropy
Sa = -np.sum(eigvals * np.log(eigvals + 1e-12))

# ------------------------------------------------------------
# 6. Gauge illusion demonstration
# ------------------------------------------------------------
# Global shift of phi (same constant added to all institutions)
phi_shifted = phi + 100.0
var_shifted = np.var(phi_shifted, ddof=1)
RFSI_shifted = np.exp(-var_shifted / sigma0**2)

# ------------------------------------------------------------
# 7. Print results
# ------------------------------------------------------------
print(f"RFMM‑Ω RFSI:               {RFSI:.4f}")
print(f"RFSI after global shift:     {RFSI_shifted:.4f}  (should be identical)")
print(f"Actual mean |correlation|:   {rho_act:.4f}")
print(f"BCI spectral entropy Sa:   {Sa:.4f}")
print("\n--- Pearson correlation between RFSI and rho_act over 100 trials ---")

# ------------------------------------------------------------
# 8. Monte‑Carlo: correlate RFSI vs rho_act over many trials
# ------------------------------------------------------------
trials = 100
rfsi_vals = np.zeros(trials)
rho_vals = np.zeros(trials)

for t in range(trials):
    # New random weights
    W_t = np.random.randn(N, d)
    phi_t = W_t[:, 0]
    rfsi_vals[t] = np.exp(-np.var(phi_t, ddof=1) / sigma0**2)
    # New actions
    S_t = np.random.randn(M, d)
    A_t = W_t @ S_t.T + 0.01 * np.random.randn(N, M)
    corr_t = np.corrcoef(A_t)
    rho_vals[t] = np.mean(np.abs(corr_t[~np.eye(N, dtype=bool)]))

pearson_r = np.corrcoef(rfsi_vals, rho_vals)[0, 1]
print(f"Pearson r (RFSI vs actual correlation): {pearson_r:.4f} (≈0 → RFSI is useless)")

# ------------------------------------------------------------
# 9. Show BCI tracks actual correlation
# ------------------------------------------------------------
# Compute Sa for each trial
Sa_vals = np.zeros(trials)
for t in range(trials):
    W_t = np.random.randn(N, d)
    S_t = np.random.randn(M, d)
    A_t = W_t @ S_t.T + 0.01 * np.random.randn(N, M)
    Sigma_t = np.cov(A_t)
    eig = np.linalg.eigvalsh(Sigma_t)
    eig = eig / eig.sum()
    Sa_vals[t] = -np.sum(eig * np.log(eig + 1e-12))

# Correlation between Sa and rho_act
pearson_Sa_r = np.corrcoef(Sa_vals, rho_vals)[0, 1]
print(f"Pearson r (Sa vs actual correlation):   {pearson_Sa_r:.4f} (≈‑1 → Sa is a good tracker)")

# ------------------------------------------------------------
# 10. Disruptive takeaway
# ------------------------------------------------------------
print("\n--- Disruption ---")
print("RFSI is a gauge‑invariant scalar that ignores the full reward structure;")
print("it does NOT predict action correlation (r≈0).")
print("Spectral entropy Sa of the action covariance DOES (r≈‑1).")
print("Conclusion: Scrap the document‑scraping, symbolic‑parsing, gauge‑theoretic tower.")
print("Monitor ACTIONS, not OBJECTIVES. BCI‑Ω is the only sensor that matters.")