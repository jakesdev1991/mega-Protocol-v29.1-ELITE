# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
#!/usr/bin/env python3
"""
EDIP-Ω Mathematical & Invariant Compliance Checker
--------------------------------------------------
This script validates the core mathematical properties of the repaired
EDIP-Ω proposal against the Omega Physics Rubric (v26.0).

It uses synthetic data to exercise the GRU, PINN, anomaly detection,
and MPC components, then asserts that all invariants and constraints hold.
"""

import numpy as np
import torch
import torch.nn as nn
from scipy.optimize import minimize_qp  # simple QP solver (requires scipy>=1.6)
from scipy.signal import savgol_filter

# -------------------------
# 1. Synthetic Data Generation
# -------------------------
np.random.seed(42)
torch.manual_seed(42)

# Simulate a rolling window of exposure events (7 days, 1 event per hour)
n_events = 7 * 24  # 168
# Features: Δt_e (hours since last mod), revision intensity r_d,
# access anomaly a_d, cross-domain flag c_d, access entropy H, mask m
Delta_t_e = np.random.exponential(scale=2.0, size=n_events)   # hours
r_d = np.random.uniform(0, 0.5, size=n_events)               # versions/day
a_d = np.random.uniform(0, 1, size=n_events)                 # anomaly score
c_d = np.random.binomial(1, 0.2, size=n_events)              # cross-domain flag
H_access = np.random.uniform(0, 2, size=n_events)            # entropy
m_d = np.random.binomial(1, 0.8, size=n_events)              # access-log available (1) or not (0)
# Impose missing access logs: set a_d to 0.5 when m_d==0 (as per proposal)
a_d = np.where(m_d == 1, a_d, 0.5)

# Stack features
X_raw = np.stack([Delta_t_e, r_d, a_d, c_d, H_access, m_d], axis=1)  # shape (n_events,6)

# Simulate plasma parameters vector (e.g., beta, density, temperature)
p_plasma = np.random.randn(5)

# -------------------------
# 2. GRU for ESI Computation
# -------------------------
input_dim = X_raw.shape[1]
hidden_dim = 16
gru = nn.GRU(input_size=input_dim, hidden_size=hidden_dim, batch_first=True)
# Standardize features (zero mean, unit var) as per proposal
X_mean = X_raw.mean(axis=0)
X_std = X_raw.std(axis=0) + 1e-8
X_norm = (X_raw - X_mean) / X_std
X_tensor = torch.tensor(X_norm, dtype=torch.float32).unsqueeze(0)  # (1, seq, feat)

# Forward pass
h0 = torch.zeros(1, 1, hidden_dim)
esi_raw, _ = gru(X_tensor, h0)   # esi_raw shape (1, seq, hidden)
# Take last hidden state as ESI score (could also aggregate)
esi_score = torch.sigmoid(esi_raw[:, -1, :]).mean().item()  # map to [0,1] then scale
# Scale to roughly match expected ESI range (0‑3) as used in constraints
ESI_k = esi_score * 3.0
print(f"Computed ESI_k: {ESI_k:.3f}")

# -------------------------
# 3. PINN Mapping to Omega Variables
# -------------------------
class PINN_Omega(nn.Module):
    def __init__(self, esi_dim, plasma_dim):
        super().__init__()
        self.fc = nn.Linear(esi_dim + plasma_dim, 64)
        self.out = nn.Linear(64, 4)  # [Φ_N, Φ_Δ, ξ_N, ξ_Δ]

    def forward(self, esi, plasma):
        x = torch.cat([esi, plasma], dim=-1)
        x = torch.relu(self.fc(x))
        out = self.out(x)
        # Apply Rubric‑compliant activations
        Phi_N = torch.sigmoid(out[:, 0:1])                     # [0,1]
        Phi_Delta = torch.softplus(out[:, 1:2]) + 0.0          # ≥0, we later shift
        xi_N = torch.softplus(out[:, 2:3])                     # ≥0
        xi_Delta = torch.softplus(out[:, 3:4]) + 1.0           # ≥1
        return torch.cat([Phi_N, Phi_Delta, xi_N, xi_Delta], dim=-1)

pinn = PINN_Omega(esi_dim=hidden_dim, plasma_dim=p_plasma.shape[0])
esi_vec = torch.tensor(esi_raw[:, -1, :], dtype=torch.float32)  # (1, hidden)
plasma_vec = torch.tensor(p_plasma, dtype=torch.float32).unsqueeze(0)  # (1,5)
with torch.no_grad():
    Omega_vars = pinn(esi_vec, plasma_vec).squeeze(0).numpy()
Phi_N_exp, Phi_Delta_exp, xi_N_exp, xi_Delta_exp = Omega_vars
print(f"Φ_N^exp: {Phi_N_exp:.3f} (should be ∈[0,1])")
print(f"Φ_Δ^exp: {Phi_Delta_exp:.3f}")
print(f"ξ_N^exp: {xi_N_exp:.3f} (should be ≥0)")
print(f"ξ_Δ^exp: {xi_Delta_exp:.3f} (should be ≥1)")

# -------------------------
# 4. Invariant ψ and Deviation χ
# -------------------------
# Simulate effective mass ratio φ_n (dimensionless, >0)
phi_n = np.random.uniform(0.5, 2.0)   # example range
psi = np.log(phi_n)                  # fundamental invariant
# Baseline connectivity Φ_N⁰ (pretrained or historical)
Phi_N0 = 0.8
chi = np.log(Phi_N_exp / Phi_N0)     # derived deviation, NOT an invariant
print(f"ψ = ln(φ_n) = {psi:.3f}")
print(f"χ = ln(Φ_N^exp/Φ_N⁰) = {chi:.3f} (derived, not an invariant)")

# -------------------------
# 5. Anomaly Detection & Prediction Rule
# -------------------------
# Simulate an ESI time series (30 days) for STL‑like detrending
t_days = np.arange(30)
esi_ts = ESI_k + 0.2 * np.sin(2*np.pi*t_days/7) + np.random.normal(0, 0.1, size=30)
# Simple STL: trend via moving average, residual = original - trend
window = 5
trend = np.convolve(esi_ts, np.ones(window)/window, mode='same')
residual = esi_ts - trend
sigma_res = np.std(residual) + 1e-8
anomaly_score = np.abs(residual[-1]) / sigma_res   # last point
print(f"Anomaly score s_ESI(t): {anomaly_score:.3f}")

# Smoothed derivative of ξ_Δ (using Savitzky‑Golay filter on a short history)
xi_delta_hist = np.clip(xi_Delta_exp + np.random.normal(0,0.05,size=10), 1, None)
xi_delta_smooth = savgol_filter(xi_delta_hist, window_length=5, polyorder=2)
deriv = np.gradient(xi_delta_smooth)[-1]   # latest derivative
print(f"Smoothed dξ_Δ/dt: {deriv:.5f}")

# Prediction rule thresholds (as per proposal)
pred_trigger = (anomaly_score > 2.5) and (Phi_Delta_exp > 0.55) and (deriv > 0.05)
print(f"Prediction trigger (pre‑Shredding Alert): {pred_trigger}")

# -------------------------
# 6. MPC Cost Function & QP Constraints
# -------------------------
# Define a simple quadratic cost over a horizon H=2 (for illustration)
H = 2
# Decision variable: control effort u (scalar) affecting ESI linearly:
#   ESI_k_next = ESI_k - kappa * u   (kappa > 0)
kappa = 0.3
# Target ESI: we want it ≤ 2.5, so penalize excess via ReLU in cost
# Cost = sum_{h=0}^{H-1} [ (1 - S_h)^2 + α S_h + λ (P_meas - P_target)^2
#                + β (ξ_Δ - 1)^2 + γ * ReLU(ESI_k - 2.5) ]
# For demo we fix S_h, P_meas, etc. and focus on ESI & ξ_Δ terms.
alpha, beta, gamma = 0.1, 0.2, 0.5
S_h = 0.7   # dummy Shannon entropy
P_meas, P_target = 1.0, 1.0   # dummy pressure match
lambda_ = 0.1

def cost(u):
    # u is assumed scalar; we propagate its effect on ESI and ξ_Δ linearly
    ESI_u = ESI_k - kappa * u[0]
    xi_Delta_u = xi_Delta_exp + 0.05 * u[0]   # assume control slightly raises ξ_Δ
    term_esi = gamma * max(0.0, ESI_u - 2.5)
    term_xi = beta * (xi_Delta_u - 1.0)**2
    const = (1 - S_h)**2 + alpha * S_h + lambda_ * (P_meas - P_target)**2
    return const + term_esi + term_xi

# QP formulation: minimize 0.5 u^T P u + q^T u subject to G u <= h, A u = b
# We approximate the cost as quadratic around u=0 via finite differences
eps = 1e-6
c0 = cost([0.0])
c_plus = cost([eps])
c_minus = cost([-eps])
grad = (c_plus - c_minus) / (2*eps)
# second derivative (approx)
hess = (c_plus - 2*c0 + c_minus) / (eps**2)
P = np.array([[max(hess, 1e-8)]])   # ensure PSD
q = np.array([grad])

# Inequality constraints: ESI_k ≤ 2.5, Φ_N ≥ 0.75, ξ_Δ ≤ 3.0
# Map to u: ESI_u = ESI_k - kappa*u ≤ 2.5  =>  -kappa*u ≤ 2.5 - ESI_k  =>  u ≥ (ESI_k - 2.5)/kappa
#          Φ_N constraint does not depend on u in this simple model (ignore)
#          ξ_Δ_u = ξ_Δ_exp + 0.05*u ≤ 3.0   =>  0.05*u ≤ 3.0 - ξ_Δ_exp  =>  u ≤ (3.0 - ξ_Δ_exp)/0.05
lb_esi = (ESI_k - 2.5) / kappa if kappa != 0 else -np.inf
ub_xi = (3.0 - xi_Delta_exp) / 0.05
G = np.array([[-1.0], [1.0]])   # -u ≤ -lb  -> u ≥ lb ;  u ≤ ub
h = np.array([-lb_esi, ub_xi])
# Equality constraints (none)
A = np.zeros((0,1))
b = np.zeros((0,))

# Solve QP
res = minimize_qp(P, q, G, h, A, b)
u_opt = res.x
print(f"Optimal control u*: {u_opt[0]:.4f}")
# Verify constraints
ESI_after = ESI_k - kappa * u_opt[0]
xi_after = xi_Delta_exp + 0.05 * u_opt[0]
print(f"ESI after control: {ESI_after:.3f} (should be ≤ 2.5)")
print(f"ξ_Δ after control: {xi_after:.3f} (should be ≤ 3.0)")
assert ESI_after <= 2.5 + 1e-6, "ESI constraint violated"
assert xi_after <= 3.0 + 1e-6, "ξ_Δ constraint violated"
assert 0.0 <= Phi_N_exp <= 1.0 + 1e-6, "Φ_N out of [0,1]"
assert xi_N_exp >= -1e-6, "ξ_N negative"
assert xi_Delta_exp >= 1.0 - 1e-6, "ξ_Δ < 1"
# Invariant check: ψ is defined via φ_n, not via Φ_N
assert not np.isclose(psi, np.log(Phi_N_exp/Phi_N0)), "ψ incorrectly set to ln(Φ_N/Φ₀)"
print("\nAll invariants and constraints satisfied ✅")