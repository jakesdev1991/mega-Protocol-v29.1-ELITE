# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
"""
Omega Protocol Invariant Validator for ARG v53.1 (Adiabatic Reboot Gate)
Validates mathematical soundness and strict compliance with the six Smith invariants.
All quantities are dimensionless and bounded [0,1] unless otherwise noted.
"""

import numpy as np

# Constants from the derivation
GAMMA = 0.008          # hr^-1, ultra-slow integration rate
R_MAX = 2.5            # maximum tolerable validation pressure
K_B_LN2 = 1.0          # setting k_B * ln(2) = 1 for dimensionless audit cost (scales linearly)
EPS = 1e-12            # numerical tolerance

def validate_inputs(**kwargs):
    """Ensure all inputs are within [0,1] (or appropriate log ranges)."""
    for name, val in kwargs.items():
        if isinstance(val, (int, float)):
            if name in ('psi', 'Phi_N', 'Phi_Delta', 'Delta_S_audit', 'COD', 'H_fracture',
                        'Xi_con', 'Xi_sub', 'Xi_val', 'R_validation'):
                if not (0.0 - EPS <= val <= 1.0 + EPS):
                    raise ValueError(f"{name}={val} out of bounds [0,1]")
            elif name in ('Phi_N_log',):  # psi = ln(Phi_N) can be negative
                if val < -EPS:
                    raise ValueError(f"{name}={val} must be >= 0 (since Phi_N in [0,1])")
        else:
            raise TypeError(f"{name} must be numeric")

def compute_Phi_N(COD, H_fracture):
    """Φ_N = log2( COD / (1 + H_fracture) )"""
    validate_inputs(COD=COD, H_fracture=H_fracture)
    if COD <= 0:
        return -np.inf
    return np.log2(COD / (1.0 + H_fracture))

def compute_psi(Phi_N):
    """ψ = ln(Φ_N)  (mandatory coupling invariant)"""
    validate_inputs(Phi_N=Phi_N)
    if Phi_N <= 0:
        return -np.inf
    return np.log(Phi_N)

def compute_Phi_Delta(psi, R_validation):
    """Φ_Δ = ψ * tanh( R_validation / R_MAX )"""
    validate_inputs(psi=psi, R_validation=R_validation)
    # psi can be negative; tanh yields [-1,1]; product still dimensionless
    return psi * np.tanh(R_validation / R_MAX)

def compute_Delta_S_audit(N_steps):
    """ΔS_audit = k_B ln 2 * N_steps  (set k_B ln 2 = 1 for dimensionless)"""
    if not isinstance(N_steps, int) or N_steps < 0:
        raise ValueError("N_steps must be a non-negative integer")
    return float(N_steps)  # because k_B ln 2 = 1

def compute_Phi_net(COD, H_fracture, psi, R_validation, N_steps):
    """Full Φ_net = Φ_N + Φ_Δ - ΔS_audit"""
    Phi_N = compute_Phi_N(COD, H_fracture)
    Phi_Delta = compute_Phi_Delta(psi, R_validation)
    Delta_S = compute_Delta_S_audit(N_steps)
    return Phi_N + Phi_Delta - Delta_S, Phi_N, Phi_Delta, Delta_S

def ARG_Xi_val(t, Xi_val0, Xi_sub):
    """Ξ_val(t) = Ξ_val(0)·e^{-γt} + Ξ_sub·(1 - e^{-γt})"""
    validate_inputs(Xi_val0=Xi_val0, Xi_sub=Xi_sub)
    if t < 0:
        raise ValueError("time t must be non-negative")
    return Xi_val0 * np.exp(-GAMMA * t) + Xi_sub * (1.0 - np.exp(-GAMMA * t))

def check_invariants(COD, H_fracture, Phi_N, psi, Xi_val, Xi_sub, R_validation, Phi_Delta, Delta_S_audit, N_steps):
    """
    Returns a dict of boolean results for each Smith invariant.
    Also returns overall pass/fail.
    """
    results = {}

    # 1. Metric Non-Degeneracy: det(g) > 1e-15  <=>  Ξ_val ≤ Ξ_sub (since det ∝ exp(-Γ|Ξ_val-Ξ_sub|))
    results["Metric_Non_Degeneracy"] = Xi_val <= Xi_sub + EPS

    # 2. Identity Continuity: ψ = ln(Φ_N) ≥ ln(0.95)  =>  Φ_N ≥ 0.95
    results["Identity_Continuity"] = Phi_N >= 0.95 - EPS

    # 3. Validation Safety: Ξ_val(t) ≤ Ξ_sub(t)
    results["Validation_Safety"] = Xi_val <= Xi_sub + EPS

    # 4. Fracture Cap: H_fracture ≤ 0.75
    results["Fracture_Cap"] = H_fracture <= 0.75 + EPS

    # 5. Information Conservation: ΔΦ_net ≥ 0 (post-audit)
    Phi_net, _, _, _ = compute_Phi_net(COD, H_fracture, psi, R_validation, N_steps)
    results["Information_Conservation"] = Phi_net >= -EPS  # allow tiny negative due to rounding

    # 6. Asymmetry Control: Φ_Δ < 0.5 · Φ_N
    results["Asymmetry_Control"] = Phi_Delta < 0.5 * Phi_N + EPS

    all_pass = all(results.values())
    return results, all_pass

def run_validation_suite():
    """Test a few scenarios: nominal (should pass), and deliberate violations."""
    print("=== Omega Protocol Invariant Validation Suite ===\n")

    # Nominal parameters from the derivation (claimed net gain +0.77Φ)
    # We back-solve to get plausible numbers:
    #   COD_post ≈ 0.88, H_fracture_post ≈ 0.22  => Φ_N = log2(0.88/(1+0.22)) ≈ log2(0.721) ≈ -0.47
    #   But note: Φ_N can be negative; ψ = ln(Φ_N) would be undefined if Φ_N<1? Wait: ψ = ln(Φ_N) with Φ_N in [0,1] => ψ ≤ 0.
    #   The paper treats ψ as ln(Φ_N) and requires ψ ≥ ln(0.95) ≈ -0.051, meaning Φ_N must be ≥0.95.
    #   However their Φ_N expression can be <1. There's a tension: they likely intend Φ_N to be a *positive* fidelity-like term
    #   and then take its log. Let's reinterpret: Φ_N = log2( ... ) yields a value that can be negative, but then they
    #   define ψ = ln(Φ_N) only if Φ_N>0? Actually they say ψ = ln(Φ_N) — mandatory coupling invariant.
    #   For ψ to be real, Φ_N must be >0. The log2 can be negative, but ln of a negative is undefined.
    #   Therefore we must assume the inner argument of log2 is ≥1 so that Φ_N ≥0? No, log2 of a number <1 is negative.
    #   To salvage, we treat Φ_N as the *argument* of the log2 (i.e., the fidelity ratio) and then the equation is miswritten.
    #   For the sake of invariant checking we will enforce the *spirit*: ψ = ln(Φ_N) with Φ_N in (0,1] => ψ ≤0.
    #   The identity continuity invariant they gave: ψ ≥ ln(0.95) ≈ -0.051, so Φ_N must be ≥0.95.
    #   Hence we will enforce that the *ratio* inside the log2 must be ≥0.95, and we will compute ψ from that ratio directly.
    #   Let's define:
    #       raw_ratio = COD / (1 + H_fracture)   ∈ (0,1]
    #       ψ = ln(raw_ratio)
    #       Φ_N = log2(raw_ratio)   (used elsewhere)
    #   This matches their text: "ψ = ln(Φ_N)" is likely a typo; they meant ψ = ln(raw_ratio).
    #   We'll adopt this interpretation for validation.

    def compute_psi_from_raw(COD, H_fracture):
        raw = COD / (1.0 + H_fracture)
        if raw <= 0:
            return -np.inf
        return np.log(raw)   # this is ψ

    def compute_Phi_N_from_raw(COD, H_fracture):
        raw = COD / (1.0 + H_fracture)
        if raw <= 0:
            return -np.inf
        return np.log2(raw)

    # Nominal post-reboot state (claimed):
    COD_nom = 0.88
    H_fracture_nom = 0.22
    psi_nom = compute_psi_from_raw(COD_nom, H_fracture_nom)   # should be ≥ ln(0.95)
    Phi_N_nom = compute_Phi_N_from_raw(COD_nom, H_fracture_nom)
    # Validation parameters: they claim R_validation such that Φ_Δ ≈ +0.15Φ
    # Let's set R_validation = 1.0 (moderate) and compute.
    R_val_nom = 1.0
    Phi_Delta_nom = psi_nom * np.tanh(R_val_nom / R_MAX)
    # Audit steps: they say 8 steps → ΔS_audit = 0.18Φ (with k_B ln2 =1)
    N_steps_nom = 8
    # Compute net
    Phi_net_nom, _, _, _ = compute_Phi_net(COD_nom, H_fracture_nom, psi_nom, R_val_nom, N_steps_nom)

    # Xi values: we need Xi_val ≤ Xi_sub. Choose Xi_sub = 0.6, Xi_val = 0.5 (safe)
    Xi_sub_nom = 0.6
    Xi_val_nom = 0.5
    # Also check ARG evolution at t=0 and t=24h
    t0 = 0.0
    t24 = 24.0
    Xi_val_t0 = ARG_Xi_val(t0, Xi_val_nom, Xi_sub_nom)
    Xi_val_t24 = ARG_Xi_val(t24, Xi_val_nom, Xi_sub_nom)

    print("--- Nominal (claimed successful reboot) ---")
    print(f"COD={COD_nom:.3f}, H_fracture={H_fracture_nom:.3f}")
    print(f"raw_ratio={COD_nom/(1+H_fracture_nom):.3f} => ψ={psi_nom:.3f}, Φ_N={Phi_N_nom:.3f}")
    print(f"R_validation={R_val_nom:.3f} => Φ_Δ={Phi_Delta_nom:.3f}")
    print(f"Audit steps={N_steps_nom} => ΔS_audit={compute_Delta_S_audit(N_steps_nom):.3f}")
    print(f"Φ_net = {Phi_net_nom:.3f} (claimed +0.77Φ)")
    print(f"Xi_sub={Xi_sub_nom:.3f}, Xi_val(t=0)={Xi_val_t0:.3f}, Xi_val(t=24h)={Xi_val_t24:.3f}")
    invar_nom, pass_nom = check_invariants(
        COD_nom, H_fracture_nom, Phi_N_nom, psi_nom,
        Xi_val_t0, Xi_sub_nom, R_val_nom, Phi_Delta_nom,
        compute_Delta_S_audit(N_steps_nom), N_steps_nom
    )
    print("Invariant results:", invar_nom)
    print("Overall PASS?" , pass_nom, "\n")

    # --- Violation 1: Identity Continuity broken (ψ too low) ---
    COD_bad1 = 0.50
    H_fracture_bad1 = 0.50   # raw ratio = 0.5/1.5 = 0.333 → ψ = ln(0.333) ≈ -1.099 < ln(0.95)
    psi_bad1 = compute_psi_from_raw(COD_bad1, H_fracture_bad1)
    Phi_N_bad1 = compute_Phi_N_from_raw(COD_bad1, H_fracture_bad1)
    R_val_bad1 = 0.5
    Phi_Delta_bad1 = psi_bad1 * np.tanh(R_val_bad1 / R_MAX)
    N_steps_bad1 = 4
    Xi_sub_bad1 = 0.4
    Xi_val_bad1 = 0.3   # still safe but identity fails
    print("--- Violation 1: Identity Continuity (ψ < ln(0.95)) ---")
    invar_bad1, pass_bad1 = check_invariants(
        COD_bad1, H_fracture_bad1, Phi_N_bad1, psi_bad1,
        Xi_val_bad1, Xi_sub_bad1, R_val_bad1, Phi_Delta_bad1,
        compute_Delta_S_audit(N_steps_bad1), N_steps_bad1
    )
    print("Invariant results:", invar_bad1)
    print("Overall PASS?" , pass_bad1, "\n")

    # --- Violation 2: Validation Safety (Ξ_val > Ξ_sub) ---
    COD_bad2 = 0.90
    H_fracture_bad2 = 0.10
    psi_bad2 = compute_psi_from_raw(COD_bad2, H_fracture_bad2)
    Phi_N_bad2 = compute_Phi_N_from_raw(COD_bad2, H_fracture_bad2)
    R_val_bad2 = 0.2
    Phi_Delta_bad2 = psi_bad2 * np.tanh(R_val_bad2 / R_MAX)
    N_steps_bad2 = 6
    Xi_sub_bad2 = 0.3
    Xi_val_bad2 = 0.5   # violation: validation pressure exceeds subconscious capacity
    print("--- Violation 2: Validation Safety (Ξ_val > Ξ_sub) ---")
    invar_bad2, pass_bad2 = check_invariants(
        COD_bad2, H_fracture_bad2, Phi_N_bad2, psi_bad2,
        Xi_val_bad2, Xi_sub_bad2, R_val_bad2, Phi_Delta_bad2,
        compute_Delta_S_audit(N_steps_bad2), N_steps_bad2
    )
    print("Invariant results:", invar_bad2)
    print("Overall PASS?" , pass_bad2, "\n")

    # --- Violation 3: Asymmetry Control (Φ_Δ ≥ 0.5·Φ_N) ---
    # To get large Φ_Δ we need large |ψ| and high R_validation.
    COD_bad3 = 0.96   # raw ratio high → ψ small magnitude (close to 0) → actually need ψ negative large magnitude.
    # Let's instead make raw ratio low (so ψ large negative) and R_validation high.
    COD_bad3 = 0.60
    H_fracture_bad3 = 0.20   # raw = 0.6/1.2 = 0.5 → ψ = ln(0.5) ≈ -0.693
    psi_bad3 = compute_psi_from_raw(COD_bad3, H_fracture_bad3)
    Phi_N_bad3 = compute_Phi_N_from_raw(COD_bad3, H_fracture_bad3)
    R_val_bad3 = 2.4   # near R_MAX → tanh ≈ 0.98
    Phi_Delta_bad3 = psi_bad3 * np.tanh(R_val_bad3 / R_MAX)   # ≈ -0.693*0.98 ≈ -0.679
    # Φ_N is negative (since raw<1 → log2<0). Let's compute:
    #   Φ_N = log2(0.5) = -1.0
    #   0.5·Φ_N = -0.5
    #   Φ_Δ ≈ -0.679 < -0.5 => actually satisfies Φ_Δ < 0.5·Φ_N (more negative is less).
    # We need Φ_Δ to be *less negative* than 0.5·Φ_N (i.e., closer to zero) to violate.
    # Since both are negative, the inequality Φ_Δ < 0.5·Φ_N means Φ_Δ must be more negative.
    # To violate we want Φ_Δ *greater* (i.e., less negative) than 0.5·Φ_N.
    # So we need ψ small magnitude (close to zero) and R_validation high → Φ_Δ small negative.
    # Let's set raw ratio near 1 => ψ ≈ 0 → Φ_Δ ≈ 0, while Φ_N slightly negative.
    COD_bad3 = 0.99
    H_fracture_bad3 = 0.00   # raw = 0.99/1.00 = 0.99 → ψ = ln(0.99) ≈ -0.01005
    psi_bad3 = compute_psi_from_raw(COD_bad3, H_fracture_bad3)
    Phi_N_bad3 = compute_Phi_N_from_raw(COD_bad3, H_fracture_bad3)   # log2(0.99) ≈ -0.0145
    R_val_bad3 = 2.4
    Phi_Delta_bad3 = psi_bad3 * np.tanh(R_val_bad3 / R_MAX)   # ≈ -0.01005*0.98 ≈ -0.00985
    # 0.5·Φ_N ≈ -0.00725
    # Now Φ_Δ (-0.00985) < -0.00725 → still satisfies (more negative). Need Φ_Δ > 0.5·Φ_N.
    # Make ψ positive? ψ cannot be positive because raw ≤1 => ln(raw) ≤0.
    # Thus Φ_Δ will always be ≤0 (since ψ≤0, tanh≥0). Φ_N is also ≤0.
    # The inequality Φ_Δ < 0.5·Φ_N for negative numbers: e.g., Φ_N=-2, 0.5·Φ_N=-1.
    # If Φ_Δ=-0.5 then -0.5 < -1? No, -0.5 > -1 → violates.
    # So we need Φ_N negative with large magnitude, and Φ_Δ small magnitude.
    # Let's set raw ratio very small → ψ large negative, Φ_N large negative.
    # Then 0.5·Φ_N is also large negative (half). To violate we need Φ_Δ *greater* (i.e., less negative) than that.
    # So we need ψ large negative but R_validation very small → Φ_Δ ≈ 0.
    COD_bad3 = 0.20
    H_fracture_bad3 = 0.05   # raw = 0.20/1.05 ≈ 0.1905 → ψ = ln(0.1905) ≈ -1.658
    psi_bad3 = compute_psi_from_raw(COD_bad3, H_fracture_bad3)
    Phi_N_bad3 = compute_Phi_N_from_raw(COD_bad3, H_fracture_bad3)   # log2(0.1905) ≈ -2.39
    R_val_bad3 = 0.01   # near zero → tanh ≈ 0.01
    Phi_Delta_bad3 = psi_bad3 * np.tanh(R_val_bad3 / R_MAX)   # ≈ -1.658*0.01 ≈ -0.0166
    # 0.5·Φ_N ≈ -1.195
    # Now Φ_Δ (-0.0166) > -1.195 → violates Φ_Δ < 0.5·Φ_N (since -0.0166 is NOT less than -1.195).
    print("--- Violation 3: Asymmetry Control (Φ_Δ ≥ 0.5·Φ_N) ---")
    print(f"COD={COD_bad3:.3f}, H_fracture={H_fracture_bad3:.3f} => raw={COD_bad3/(1+H_fracture_bad3):.3f}")
    print(f"ψ={psi_bad3:.3f}, Φ_N={Phi_N_bad3:.3f}")
    print(f"R_validation={R_val_bad3:.3f} => Φ_Δ={Phi_Delta_bad3:.3f}")
    print(f"0.5·Φ_N={0.5*Phi_N_bad3:.3f}")
    invar_bad3, pass_bad3 = check_invariants(
        COD_bad3, H_fracture_bad3, Phi_N_bad3, psi_bad3,
        Xi_val_bad3:=0.2, Xi_sub_bad3:=0.3, R_val_bad3, Phi_Delta_bad3,
        compute_Delta_S_audit(N_steps_bad3:=5), N_steps_bad3:=5
    )
    print("Invariant results:", invar_bad3)
    print("Overall PASS?" , pass_bad3, "\n")

    # Summary
    print("=== Summary ===")
    print(f"Nominal case PASS: {pass_nom}")
    print(f"Violation 1 (Identity) PASS: {pass_bad1} (should be False)")
    print(f"Violation 2 (Safety) PASS: {pass_bad2} (should be False)")
    print(f"Violation 3 (Asymmetry) PASS: {pass_bad3} (should be False)")
    if pass_nom and not (pass_bad1 or pass_bad2 or pass_bad3):
        print("\nInvariant enforcement is working as expected.")
    else:
        print("\nUnexpected results – check invariant logic or test values.")

if __name__ == "__main__":
    run_validation_suite()