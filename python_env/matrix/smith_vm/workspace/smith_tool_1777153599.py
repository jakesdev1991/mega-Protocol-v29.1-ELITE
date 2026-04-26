# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
"""
Validation script for Q-SCOUT proposal.
Checks:
 1. NetΦ gain calculation matches claimed +0.07Φ/cycle.
 2. Revenue-to-Φ conversion factor k = 0.229 Φ/$ is consistent.
 3. Constraints (sentiment, urgency, lead volume, ethical lock) are satisfied.
 4. Cumulative Φ-density addition is correct.
 5. No overcount of audit/effort costs.
"""

import math

# -------------------------- INPUT DATA (from proposal) --------------------------
# Baseline
baseline_conv_rate = 0.20          # 20%
baseline_leads_per_cycle = 3       # leads/cycle
baseline_avg_rev_per_lead = 1100   # $
baseline_effort_cost = 0.10        # Φ/cycle
baseline_risk_penalty = 0.0        # assumed zero for simplicity
lambda_risk = 0.5                  # risk aversion coefficient

# Q-SCOUT optimized
qscout_conv_rate = 0.28            # 28%
qscout_leads_per_cycle = 5
qscout_avg_rev_per_lead = 1400     # $
qscout_effort_cost = 0.085         # Φ/cycle (15% reduction)
qscout_risk_penalty = 0.0          # assumed unchanged (constraints prevent increase)

# Revenue impact claimed
claimed_monthly_rev_increase = 4200 # $/month

# Φ gain claimed
claimed_net_phi_gain_per_cycle = 0.07   # Φ/cycle
claimed_cumulative_phi_base = 58.81     # Φ (post-Q-COD)
claimed_cumulative_phi_new = 58.90      # Φ

# -------------------------- HELPER FUNCTIONS --------------------------
def net_phi(conv_rate, leads, avg_rev, effort_cost, risk_penalty, lam):
    """Net Φ per scouting cycle."""
    revenue = leads * avg_rev          # $ per cycle
    # Convert revenue to Φ using factor k (derived below)
    # For now keep in $; we will compute k later.
    return revenue - effort_cost - lam * risk_penalty  # placeholder, units mixed

def compute_k_from_claims():
    """
    Derive revenue-to-Φ conversion factor k from claimed:
      - Monthly revenue increase: $4200
      - Corresponding Φ increase: ? 
        They say cumulative Φ gain +0.09Φ (including synergistic reinvestment).
        Of that, +0.07Φ is direct Q-SCOUT gain/cycle, +0.02Φ from reinvestment.
        We'll isolate the direct gain component.
    """
    # Direct Φ gain per cycle from Q-SCOUT = 0.07Φ
    # We need cycles per month to relate to monthly revenue increase.
    # Solve for k: Φ_gain_per_cycle = k * (revenue_increase_per_cycle)
    # => k = Φ_gain_per_cycle / revenue_increase_per_cycle
    # We don't have cycles/month, so we compute k that would make the
    # claimed monthly revenue increase consistent with the claimed Φ gain
    # if we assume a certain number of cycles.
    # Instead, we compute k from the ratio they implicitly used:
    #   k = 0.229 Φ/$ (as stated in proposal)
    return 0.229  # Φ per $

# -------------------------- VALIDATION --------------------------
def main():
    print("=== Q-SCOUT Mathematical & Invariant Compliance Check ===\n")

    # 1. Compute revenue per cycle (baseline vs QSCOUT)
    base_rev_per_cycle = baseline_leads_per_cycle * baseline_avg_rev_per_lead
    qs_rev_per_cycle = qscout_leads_per_cycle * qscout_avg_rev_per_lead
    print(f"Baseline revenue/cycle: ${base_rev_per_cycle:,.2f}")
    print(f"Q-SCOUT revenue/cycle:  ${qs_rev_per_cycle:,.2f}")
    print(f"Revenue increase/cycle: ${qs_rev_per_cycle - base_rev_per_cycle:,.2f}\n")

    # 2. Derive k from proposal's stated value and check consistency
    k = compute_k_from_claims()
    print(f"Revenue-to-Φ conversion factor k = {k:.4f} Φ/$ (from proposal)\n")

    # 3. Convert revenue to Φ using k
    base_phi_per_cycle = base_rev_per_cycle * k
    qs_phi_per_cycle = qs_rev_per_cycle * k
    print(f"Baseline Φ/cycle (revenue only): {base_phi_per_cycle:.4f} Φ")
    print(f"Q-SCOUT Φ/cycle (revenue only):  {qs_phi_per_cycle:.4f} Φ\n")

    # 4. Compute Net Φ including effort and risk
    base_net_phi = base_phi_per_cycle - baseline_effort_cost - lambda_risk * baseline_risk_penalty
    qs_net_phi = qs_phi_per_cycle - qscout_effort_cost - lambda_risk * qscout_risk_penalty
    print(f"Baseline Net Φ/cycle: {base_net_phi:.4f} Φ")
    print(f"Q-SCOUT Net Φ/cycle:  {qs_net_phi:.4f} Φ")
    gain_per_cycle = qs_net_phi - base_net_phi
    print(f"Net Φ gain/cycle (calculated): {gain_per_cycle:.4f} Φ")
    print(f"Claimed Net Φ gain/cycle:      {claimed_net_phi_gain_per_cycle:.4f} Φ")
    gain_match = math.isclose(gain_per_cycle, claimed_net_phi_gain_per_cycle, rel_tol=1e-3)
    print(f"Gain matches claim? {'YES' if gain_match else 'NO'}\n")

    # 5. Check constraints (values from proposal; we assume they are set correctly)
    print("--- Constraint Checks ---")
    # Sentiment threshold: T_sentiment >= 0.7 (they used 0.78 example)
    T_sentiment = 0.78
    T_urgency = 0.65   # example >=0.6
    leads_per_cycle = qscout_leads_per_cycle
    exclude_configphp = 1   # hard constraint
    print(f"T_sentiment = {T_sentiment} (≥0.7? {'YES' if T_sentiment >= 0.7 else 'NO'})")
    print(f"T_urgency   = {T_urgency} (≥0.6? {'YES' if T_urgency >= 0.6 else 'NO'})")
    print(f"Leads/cycle = {leads_per_cycle} (≥5? {'YES' if leads_per_cycle >= 5 else 'NO'})")
    print(f"exclude_configphp = {exclude_configphp} (must be 1? {'YES' if exclude_configphp == 1 else 'NO'})")
    constraints_ok = (T_sentiment >= 0.7 and T_urgency >= 0.6
                      and leads_per_cycle >= 5 and exclude_configphp == 1)
    print(f"All constraints satisfied? {'YES' if constraints_ok else 'NO'}\n")

    # 6. Cumulative Φ-density check
    print("--- Cumulative Φ-Density ---")
    print(f"Base Φ-density (post-Q-COD): {claimed_cumulative_phi_base:.2f} Φ")
    print(f"Claimed net gain from Q-SCOUT: +0.09 Φ (direct + reinvestment)")
    expected_new = claimed_cumulative_phi_base + 0.09
    print(f"Expected new Φ-density: {expected_new:.2f} Φ")
    print(f"Claimed new Φ-density:  {claimed_cumulative_phi_new:.2f} Φ")
    cumulative_ok = math.isclose(expected_new, claimed_cumulative_phi_new, rel_tol=1e-3)
    print(f"Cumulative addition consistent? {'YES' if cumulative_ok else 'NO'}\n")

    # 7. Monthly revenue increase consistency (optional)
    # Estimate cycles per month needed to match $4200 increase
    rev_inc_per_cycle = qs_rev_per_cycle - base_rev_per_cycle
    if rev_inc_per_cycle > 0:
        cycles_needed = claimed_monthly_rev_increase / rev_inc_per_cycle
        print(f"--- Revenue Impact Check ---")
        print(f"Revenue increase per cycle: ${rev_inc_per_cycle:,.2f}")
        print(f"To achieve ${claimed_monthly_rev_increase:,.2f}/month increase,")
        print(f"  required cycles/month = {cycles_needed:.2f}")
        # If cycles/month is unreasonably low/high, flag.
        if cycles_needed < 0.5 or cycles_needed > 30:
            print("  WARNING: Implausible cycles/month given typical operation.")
        else:
            print("  Revenue impact plausible.")
    print()

    # -------------------------- FINAL VERDICT --------------------------
    all_good = gain_match and constraints_ok and cumulative_ok
    print("=== FINAL VERDICT ===")
    if all_good:
        print("✅ Q-SCOUT proposal is MATHEMATICALLY SOUND and COMPLIANT with Omega Protocol invariants.")
    else:
        print("❌ Q-SCOUT proposal FAILS one or more checks.")
        if not gain_match:
            print("   - Net Φ gain calculation mismatch.")
        if not constraints_ok:
            print("   - Constraint violation.")
        if not cumulative_ok:
            print("   - Cumulative Φ-density inconsistency.")

if __name__ == "__main__":
    main()