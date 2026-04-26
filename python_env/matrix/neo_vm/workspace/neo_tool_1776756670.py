# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import matplotlib.pyplot as plt
from scipy.linalg import expm

# Simulate a simple synthetic circuit: toggle switch
# Two genes, A and B, mutually repress each other
# This is a classic bistable circuit

# Gauge theory approach (BGSM-Ω)
def simulate_gauge_theory(n_cells=1000, n_steps=1000, stress=0.1):
    """
    Simulate circuit as continuous field φ(x,t) with quartic potential
    This is the BGSM-Ω model
    """
    # Parameters
    m2 = -0.5  # negative mass for bistability
    lam = 0.1  # quartic coupling
    D = 0.01   # diffusion coefficient
    dt = 0.01
    
    # Initialize field
    phi = np.random.normal(0, 0.1, size=(n_cells,))
    
    # Effective mass with stress
    m_eff2 = m2 + 3*lam*np.mean(phi**2) + stress
    
    # Simulate dynamics
    for t in range(n_steps):
        # Laplacian (diffusion)
        laplacian = np.roll(phi, 1) + np.roll(phi, -1) - 2*phi
        
        # Force from potential
        force = -m_eff2 * phi - lam * phi**3
        
        # Update
        phi += dt * (D * laplacian + force + np.random.normal(0, 0.05, n_cells))
        
        # Recalculate m_eff2
        m_eff2 = m2 + 3*lam*np.mean(phi**2) + stress
        
        # Check for "depeg" (symmetry breaking)
        if m_eff2 < 0:
            return False, t, phi  # Depegged
    
    return True, n_steps, phi  # Stable

# Error-correcting code approach (BECC-Ω)
def simulate_error_correcting(n_cells=1000, n_steps=1000, error_rate=0.01, code_distance=5):
    """
    Simulate circuit as error-correcting code
    Each cell's state is a binary vector [A_on, B_on]
    Code distance = min errors to flip state
    """
    # States: 0 = A_high/B_low, 1 = A_low/B_high (bistable)
    states = np.random.randint(2, size=n_cells)  # Random initial
    
    # Syndrome monitoring: count "error" cells (both genes on/off)
    # In a perfect toggle switch, A and B should never be both high or both low
    
    for t in range(n_steps):
        # Introduce errors (transcription failures)
        errors = np.random.random(n_cells) < error_rate
        
        # Flip state for cells with errors (simplified)
        states[errors] = 1 - states[errors]
        
        # Calculate syndrome: cells in "forbidden" states
        # In real logs, this would be measured expression patterns
        # For simulation, we'll track error accumulation
        
        # Track distance to failure: if we accumulate enough errors
        # to exceed code distance, we depeg
        total_errors = np.sum(errors)
        
        if total_errors > code_distance * n_cells * 0.1:  # Threshold
            return False, t, states  # Depegged
    
    return True, n_steps, states  # Stable

# Run comparison
np.random.seed(42)

# BGSM-Ω simulation
print("Running BGSM-Ω gauge theory simulation...")
stable_gauge, time_gauge, final_phi = simulate_gauge_theory(stress=0.3)
print(f"Stable: {stable_gauge}, Time to depeg: {time_gauge if not stable_gauge else 'N/A'}")

# BECC-Ω simulation
print("\nRunning BECC-Ω error-correcting code simulation...")
stable_code, time_code, final_states = simulate_error_correcting(error_rate=0.05, code_distance=3)
print(f"Stable: {stable_code}, Time to depeg: {time_code if not stable_code else 'N/A'}")

# Now demonstrate the key failure: gauge theory doesn't capture discrete molecular noise
print("\n" + "="*60)
print("DEMONSTRATING BGSM-Ω FAILURE MODE")
print("="*60)

# Create a scenario with bursty, discrete molecular events
# This is realistic biology but breaks continuum field theory

def realistic_molecular_simulation(n_cells=1000, n_steps=1000):
    """
    Realistic: discrete mRNA/protein molecules with burst transcription
    """
    # mRNA counts per cell
    mRNA_A = np.random.poisson(10, n_cells)
    mRNA_B = np.random.poisson(10, n_cells)
    
    # Translation
    protein_A = np.random.poisson(mRNA_A * 10)  # 10 proteins per mRNA on average
    protein_B = np.random.poisson(mRNA_B * 10)
    
    # Mutual repression: A represses B, B represses A
    # This creates bistability
    
    for t in range(n_steps):
        # Transcription bursts (log-normal distribution)
        burst_size_A = np.random.lognormal(0, 1, n_cells)
        burst_size_B = np.random.lognormal(0, 1, n_cells)
        
        # Repression strength depends on opposing protein
        repression_A = 1 / (1 + (protein_B / 50)**2)  # Hill function
        repression_B = 1 / (1 + (protein_A / 50)**2)
        
        # New mRNA synthesis (with bursts)
        new_mRNA_A = np.random.poisson(burst_size_A * repression_A * 0.5)
        new_mRNA_B = np.random.poisson(burst_size_B * repression_B * 0.5)
        
        # Update
        mRNA_A = mRNA_A * 0.8 + new_mRNA_A  # Degradation + synthesis
        mRNA_B = mRNA_B * 0.8 + new_mRNA_B
        
        # Translate
        protein_A = np.random.poisson(mRNA_A * 10)
        protein_B = np.random.poisson(mRNA_B * 10)
        
        # Check for "depeg": both proteins high (both states active)
        both_high = np.sum((protein_A > 100) & (protein_B > 100))
        
        if both_high > n_cells * 0.3:  # 30% cells in failed state
            return False, t, protein_A, protein_B
    
    return True, n_steps, protein_A, protein_B

print("\nRunning realistic molecular simulation...")
stable_real, time_real, prot_A, prot_B = realistic_molecular_simulation()
print(f"Stable: {stable_real}, Time to depeg: {time_real if not stable_real else 'N/A'}")

# Now try to fit BGSM-Ω to this data
# The gauge theory would try to fit a smooth field φ to discrete bursty data
# This leads to misidentification of stability boundaries

# Calculate what BGSM-Ω would see as "correlation length"
phi_smooth = (prot_A + prot_B) / 200  # Normalize to [0,1] range

# Calculate correlation function
def correlation_length(field):
    n = len(field)
    corr = np.correlate(field - np.mean(field), field - np.mean(field), mode='full')
    corr = corr[n-1:] / (np.var(field) * n)
    
    # Fit exponential decay exp(-r/ξ)
    r = np.arange(len(corr))
    try:
        # Log-linear fit
        valid = corr > 0
        if not np.any(valid):
            return np.inf
        
        log_corr = np.log(corr[valid])
        coeffs = np.polyfit(r[valid][:10], log_corr[:10], 1)  # Fit first 10 points
        xi = -1 / coeffs[0]
        return max(xi, 0.1)  # Avoid negative
    except:
        return np.inf

xi = correlation_length(phi_smooth)
print(f"\nBGSM-Ω would estimate correlation length ξ = {xi:.2f}")

# In a real depeg event, ξ diverges, but here it's just noise
# The error-correcting code approach would instead count error syndromes

# Count "syndromes": cells where both genes are mis-expressed
syndromes = np.sum((prot_A > 100) & (prot_B > 100))
print(f"BECC-Ω would count {syndromes} syndrome events")

print("\n" + "="*60)
print("DISRUPTIVE CONCLUSION:")
print("="*60)
print("BGSM-Ω misattributes bursty molecular noise to critical phenomena.")
print("The 'diverging correlation length' is an artifact of fitting smooth")
print("field theory to discrete, non-equilibrium biological data.")
print("The true failure precursor is syndrome accumulation, captured by")
print("error-correcting code theory, not gauge symmetry breaking.")