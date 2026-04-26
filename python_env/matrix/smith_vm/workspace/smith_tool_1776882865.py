# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
#!/usr/bin/env python3
"""
Validation script for Tokamak Governor constants (SHOCK_LIMIT, VAA_SENSITIVITY,
MANIFOLD_DIVERGENCE) against the Omega Protocol requirements.

Checks:
1. Linear sensitivity-based AUC projection (with interaction term).
2. Safety bounds from prior audits:
   - VAA_SENSITIVITY ≤ 1.2 (Smith's audit Case #ITDB-117)
   - MANIFOLD_DIVERGENCE ≤ 0.35 (PIS-Ω §4.2 tungsten-wall limit)
   - SHOCK_LIMIT < 0.82 (to avoid ψ_N ≥ 0.82 metric freeze)
3. Whether the projected AUC exceeds the target >0.85.
"""

import math

# ----------------------------------------------------------------------
# Baseline and sensitivity coefficients (as stated by the Engine)
# ----------------------------------------------------------------------
BASELINE_AUC = 0.6793

# Sensitivities (dAUC/dx) used in the Engine's linear model
SENS_SHOCK = 0.12          # per unit SHOCK_LIMIT
SENS_VAA   = 0.09          # per unit VAA_SENSITIVITY
SENS_MANI  = 0.07          # per unit MANIFOLD_DIVERGENCE

# Prior (baseline) values from Engine's pleading history
PRIOR_SHOCK      = 0.85
PRIOR_VAA        = 1.00
PRIOR_MANI       = 0.30

# Proposed (new) values from Engine's output
NEW_SHOCK      = 0.72
NEW_VAA        = 1.28
NEW_MANI       = 0.42

# ----------------------------------------------------------------------
# Compute deltas
# ----------------------------------------------------------------------
delta_shock = NEW_SHOCK - PRIOR_SHOCK      # -0.13
delta_vaa   = NEW_VAA   - PRIOR_VAA        # +0.28
delta_mani  = NEW_MANI  - PRIOR_MANI       # +0.12

# ----------------------------------------------------------------------
# Linear AUC contribution
# ----------------------------------------------------------------------
linear_auc = (SENS_SHOCK * delta_shock +
              SENS_VAA   * delta_vaa   +
              SENS_MANI  * delta_mani)

# ----------------------------------------------------------------------
# Interaction term (as the Engine attempted)
# Engine used: 0.03 * delta_shock * delta_vaa  (but with wrong sign)
# We compute the correct term and also show the Engine's erroneous version.
INTERACTION_COEFF = 0.03
interaction_correct = INTERACTION_COEFF * delta_shock * delta_vaa   # should be negative
interaction_engine  =  INTERACTION_COEFF * (-delta_shock) * delta_vaa  # Engine's sign flip

# ----------------------------------------------------------------------
# Total delta AUC and predicted AUC
# ----------------------------------------------------------------------
total_delta_auc_linear_only = linear_auc
total_delta_auc_with_interaction = linear_auc + interaction_correct

pred_auc_linear_only = BASELINE_AUC + total_delta_auc_linear_only
pred_auc_with_interaction = BASELINE_AUC + total_delta_auc_with_interaction

# ----------------------------------------------------------------------
# Safety bound checks
# ----------------------------------------------------------------------
SAFE_VAA_MAX   = 1.2   # Smith's audit limit
SAFE_MANI_MAX  = 0.35  # PIS-Ω tungsten-wall limit (pre‑update)
SAFE_SHOCK_MAX = 0.82  # ψ_N < 0.82 to avoid metric freeze

vaa_ok   = NEW_VAA   <= SAFE_VAA_MAX
mani_ok  = NEW_MANI  <= SAFE_MANI_MAX
shock_ok = NEW_SHOCK <  SAFE_SHOCK_MAX

# ----------------------------------------------------------------------
# Output results
# ----------------------------------------------------------------------
print("=== Tokamak Governor Constants Validation ===\n")
print(f"Baseline AUC: {BASELINE_AUC:.4f}")
print(f"Proposed constants:")
print(f"  SHOCK_LIMIT      = {NEW_SHOCK:.3f}  (Δ = {delta_shock:+.3f})")
print(f"  VAA_SENSITIVITY  = {NEW_VAA:.3f}    (Δ = {delta_vaa:+.3f})")
print(f"  MANIFOLD_DIVERGENCE= {NEW_MANI:.3f}  (Δ = {delta_mani:+.3f})\n")

print("Sensitivity-based AUC projection:")
print(f"  Linear contribution (Σ sens·Δ)          = {linear_auc:+.6f}")
print(f"  Interaction term (correct)              = {interaction_correct:+.6f}")
print(f"  Interaction term (Engine's version)    = {interaction_engine:+.6f}")
print(f"  Total ΔAUC (linear only)               = {total_delta_auc_linear_only:+.6f}")
print(f"  Total ΔAUC (linear + interaction)      = {total_delta_auc_with_interaction:+.6f}\n")
print(f"  Predicted AUC (linear only)            = {pred_auc_linear_only:.4f}")
print(f"  Predicted AUC (linear + interaction)   = {pred_auc_with_interaction:.4f}\n")

print("Safety bound compliance:")
print(f"  VAA_SENSITIVITY ≤ {SAFE_VAA_MAX}?   {'PASS' if vaa_ok   else 'FAIL'}  ({NEW_VAA:.3f} vs {SAFE_VAA_MAX})")
print(f"  MANIFOLD_DIVERGENCE ≤ {SAFE_MANI_MAX}? {'PASS' if mani_ok  else 'FAIL'}  ({NEW_MANI:.3f} vs {SAFE_MANI_MAX})")
print(f"  SHOCK_LIMIT < {SAFE_SHOCK_MAX}?      {'PASS' if shock_ok else 'FAIL'}  ({NEW_SHOCK:.3f} vs {SAFE_SHOCK_MAX})\n")

print("Goal check (AUC > 0.85):")
goal_linear_only   = pred_auc_linear_only   > 0.85
goal_with_interact = pred_auc_with_interaction > 0.85
print(f"  Using linear-only model:    {'PASS' if goal_linear_only   else 'FAIL'}  ({pred_auc_linear_only:.4f})")
print(f"  Using linear+interaction:   {'PASS' if goal_with_interact else 'FAIL'}  ({pred_auc_with_interaction:.4f})\n")

# Overall verdict
overall_pass = (vaa_ok and mani_ok and shock_ok and goal_with_interact)
print("=== OVERALL VERDICT ===")
print("PASS (all invariants satisfied and goal met)" if overall_pass else "FAIL")
if not overall_pass:
    print("Reason(s) for failure:")
    if not vaa_ok:   print(" - VAA_SENSITIVITY exceeds Smith's audit limit (≤1.2).")
    if not mani_ok:  print(" - MANIFOLD_DIVERGENCE exceeds tungsten‑wall limit (≤0.35).")
    if not shock_ok: print(" - SHOCK_LIMIT approaches or exceeds metric‑freeze threshold (<0.82).")
    if not goal_with_interact:
        print(" - Projected AUC does not reach the required >0.85 target.")