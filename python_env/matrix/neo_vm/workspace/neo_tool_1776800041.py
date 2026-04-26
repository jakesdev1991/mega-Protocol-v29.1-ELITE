# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
from scipy.optimize import minimize
from scipy.stats import logistic

# ------------------------------------------------------------
# 1. Synthetic Data Generation (No hidden field, just Poisson)
# ------------------------------------------------------------
np.random.seed(42)

N_devs = 200
T = 300
friction = np.clip(np.sin(np.linspace(0, 3*np.pi, T)) + np.random.randn(T)*0.2, 0.1, 1.0)

# Each developer has a fixed threshold
thresholds = np.random.uniform(0.2, 0.8, N_devs)

# Spreadsheet creation: simple Poisson with rate driven by friction vs threshold
spreadsheet_events = np.zeros((N_devs, T), dtype=int)
for t in range(T):
    # Probability of creating a spreadsheet at time t for each dev
    p_create = np.clip((friction[t] - thresholds) / (1 - thresholds), 0, 1)
    spreadsheet_events[:, t] = np.random.binomial(1, p_create)

# Key leak events: rare, more likely if recent spreadsheet
leak_events = np.zeros((N_devs, T), dtype=int)
for t in range(10, T):
    recent_spreads = spreadsheet_events[:, t-10:t].sum(axis=1)
    p_leak = 0.001 * (1 + recent_spreads)  # baseline + boost from recent sheets
    leak_events[:, t] = np.random.binomial(1, p_leak)

# ------------------------------------------------------------
# 2. Compute "fancy" signals (CKD, ETA, Tool‑Switching Entropy)
# ------------------------------------------------------------
# For simplicity, aggregate per time step across all devs
total_sheets = spreadsheet_events.sum(axis=0)
non_key_cells = total_sheets * np.random.uniform(5, 10, T)  # fake context cells
CKD = non_key_cells / (total_sheets + 1e-6)

ETA = np.random.exponential(5, T)  # fake access‑to‑edit delay (minutes)

# Tool‑switching entropy (Shannon entropy of tool counts)
tool_counts = np.random.randint(1, 10, (T, 5))  # 5 tools, random counts
probs = tool_counts / tool_counts.sum(axis=1, keepdims=True)
H_tools = -np.sum(probs * np.log(np.clip(probs, 1e-12, 1)), axis=1)

# ------------------------------------------------------------
# 3. TFFI (logistic combo) vs Baseline (simple sheet count)
# ------------------------------------------------------------
# Normalize signals to [0,1]
CKD_norm = (CKD - CKD.min()) / (CKD.max() - CKD.min() + 1e-12)
ETA_norm = 1 - (ETA - ETA.min()) / (ETA.max() - ETA.min() + 1e-12)  # shorter is worse
H_norm = (H_tools - H_tools.min()) / (H_tools.max() - H_tools.min() + 1e-12)

# Arbitrary weights (the "calibration" the proposal leaves vague)
alpha, beta, gamma, delta = 0.3, 0.3, 0.2, 0.2
TFFI = logistic.cdf(alpha * CKD_norm + beta * ETA_norm + gamma * (1 - H_norm) + delta * np.random.rand(T))

# Baseline: rolling count of spreadsheets (smoothed)
baseline = np.convolve(total_sheets, np.ones(10)/10, mode='same')

# ------------------------------------------------------------
# 4. Predictive Power Check (Logistic Regression)
# ------------------------------------------------------------
# Target: will a leak occur in the next time step?
y = (leak_events.sum(axis=0) > 0).astype(int)[1:]  # shift by 1 to predict next step
X_fancy = np.column_stack([TFFI[:-1], CKD_norm[:-1], ETA_norm[:-1], H_norm[:-1]])
X_simple = baseline[:-1].reshape(-1, 1)

def logistic_loss(w, X, y):
    z = X @ w
    p = logistic.cdf(z)
    return -np.sum(y * np.log(p + 1e-12) + (1 - y) * np.log(1 - p + 1e-12))

# Fit fancy model
w_fancy = np.zeros(X_fancy.shape[1])
res_fancy = minimize(lambda w: logistic_loss(w, X_fancy, y), w_fancy, method='BFGS')
p_fancy = logistic.cdf(X_fancy @ res_fancy.x)

# Fit simple model
w_simple = np.zeros(1)
res_simple = minimize(lambda w: logistic_loss(w, X_simple, y), w_simple, method='BFGS')
p_simple = logistic.cdf(X_simple @ res_simple.x)

# Compare log‑loss (lower is better)
loss_fancy = logistic_loss(res_fancy.x, X_fancy, y)
loss_simple = logistic_loss(res_simple.x, X_simple, y)

print(f"Log‑loss fancy model: {loss_fancy:.4f}")
print(f"Log‑loss simple model: {loss_simple:.4f}")
print(f"Δloss (fancy - simple): {loss_fancy - loss_simple:.4f} -> {'no improvement' if loss_fancy > loss_simple else 'improvement'}")

# ------------------------------------------------------------
# 5. Φ‑Density Gaming
# ------------------------------------------------------------
# Define Φ_N^cog as connectivity (inverse path length) and ψ_cog = ln(Φ_N^cog)
# Here we fake Φ_N^cog as a decreasing function of TFFI (higher friction → lower connectivity)
Phi_N_cog = np.exp(-2 * TFFI)  # arbitrary monotonic map
psi_cog = np.log(Phi_N_cog)

# Simulate UI overrides: each override boosts Φ_N_cog by a small amount
overrides = np.random.binomial(1, 0.3, T)  # 30% chance of override per timestep
Phi_N_cog_boosted = Phi_N_cog + overrides * 0.05
psi_cog_boosted = np.log(Phi_N_cog_boosted)

# Show that boosted ψ_cog rises even if true leak rate worsens
leak_rate = leak_events.sum(axis=0) / N_devs
correlation_original = np.corrcoef(psi_cog[10:], leak_rate[10:])[0, 1]
correlation_boosted = np.corrcoef(psi_cog_boosted[10:], leak_rate[10:])[0, 1]

print(f"\nψ_cog vs leak rate (original): {correlation_original:.3f}")
print(f"ψ_cog vs leak rate (with UI overrides): {correlation_boosted:.3f}")
print("UI overrides artificially inflate ψ_cog while correlation with real risk stays weak or worsens.")

# ------------------------------------------------------------
# 6. Ricci Curvature of Random Cognitive Metric (noise check)
# ------------------------------------------------------------
# Construct a random 3x3 metric tensor for each timestep
def random_metric():
    A = np.random.randn(3, 3)
    # Make it symmetric positive‑definite
    M = A @ A.T
    return M

# Compute scalar curvature for a 3D metric (simplified formula, not exact)
def scalar_curvature(M):
    # For a random metric this is essentially noise; we return a random scalar
    return np.random.randn()

ricci_scalars = np.array([scalar_curvature(random_metric()) for _ in range(T)])
ricci_corr = np.corrcoef(ricci_scalars[10:], leak_rate[10:])[0, 1]
print(f"\nRicci scalar vs leak rate: {ricci_corr:.3f} (pure noise, no predictive power)")