# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
# Omega Protocol Φ-Density Impact Validator
# Validates the mathematical consistency of Φ-density impact claims
# Enforces invariants: 
#   Φ_N   : Net Φ-density change must equal sum of component changes.
#   Φ_Delta: No component may exceed plausible bounds (±10% per phase).
#   J*    : Total protocol Φ-gain must be non-negative (net gain or zero).

def validate_phi_impacts():
    # ----- Section 1: Device-specific Φ-density impact (from Engine output) -----
    phases = {
        "immediate": -1.0,   # %
        "deployment": 0.0,   # %
        "months_1_6": 4.0,   # %
        "months_7_12": 2.0,  # %
        "trust": 1.0,        # %
    }
    claimed_net = sum(phases.values())
    reported_net = 6.0  # % from Engine output

    # ----- Section 2: Protocol-level Φ-density gain breakdown -----
    protocol_components = {
        "pattern_recognition": 2.5,   # %
        "vendor_path_correction": 2.0, # %
        "phi_density_accounting": 1.0, # %
        "protocol_learning": 1.0,      # %
    }
    claimed_protocol_gain = sum(protocol_components.values())
    reported_protocol_gain = 6.5  # % from Engine output

    # ----- Section 3: Meta-learning adjusted gain (later claim) -----
    meta_components = {
        "vendor_mismatch_correction": 2.5,   # %
        "os_family_gatekeeper": 2.0,         # %
        "consistent_error_handling": 1.5,    # %
        "trust_documentation": 1.0,          # %
    }
    claimed_meta_gain = sum(meta_components.values())
    reported_meta_gain = 7.0  # % from Engine output

    # ----- Invariants -----
    errors = []

    # Φ_N: Net must equal sum of components (within tolerance)
    if not abs(claimed_net - reported_net) < 0.01:
        errors.append(
            f"Φ_N violation: Device-specific net Φ ({claimed_net}%) ≠ reported net ({reported_net}%)."
        )
    if not abs(claimed_protocol_gain - reported_protocol_gain) < 0.01:
        errors.append(
            f"Φ_N violation: Protocol gain sum ({claimed_protocol_gain}%) ≠ reported gain ({reported_protocol_gain}%)."
        )
    if not abs(claimed_meta_gain - reported_meta_gain) < 0.01:
        errors.append(
            f"Φ_N violation: Meta-gain sum ({claimed_meta_gain}%) ≠ reported meta-gain ({reported_meta_gain}%)."
        )

    # Φ_Delta: Each component must be within plausible bounds (±10% per phase/component)
    for name, val in phases.items():
        if abs(val) > 10.0:
            errors.append(
                f"Φ_Delta violation: Device phase '{name}' impact {val}% exceeds ±10% bound."
            )
    for name, val in protocol_components.items():
        if abs(val) > 10.0:
            errors.append(
                f"Φ_Delta violation: Protocol component '{name}' impact {val}% exceeds ±10% bound."
            )
    for name, val in meta_components.items():
        if abs(val) > 10.0:
            errors.append(
                f"Φ_Delta violation: Meta component '{name}' impact {val}% exceeds ±10% bound."
            )

    # J*: Total protocol Φ-gain must be non-negative (net gain or zero)
    if claimed_net < 0:
        errors.append(
            f"J* violation: Device-specific net Φ ({claimed_net}%) is negative (protocol requires non-negative gain)."
        )
    if claimed_protocol_gain < 0:
        errors.append(
            f"J* violation: Protocol Φ-gain ({claimed_protocol_gain}%) is negative."
        )
    if claimed_meta_gain < 0:
        errors.append(
            f"J* violation: Meta Φ-gain ({claimed_meta_gain}%) is negative."
        )

    # ----- Output -----
    if errors:
        print("Ω-PROTOCOL INVARIANT VIOLATIONS DETECTED:")
        for err in errors:
            print(f" - {err}")
        return False
    else:
        print("Ω-PROTOCOL INVARIANTS SATISFIED:")
        print(f"Device-specific phases sum: {claimed_net:.2f}% (reported {reported_net:.2f}%)")
        print(f"Protocol components sum:    {claimed_protocol_gain:.2f}% (reported {reported_protocol_gain:.2f}%)")
        print(f"Meta-learning sum:          {claimed_meta_gain:.2f}% (reported {reported_meta_gain:.2f}%)")
        print("All Φ-density calculations are mathematically sound.")
        return True

# Enforce the rules: raise if validation fails
if not validate_phi_impacts():
    raise AssertionError("Ω-PROTOCOL Φ-Density invariants violated. Aborting to maintain matrix stability.")
else:
    print("✅ Validation passed. Matrix stability maintained.")