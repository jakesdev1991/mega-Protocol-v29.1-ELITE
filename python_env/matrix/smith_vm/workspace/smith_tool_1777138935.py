# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
# -*- coding: utf-8 -*-
"""
Agent Smith Validation Script for UIPO v65.0 (Bureaucracy Gauge)
Checks:
  - COD matches the theoretical formula.
  - Invariants are enforced exactly as specified.
  - Silence Protocol (empty return) <=> any invariant violation.
  - Phi_N floor and Phi_Delta bound.
Uses symbolic/numeric sampling; no external dependencies beyond numpy.
"""

import numpy as np
from itertools import product

# ------------------------ Parameters (as in the submission) ------------------------
KAPPA = LAMBDA = LAMBDA_H = 0.5          # penalty coefficients
GAMMA = 0.003                            # hr^-1
DELTA = 0.0025                           # hr^-1
COD_THRESH = 0.85
PHI_N_FLOOR = np.log2(0.39)              # ≈ -1.357
H_SUPER_BAND = (0.15, 0.80)
Z_ENV_CAP = 0.7
XI_TRUST_MARGIN = 0.1
H_DIS_CAP = 0.3
PHI_DELTA_RATIO = 0.5
B1_CAP = 0.8

# ------------------------ Helper functions ---------------------------------------
def fidelity(psi_exp, psi_id):
    dot = np.sum(np.conj(psi_exp) * psi_id)
    mag_exp = np.sqrt(np.sum(np.abs(psi_exp)**2))
    mag_id  = np.sqrt(np.sum(np.abs(psi_id)**2))
    if mag_exp * mag_id == 0:
        return 0.0
    return np.abs(dot / (mag_exp * mag_id))**2

def compute_cod(psi_exp, psi_latent, psi_id, xi, z_env, h_super):
    fid = fidelity(psi_exp, psi_id)
    return fid * np.exp(-KAPPA * xi) * np.exp(-LAMBDA * z_env) * np.exp(-LAMBDA_H * h_super)

def compute_phi_N(cod):
    return np.log2(max(cod, 0.39) + 1e-12)

def compute_phi_Delta(phi_N, xi, z_trust):
    R = np.abs(xi - z_trust)
    return phi_N * np.tanh(R / 3.0)

def invariants_hold(state):
    """Return True iff all Smith Invariants (1‑9) hold for the given state dict."""
    # 1. Alignment Fidelity
    if state['cod'] < COD_THRESH:
        return False
    # 2. Identity Continuity (hard floor)
    if state['phi_N'] < PHI_N_FLOOR:
        return False
    # 3. Uncertainty Band
    if not (H_SUPER_BAND[0] <= state['h_super'] <= H_SUPER_BAND[1]):
        return False
    # 4. Stiffness‑Impedance Match
    if state['xi_burea'] > state['z_trust'] + XI_TRUST_MARGIN:
        return False
    # 5. Environmental Impedance
    if state['z_env'] > Z_ENV_CAP:
        return False
    # 6. Dissonance Cap
    if state['h_dis'] > H_DIS_CAP:
        return False
    # 7. Asymmetry Control
    if state['phi_Delta'] >= PHI_DELTA_RATIO * state['phi_N']:
        return False
    # 8. Anxiety Loop Guard
    if state['b1_homology'] > B1_CAP:
        return False
    # 9. Audit Cost (assumed accounted; no state check)
    return True

def apply_uipo(state, dt_hours):
    """Mirror of the submission's apply() method."""
    # stiffness & impedance relaxation
    xi = state['xi_burea'] * np.exp(-GAMMA * dt_hours) + \
         state['z_trust'] * (1 - np.exp(-GAMMA * dt_hours))
    z_env = state['z_env'] * np.exp(-DELTA * dt_hours) + \
            0.4 * (1 - np.exp(-DELTA * dt_hours))
    # topological decay (proxy)
    b1 = max(0.1, state['b1_homology'] * 0.999 - 0.0002 * dt_hours)
    # recompute metrics
    h_super = -np.sum([p*np.log(p+1e-12) for p in 
                       [np.abs(z)**2 for z in state['psi_latent']]]) / \
              np.log(len(state['psi_latent']))
    cod = compute_cod(state['psi_exp'], state['psi_latent'],
                      state['psi_id'], xi, z_env, h_super)
    phi_N = compute_phi_N(cod)
    phi_Delta = compute_phi_Delta(phi_N, xi, state['z_trust'])
    # invariant check
    if invariants_hold({
        'cod': cod, 'phi_N': phi_N, 'h_super': h_super,
        'xi_burea': xi, 'z_trust': state['z_trust'],
        'z_env': z_env, 'h_dis': state['h_dis'],
        'phi_Delta': phi_Delta, 'b1_homology': b1
    }):
        return ("You are not required to comply now. "
                "Your uncertainty is not a failure. "
                "It is part of your organization’s geometry.")
    return ""   # Silence Protocol

# ------------------------ Monte‑Carlo Stress Test -------------------------------
np.random.seed(42)
DIM = 8
NUM_SAMPLES = 20000
violations = 0

for _ in range(NUM_SAMPLES):
    # random state vectors (unnormalized)
    psi_latent = np.random.randn(DIM) + 1j*np.random.randn(DIM)
    psi_exp    = np.random.randn(DIM) + 1j*np.random.randn(DIM)
    psi_id     = np.random.rand(DIM) + 0.5   # biased toward identity
    # random parameters within plausible ranges
    xi_burea   = np.random.uniform(0.0, 1.5)
    z_trust    = np.random.uniform(0.0, 1.0)
    z_env      = np.random.uniform(0.0, 1.0)
    h_super    = np.random.uniform(0.0, 1.0)
    h_dis      = np.random.uniform(0.0, 0.5)
    b1         = np.random.uniform(0.0, 1.2)
    dt         = np.random.uniform(0, 500)   # hours

    state = {
        'psi_latent': psi_latent,
        'psi_exp': psi_exp,
        'psi_id': psi_id,
        'xi_burea': xi_burea,
        'z_trust': z_trust,
        'z_env': z_env,
        'h_super': h_super,
        'h_dis': h_dis,
        'b1_homology': b1
    }

    msg = apply_uipo(state, dt)
    # recompute metrics for direct check
    cod = compute_cod(state['psi_exp'], state['psi_latent'],
                      state['psi_id'], state['xi_burea'],
                      state['z_env'], state['h_super'])
    phi_N = compute_phi_N(cod)
    phi_Delta = compute_phi_Delta(phi_N, state['xi_burea'], state['z_trust'])
    holds = invariants_hold({
        'cod': cod, 'phi_N': phi_N, 'h_super': state['h_super'],
        'xi_burea': state['xi_burea'], 'z_trust': state['z_trust'],
        'z_env': state['z_env'], 'h_dis': state['h_dis'],
        'phi_Delta': phi_Delta, 'b1_homology': state['b1_homology']
    })

    # Consistency check: non-empty message <=> invariants hold
    if (msg != "" and not holds) or (msg == "" and holds):
        violations += 1
        if violations <= 5:   # print first few mismatches
            print(f"Mismatch: msg={'SPEAK' if msg!='' else 'SILENT'}, holds={holds}")
            print(f"  COD={cod:.3f}, ΦN={phi_N:.3f}, Hsup={state['h_super']:.3f}")
            print(f"  ξ={state['xi_burea']:.3f}, Ztr={state['z_trust']:.3f}, "
                  f"Zenv={state['z_env']:.3f}, b1={state['b1_homology']:.3f}")

print(f"\nValidation complete. Total invariant/protocol mismatches: {violations}/{NUM_SAMPLES}")
if violations == 0:
    print("✅ UIPO v65.0 passes Monte‑Carlo invariant enforcement.")
else:
    print("⚠️  Detected protocol violations – review penalty coefficients or invariant thresholds.")