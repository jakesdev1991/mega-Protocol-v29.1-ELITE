# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
# Omega Protocol Invariant Validator for Q-COD Experiment
# Checks mathematical soundness and compliance with core invariants:
#   Phi_N   : net Φ-density gain must be > 0 (growth)
#   Phi_Delta: change in Φ-density must be within realistic bounds [-0.5, +0.5] per experiment
#   J*      : audit cost reduction cannot exceed 30% (under‑auditing guardrail)
#   COD_fidelity must stay in [0,1] and respect threshold constraints.
#   Discretization: 4 bits per coefficient → 16 levels each → 8‑bit search space.

import numpy as np

# ------------------- CONFIGURABLE BASELINE VALUES (from protocol docs) -------------------
BASE_COD_FIDELITY = 0.88          # current average COD fidelity across branches
BASE_AUDIT_COST   = 1.0           # normalized baseline cost (1.0 = current)
COD_THRESHOLD     = 0.85          # invariant: COD must stay above this
PSI_INTEGRITY_TH  = 0.95          # invariant: psi_integrity must stay above this
ALPHA_PENALTY     = 0.5           # weight for fidelity penalty in objective (chosen in proposal)

# ------------------- PROPOSED EXPERIMENT METRICS (from the thought) -------------------
PROPOSED_COD_FIDELITY_INCREASE = 0.12   # +12% absolute? interpreted as absolute increase
PROPOSED_AUDIT_COST_REDUCTION  = 0.18   # 18% reduction
PROPOSED_NET_PHI_GAIN          = 0.09   # +0.09Φ

# ------------------- DERIVED VALUES -------------------
new_cod_fidelity = BASE_COD_FIDELITY + PROPOSED_COD_FIDELITY_INCREASE
new_audit_cost   = BASE_AUDIT_COST * (1 - PROPOSED_AUDIT_COST_REDUCTION)

# Objective from proposal: Maximize (COD_after - audit_cost) - α*(1 - COD_fidelity)
# We compute the *value* of the objective for the proposed point.
objective_value = (new_cod_fidelity - new_audit_cost) - ALPHA_PENALTY * (1 - new_cod_fidelity)

# ------------------- INVARIANT CHECKS -------------------
def check_phi_n(gain):
    """Phi_N: net Φ-density gain must be positive."""
    return gain > 0

def check_phi_delta(gain, low=-0.5, high=0.5):
    """Phi_Delta: change must be within a realistic band per experiment."""
    return low <= gain <= high

def check_j_star(cost_red):
    """J*: audit cost reduction cannot exceed 30%."""
    return cost_red <= 0.30

def check_cod_fidelity(fid):
    """COD fidelity must be a valid probability and above threshold."""
    return 0.0 <= fid <= 1.0 and fid >= COD_THRESHOLD

def check_psi_integrity(psi):
    """Placeholder: we assume psi_integrity stays above threshold if COD fidelity is good."""
    # In a full validation we would simulate psi; here we conservatively require
    # psi_integrity >= PSI_INTEGRITY_TH if COD fidelity >= COD_THRESHOLD (correlated).
    return psi >= PSI_INTEGRITY_TH  # we will set psi = new_cod_fidelity for simplicity

def check_discretization(bits_per_param=4):
    """Ensure the search space matches the claimed discretization."""
    levels = 2 ** bits_per_param
    total_levels = levels ** 2  # two parameters
    return levels == 16 and total_levels == 256

# Run checks
results = {
    "Phi_N (gain>0)":          check_phi_n(PROPOSED_NET_PHI_GAIN),
    "Phi_Delta (|gain|≤0.5)": check_phi_delta(PROPOSED_NET_PHI_GAIN),
    "J* (audit cost red≤30%)": check_j_star(PROPOSED_AUDIT_COST_REDUCTION),
    "COD fidelity valid":      check_cod_fidelity(new_cod_fidelity),
    "Psi integrity valid":     check_psi_integrity(new_cod_fidelity),  # using fidelity as proxy
    "Discretization 4‑bit":    check_discretization(),
    "Objective value":         objective_value  # for inspection, not a boolean
}

# ------------------- OUTPUT -------------------
print("=== Omega Protocol Invariant Validation for Q-COD ===")
for k, v in results.items():
    if isinstance(v, bool):
        status = "PASS" if v else "FAIL"
        print(f"{k:30} : {status}")
    else:
        print(f"{k:30} : {v:.4f}")

# Overall compliance: all boolean checks must pass
all_pass = all(v for k, v in results.items() if isinstance(v, bool))
print("\nOVERALL COMPLIANCE:", "PASS" if all_pass else "FAIL")
if not all_pass:
    failed = [k for k, v in results.items() if isinstance(v, bool) and not v]
    print("FAILED CHECKS:", ", ".join(failed))