# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
# -*- coding: utf-8 -*-
"""
Agent Smith Validation Suite for Trauma‑Induced Performance Anxiety
Checks:
  - COD definition bounds
  - Phase‑Shift Decoupling (PSD) preserves performance amplitude
  - Informational Stiffness invariant (ξ_id) respected
"""

import numpy as np

# ---------------------------
# Helper functions
# ---------------------------
def inner_product(a, b):
    """Standard complex inner product ⟨a|b⟩."""
    return np.vdot(a, b)  # vdot conjugates first argument

def COD(psi_threat, psi_reality):
    """Chain Overlap Density (normalized squared overlap)."""
    num = np.abs(inner_product(psi_threat, psi_reality))**2
    den = (inner_product(psi_threat, psi_threat) *
           inner_product(psi_reality, psi_reality))
    return num / den if den != 0 else 0.0

def apply_psd(psi_initial, gamma_t, sigma_x):
    """
    Time‑evolution under H_eff = H_org + gamma(t)*σₓ.
    For validation we set H_org = 0 (interaction picture) and
    integrate d|ψ>/dt = -i * gamma(t) * σₓ |ψ>.
    Solution: |ψ(t)> = exp(-i * φ(t) * σₓ) |ψ(0)>,
    where φ(t) = ∫₀ᵗ gamma(t') dt'.
    """
    phi = np.trapz(gamma_t, dx=1.0)  # simple integral assuming unit dt steps
    # exp(-i φ σₓ) = cos(φ) I - i sin(φ) σₓ
    U = np.cos(phi) * np.eye(2) - 1j * np.sin(phi) * sigma_x
    return U @ psi_initial

# ---------------------------
# Basis definitions (2‑level subspace)
# ---------------------------
# |threat>  = |0>
# |safety>  = |1>
# |perf>    = cosθ|0> + sinθ|1>  (performance state, arbitrary but fixed)
theta_perf = np.pi / 3  # 60° example; can be changed
psi_threat = np.array([1.0, 0.0])          # |0>
psi_safety = np.array([0.0, 1.0])          # |1>
psi_perf   = np.array([np.cos(theta_perf), np.sin(theta_perf)])

# ---------------------------
# 1. COD Normalization Check
# ---------------------------
# Random reality states to test bounds
np.random.seed(42)
for _ in range(5):
    psi_real = np.random.randn(2) + 1j*np.random.randn(2)
    psi_real /= np.linalg.norm(psi_real)  # normalize
    cod_val = COD(psi_threat, psi_real)
    assert 0.0 <= cod_val <= 1.0 + 1e-12, f"COD out of bounds: {cod_val}"
print("✓ COD normalization passed.")

# ---------------------------
# 2. PSD Action Check
# ---------------------------
# Define a simple time‑dependent coupling: a pulse
time_steps = 100
gamma_t = np.zeros(time_steps)
gamma_t[20:80] = 0.5  # constant coupling during mid‑interval

# Evolve the threat state under PSD
psi_t = apply_psd(psi_threat, gamma_t, sigma_x=np.array([[0,1],[1,0]]))

# Performance amplitude before and after
amp_before = np.abs(inner_product(psi_perf, psi_threat))**2
amp_after  = np.abs(inner_product(psi_perf, psi_t))**2

# Informational Stiffness proxy: require amplitude change < 1e-3
assert np.abs(amp_before - amp_after) < 1e-3, \
    f"Performance amplitude changed: {amp_before} -> {amp_after}"
print("✓ Informational Stiffness (performance amplitude) preserved.")

# COD_trauma should drop
cod_before = COD(psi_threat, psi_threat)  # =1 by definition
cod_after  = COD(psi_t, psi_threat)
assert cod_after < cod_before - 0.1, f"COD not reduced enough: {cod_after}"
print(f"✓ COD_trauma reduced from {cod_before:.3f} to {cod_after:.3f}")

# ---------------------------
# 3. Invariant Guard (ξ_id)
# ---------------------------
# Define a critical stiffness threshold
xi_c = 0.5  # arbitrary but >0
# Proxy for ξ_id = performance amplitude (must stay above xi_c)
xi_id_t = amp_after
assert xi_id_t >= xi_c, f"Informational Stiffness violated: {xi_id_t} < {xi_c}"
print(f"✓ Informational Stiffness maintained: {xi_id_t:.3f} ≥ {xi_c}")

print("\nAll validation checks passed. The model is mathematically sound and Omega‑Protocol compliant.")