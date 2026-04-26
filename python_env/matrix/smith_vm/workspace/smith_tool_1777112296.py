# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import math
import numpy as np

def validate_omega_invariants(state):
    """
    Validates Omega Protocol invariants for QRSI v57.0 proposal.
    
    Args:
        state (dict): Contains:
            - COD: float [0,1] (fidelity squared)
            - Xi_seller: float (seller stiffness)
            - Xi_buyer: float (buyer readiness)
            - H_collapse: float (entropy of collapse)
            - metric_det: float (determinant of deal manifold metric)
            - delta_phi_net: float (change in Phi-net post-audit)
            - psi: float (system's Identity Continuity value)
    
    Returns:
        dict: Validation results per invariant and overall status
    """
    # Extract state variables
    COD = state.get('COD', 0.0)
    Xi_seller = state.get('Xi_seller', 0.0)
    Xi_buyer = state.get('Xi_buyer', 0.0)
    H_collapse = state.get('H_collapse', 0.0)
    metric_det = state.get('metric_det', 0.0)
    delta_phi_net = state.get('delta_phi_net', 0.0)
    psi = state.get('psi', 0.0)
    
    # Constants from proposal
    R_max = 2.8
    tolerance = 1e-9
    
    # Precompute derived quantities
    # Phi_N = log2(COD) [as per proposal Section 1.2]
    if COD <= 0:
        Phi_N = -np.inf
    else:
        Phi_N = math.log2(COD)
    
    # R_align = |Xi_buyer - Xi_seller| (per proposal Section 1.2 and Fig 2)
    R_align = abs(Xi_buyer - Xi_seller)
    
    # Phi_Delta = psi * tanh(R_align / R_max) [per proposal Section 1.2]
    Phi_Delta = psi * math.tanh(R_align / R_max) if not math.isinf(Phi_N) else 0.0
    
    # Initialize results
    results = {
        'Invariant 1 (Metric Non-Degeneracy)': False,
        'Invariant 2 (Identity Continuity)': False,
        'Invariant 3 (Stiffness Matching)': False,
        'Invariant 4 (Entropy Cap)': False,
        'Invariant 5 (Information Conservation)': False,
        'Invariant 6 (Asymmetry Control)': False,
        'Overall': False,
        'Details': {}
    }
    
    # Invariant 1: Metric Non-Degeneracy
    # ||det(g)|| > exp(-psi)
    # Note: exp(-psi) is always positive. We compare absolute value of metric_det.
    if not math.isinf(psi) and not math.isnan(psi):
        threshold = math.exp(-psi)
        results['Invariant 1 (Metric Non-Degeneracy)'] = abs(metric_det) > threshold
        results['Details']['Invariant 1'] = f"|det(g)|={abs(metric_det):.6f} > exp(-psi)={threshold:.6f}"
    else:
        results['Details']['Invariant 1'] = "Invalid psi (inf/nan)"
    
    # Invariant 2: Identity Continuity
    # psi = ln(Phi_N) AND psi >= ln(0.95)
    # Critical check: Phi_N must be > 0 for ln(Phi_N) to be real
    if Phi_N > 0 and not math.isinf(Phi_N):
        expected_psi = math.log(Phi_N)
        # Check equality (within tolerance) and minimum value
        equality_ok = abs(psi - expected_psi) < tolerance
        min_ok = psi >= math.log(0.95)
        results['Invariant 2 (Identity Continuity)'] = equality_ok and min_ok
        results['Details']['Invariant 2'] = (
            f"psi={psi:.6f}, expected ln(Phi_N)={expected_psi:.6f} (equal: {equality_ok}), "
            f"min ln(0.95)={math.log(0.95):.6f} (ok: {min_ok})"
        )
    else:
        results['Details']['Invariant 2'] = (
            f"Phi_N={Phi_N:.6f} must be >0 for ln(Phi_N) to be real (current: {'-inf' if Phi_N==-np.inf else Phi_N})"
        )
    
    # Invariant 3: Stiffness Matching
    # Xi_seller <= Xi_buyer
    results['Invariant 3 (Stiffness Matching)'] = Xi_seller <= Xi_buyer
    results['Details']['Invariant 3'] = f"Xi_seller={Xi_seller:.6f} <= Xi_buyer={Xi_buyer:.6f}"
    
    # Invariant 4: Entropy Cap
    # H_collapse <= 0.3
    results['Invariant 4 (Entropy Cap)'] = H_collapse <= 0.3
    results['Details']['Invariant 4'] = f"H_collapse={H_collapse:.6f} <= 0.3"
    
    # Invariant 5: Information Conservation
    # Delta Phi_net >= 0 (post-audit)
    results['Invariant 5 (Information Conservation)'] = delta_phi_net >= -tolerance  # Allow small negative due to FP
    results['Details']['Invariant 5'] = f"ΔΦ_net={delta_phi_net:.6f} >= 0"
    
    # Invariant 6: Asymmetry Control
    # Phi_Delta < 0.5 * Phi_N
    # Note: Only valid if Phi_N > 0 (else RHS negative/undefined)
    if Phi_N > 0 and not math.isinf(Phi_N):
        results['Invariant 6 (Asymmetry Control)'] = Phi_Delta < 0.5 * Phi_N
        results['Details']['Invariant 6'] = (
            f"Phi_Delta={Phi_Delta:.6f} < 0.5*Phi_N={0.5*Phi_N:.6f}"
        )
    else:
        results['Details']['Invariant 6'] = (
            f"Phi_N={Phi_N:.6f} must be >0 for asymmetry check (current: {'-inf' if Phi_N==-np.inf else Phi_N})"
        )
    
    # Overall status: all invariants must pass
    results['Overall'] = all([
        results['Invariant 1 (Metric Non-Degeneracy)'],
        results['Invariant 2 (Identity Continuity)'],
        results['Invariant 3 (Stiffness Matching)'],
        results['Invariant 4 (Entropy Cap)'],
        results['Invariant 5 (Information Conservation)'],
        results['Invariant 6 (Asymmetry Control)']
    ])
    
    return results

# Test with values from proposal's claimed verification (Section 5.3)
# They claim: "Identity Continuity: ψ ≥ ln(0.95) — VERIFIED"
# But we know this is impossible due to Phi_N definition. Let's test with COD=0.95 (their threshold)
test_state = {
    'COD': 0.95,          # Fidelity squared
    'Xi_seller': 0.5,     # Example stiffness
    'Xi_buyer': 0.7,      # Buyer readiness > seller (should pass Invariant 3)
    'H_collapse': 0.25,   # Below entropy cap
    'metric_det': 0.1,    # Example metric determinant
    'delta_phi_net': 0.1, # Positive net gain
    'psi': math.log(math.log2(0.95))  # What psi SHOULD be if invariant held (but note: log2(0.95)<0 -> invalid)
}

# Note: The above psi calculation is invalid because log2(0.95) is negative -> log of negative is complex.
# Instead, we'll test with a COD that makes Phi_N positive? Impossible per definition.
# So we test with COD=0.95 and show Invariant 2 fails.

print("Ω-PROTOCOL INVARIANT VALIDATION: QRSI v57.0")
print("=" * 50)
results = validate_omega_invariants(test_state)

for inv, passed in results.items():
    if inv != 'Details' and inv != 'Overall':
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{inv}: {status}")
        if not passed:
            print(f"  → {results['Details'][inv]}")

print("-" * 50)
print(f"OVERALL STATUS: {'✅ METAPASS' if results['Overall'] else '❌ META-FAIL'}")
print("=" * 50)

# Critical flaw demonstration
print("\n🔍 CRITICAL FLAW ANALYSIS:")
print("Phi_N = log2(COD) where COD ∈ [0,1] → Phi_N ≤ 0")
print("Therefore ln(Phi_N) is undefined (for Phi_N<0) or -∞ (at Phi_N=0)")
print("Invariant #2 requires psi = ln(Phi_N) ≥ ln(0.95) ≈ -0.05")
print("This is mathematically impossible → System fundamentally violates Omega Protocol")
print("→ PROPOSAL IS INVALID")