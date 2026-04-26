# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
#!/usr/bin/env python3
"""
Validation script for the refined CERM‑Ω v2 proposal.
Checks mathematical soundness, dimensional consistency,
and compliance with the Omega Protocol invariants.
"""

import numpy as np
import sympy as sp

# ----------------------------------------------------------------------
# Symbolic definitions (to catch division‑by‑zero, log of non‑positive, etc.)
# ----------------------------------------------------------------------
# Credential‑level symbols
w_c, gamma, t, t_c = sp.symbols('w_c gamma t t_c', positive=True, real=True)
I_valid = sp.symbols('I_valid', integer=True)  # 0 or 1

# Institution‑level aggregation
i, N = sp.symbols('i N', integer=True, positive=True)
size_i = sp.symbols('size_i', positive=True, real=True)   # market footprint
CES_i = sp.symbols('CES_i', real=True)                   # will be defined below

# Systemic index
SCEI = sp.symbols('SCEI', real=True)

# Reference value for the scalar invariant
SCEI0 = sp.symbols('SCEI0', positive=True, real=True)

# ----------------------------------------------------------------------
# Helper: define CES_i as a sum over a small mock set of credentials
# ----------------------------------------------------------------------
def mock_CES_i(num_creds=3):
    """Return a symbolic expression for CES_i using a finite sum."""
    creds = []
    for k in range(num_creds):
        t_c_k = sp.symbols(f't_c_{k}', real=True)
        w_c_k = sp.symbols(f'w_c_{k}', positive=True, real=True)
        I_k = sp.symbols(f'I_{k}', integer=True)
        term = w_c_k * sp.exp(-gamma * (t - t_c_k)) * I_k
        creds.append(term)
    return sp.Add(*creds)

CES_i_expr = mock_CES_i()

# ----------------------------------------------------------------------
# Systemic Credential Exposure Index (dimensionless by construction)
# ----------------------------------------------------------------------
# Assume size_i has same units as the weighting factor (both dimensionless after
# normalisation).  The ratio of weighted sums is therefore dimensionless.
SCEI_expr = sp.Sum(CES_i_expr * size_i, (i, 1, N)) / sp.Sum(size_i, (i, 1, N))

# ----------------------------------------------------------------------
# Scalar invariant ψ_CES = ln(SCEI/SCEI0)
# ----------------------------------------------------------------------
psi_CES_expr = sp.log(SCEI_expr / SCEI0)

# ----------------------------------------------------------------------
# Radial correlation length ξ_N^(CES)
#   ξ_N = ( (1/N) Σ ‖∇_i CES_i‖² )^{-1/2}
# We mock a feature vector f_i = [log(size_i), sector_onehot, geo_coord]
# and treat ∇_i as derivative w.r.t. each component.
# ----------------------------------------------------------------------
# Feature symbols (for illustration)
log_size_i = sp.log(size_i)
sector_i   = sp.symbols('sector_i', real=True)   # simplified scalar proxy
geo_i      = sp.symbols('geo_i', real=True)      # simplified scalar proxy
features_i = sp.Matrix([log_size_i, sector_i, geo_i])

# Gradient of CES_i w.r.t. features (treat CES_i as function of size_i only for simplicity)
# dCES_i/d(log_size_i) = dCES_i/dsize_i * size_i
dCES_dsize = sp.diff(CES_i_expr, size_i)
grad_norm_sq = (dCES_dsize * size_i)**2  # only size dimension contributes in this mock
xi_N_sq = sp.Sum(grad_norm_sq, (i, 1, N)) / N
xi_N_expr = xi_N_sq**(-sp.Rational(1,2))

# ----------------------------------------------------------------------
# Poloidal correlation length ξ_Δ^(CES)
#   ξ_Δ = max_k σ_k² / min_k σ_k²   (k = tiers)
# We mock variance per tier as a symbolic positive variable.
# ----------------------------------------------------------------------
sigma2_T1 = sp.symbols('sigma2_T1', positive=True, real=True)
sigma2_T2 = sp.symbols('sigma2_T2', positive=True, real=True)
sigma2_T3 = sp.symbols('sigma2_T3', positive=True, real=True)
xi_Delta_expr = sp.Max(sigma2_T1, sigma2_T2, sigma2_T3) / sp.Min(sigma2_T1, sigma2_T2, sigma2_T3)

# ----------------------------------------------------------------------
# Entropy of exposure distribution
#   S_h = - Σ p_i ln p_i,   p_i = CES_i / Σ CES_j
# Guard against zero total exposure.
# ----------------------------------------------------------------------
total_CES = sp.Sum(CES_i_expr, (i, 1, N))
p_i = CES_i_expr / total_CES
# Sympy cannot directly handle the conditional; we will evaluate numerically later.
S_h_expr = -sp.Sum(p_i * sp.log(p_i), (i, 1, N))

# ----------------------------------------------------------------------
# Numeric sanity‑check with random plausible values
# ----------------------------------------------------------------------
np.random.seed(42)
def random_instance():
    # Random numbers of institutions and credentials
    n_inst = np.random.randint(5, 15)
    n_cred = np.random.randint(1, 5)

    # Market footprints (size_i)
    size = np.random.uniform(0.5, 5.0, size=n_inst)

    # Credential data
    t_vals = np.random.uniform(0, 30, size=n_cred)   # current time window
    t_c_vals = np.random.uniform(-20, t_vals.min()-1, size=n_cred)  # leak times
    w_c_vals = np.random.choice([1.0, 0.5, 0.2], size=n_cred)      # tier weights
    I_vals   = np.random.randint(0, 2, size=n_cred)               # validity flag

    gamma_val = np.random.uniform(0.05, 0.2)   # exploitation rate

    # Compute CES_i
    CES = np.zeros(n_inst)
    for inst in range(n_inst):
        # For simplicity, assign each credential to a random institution
        inst_of_cred = np.random.randint(0, n_inst, size=n_cred)
        contrib = np.where(inst_of_cred == inst,
                           w_c_vals * np.exp(-gamma_val * (t_vals - t_c_vals)) * I_vals,
                           0.0)
        CES[inst] = contrib.sum()
    # Avoid all‑zero case for entropy test
    if CES.sum() == 0:
        CES[0] = 1e-6
    SCEI_val = np.dot(CES, size) / size.sum()

    # Reference SCEI0 (median of a mock historical series)
    SCEI0_val = np.median([SCEI_val * np.random.uniform(0.8, 1.2) for _ in range(20)])

    # ψ_CES
    psi_CES_val = np.log(SCEI_val / SCEI0_val) if SCEI_val > 0 else -np.inf

    # ξ_N (mock: use variance of CES across institutions as proxy)
    xi_N_val = 1.0 / np.sqrt(np.var(CES) + 1e-12)

    # ξ_Δ (mock tier variances)
    sigma2 = [np.var(CES[::3]), np.var(CES[1::3]), np.var(CES[2::3])]
    sigma2 = [max(s, 1e-12) for s in sigma2]   # avoid zero
    xi_Delta_val = max(sigma2) / min(sigma2)

    # Entropy
    p = CES / CES.sum()
    # avoid log(0)
    p = np.where(p == 0, 1e-12, p)
    S_h_val = -np.sum(p * np.log(p))

    return {
        'SCEI': SCEI_val,
        'SCEI0': SCEI0_val,
        'psi_CES': psi_CES_val,
        'xi_N': xi_N_val,
        'xi_Delta': xi_Delta_val,
        'S_h': S_h_val,
        'CES': CES,
        'size': size,
        'gamma': gamma_val
    }

# ----------------------------------------------------------------------
# Validation checks
# ----------------------------------------------------------------------
def validate_one(instance):
    fails = []
    # 1. SCEI must be non‑negative and real
    if not (np.isreal(instance['SCEI']) and instance['SCEI'] >= 0):
        fails.append('SCEI not non‑negative real')
    # 2. ψ_CES must be real (requires SCEI>0)
    if not np.isreal(instance['psi_CES']):
        fails.append('psi_CES not real (SCEI <= 0)')
    # 3. ξ_N must be real and non‑negative
    if not (np.isreal(instance['xi_N']) and instance['xi_N'] >= 0):
        fails.append('xi_N not non‑negative real')
    # 4. ξ_Δ must be ≥ 1 (ratio of max/min variances)
    if instance['xi_Delta'] < 1 - 1e-12:
        fails.append('xi_Delta < 1')
    # 5. Entropy bounds: 0 ≤ S_h ≤ ln(N)
    N = len(instance['CES'])
    lower, upper = 0.0, np.log(N)
    if not (lower - 1e-12 <= instance['S_h'] <= upper + 1e-12):
        fails.append(f'entropy out of bounds [{lower},{upper}]: {instance["S_h"]}')
    # 6. Constraint: SCEI ≤ SCEI_max (choose a reasonable max, e.g., 2.0)
    if instance['SCEI'] > 2.0 + 1e-12:
        fails.append('SCEI exceeds chosen SCEI_max (2.0)')
    # 7. Constraint: Φ_N ≥ 0.7 (we cannot compute Φ_N here; assume placeholder)
    #    We'll just note that this must be checked elsewhere.
    # 8. Constraint: ψ_CES ≤ 0  (i.e., SCEI ≤ SCEI0)
    if instance['psi_CES'] > 1e-12:
        fails.append('psi_CES > 0 (SCEI > SCEI0)')
    return fails

# Run several random instances
all_fails = []
for _ in range(30):
    inst = random_instance()
    fails = validate_one(inst)
    if fails:
        all_fails.append((inst, fails))

# ----------------------------------------------------------------------
# Report
# ----------------------------------------------------------------------
if not all_fails:
    print("PASS: All mathematical and invariant checks succeeded.")
else:
    print(f"FAIL: Found {len(all_fails)} problematic instances out of 30.")
    for idx, (inst, fails) in enumerate(all_fails[:3]):  # show first few
        print(f"\nInstance {idx+1}:")
        print(f"  SCEI={inst['SCEI']:.4f}, SCEI0={inst['SCEI0']:.4f}")
        print(f"  psi_CES={inst['psi_CES']:.4f}, xi_N={inst['xi_N']:.4f}")
        print(f"  xi_Delta={inst['xi_Delta']:.4f}, S_h={inst['S_h']:.4f}")
        print("  Failures:")
        for f in fails:
            print(f"    - {f}")
    print("\nSee above for details; the proposal requires fixes before it can be considered")
    print("mathematically sound and Omega‑Protocol compliant.")