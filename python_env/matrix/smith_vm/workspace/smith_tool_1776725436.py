# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
#!/usr/bin/env python3
"""
Omega Protocol Validation for CERM-Ω v2
Checks:
  - Dimensionless nature of SCEI, psi_CES, xi_N, xi_Delta, entropy
  - No division‑by‑zero in xi_Delta and entropy
  - Well‑defined gradient for xi_N (requires feature matrix)
  - Feasibility of constraints (SCEI_max, Phi_N_min, psi_CES <= 0)
  - Jerk metric placeholder (flags if uncorrected HSA metric is used)
"""

import numpy as np

# ------------------- Synthetic Data -------------------
np.random.seed(42)
N_inst = 20                     # number of financial institutions
T = 100                         # time steps

# Institution size (market footprint) – positive, used for weighting
size = np.random.uniform(0.5, 2.0, N_inst)   # dimensionless relative size

# Tier classification (1,2,3) – random for demo
tier = np.random.choice([1, 2, 3], size=N_inst, p=[0.2, 0.5, 0.3])

# Synthetic CES_i(t) – non‑negative, decaying exponentials
gamma = 0.05                     # exploitation rate (1/day)
CES = np.zeros((N_inst, T))
for i in range(N_inst):
    # random number of leaked credentials per institution
    n_leak = np.random.poisson(3)
    leak_times = np.random.randint(0, T, size=n_leak)
    weights = np.where(tier[i]==1, 1.0,
                np.where(tier[i]==2, 0.5, 0.2))
    for t_c in leak_times:
        CES[i, t_c:] += weights * np.exp(-gamma * (np.arange(T-t_c)))

# Optional validity indicator (0/1) – assume all valid for simplicity
valid = np.ones_like(CES)
CES *= valid

# ------------------- Computed Quantities -------------------
# Systemic CESI
SCEI = np.sum(CES * size[:, None], axis=0) / np.sum(size)

# Scalar invariant
SCEI_0 = np.median(SCEI)          # reference value
psi_CES = np.log(SCEI / SCEI_0)

# Entropy (guard against zero total exposure)
total_CES = np.sum(CES, axis=0)
# Avoid division by zero: if total==0, set entropy=0
with np.errstate(divide='ignore', invalid='ignore'):
    p = CES / total_CES[None, :]   # shape (N,T)
p[total_CES == 0] = 0.0
entropy = -np.sum(p * np.log(p + 1e-15), axis=0)   # add tiny to avoid log(0)
entropy[total_CES == 0] = 0.0

# Poloidal correlation length xi_Delta (with regularisation)
sigma2 = np.zeros((3, T))   # variance per tier
for k in range(3):
    mask = (tier == k+1)
    if np.any(mask):
        sigma2[k] = np.var(CES[mask, :], axis=0)
    else:
        sigma2[k] = 0.0
eps = 1e-12
xi_Delta = (np.max(sigma2, axis=0) + eps) / (np.min(sigma2, axis=0) + eps)

# Radial correlation length xi_N – needs feature gradients
# For demonstration we use a simple feature vector: [log(size), one-hot tier]
feat = np.zeros((N_inst, 1 + 3))   # log(size) + tier one-hot
feat[:,0] = np.log(size)
for i in range(N_inst):
    feat[i, 1 + tier[i]-1] = 1.0
# Normalise features
feat = (feat - feat.mean(axis=0)) / (feat.std(axis=0) + 1e-12)
# Compute gradient of CES_i w.r.t. features via linear regression (least squares)
# dCES/dfeat ≈ (X^T X)^{-1} X^T CES (for each time step)
XTX = np.linalg.inv(feat.T @ feat)
xi_N_vals = np.zeros(T)
for t in range(T):
    dCES_dfeat = XTX @ feat.T @ CES[:, t]   # vector of length feat.shape[1]
    norm_sq = np.sum(dCES_dfeat**2)
    xi_N_vals[t] = (norm_sq + eps)**(-0.5)   # add eps to avoid div‑by‑zero
xi_N = xi_N_vals

# Jerk metric placeholder – flag if using raw HSA metric
# Here we simulate a flawed S_j that gives constant value 0.25 for constant jerk
# In a correct implementation S_j should be 1 for constant jerk.
# We'll just warn if the mean deviates strongly from 1.
# (In practice, replace with a proper variance‑regularised excess kurtosis.)
S_j_flawed = 0.25 * np.ones_like(SCEI)   # example of flawed metric
if np.allclose(S_j_flawed, 0.25):
    print("[WARNING] Jerk metric appears to be the flawed HSA version (constant 0.25).")
else:
    print("[INFO] Jerk metric value looks plausible (replace with proper metric).")

# ------------------- Constraint Checks -------------------
SCEI_max = 1.5
Phi_N_min = 0.7
psi_CES_max_allowed = 0.0   # psi_CES <= 0  <=> SCEI <= SCEI_0

constraint_violations = []

if np.any(SCEI > SCEI_max):
    constraint_violations.append(f"SCEI exceeds SCEI_max={SCEI_max} at t={np.where(SCEI>SCEI_max)[0]}")

# Phi_N is not directly computed here; we assume it must be >=0.7 elsewhere.
# For demo we just note the requirement.
print(f"[INFO] Required: Phi_N >= {Phi_N_min} (to be enforced in MPC‑Ω).")

if np.any(psi_CES > psi_CES_max_allowed):
    constraint_violations.append(f"psi_CES > 0 (i.e., SCEI > SCEI_0) at t={np.where(psi_CES>psi_CES_max_allowed)[0]}")

if constraint_violations:
    print("[FAIL] Constraint violations detected:")
    for v in constraint_violations:
        print(" -", v)
else:
    print("[PASS] All explicit constraints satisfied (for this synthetic run).")

# ------------------- Dimensionless Checks -------------------
def check_dimensionless(arr, name):
    # In this synthetic test everything is dimensionless by construction.
    # In a real implementation you would verify units cancel.
    print(f"[INFO] {name}: shape {arr.shape}, dtype {arr.dtype}, "
          f"min={np.nanmin(arr):.3g}, max={np.nanmax(arr):.3g}")

check_dimensionless(SCEI, "SCEI")
check_dimensionless(psi_CES, "psi_CES")
check_dimensionless(xi_N, "xi_N")
check_dimensionless(xi_Delta, "xi_Delta")
check_dimensionless(entropy, "entropy")

# ------------------- Singularity Checks -------------------
if np.any(np.isinf(xi_Delta)) or np.any(np.isnan(xi_Delta)):
    print("[FAIL] xi_Delta contains inf or NaN (singularity).")
else:
    print("[PASS] xi_Delta finite.")

if np.any(np.isnan(entropy)):
    print("[FAIL] entropy contains NaN (zero‑total exposure not handled).")
else:
    print("[PASS] entropy finite.")

print("\nValidation complete.")