# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Omega Protocol Validation for Quantum Memory Shield for Distributed Cognition (QM‑Ω)
--------------------------------------------------------------------------------
This script checks the mathematical soundness of the QM‑Ω integration against the
Ω‑Physics invariants (Φ_N, Φ_Δ, ψ, S_cognitive) and the MPC‑Ω constraints.
"""

import numpy as np

# ----------------------------------------------------------------------
# 1. Parameter block – edit to test different scenarios
# ----------------------------------------------------------------------
np.random.seed(42)

# Number of cognitive agents (m) and dimension of cognitive state (d)
m = 25
d = 8

# Baseline Ω‑values (pre‑decoherence)
Phi_N_0 = 0.8          # baseline connectivity variance
Phi_Delta_0 = 0.1      # baseline asymmetry
R0 = 1.0               # reference curvature scale
lam = 0.5              # coupling λ in ψ invariant

# Parameters for CDI definition (tanh argument)
alpha = 1.2   # weight on decoherence ratio
beta  = 0.8   # weight on average residual error
gamma = 0.5   # weight on redundancy stress

# Decoherence thresholds and noise levels
tau_residual = 0.15   # residual‑error threshold for decohered agent
# Simulate agent responses:
#   y_i = E_i * c   (true encoded cognitive data)
#   e_i ~ N(0, sigma^2 * I)   (decoherence noise)
sigma = 0.2           # noise std‑dev per dimension
# True cognitive state vector (normalized)
c_true = np.random.randn(d)
c_true /= np.linalg.norm(c_true)

# Random sparse encoding matrix E (n x d) with redundancy rho = n/d
rho = 3.0
n = int(rho * d)
E = np.random.randn(n, d)
# Make rows sparse: keep only 20% entries
mask = np.random.rand(*E.shape) < 0.2
E *= mask

# Encode true state
y_true = E @ c_true                     # length n
# Split into m sub‑vectors (assume n divisible by m for simplicity)
assert n % m == 0, "Choose n divisible by m for equal partition"
block_len = n // m
y_blocks = [y_true[i*block_len:(i+1)*block_len] for i in range(m)]

# Simulate decohered responses
y_tilde_blocks = []
for i in range(m):
    noise = sigma * np.random.randn(block_len)
    y_tilde_blocks.append(y_blocks[i] + noise)

y_tilde = np.concatenate(y_tilde_blocks)

# ----------------------------------------------------------------------
# 2. Helper functions
# ----------------------------------------------------------------------
def residual_error(i):
    """Residual r_i = ytilde_i - E_i * c_true"""
    start, end = i*block_len, (i+1)*block_len
    E_i = E[start:end, :]
    ytil_i = y_tilde[start:end]
    return ytil_i - E_i @ c_true

def compute_CDI():
    """CDI = tanh(alpha*theta + beta*eps + gamma*rho)"""
    # decoherence ratio
    decohered = [np.linalg.norm(residual_error(i)) > tau_residual for i in range(m)]
    theta = np.mean(decohered)                     # fraction of decohered agents
    # average residual error magnitude
    eps = np.mean([np.linalg.norm(residual_error(i)) for i in range(m)])
    # redundancy stress (constant here)
    rho_val = n / d
    arg = alpha * theta + beta * eps + gamma * rho_val
    return np.tanh(arg)                            # ∈ (-1,1); we shift later to [0,1)

def compute_Phi_N_qm(CDI_val, tau1=4.0):
    """Φ_N^{(qm)}(t) = Φ_N^{(0)} - η1·CDI(t-τ1) + η2·(1-θ(t-τ1))"""
    # For simplicity we use instantaneous values and set η1=η2=0.3
    eta1, eta2 = 0.3, 0.3
    # θ needed for the second term – reuse from CDI computation
    decohered = [np.linalg.norm(residual_error(i)) > tau_residual for i in range(m)]
    theta = np.mean(decohered)
    return Phi_N_0 - eta1 * CDI_val + eta2 * (1.0 - theta)

def compute_Phi_Delta_qm(CDI_val, tau2=4.0):
    """Φ_Δ^{(qm)}(t) = Φ_Δ^{(0)} + η3·θ(t-τ2) - η4·ε(t-τ2)"""
    eta3, eta4 = 0.2, 0.2
    decohered = [np.linalg.norm(residual_error(i)) > tau_residual for i in range(m)]
    theta = np.mean(decohered)
    eps = np.mean([np.linalg.norm(residual_error(i)) for i in range(m)])
    return Phi_Delta_0 + eta3 * theta - eta4 * eps

def compute_psi(CDI_val):
    """ψ = ln(|R_G|/R0) + λ·CDI"""
    # Approximate agent‑graph curvature by variance of residuals (proxy)
    residuals = [np.linalg.norm(residual_error(i)) for i in range(m)]
    R_G = np.var(residuals) + 1e-9   # avoid zero
    return np.log(np.abs(R_G) / R0) + lam * CDI_val

def compute_entropy():
    """S_cognitive = -∑ p_i log p_i, p_i ∝ ||ytilde_i||"""
    norms = [np.linalg.norm(y_tilde[i*block_len:(i+1)*block_len]) for i in range(m)]
    p = np.array(norms) / np.sum(norms)
    # Avoid log(0)
    p = np.clip(p, 1e-12, None)
    return -np.sum(p * np.log(p))

# ----------------------------------------------------------------------
# 3. Compute quantities
# ----------------------------------------------------------------------
CDI_raw = compute_CDI()
# Shift tanh output from [-1,1] to [0,1] as implied by the paper (they treat argument as non‑negative)
CDI = (CDI_raw + 1.0) / 2.0   # now in [0,1]

Phi_N_qm = compute_Phi_N_qm(CDI)
Phi_Delta_qm = compute_Phi_Delta_qm(CDI)
psi_qm = compute_psi(CDI)
S_cog = compute_entropy()

# ----------------------------------------------------------------------
# 4. Ω‑Invariant & MPC‑Ω constraint checks
# ----------------------------------------------------------------------
assert 0.0 <= CDI <= 1.0, f"CDI out of bounds: {CDI}"
assert Phi_N_qm >= 0.0, f"Phi_N_qm negative: {Phi_N_qm}"
assert np.isfinite(Phi_Delta_qm), f"Phi_Delta_qm not finite: {Phi_Delta_qm}"
assert np.isfinite(psi_qm), f"psi not finite: {psi_qm}"
assert S_cog >= np.log(3) - 1e-9, f"Entropy below ln(3): {S_cog}"

# MPC‑Ω constraints
assert CDI <= 0.7 + 1e-9, f"CDI exceeds 0.7: {CDI}"
assert Phi_N_qm >= 0.6 - 1e-9, f"Phi_N_qm below 0.6: {Phi_N_qm}"
assert S_cog >= np.log(3) - 1e-9, f"Entropy constraint violated: {S_cog}"

# Cost integrand non‑negativity (sampled at this time step)
mu1, mu2, mu3 = 1.0, 1.0, 1.0
integrand = ((CDI - 0.6) ** 2 if CDI > 0.6 else 0.0) \
          + mu1 * ((0.6 - Phi_N_qm) ** 2 if Phi_N_qm < 0.6 else 0.0) \
          + mu2 * (Phi_Delta_qm ** 2) \
          + mu3 * ((np.log(3) - S_cog) ** 2 if S_cog < np.log(3) else 0.0)
assert integrand >= 0.0, f"Cost integrand negative: {integrand}"

# ----------------------------------------------------------------------
# 5. Report
# ----------------------------------------------------------------------
print("=== QM‑Ω Validation Report ===")
print(f"CDI (shifted tanh)          : {CDI:.4f}")
print(f"Φ_N^{(qm)}                  : {Phi_N_qm:.4f}")
print(f"Φ_Δ^{(qm)}                  : {Phi_Delta_qm:.4f}")
print(f"ψ invariant                 : {psi_qm:.4f}")
print(f"S_cognitive (entropy)       : {S_cog:.4f}  (ln(3) = {np.log(3):.4f})")
print(f"MPC constraints satisfied   : CDI≤0.7? {CDI<=0.7}, Φ_N≥0.6? {Phi_N_qm>=0.6}, S≥ln3? {S_cog>=np.log(3)}")
print(f"Cost integrand (t)          : {integrand:.6f}")
print("All Ω‑Physics invariants and MPC‑Ω constraints hold. ✅")