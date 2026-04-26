# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import math

def validate_phi_density_reflection():
    """
    Validates the Φ-density reflection math from the Engine's output.
    Checks mathematical soundness of the net Φ calculation and compliance 
    with Omega Protocol invariants (Phi_N, Phi_Delta, J*).
    
    Omega Protocol Invariants Interpretation:
    - Phi_N: Nominal Φ density (baseline stability)
    - Phi_Delta: Rate of Φ change (must be non-negative in steady state)
    - J*: Justice metric (must increase with ethical compliance)
    
    Validation Criteria:
    1. Mathematical consistency of period impacts → net annualized Φ
    2. Short-term Phi_Delta negativity must be bounded and justified
    3. Long-term Phi_Delta must be positive and sustainable
    4. Net annualized Φ must be non-negative (J* increase)
    """
    
    # Engine's reported impacts (from output)
    periods = [
        {"months": 3, "impact_pct": -5.0, "label": "Months 1–3"},
        {"months": 9, "impact_pct": 8.0,  "label": "Months 4–12"},
        {"months": 12, "impact_pct": 12.0, "label": "Months 13–24"}
    ]
    
    # 1. Validate mathematical consistency
    total_months = sum(p["months"] for p in periods)
    assert total_months == 24, f"Total months must be 24, got {total_months}"
    
    # Calculate compounded growth factor
    growth_factor = 1.0
    for p in periods:
        growth_factor *= (1 + p["impact_pct"] / 100.0)
    
    # Calculate annualized growth rate (24 months = 2 years)
    annual_growth_factor = growth_factor ** (12 / total_months)  # 12 months/year
    annual_growth_rate_pct = (annual_growth_factor - 1) * 100
    
    # Engine reported net: +7% (annualized)
    engine_net_pct = 7.0
    tolerance = 0.5  # Allow ±0.5% tolerance for rounding
    
    math_sound = abs(annual_growth_rate_pct - engine_net_pct) <= tolerance
    
    # 2. Validate Omega Protocol invariants
    # Phi_N: Baseline stability - short-term dip must be recoverable
    short_term_factor = 1 + periods[0]["impact_pct"] / 100.0
    phi_n_stable = short_term_factor >= 0.90  # Max 10% temporary dip allowed
    
    # Phi_Delta: Rate of change - long-term must be positive
    long_term_impact = sum(p["impact_pct"] * p["months"] for p in periods[1:]) / sum(p["months"] for p in periods[1:])
    phi_delta_positive = long_term_impact > 0
    
    # J*: Justice metric - net annualized Φ must increase (ethical compliance)
    j_star_increase = annual_growth_rate_pct > 0
    
    # Overall compliance
    protocol_compliant = phi_n_stable and phi_delta_positive and j_star_increase
    
    # Output validation results
    print("Ω PROTOCOL Φ-DENSITY REFLECTION VALIDATION")
    print("=" * 50)
    print(f"Period Validation:")
    for p in periods:
        print(f"  {p['label']:15} | {p['impact_pct']:+.1f}% over {p['months']:2d} months")
    print(f"\nCompounded Growth Factor: {growth_factor:.4f}")
    print(f"Annualized Growth Rate:   {annual_growth_rate_pct:+.2f}%")
    print(f"Engine Reported Net:      {engine_net_pct:+.1f}%")
    print(f"Math Sound (±{tolerance}%): {'✓ PASS' if math_sound else '✗ FAIL'}")
    print("\nInvariant Checks:")
    print(f"  Phi_N Stability (Baseline): {'✓ PASS' if phi_n_stable else '✗ FAIL'} "
          f"(min factor: {short_term_factor:.3f} ≥ 0.90)")
    print(f"  Phi_Delta Positivity (LT):  {'✓ PASS' if phi_delta_positive else '✗ FAIL'} "
          f"(avg: {long_term_impact:+.1f}%/month)")
    print(f"  J* Increase (Justice):      {'✓ PASS' if j_star_increase else '✗ FAIL'} "
          f"(net: {annual_growth_rate_pct:+.2f}%/year)")
    print(f"\nOVERALL PROTOCOL COMPLIANCE: {'✓ PASS' if protocol_compliant and math_sound else '✗ FAIL'}")
    
    # Return boolean for programmatic use
    return protocol_compliant and math_sound

# Execute validation
if __name__ == "__main__":
    result = validate_phi_density_reflection()
    exit(0 if result else 1)