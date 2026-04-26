# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
# Omega Protocol Φ-Density Ledger Validator
# Checks internal consistency of the Φ-density ledger presented in the Scrutiny audit.
# Invariant: Net = Claimed - Audit_Correction - Audit_Cost
# Invariant: Sum of individual nets = Total Net reported
# Tolerance for floating-point comparison
TOL = 1e-9

# Ledger data as presented (Φ units)
ledger = [
    {"task": "Bureaucracy Manifold",
     "claimed": 1.40,
     "correction": 0.00,
     "cost": 0.10,
     "net_reported": 1.30},
    {"task": "Children's Footwear",
     "claimed": 1.50,
     "correction": 0.15,
     "cost": 0.08,
     "net_reported": 0.10},
    {"task": "Trauma-Performance",
     "claimed": 0.65,
     "correction": 0.00,
     "cost": 0.10,
     "net_reported": 0.55},
]

def validate_ledger(entries):
    errors = []
    total_calculated = 0.0
    for e in entries:
        claimed = e["claimed"]
        correction = e["correction"]
        cost = e["cost"]
        net_reported = e["net_reported"]
        net_calc = claimed - correction - cost
        if abs(net_calc - net_reported) > TOL:
            errors.append(
                f"{e['task']}: Net mismatch. "
                f"Claimed({claimed}) - Correction({correction}) - Cost({cost}) = {net_calc:.3f}, "
                f"but reported net = {net_reported:.3f}"
            )
        total_calculated += net_calc
    total_reported = sum(e["net_reported"] for e in entries)
    if abs(total_calculated - total_reported) > TOL:
        errors.append(
            f"Total net mismatch. Sum of calculated nets = {total_calculated:.3f}, "
            f"reported total net = {total_reported:.3f}"
        )
    return errors

if __name__ == "__main__":
    errs = validate_ledger(ledger)
    if errs:
        print("Ω-PROTOCOL VIOLATION DETECTED in Φ-Density Ledger:")
        for err in errs:
            print(" -", err)
        print("\nViolation of invariant: Φ-Density Accounting (Net = Claimed - Correction - Cost).")
        print("Result: META-FAIL")
    else:
        print("All ledger invariants satisfied.")
        print("Result: META-PASS")