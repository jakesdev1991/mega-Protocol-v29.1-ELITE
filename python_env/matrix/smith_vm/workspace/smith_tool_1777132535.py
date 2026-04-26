# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import math
import numpy as np

def validate_avri_v64(state):
    """
    Validates the AVRI-v64.0 proposal against Omega Protocol invariants.
    
    Args:
        state (dict): Contains:
            - intel_state: np.array (intellectual validation vector)
            - sub_state: np.array (subconscious reality vector)
            - xi_intel: float (intellectual stiffness)
            - xi_sub: float (subconscious capacity)
            - z_env: float (environmental impedance)
            - h_super: float (superentropy)
            - h_dis: float (dissonance entropy)
            - z_trust: float (trust baseline for stiffness)
    
    Returns:
        tuple: (is_compliant: bool, phi_net: float or None, error_msg: str)
               is_compliant=True only if all invariants hold and math is sound.
               phi_net is the computed net Φ-density if valid.
               error_msg explains failure if any.
    """
    try:
        # --- Step 1: Compute COD (Chain Overlap Density) ---
        intel_state = np.array(state['intel_state'], dtype=float)
        sub_state = np.array(state['sub_state'], dtype=float)
        
        # Handle zero vectors
        norm_intel = np.linalg.norm(intel_state)
        norm_sub = np.linalg.norm(sub_state)
        if norm_intel == 0 or norm_sub == 0:
            fidelity = 0.0
        else:
            dot_product = np.dot(intel_state, sub_state)
            fidelity = (dot_product / (norm_intel * norm_sub)) ** 2
            fidelity = max(0.0, min(1.0, fidelity))  # Clamp to [0,1]
        
        # Environmental and stiffness penalties (from AVO v64.0 pseudocode)
        env_penalty = math.exp(-0.5 * state['z_env'])
        stiffness_penalty = math.exp(-0.5 * state['xi_intel'])
        cod = fidelity * env_penalty * stiffness_penalty
        cod = max(0.0, min(1.0, cod))  # Final clamp
        
        # --- Step 2: Compute Φ_N (Identity Density) ---
        # Hard floor COD ≥ 0.39 to prevent log singularity (per proposal)
        phi_N = math.log2(max(cod, 0.39) + 1e-9)
        
        # --- Step 3: Compute ψ (Identity Continuity) ---
        # Mandatory coupling: ψ = ln(Φ_N + ε)
        psi_arg = phi_N + 1e-9
        if psi_arg <= 0:
            return (False, None, f"ψ calculation failed: phi_N + 1e-9 = {psi_arg} ≤ 0")
        psi = math.log(psi_arg)  # Natural log
        
        # --- Step 4: Compute Φ_Δ (Adaptation Asymmetry) ---
        R_align = abs(state['xi_sub'] - state['xi_intel'])
        R_max = 2.8
        phi_Delta = psi * math.tanh(R_align / R_max)
        
        # --- Step 5: Compute Net Φ-Density (with Audit Cost) ---
        delta_S_audit = math.log(2) * 7  # Landauer bound for 7 invariants
        phi_net = phi_N + phi_Delta - delta_S_audit
        
        # --- Step 6: Enforce Smith Audit Invariants (Hard Gates) ---
        # Invariant 1: COD ≥ 0.85 (Alignment Fidelity)
        if cod < 0.85:
            return (False, phi_net, f"Invariant 1 violated: COD = {cod:.4f} < 0.85")
        
        # Invariant 2: H_super in healthy band [0.15, 0.80]
        h_super = state['h_super']
        if h_super < 0.15 or h_super > 0.80:
            return (False, phi_net, f"Invariant 2 violated: H_super = {h_super:.4f} ∉ [0.15, 0.80]")
        
        # Invariant 3: H_dis ≤ 0.3 (Dissonance Cap)
        h_dis = state['h_dis']
        if h_dis > 0.3:
            return (False, phi_net, f"Invariant 3 violated: H_dis = {h_dis:.4f} > 0.3")
        
        # Invariant 4: Ξ_intel ≤ Z_trust + 0.1 (Stiffness Matching)
        xi_intel = state['xi_intel']
        z_trust = state['z_trust']
        if xi_intel > z_trust + 0.1:
            return (False, phi_net, f"Invariant 4 violated: Ξ_intel = {xi_intel:.4f} > Z_trust + 0.1 = {z_trust + 0.1:.4f}")
        
        # Invariant 5: Z_env ≤ 0.7 (Environmental Impedance Cap)
        z_env = state['z_env']
        if z_env > 0.7:
            return (False, phi_net, f"Invariant 5 violated: Z_env = {z_env:.4f} > 0.7")
        
        # Invariant 6: Φ_Δ < 0.5 · Φ_N (Asymmetry Control)
        if phi_Delta >= 0.5 * phi_N:
            return (False, phi_net, f"Invariant 6 violated: Φ_Δ = {phi_Delta:.4f} ≥ 0.5·Φ_N = {0.5 * phi_N:.4f}")
        
        # All invariants passed
        return (True, phi_net, "All Omega Protocol invariants satisfied")
    
    except ValueError as e:
        return (False, None, f"Math domain error: {str(e)}")
    except Exception as e:
        return (False, None, f"Unexpected error: {str(e)}")

# --- Example Usage: Test with a state that should be valid per proposal claims ---
if __name__ == "__main__":
    # State designed to meet invariants (based on proposal's net gain claim)
    test_state = {
        'intel_state': np.array([0.99, 0.1]),  # Near-aligned intellectual vector
        'sub_state': np.array([0.98, 0.2]),    # Near-aligned subconscious vector
        'xi_intel': 0.25,                      # Intellectual stiffness
        'xi_sub': 0.30,                        # Subconscious capacity
        'z_env': 0.5,                          # Environmental impedance
        'h_super': 0.5,                        # Superentropy (healthy band)
        'h_dis': 0.2,                          # Dissonance entropy
        'z_trust': 0.2                         # Trust baseline
    }
    
    is_compliant, phi_net, msg = validate_avri_v64(test_state)
    print(f"Compliant: {is_compliant}")
    print(f"Phi-net: {phi_net:.4f} Φ" if phi_net is not None else "Phi-net: N/A")
    print(f"Message: {msg}")
    
    # --- Test the mathematical flaw: Try a state with COD=0.85 (minimum for Invariant 1) ---
    # We'll adjust states to get COD≈0.85
    test_state_marginal = {
        'intel_state': np.array([0.9, 0.0]),
        'sub_state': np.array([0.85, 0.0]),
        'xi_intel': 0.1,
        'xi_sub': 0.2,
        'z_env': 0.1,
        'h_super': 0.5,
        'h_dis': 0.2,
        'z_trust': 0.15
    }
    
    is_compliant2, phi_net2, msg2 = validate_avri_v64(test_state_marginal)
    print("\n--- Marginal COD Test (COD≈0.85) ---")
    print(f"Compliant: {is_compliant2}")
    print(f"Phi-net: {phi_net2:.4f} Φ" if phi_net2 is not None else "Phi-net: N/A (Math Error)")
    print(f"Message: {msg2}")
    
    # --- Test the core mathematical flaw: Show why psi calculation fails for COD<~0.999999 ---
    print("\n--- Mathematical Flaw Demonstration ---")
    cod_values = [0.99, 0.999, 0.9999, 0.99999, 0.999999, 0.9999999]
    for cod in cod_values:
        # Compute phi_N as in the proposal
        phi_N = math.log2(max(cod, 0.39) + 1e-9)
        psi_arg = phi_N + 1e-9
        if psi_arg <= 0:
            print(f"COD={cod}: phi_N={phi_N:.6f}, psi_arg={psi_arg:.2e} → INVALID (log of non-positive)")
        else:
            psi_val = math.log(psi_arg)
            print(f"COD={cod}: phi_N={phi_N:.6f}, psi_arg={psi_arg:.2e}, ψ={psi_val:.4f} → VALID")