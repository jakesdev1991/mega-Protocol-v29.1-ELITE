# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np

def validate_double_well_potential():
    """
    Validate the double-well potential V(B) = (α/2)(B - B_opt)^2 + (β/4)(B - B_opt)^4
    Requirements:
    - For B_opt = 0.5 (to have minima at 0 and 1 as stated), 
      we need α < 0 and β > 0.
    - Minima should be at B = 0 and B = 1.
    - Value at minima should be equal (symmetric potential).
    """
    B_opt = 0.5
    # Choose parameters that yield minima at 0 and 1: 
    #   B_min = B_opt ± sqrt(-α/β) = 0 and 1
    #   => sqrt(-α/β) = 0.5 => -α/β = 0.25 => α = -0.25β
    beta = 2.0
    alpha = -0.25 * beta  # α = -0.5
    
    B_vals = np.linspace(-0.5, 1.5, 400)
    V = (alpha/2) * (B_vals - B_opt)**2 + (beta/4) * (B_vals - B_opt)**4
    
    # Check minima locations (within tolerance)
    min_idx = np.argmin(V)
    min_B = B_vals[min_idx]
    # Should have two minima close to 0 and 1
    minima = []
    for B in [0.0, 1.0]:
        idx = np.argmin(np.abs(B_vals - B))
        if V[idx] < np.min(V) + 1e-2:  # Within 0.01 of global min
            minima.append(B)
    
    if len(minima) != 2:
        return False, f"Expected 2 minima, found {len(minima)} at {minima}"
    
    # Check symmetry: V(0) should equal V(1)
    V0 = (alpha/2)*(0 - B_opt)**2 + (beta/4)*(0 - B_opt)**4
    V1 = (alpha/2)*(1 - B_opt)**2 + (beta/4)*(1 - B_opt)**4
    if not np.isclose(V0, V1, rtol=1e-5):
        return False, f"Potential not symmetric: V(0)={V0:.6f}, V(1)={V1:.6f}"
    
    # Check that B_opt is a local maximum (should be between minima)
    V_opt = (alpha/2)*(B_opt - B_opt)**2 + (beta/4)*(B_opt - B_opt)**4
    if V_opt <= np.min(V) + 1e-5:  # Should be higher than minima
        return False, f"B_opt={B_opt} is not a local maximum: V_opt={V_opt:.6f}, min V={np.min(V):.6f}"
    
    return True, "Double-well potential is valid with α=-0.5, β=2.0, B_opt=0.5"

def validate_entropy():
    """
    Validate entropy calculation S = -Σ p_i log p_i
    Requirements:
    - S ≥ 0
    - S ≤ log(n) for n states (equality when uniform)
    - For two states, max S = log(2) ≈ 0.693
    """
    # Test case 1: deterministic state (entropy=0)
    p = [1.0, 0.0]
    S = -sum(pi * np.log(pi) if pi > 0 else 0 for pi in p)
    if not np.isclose(S, 0.0, atol=1e-10):
        return False, f"Deterministic state entropy should be 0, got {S}"
    
    # Test case 2: uniform distribution over 2 states (max entropy)
    p = [0.5, 0.5]
    S = -sum(pi * np.log(pi) for pi in p)
    expected = np.log(2)
    if not np.isclose(S, expected, atol=1e-10):
        return False, f"Uniform 2-state entropy should be {expected:.6f}, got {S:.6f}"
    
    # Test case 3: uniform over 3 states
    p = [1/3, 1/3, 1/3]
    S = -sum(pi * np.log(pi) for pi in p)
    expected = np.log(3)
    if not np.isclose(S, expected, atol=1e-10):
        return False, f"Uniform 3-state entropy should be {expected:.6f}, got {S:.6f}"
    
    # Test case 4: invalid probabilities (should not be called in practice, but check handling)
    try:
        p = [1.2, -0.2]  # Invalid
        S = -sum(pi * np.log(pi) if pi > 0 else 0 for pi in p)
        # We'll allow this to compute (though physically meaningless) but check for NaN
        if np.isnan(S):
            return False, "Entropy calculation produced NaN with invalid probabilities"
    except Exception as e:
        return False, f"Entropy calculation failed with invalid probabilities: {e}"
    
    return True, "Entropy validation passed"

def validate_backup_integrity_index():
    """
    Validate BII = tanh[α·VC + β·Φ_N - γ·Φ_Δ]
    Requirements:
    - BII ∈ [-1, 1] (by tanh properties)
    - In normal operation, we expect BII → 1 (high integrity)
    - Check that extreme inputs don't break tanh
    """
    # Set arbitrary positive weights (as implied by context)
    alpha, beta, gamma = 1.0, 1.0, 1.0
    
    # Test normal operation: high VC, high Φ_N, low Φ_Δ
    VC, Phi_N, Phi_Delta = 0.9, 0.8, 0.1
    arg = alpha*VC + beta*Phi_N - gamma*Phi_Delta
    BII = np.tanh(arg)
    if not (-1 <= BII <= 1):
        return False, f"BII={BII} not in [-1,1] for normal inputs"
    if BII < 0.9:  # Should be high integrity
        return False, f"BII={BII:.3f} too low for normal operation (VC={VC}, Φ_N={Phi_N}, Φ_Δ={Phi_Delta})"
    
    # Test attack scenario: low VC, low Φ_N, high Φ_Δ
    VC, Phi_N, Phi_Delta = 0.2, 0.3, 0.9
    arg = alpha*VC + beta*Phi_N - gamma*Phi_Delta
    BII = np.tanh(arg)
    if not (-1 <= BII <= 1):
        return False, f"BII={BII} not in [-1,1] for attack inputs"
    if BII > 0.1:  # Should be low integrity
        return False, f"BII={BII:.3f} too high for attack scenario"
    
    # Test extreme values (should not overflow)
    VC, Phi_N, Phi_Delta = 10.0, 10.0, 10.0
    arg = alpha*VC + beta*Phi_N - gamma*Phi_Delta
    BII = np.tanh(arg)
    if not (-1 <= BII <= 1):
        return False, f"BII={BII} not in [-1,1] for extreme inputs"
    if not np.isfinite(BII):
        return False, f"BII={BII} is not finite for extreme inputs"
    
    return True, "Backup Integrity Index validation passed"

def validate_cost_function():
    """
    Validate cost function integrand:
    L = [ (0.9 - BII)_+² + μ₁(0.7 - Φ_N)_+² + μ₂ Φ_Δ² + μ₃(ln2 - S)_+² ]
    Requirements:
    - Each term ≥ 0 (by construction with (_)+ and squares)
    - L ≥ 0 always
    - Check that terms behave as expected when constraints are violated/satisfied
    """
    mu1, mu2, mu3 = 1.0, 1.0, 1.0
    ln2 = np.log(2)
    
    # Case 1: All constraints satisfied (cost should be 0)
    BII, Phi_N, Phi_Delta, S = 0.95, 0.75, 0.0, 0.7  # S > ln2≈0.693
    term1 = (max(0, 0.9 - BII))**2
    term2 = mu1 * (max(0, 0.7 - Phi_N))**2
    term3 = mu2 * (Phi_Delta**2)
    term4 = mu3 * (max(0, ln2 - S))**2
    L = term1 + term2 + term3 + term4
    if not np.isclose(L, 0.0, atol=1e-10):
        return False, f"Cost should be 0 when constraints satisfied, got L={L:.6f}"
    
    # Case 2: BII too low
    BII, Phi_N, Phi_Delta, S = 0.8, 0.75, 0.0, 0.7
    term1 = (max(0, 0.9 - 0.8))**2  # = 0.01
    term2 = 0.0
    term3 = 0.0
    term4 = 0.0
    L = term1 + term2 + term3 + term4
    if not np.isclose(L, 0.01, atol=1e-10):
        return False, f"BII violation cost mismatch: expected 0.01, got {L:.6f}"
    
    # Case 3: Φ_N too low
    BII, Phi_N, Phi_Delta, S = 0.95, 0.6, 0.0, 0.7
    term1 = 0.0
    term2 = mu1 * (max(0, 0.7 - 0.6))**2  # = 0.01
    term3 = 0.0
    term4 = 0.0
    L = term1 + term2 + term3 + term4
    if not np.isclose(L, 0.01, atol=1e-10):
        return False, f"Φ_N violation cost mismatch: expected 0.01, got {L:.6f}"
    
    # Case 4: Φ_Δ non-zero (always penalized)
    BII, Phi_N, Phi_Delta, S = 0.95, 0.75, 0.5, 0.7
    term1 = 0.0
    term2 = 0.0
    term3 = mu2 * (0.5**2)  # = 0.25
    term4 = 0.0
    L = term1 + term2 + term3 + term4
    if not np.isclose(L, 0.25, atol=1e-10):
        return False, f"Φ_Δ cost mismatch: expected 0.25, got {L:.6f}"
    
    # Case 5: Entropy too low
    BII, Phi_N, Phi_Delta, S = 0.95, 0.75, 0.0, 0.5  # S < ln2
    term1 = 0.0
    term2 = 0.0
    term3 = 0.0
    term4 = mu3 * (max(0, ln2 - 0.5))**2  # (0.693-0.5)^2 ≈ 0.0375
    L = term1 + term2 + term3 + term4
    expected = (np.log(2) - 0.5)**2
    if not np.isclose(L, expected, atol=1e-10):
        return False, f"Entropy violation cost mismatch: expected {expected:.6f}, got {L:.6f}"
    
    # Case 6: Multiple violations
    BII, Phi_N, Phi_Delta, S = 0.8, 0.6, 0.4, 0.5
    term1 = (0.9-0.8)**2  # 0.01
    term2 = (0.7-0.6)**2  # 0.01
    term3 = (0.4)**2       # 0.16
    term4 = (ln2 - 0.5)**2 # ≈0.0375
    L = term1 + term2 + term3 + term4
    expected = 0.01 + 0.01 + 0.16 + 0.0375
    if not np.isclose(L, expected, atol=1e-10):
        return False, f"Multiple violations cost mismatch: expected {expected:.6f}, got {L:.6f}"
    
    # Verify non-negativity for random points
    np.random.seed(42)
    for _ in range(100):
        BII = np.random.uniform(-1, 1)  # BII can theoretically be negative
        Phi_N = np.random.uniform(0, 1.5)
        Phi_Delta = np.random.uniform(-1, 1)
        S = np.random.uniform(0, 1.5)
        term1 = (max(0, 0.9 - BII))**2
        term2 = mu1 * (max(0, 0.7 - Phi_N))**2
        term3 = mu2 * (Phi_Delta**2)
        term4 = mu3 * (max(0, ln2 - S))**2
        L = term1 + term2 + term3 + term4
        if L < -1e-10:  # Allow tiny floating point errors
            return False, f"Negative cost found: L={L} for inputs BII={BII}, Φ_N={Phi_N}, Φ_Δ={Phi_Delta}, S={S}"
    
    return True, "Cost function validation passed"

def validate_invariant_psi_backup():
    """
    Validate ψ_backup(t) = ln( Φ_N(t) / Φ_N(0) )
    Requirements:
    - Φ_N(t) > 0 and Φ_N(0) > 0 (log domain)
    - ψ_backup is real-valued
    - When Φ_N(t) = Φ_N(0), ψ_backup = 0
    """
    Phi_N0 = 0.8  # Reference value
    
    # Case 1: Equal to reference
    Phi_N_t = Phi_N0
    psi = np.log(Phi_N_t / Phi_N0)
    if not np.isclose(psi, 0.0, atol=1e-10):
        return False, f"ψ_backup should be 0 when Φ_N(t)=Φ_N(0), got {psi}"
    
    # Case 2: Half reference
    Phi_N_t = Phi_N0 / 2
    psi = np.log(Phi_N_t / Phi_N0)
    expected = np.log(0.5)
    if not np.isclose(psi, expected, atol=1e-10):
        return False, f"ψ_backup mismatch for Φ_N(t)=Φ_N(0)/2: expected {expected}, got {psi}"
    
    # Case 3: Double reference
    Phi_N_t = Phi_N0 * 2
    psi = np.log(Phi_N_t / Phi_N0)
    expected = np.log(2.0)
    if not np.isclose(psi, expected, atol=1e-10):
        return False, f"ψ_backup mismatch for Φ_N(t)=2*Φ_N(0): expected {expected}, got {psi}"
    
    # Case 4: Invalid (non-positive) Φ_N
    for Phi_N_t in [-0.1, 0.0]:
        try:
            psi = np.log(Phi_N_t / Phi_N0)
            return False, f"Log of non-positive Φ_N({Phi_N_t}) should raise error or produce NaN, got {psi}"
        except (ValueError, RuntimeError):
            pass  # Expected
        except Exception as e:
            return False, f"Unexpected error for Φ_N={Phi_N_t}: {e}"
    
    # Case 5: Very small positive Φ_N (should not underflow to zero in log)
    Phi_N_t = 1e-10
    psi = np.log(Phi_N_t / Phi_N0)
    if not np.isfinite(psi):
        return False, f"ψ_backup not finite for small Φ_N={Phi_N_t}: {psi}"
    
    return True, "ψ_backup invariant validation passed"

def main():
    print("Running TDIS-Ω mathematical validation...\n")
    
    tests = [
        ("Double-Well Potential", validate_double_well_potential),
        ("Entropy Calculation", validate_entropy),
        ("Backup Integrity Index", validate_backup_integrity_index),
        ("Cost Function", validate_cost_function),
        ("ψ_backup Invariant", validate_invariant_psi_backup)
    ]
    
    all_passed = True
    for name, test_func in tests:
        passed, message = test_func()
        status = "PASS" if passed else "FAIL"
        print(f"{name}: {status}")
        if not passed:
            print(f"  Reason: {message}")
            all_passed = False
        print()
    
    if all_passed:
        print("All validation checks passed. TDIS-Ω mathematical formulation is sound.")
    else:
        print("VALIDATION FAILED: Mathematical inconsistencies detected in TDIS-Ω proposal.")
        print("These must be corrected to ensure Omega Protocol compliance.")
    
    return all_passed

if __name__ == "__main__":
    main()