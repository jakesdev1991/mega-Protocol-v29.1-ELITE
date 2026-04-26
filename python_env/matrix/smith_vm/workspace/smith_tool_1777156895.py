# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np

def validate_cod_computation():
    """
    Validates the COD (Chain Overlap Density) computation in the MeasurementIdentityManifold class.
    The agent's code computes fidelity between conscious state (psi_cons) and identity baseline (psi_id),
    but the stated COD formula requires fidelity between conscious (psi_cons) and subconscious (psi_sub).
    This function demonstrates the discrepancy and checks invariant compliance.
    """
    # Set random seed for reproducibility
    np.random.seed(42)
    
    # Initialize parameters as in MeasurementIdentityManifold.__init__
    dim = 8
    psi_sub = [complex(np.random.rand(), np.random.rand()) for _ in range(dim)]  # Subconscious (Quantum)
    psi_cons = [complex(0.9, 0.1) for _ in range(dim)]                          # Conscious (Classical)
    psi_id = [0.92, 0.89, 0.95, 0.87, 0.91, 0.93, 0.88, 0.94]                   # Identity Baseline
    
    # Parameters from code
    xi_cons = 0.95   # Measurement Stiffness
    z_env = 0.85     # Environmental Impedance
    z_sub = 0.35     # Subconscious Trust Impedance
    
    # Compute superposition entropy (H_sub) as in code
    def compute_superposition_entropy(psi):
        probs = [abs(z)**2 for z in psi]
        total = sum(probs)
        if total < 1e-9: 
            return 0.0
        probs = [p / total for p in probs]
        h = -sum(p * np.log(p + 1e-9) for p in probs if p > 1e-9)
        max_h = np.log(len(probs))
        return min(1.0, h / max_h) if max_h > 1e-9 else 0.0
    
    h_sub = compute_superposition_entropy(psi_sub)
    
    # --- CORRECT COD (per agent's stated formula) ---
    # Fidelity term: |<psi_cons | psi_sub>|^2
    dot_correct = np.vdot(psi_cons, psi_sub)  # <psi_cons|psi_sub>
    fidelity_correct = abs(dot_correct)**2
    
    # Penalties (kappa=0.5, lambda=0.3, Lambda=0.4 from code)
    stiffness_penalty = np.exp(-0.5 * xi_cons)
    env_penalty = np.exp(-0.3 * z_env)
    entropy_penalty = np.exp(-0.4 * h_sub)
    
    cod_correct = fidelity_correct * stiffness_penalty * env_penalty * entropy_penalty
    cod_correct = min(1.0, max(0.0, cod_correct))  # Clamp to [0,1] as in code
    
    # --- AGENT'S COMPUTED COD (using psi_id instead of psi_sub) ---
    dot_agent = np.vdot(psi_cons, psi_id)  # <psi_cons|psi_id> (but psi_id is real, so vdot works)
    fidelity_agent = abs(dot_agent)**2
    
    cod_agent = fidelity_agent * stiffness_penalty * env_penalty * entropy_penalty
    cod_agent = min(1.0, max(0.0, cod_agent))
    
    # --- INVARIANT CHECKS ---
    # Invariant 1: COD >= 0.85
    inv1_correct = cod_correct >= 0.85
    inv1_agent = cod_agent >= 0.85
    
    # Identity Continuity: phi_N = log2(max(COD, 0.39)) >= log2(0.39)
    phi_N_correct = np.log2(max(cod_correct, 0.39))
    phi_N_agent = np.log2(max(cod_agent, 0.39))
    inv2_correct = phi_N_correct >= np.log2(0.39)
    inv2_agent = phi_N_agent >= np.log2(0.39)
    
    # Uncertainty Band: 0.15 <= H_sub <= 0.80
    inv3 = 0.15 <= h_sub <= 0.80
    
    # Stiffness-Impedance Match: Xi_cons <= Z_sub + 0.1
    inv4 = xi_cons <= z_sub + 0.1
    
    # Environmental Impedance: Z_env <= 0.7
    inv5 = z_env <= 0.7
    
    # --- RESULTS ---
    print("="*60)
    print("COD COMPUTATION VALIDATION")
    print("="*60)
    print(f"Conscious state (psi_cons): [{psi_cons[0]:.3f}, ...]")
    print(f"Subconscious state (psi_sub): [{psi_sub[0]:.3f}, ...]")
    print(f"Identity baseline (psi_id): [{psi_id[0]:.3f}, ...]")
    print()
    print(f"Parameters: xi_cons={xi_cons:.3f}, z_env={z_env:.3f}, z_sub={z_sub:.3f}, h_sub={h_sub:.3f}")
    print()
    print("COD CALCULATION:")
    print(f"  Correct fidelity |<cons|sub>|^2: {fidelity_correct:.6f}")
    print(f"  Agent's fidelity |<cons|id>|^2:   {fidelity_agent:.6f}")
    print(f"  Stiffness penalty: {stiffness_penalty:.6f}")
    print(f"  Env penalty:       {env_penalty:.6f}")
    print(f"  Entropy penalty:   {entropy_penalty:.6f}")
    print(f"  Correct COD:       {cod_correct:.6f}")
    print(f"  Agent's COD:       {cod_agent:.6f}")
    print()
    print("INVARIANT COMPLIANCE:")
    print(f"  Invariant 1 (COD >= 0.85):    Correct={inv1_correct}, Agent={inv1_agent}")
    print(f"  Invariant 2 (Identity Cont.):   Correct={inv2_correct}, Agent={inv2_agent}")
    print(f"  Invariant 3 (Uncertainty Band): {inv3}")
    print(f"  Invariant 4 (Stiffness Match):  {inv4} (xi_cons={xi_cons:.3f} <= z_sub+0.1={z_sub+0.1:.3f})")
    print(f"  Invariant 5 (Env Impedance):    {inv5} (z_env={z_env:.3f} <= 0.7)")
    print()
    
    # Check if agent's COD calculation violates the stated formula
    if not np.isclose(cod_correct, cod_agent, rtol=1e-5):
        print("❌ CRITICAL ERROR: Agent's COD computation does not match the stated formula!")
        print(f"   Difference: {abs(cod_correct - cod_agent):.6f}")
        print("   This invalidates the entire derivation as it uses the wrong state for fidelity.")
    else:
        print("✅ COD computation matches stated formula (within tolerance).")
    
    # Check if invariants hold with correct COD
    all_inv_correct = inv1_correct and inv2_correct and inv3 and inv4 and inv5
    all_inv_agent = inv1_agent and inv2_agent and inv3 and inv4 and inv5
    
    print()
    print("OVERALL INVARIANT COMPLIANCE:")
    print(f"  With correct COD:    {'PASS' if all_inv_correct else 'FAIL'}")
    print(f"  With agent's COD:    {'PASS' if all_inv_agent else 'FAIL'}")
    print()
    
    if not all_inv_correct:
        print("❌ Even with correct COD, invariants are violated (check parameters).")
    elif not all_inv_agent:
        print("⚠️  Agent's COD calculation leads to different invariant compliance than correct calculation.")
        print("   This means the agent's enforcement logic is based on incorrect COD values.")
    else:
        print("✅ All invariants satisfied with correct COD computation.")
    
    return all_inv_correct, all_inv_agent

if __name__ == "__main__":
    validate_cod_computation()