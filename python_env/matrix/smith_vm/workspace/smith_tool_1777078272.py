# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
# Omega Protocol Phi Invariant Validator
# Checks internal consistency of claimed Phi impact numbers
# Invariants:
#   Phi_N: Net impact must equal sum of all constituent impacts.
#   Phi_Delta: Difference between claimed net and computed net must be zero.
#   J*: No overstatement of benefit (claimed net <= actual net + epsilon) to prevent
#        optimistic bias that increases entropy.

import math

def validate_impacts(label, impacts, claimed_net, tolerance=1e-9):
    """
    impacts: dict of phase->impact (float, percent)
    claimed_net: float, claimed net impact (percent)
    Returns (is_consistent, computed_net, delta)
    """
    computed = sum(impacts.values())
    delta = claimed_net - computed
    consistent = math.isclose(delta, 0.0, abs_tol=tolerance)
    return consistent, computed, delta

# --- Engine's claimed numbers (from Engine output) ---
engine_impacts = {
    "Immediate": -3.0,
    "Months 1–6": +6.0,
    "Months 7–12": +8.0,
    "Months 13–24": +8.0,
}
engine_claimed_net = +22.0

cons_eng, comp_eng, delta_eng = validate_impacts("Engine", engine_impacts, engine_claimed_net)
print(f"Engine: claimed net {engine_claimed_net}%, computed {comp_eng:.2f}%, delta {delta_eng:.2f}%")
print(f"  Consistent? {cons_eng}")

# --- Scrutiny's numbers (from Scrutiny output) ---
# Short-term components
scrutiny_short = {
    "Pattern Rule Over-Matching": -2.0,
    "Broken Stem Extraction": -1.5,
    "ZRAM Script Gaps": -0.5,
    "Phantom Process Killer Dependency Gap": -0.2,
}
# Long-term trajectory phases (as given in the table)
scrutiny_long = {
    "Immediate (setup)": -4.2,   # note: this duplicates short-term sum; we treat as separate phase
    "Months 1–3": -2.5,
    "Months 4–12": +0.5,
}
# Scrutiny gave multiple claimed nets; we check each claim
scrutiny_claims = {
    "Short-term net (from component sum)": -4.2,
    "Long-term net (explicit statement)": -1.8,
    "Long-term net (from trajectory table)": -6.2,
}

print("\nScrutiny short-term components:")
cons_st, comp_st, delta_st = validate_impacts("Scrutiny Short", scrutiny_short, scrutiny_claims["Short-term net (from component sum)"])
print(f"  Claimed {scrutiny_claims['Short-term net (from component sum)']}%, computed {comp_st:.2f}%, delta {delta_st:.2f}%")
print(f"  Consistent? {cons_st}")

print("\nScrutiny long-term trajectory:")
cons_lt, comp_lt, delta_lt = validate_impacts("Scrutiny Long", scrutiny_long, scrutiny_claims["Long-term net (from trajectory table)"])
print(f"  Claimed {scrutiny_claims['Long-term net (from trajectory table)']}%, computed {comp_lt:.2f}%, delta {delta_lt:.2f}%")
print(f"  Consistent? {cons_lt}")

# Check for overstatement bias (J* invariant): claimed net should not exceed actual net
epsilon = 0.1  # allow tiny rounding tolerance
def check_J_star(label, claimed, actual):
    overstated = claimed > actual + epsilon
    return not overstated

print("\nJ* (no overstatement) checks:")
print(f"  Engine: claimed {engine_claimed_net}% vs actual {comp_eng:.2f}% -> OK? {check_J_star('Engine', engine_claimed_net, comp_eng)}")
print(f"  Scrutiny short-term: claimed {scrutiny_claims['Short-term net (from component sum)']}% vs actual {comp_st:.2f}% -> OK? {check_J_star('Scrutiny Short', scrutiny_claims['Short-term net (from component sum)'], comp_st)}")
print(f"  Scrutiny long-term (trajectory): claimed {scrutiny_claims['Long-term net (from trajectory table)']}% vs actual {comp_lt:.2f}% -> OK? {check_J_star('Scrutiny Long', scrutiny_claims['Long-term net (from trajectory table)'], comp_lt)}")

# Overall protocol compliance: all invariants must hold
overall_ok = cons_eng and cons_st and cons_lt and \
             check_J_star('Engine', engine_claimed_net, comp_eng) and \
             check_J_star('Scrutiny Short', scrutiny_claims['Short-term net (from component sum)'], comp_st) and \
             check_J_star('Scrutiny Long', scrutiny_claims['Long-term net (from trajectory table)'], comp_lt)

print(f"\nOverall Omega Protocol invariant compliance: {'PASS' if overall_ok else 'FAIL'}")