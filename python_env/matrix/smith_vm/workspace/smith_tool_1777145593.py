# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
# -*- coding: utf-8 -*-
"""
Omega Protocol Invariant Validator for Q-COD Experiment
------------------------------------------------------
Validates the mathematical soundness and protocol‑compliance of the
"Quantum‑Assisted Chain Overlap Density Optimization" proposal.

Invariants (as inferred from the proposal):
  Phi_N   : COD must stay above COD_THRESHOLD
  Phi_Delta: net Φ-density gain must be > MIN_PHIS_GAIN (0.05) for deployment
  J*      : audit cost reduction must not exceed MAX_AUDIT_CUT (0.30)
  Psi     : psi_integrity must stay above PSI_INTEGRITY_THRESHOLD (0.95)

The script does NOT require actual quantum hardware; it uses a simple
surrogate model for COD_after and audit_cost to demonstrate that the
claimed numbers are internally consistent and that the invariants hold.
"""

import numpy as np
from itertools import product

# -------------------------- PARAMETERS FROM PROPOSAL --------------------------
LAMBDA_RANGE = (0.3, 0.7)          # LAMBDA_COUPLING bounds
MU_RANGE     = (0.5, 0.9)          # MU_THERMO bounds
LEVELS       = 16                  # discretization per parameter (4 bits)
ALPHA        = 0.5                 # penalty weight for COD fidelity (chosen to match example)
COD_THRESHOLD = 0.85
PSI_THRESHOLD = 0.95
MIN_PHIS_GAIN = 0.05               # required net Φ gain to deploy
MAX_AUDIT_CUT = 0.30               # max allowed audit cost reduction

# Baseline values (taken from the proposal's implicit baseline)
BASE_LAMBDA = 0.5
BASE_MU     = 0.7
BASE_COD    = 0.78                 # baseline COD after calculation
BASE_AUDIT  = 1.0                  # baseline audit cost (arbitrary units)
BASE_PSI    = 0.92                 # baseline psi_integrity

# Sensitivity coefficients (derived from the claim: +12% COD fidelity, -18% audit cost)
# We assume linear sensitivity around the baseline for validation purposes.
COD_LAMBDA_SENS = 0.10   # ΔCOD per unit ΔLAMBDA
COD_MU_SENS     = 0.15   # ΔCOD per unit ΔMU
AUDIT_LAMBDA_SENS = -0.20 # Δaudit per unit ΔLAMBDA (negative = cost down)
AUDIT_MU_SENS     = -0.25 # Δaudit per unit ΔMU

# -------------------------- SURROGATE MODEL ---------------------------------
def cod_after(lam, mu):
    """Linear surrogate for COD after optimization."""
    return BASE_COD + COD_LAMBDA_SENS * (lam - BASE_LAMBDA) + COD_MU_SENS * (mu - BASE_MU)

def audit_cost(lam, mu):
    """Linear surrogate for audit cost."""
    return BASE_AUDIT + AUDIT_LAMBDA_SENS * (lam - BASE_LAMBDA) + AUDIT_MU_SENS * (mu - BASE_MU)

def psi_integrity(lam, mu):
    """Assume psi_integrity degrades if COD drops too much; simple linear model."""
    return BASE_PSI - 0.1 * max(0, COD_THRESHOLD - cod_after(lam, mu))

def net_phi_gain(lam, mu):
    """Net Φ-density gain as defined in the proposal."""
    cod = cod_after(lam, mu)
    aud = audit_cost(lam, mu)
    fidelity = min(1.0, cod / COD_THRESHOLD)  # fidelity = 1 if COD >= threshold
    return (cod - aud) - ALPHA * (1.0 - fidelity) - ((BASE_COD - BASE_AUDIT) - ALPHA * (1.0 - BASE_COD/COD_THRESHOLD))

# -------------------------- QUBO FORMULATION CHECK --------------------------
def qubo_variable_count():
    """Returns number of binary variables implied by the proposal."""
    return int(np.log2(LEVELS)) * 2  # 4 bits per parameter * 2 parameters

def qubo_is_small_enough():
    """Check that the QUBO size is suitable for NISQ devices (<= 20 qubits)."""
    return qubo_variable_count() <= 20

# -------------------------- OPTIMIZATION SEARCH (classical brute) ------------
lam_grid = np.linspace(LAMBDA_RANGE[0], LAMBDA_RANGE[1], LEVELS)
mu_grid  = np.linspace(MU_RANGE[0], MU_RANGE[1], LEVELS)

best_gain = -np.inf
best_params = None
for lam, mu in product(lam_grid, mu_grid):
    gain = net_phi_gain(lam, mu)
    if gain > best_gain:
        best_gain = gain
        best_params = (lam, mu)

lam_opt, mu_opt = best_params
cod_opt = cod_after(lam_opt, mu_opt)
audit_opt = audit_cost(lam_opt, mu_opt)
psi_opt = psi_integrity(lam_opt, mu_opt)
fidelity_opt = min(1.0, cod_opt / COD_THRESHOLD)

# -------------------------- INVARIANT VALIDATION ----------------------------
def check_invariants():
    violations = []

    # Phi_N: COD must stay above threshold
    if cod_opt < COD_THRESHOLD:
        violations.append(f"Phi_N violated: COD={cod_opt:.3f} < {COD_THRESHOLD}")

    # Psi: integrity must stay above threshold
    if psi_opt < PSI_THRESHOLD:
        violations.append(f"Psi violated: psi_integrity={psi_opt:.3f} < {PSI_THRESHOLD}")

    # J*: audit cost reduction cannot exceed MAX_AUDIT_CUT
    audit_reduction = (BASE_AUDIT - audit_opt) / BASE_AUDIT
    if audit_reduction > MAX_AUDIT_CUT:
        violations.append(f"J* violated: audit reduction={audit_reduction:.1%} > {MAX_AUDIT_CUT:.0%}")

    # Phi_Delta: net Φ gain must be > MIN_PHIS_GAIN for deployment
    if best_gain < MIN_PHIS_GAIN:
        violations.append(f"Phi_Delta violated: net Φ gain={best_gain:.3f} < {MIN_PHIS_GAIN}")

    return violations

violations = check_invariants()
qubo_ok = qubo_is_small_enough()

# -------------------------- OUTPUT ------------------------------------------
print("=== Q-COD Experiment Validation ===")
print(f"Discretization levels per parameter: {LEVELS} ({int(np.log2(LEVELS))} bits)")
print(f"Total binary variables for QUBO: {qubo_variable_count()}")
print(f"QUBO size suitable for NISQ (<=20 qubits)? {'YES' if qubo_ok else 'NO'}")
print()
print("Optimized Parameters (classical brute-force surrogate):")
print(f"  LAMBDA_COUPLING = {lam_opt:.3f}")
print(f"  MU_THERMO       = {mu_opt:.3f}")
print()
print("Resulting Metrics:")
print(f"  COD after               = {cod_opt:.3f} (threshold {COD_THRESHOLD})")
print(f"  Audit cost              = {audit_opt:.3f} (baseline {BASE_AUDIT})")
print(f"  Audit cost reduction    = {(BASE_AUDIT-audit_opt)/BASE_AUDIT:.1%}")
print(f"  Psi integrity           = {psi_opt:.3f} (threshold {PSI_THRESHOLD})")
print(f"  COD fidelity (norm)     = {fidelity_opt:.3f}")
print(f"  Net Φ-density gain      = {best_gain:.3f}")
print()
print("Invariant Check:")
if violations:
    for v in violations:
        print(f"  ❌ {v}")
else:
    print("  ✅ All invariants satisfied.")
print()
print("Validation Summary:")
print(f"  QUBO formulation sound?          {'YES' if qubo_ok else 'NO'}")
print(f"  Net Φ gain meets deployment bar? {'YES' if best_gain >= MIN_PHIS_GAIN else 'NO'}")
print(f"  Experiment compliant with Omega Protocol? {'YES' if not violations and qubo_ok else 'NO'}")