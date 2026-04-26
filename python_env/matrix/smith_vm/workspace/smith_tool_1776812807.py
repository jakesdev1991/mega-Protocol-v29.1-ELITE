# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import math
import numpy as np
from typing import Dict, List, Tuple

def validate_bts_omega(
    V: int,
    E: int,
    F: int,
    num_enforced: int,
    num_possible: int,
    d_norm: int,
    subsystem_data: Dict[str, List[float]],
    kappa_1: float = 1.0,
    kappa_2: float = 0.0,
    kappa_3: float = 1.0,
    kappa_4: float = 0.0,
    Phi_N0: float = 1.0,
    S_low: float = 0.0,
    S_high: float = 10.0,
    n_bins: int = 10
) -> bool:
    """
    Validate compliance of BTS-Ω proposal with Omega Protocol invariants.
    
    Checks:
    1. Covariant modes derived from Hessian of double-well potential
    2. Invariant ψ_bts = ln(Φ_N/Φ_N⁰) is well-defined
    3. Entropy gauge is Shannon conditional entropy
    4. Boundary conditions align with thermodynamics
    5. MPC-Ω constraints satisfied
    
    Parameters:
    -----------
    V, E, F : int
        Schema graph: V=tables (vertices), E=foreign keys (edges), F=query cycles (faces)
    num_enforced, num_possible : int
        Biological constraints: enforced vs. possible
    d_norm : int
        Normalization depth (BCNF level)
    subsystem_data : dict
        Maps subsystem type (e.g., 'genomic') to list of BTFI_original values
    kappa_1, kappa_2, kappa_3, kappa_4 : float
        Scaling constants for covariant modes (must ensure non-negative squares)
    Phi_N0 : float
        Reference value for robust network (Φ_N⁰ > 0)
    S_low, S_high : float
        Entropy bounds for MPC-Ω (0 ≤ S_low ≤ S_high)
    n_bins : int
        Number of bins for BTFI histogram in entropy calculation
    
    Returns:
    --------
    bool: True if all Omega Protocol invariants satisfied, False otherwise
    """
    
    # === STEP 1: Validate inputs ===
    if V <= 0:
        raise ValueError("V (number of tables) must be positive")
    if num_possible <= 0:
        raise ValueError("num_possible (possible constraints) must be positive")
    if d_norm <= 0:
        raise ValueError("d_norm (normalization depth) must be positive")
    if not (0 <= S_low <= S_high):
        raise ValueError("Entropy bounds must satisfy 0 ≤ S_low ≤ S_high")
    if Phi_N0 <= 0:
        raise ValueError("Reference Phi_N0 must be positive")
    if kappa_1 < 0 or kappa_2 < 0 or kappa_3 < 0 or kappa_4 < 0:
        raise ValueError("Scaling constants kappa_i must be non-negative")
    
    # === STEP 2: Compute topological invariants ===
    chi_schema = V - E + F  # Euler characteristic
    term1 = abs(chi_schema) / V  # |χ|/V
    
    Delta_constraint = num_enforced / num_possible  # Constraint satisfaction gap
    term2 = Delta_constraint * (1.0 / d_norm)  # Δ_constraint * (1/d_norm)
    
    BTFI_original = term1 * term2  # Original BTFI definition: (|χ|/V) * Δ * (1/d_norm)
    
    # === STEP 3: Compute covariant modes from Hessian ===
    # Double-well potential: V(B) = (α/2)B² + (β/4)B⁴ - γB
    # Hessian eigenvalues at metastable minima:
    omega_N_sq = kappa_1 * term1 + kappa_2  # ω_N² = κ₁(|χ|/V) + κ₂
    omega_Delta_sq = kappa_3 * term2 + kappa_4  # ω_Δ² = κ₃(Δ·(1/d_norm)) + κ₄
    
    # Non-negativity check (required for real square roots)
    if omega_N_sq < 0 or omega_Delta_sq < 0:
        return False
    
    Phi_N = math.sqrt(omega_N_sq)  # Φ_N = √(ω_N²)
    Phi_Delta = math.sqrt(omega_Delta_sq)  # Φ_Δ = √(ω_Δ²)
    
    # === STEP 4: Validate invariant ψ_bts ===
    if Phi_N <= 0:
        return False  # ln(Φ_N/Φ_N⁰) undefined
    psi_bts = math.log(Phi_N / Phi_N0)  # ψ_bts = ln(Φ_N/Φ_N⁰)
    # Note: ψ_bts is used in boundary conditions but not directly constrained here
    
    # === STEP 5: Compute Shannon conditional entropy ===
    total_samples = 0
    subsystem_weights = {}  # p(s) for each subsystem type
    entropy_per_subsystem = {}  # H(BTFI|s) for each subsystem
    
    for s, btfi_list in subsystem_data.items():
        if not btfi_list:
            continue  # Skip empty subsystems
        total_samples += len(btfi_list)
    
    if total_samples == 0:
        # No data: entropy undefined, treat as invalid
        return False
    
    for s, btfi_list in subsystem_data.items():
        n_s = len(btfi_list)
        p_s = n_s / total_samples
        subsystem_weights[s] = p_s
        
        # Create histogram of BTFI_original values in [0, 1] (clamped for safety)
        clamped_btfi = [max(0.0, min(1.0, x)) for x in btfi_list]
        hist, bin_edges = np.histogram(clamped_btfi, bins=n_bins, range=(0, 1), density=False)
        probs = hist / n_s  # p(k|s)
        
        # Shannon entropy: H = -∑ p(k|s) ln p(k|s) (0*ln0 = 0)
        entropy_s = 0.0
        for p in probs:
            if p > 0:
                entropy_s -= p * math.log(p)
        entropy_per_subsystem[s] = entropy_s
    
    # Weighted sum: S_bts = ∑_s p(s) H(BTFI|s)
    S_bts = sum(subsystem_weights[s] * entropy_per_subsystem[s] for s in subsystem_weights)
    
    # === STEP 6: Validate MPC-Ω constraints ===
    # From repaired proposal: 
    #   BTFI ≤ 0.7, Φ_N ≥ 0.6, S_low ≤ S_bts ≤ S_high
    if BTFI_original > 0.7:
        return False
    if Phi_N < 0.6:
        return False
    if not (S_low <= S_bts <= S_high):
        return False
    
    # === STEP 7: Validate boundary conditions (thermodynamic consistency) ===
    # Shredding Event: ψ_bts → +∞ when Φ_N → ∞ AND S_bts → S_max (high entropy)
    # Informational Freeze: ψ_bts → -∞ when Φ_N → 0 AND S_bts → 0 (low entropy)
    # We check that extreme values align with entropy extremes:
    if Phi_N > 10 * Phi_N0:  # Approximating Φ_N → ∞
        if S_bts < 0.9 * S_high:  # Should be near maximum entropy
            return False
    if Phi_N < 0.1 * Phi_N0:  # Approximating Φ_N → 0
        if S_bts > 0.1 * (S_high - S_low) + S_low:  # Should be near minimum entropy
            return False
    
    # All checks passed
    return True

# Example usage with synthetic data (would be replaced with real leak analysis)
if __name__ == "__main__":
    # Example: Genomic database leak
    V, E, F = 50, 120, 30  # Tables, foreign keys, query cycles
    num_enforced, num_possible = 45, 60  # Enforced vs. possible biological constraints
    d_norm = 3  # BCNF level
    
    # Subsystem BTFI data (simulated)
    subsystem_data = {
        'genomic': [0.2, 0.3, 0.25, 0.18, 0.22],
        'proteomic': [0.4, 0.35, 0.45, 0.3, 0.4],
        'clinical': [0.1, 0.15, 0.08, 0.12, 0.09]
    }
    
    # Validate with default parameters
    is_compliant = validate_bts_omega(
        V, E, F, num_enforced, num_possible, d_norm,
        subsystem_data,
        kappa_1=0.8, kappa_2=0.1,  # Ensures ω_N² > 0
        kappa_3=0.7, kappa_4=0.05, # Ensures ω_Δ² > 0
        Phi_N0=1.0,
        S_low=0.5, S_high=2.0,    # Entropic bounds (nats)
        n_bins=5
    )
    
    print(f"BTS-Ω proposal compliant: {is_compliant}")
    if is_compliant:
        print("All Omega Protocol invariants satisfied.")
    else:
        print("Invariant violation detected.")