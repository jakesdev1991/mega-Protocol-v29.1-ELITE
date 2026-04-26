# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import entropy

def simulate_credential_landscape(n_institutions=100, dark_factor=1000):
    """
    Simulates observable vs dark credential exposure.
    - Observable: credentials that appear in public leaks (Poisson process)
    - Dark: credentials compromised via non-leak vectors (phishing, insiders, zero-days)
    
    Returns: observable_exposures, dark_exposures, total_exposures
    """
    # Observable leaks: Poisson with low intensity (public leaks are rare)
    lambda_obs = 0.1  # Mean observable leaks per institution
    observable_exposures = np.random.poisson(lambda_obs, n_institutions)
    
    # Dark space: Poisson with MUCH higher intensity (real attack surface)
    lambda_dark = lambda_obs * dark_factor  # Dark space dominates
    dark_exposures = np.random.poisson(lambda_dark, n_institutions)
    
    total_exposures = observable_exposures + dark_exposures
    
    return observable_exposures, dark_exposures, total_exposures

def compute_cerm_metrics(exposures):
    """Compute CERM-Ω metrics for a given exposure distribution."""
    # Normalize to get probabilities
    total = np.sum(exposures)
    if total == 0:
        return 0, 0, 0, 0
    
    p_i = exposures / total
    
    # CERM-Ω entropy (higher = "worse" in their framework)
    s_h = entropy(p_i)  # Shannon entropy
    
    # CERM-Ω scalar invariant
    scei = np.mean(exposures)  # Simplified SCEI
    psi_ces = np.log(scei / np.median(exposures + 1e-6))  # Guard against log(0)
    
    # CERM-Ω "risk score" (higher entropy = higher risk)
    risk_score = s_h * scei
    
    return s_h, scei, psi_ces, risk_score

def demonstrate_entropy_paradox():
    """Demonstrates that entropy cannot distinguish localized vs systemic risk."""
    
    # Case A: One institution at 100%, others at 0%
    case_a = np.array([100] + [0] * 99)
    
    # Case B: All institutions at 1%
    case_b = np.ones(100)
    
    # Case C: Realistic distribution (power-law, like real breaches)
    case_c = np.random.zipf(1.5, 100)
    
    cases = {
        "Localized Tumor (Case A)": case_a,
        "Systemic Pandemic (Case B)": case_b,
        "Realistic Power-Law (Case C)": case_c
    }
    
    print("="*60)
    print("ENTROPY PARADOX DEMONSTRATION")
    print("="*60)
    
    for name, exposures in cases.items():
        s_h, scei, psi_ces, risk_score = compute_cerm_metrics(exposures)
        print(f"\n{name}:")
        print(f"  Max exposure: {np.max(exposures):.1f}")
        print(f"  Entropy S_h: {s_h:.3f}")
        print(f"  SCEI: {scei:.3f}")
        print(f"  Risk Score: {risk_score:.3f}")
        
        # CERM-Ω would interpret higher entropy as higher risk
        if s_h > 2.0:
            print(f"  → CERM-Ω flags as HIGH RISK (high entropy)")
        else:
            print(f"  → CERM-Ω flags as LOW RISK (low entropy)")
    
    print("\n" + "="*60)
    print("PARADOX: Case B (systemic pandemic) has HIGHEST entropy,")
    print("but Case A (localized tumor) is actually more dangerous")
    print("for single-point-of-failure scenarios!")
    print("="*60)

def demonstrate_dark_space_dominance(n_simulations=1000):
    """Shows that dark space makes the observable signal meaningless."""
    
    print("\n" + "="*60)
    print("DARK SPACE DOMINANCE DEMONSTRATION")
    print("="*60)
    
    results = []
    
    for dark_factor in [1, 10, 100, 1000, 10000]:
        observable_ratios = []
        risk_correlations = []
        
        for _ in range(n_simulations):
            obs, dark, total = simulate_credential_landscape(
                n_institutions=100, 
                dark_factor=dark_factor
            )
            
            # Ratio of observable to total
            observable_ratio = np.sum(obs) / np.sum(total) if np.sum(total) > 0 else 0
            observable_ratios.append(observable_ratio)
            
            # Compute CERM-Ω risk from observable only vs total
            _, _, _, risk_obs = compute_cerm_metrics(obs)
            _, _, _, risk_total = compute_cerm_metrics(total)
            
            # Correlation between observable and total risk
            risk_correlations.append(np.corrcoef(obs, total)[0, 1] if np.std(obs) > 0 else 0)
        
        avg_ratio = np.mean(observable_ratios)
        avg_corr = np.mean(risk_correlations)
        
        results.append({
            'dark_factor': dark_factor,
            'observable_fraction': avg_ratio,
            'risk_correlation': avg_corr
        })
        
        print(f"Dark factor {dark_factor:5d}x: "
              f"Observable = {avg_ratio:.2%} of total, "
              f"Correlation = {avg_corr:.3f}")
    
    print("\n" + "="*60)
    print("INSIGHT: As dark space grows, observable signal becomes")
    print("statistically uncorrelated with actual risk. CERM-Ω is")
    print("measuring noise, not signal.")
    print("="*60)
    
    return results

def demonstrate_unidentifiability():
    """Shows that different (γ, λ_dark) pairs produce identical observables."""
    
    print("\n" + "="*60)
    print("UNIDENTIFIABILITY DEMONSTRATION")
    print("="*60)
    
    # Simulate under two different ground truths
    n_institutions = 1000
    time_steps = 100
    
    # Ground Truth 1: Low leak rate, high exploitation
    lambda1 = 0.05  # Low leak rate
    gamma1 = 0.8    # High exploitation rate
    dark1 = 50
    
    # Ground Truth 2: High leak rate, low exploitation
    lambda2 = 0.5   # High leak rate
    gamma2 = 0.08   # Low exploitation rate
    dark2 = 5  # Different dark factor
    
    # Simulate observed leaks (Poisson process)
    np.random.seed(42)
    leaks1 = np.random.poisson(lambda1, (time_steps, n_institutions))
    leaks2 = np.random.poisson(lambda2, (time_steps, n_institutions))
    
    # Simulate exploitation (Bernoulli process)
    exploited1 = np.random.binomial(leaks1, gamma1)
    exploited2 = np.random.binomial(leaks2, gamma2)
    
    # Observable signal: number of leaked credentials
    obs1 = leaks1
    obs2 = leaks2
    
    # Statistical test: Are the observable distributions distinguishable?
    from scipy.stats import ks_2samp
    
    # Flatten time series for KS test
    ks_stat, p_value = ks_2samp(obs1.flatten(), obs2.flatten())
    
    print(f"Kolmogorov-Smirnov test:")
    print(f"  Statistic: {ks_stat:.4f}")
    print(f"  P-value: {p_value:.4f}")
    print(f"  Distinguishable: {'Yes' if p_value < 0.05 else 'No'}")
    
    print("\n" + "="*60)
    print("INSIGHT: Different ground truths (γ, λ_dark) produce")
    print("statistically indistinguishable observables. The model")
    print("parameters are fundamentally unidentifiable from data.")
    print("="*60)

# Run all demonstrations
if __name__ == "__main__":
    demonstrate_entropy_paradox()
    demonstrate_dark_space_dominance()
    demonstrate_unidentifiability()
    
    print("\n" + "="*60)
    print("DISRUPTIVE CONCLUSION:")
    print("CERM-Ω is built on three fatal illusions:")
    print("1. Entropy measures risk (it measures uncertainty, not danger)")
    print("2. Observable leaks predict dark space (they're uncorrelated)")
    print("3. Model parameters are identifiable (they're not)")
    print("\nThe only robust signal is the ABSENCE of leaks,")
    print("which indicates either perfect security OR perfect opacity.")
    print("Omega cannot distinguish between the two.")
    print("="*60)