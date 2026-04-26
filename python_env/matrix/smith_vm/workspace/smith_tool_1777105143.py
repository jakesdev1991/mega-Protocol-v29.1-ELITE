# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np

# ------------------------------
# Omega Protocol Invariant Checks
# ------------------------------
def validate_qrsi(state):
    """
    state: dict with keys
        COD          : float [0,1]  (Chain Overlap Density)
        xi_buyer     : float >=0   (Buyer readiness entropy/stiffness)
        xi_seller0   : float >=0   (Initial seller urgency stiffness)
        gamma        : float >0    (Adiabatic rate)
        t            : float >=0   (Time elapsed)
        C_audit      : int         (Number of invariant checks)
    Returns: (bool passed, list of violation messages)
    """
    violations = []

    # 1. COD bounds and dimensionless check
    if not (0.0 <= state['COD'] <= 1.0):
        violations.append(f"COD out of bounds: {state['COD']}")
    # 2. Φ_N = log2(COD + ε)  (must be >=0 for trust density)
    eps = 1e-9
    phi_N = np.log2(state['COD'] + eps)
    if phi_N < 0:
        violations.append(f"Φ_N negative (trust density invalid): {phi_N}")
    # 3. ψ = ln(Φ_N)  (Identity Continuity Invariant)
    #    Requires Φ_N > 0; convert log2 to ln: ln(Φ_N) = ln(2)*log2(Φ_N)
    if phi_N <= 0:
        violations.append("Φ_N ≤ 0, cannot compute ψ = ln(Φ_N)")
    else:
        psi = np.log(phi_N)   # natural log of Φ_N
        # Enforce ψ >= ln(0.95) as per invariant table
        if psi < np.log(0.95):
            violations.append(f"Identity Continuity violated: ψ={psi} < ln(0.95)")
    # 4. Φ_Δ = ψ * tanh(R_align / R_max)
    R_align = abs(state['xi_buyer'] - state['xi_seller'])  # xi_seller is time‑dependent
    R_max = 2.8
    phi_Delta = psi * np.tanh(R_align / R_max)
    # 5. Audit cost: ΔS_audit = k_B * ln(2) * C_audit (set k_B=1 for dimensionless)
    delta_S_audit = np.log(2) * state['C_audit']
    # 6. Net Φ = Φ_N + Φ_Δ - ΔS_audit
    phi_net = phi_N + phi_Delta - delta_S_audit
    if phi_net < 0:
        violations.append(f"Net Φ density negative: {phi_net}")
    # 7. Stiffness Matching: Ξ_seller(t) ≤ Ξ_buyer
    #    Correct adiabatic form: Ξ_seller(t) = Ξ_seller0 * e^{-γ t} + Ξ_buyer * (1 - e^{-γ t})
    xi_seller_t = state['xi_seller0'] * np.exp(-state['gamma'] * state['t']) + \
                  state['xi_buyer'] * (1 - np.exp(-state['gamma'] * state['t']))
    if xi_seller_t > state['xi_buyer'] + 1e-12:  # allow tiny numerical tolerance
        violations.append(f"Stiffness mismatch: Ξ_seller({state['t']})={xi_seller_t:.3f} > Ξ_buyer={state['xi_buyer']:.3f}")
    # 8. Entropy Cap: H_collapse ≤ 0.3 (placeholder; assume computed elsewhere)
    #    We'll just note that the proposal does not provide H_collapse; flag if missing.
    if 'H_collapse' not in state:
        violations.append("H_collapse not provided – cannot verify Entropy Cap")
    elif state['H_collapse'] > 0.3:
        violations.append(f"Entropy cap exceeded: H_collapse={state['H_collapse']}")
    # 9. Asymmetry Control: Φ_Δ < 0.5 * Φ_N
    if phi_Delta >= 0.5 * phi_N:
        violations.append(f"Asymmetry control violated: Φ_Δ={phi_Delta:.3f} ≥ 0.5*Φ_N={0.5*phi_N:.3f}")
    # 10. Metric Non-Degeneracy: |det(g)| > 1e-15 (placeholder)
    #    We approximate det(g) ∝ COD * exp(-γ|xi_seller - xi_buyer|)
    det_g_approx = state['COD'] * np.exp(-state['gamma'] * abs(state['xi_seller0'] - state['xi_buyer']))
    if abs(det_g_approx) <= 1e-15:
        violations.append(f"Metric near‑degenerate: det(g)≈{det_g_approx:.2e}")

    passed = len(violations) == 0
    return passed, violations

# ------------------------------
# Example usage with proposal numbers
# ------------------------------
example_state = {
    'COD': 0.88,                     # from proposal (COD ≥ 0.85)
    'xi_buyer': 1.2,                 # arbitrary readiness
    'xi_seller0': 2.0,               # initial seller pressure (high)
    'gamma': 0.02,                   # hr⁻¹ as stated
    't': 10.0,                       # hours elapsed
    'C_audit': 6,                    # six invariants checked
    # 'H_collapse': 0.25,            # uncomment to test entropy cap
}

passed, msgs = validate_qrsi(example_state)
if passed:
    print("✅ All Omega Protocol invariants satisfied.")
else:
    print("❌ Invariant violations detected:")
    for m in msgs:
        print(" -", m)
    print("\nSuggested fixes:")
    print(" • Use Ξ_seller(t) = Ξ_seller0 * e^{-γt} + Ξ_buyer * (1 - e^{-γt})")
    print(" • Ensure Φ_N = log2(COD) is ≥0 → COD ∈ [1,2) if using log2, or switch to ln for consistency.")
    print(" • Apply base conversion: ψ = ln(2) * log2(Φ_N) if Φ_N is log₂‑based.")
    print(" • Provide explicit H_collapse calculation to verify Entropy Cap.")