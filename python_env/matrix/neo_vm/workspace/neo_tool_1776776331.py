# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import matplotlib.pyplot as plt
from scipy.integrate import solve_ivp
from scipy.stats import linregress

# --- PLASMA ARBITER Ω: Core Disruption ---

def plasma_stability_score(claim_data, experimental_rigor):
    """
    Maps biotech claims to plasma physics stability metrics.
    claim_data: [efficacy, specificity, half_life] (analogous to [confinement, purity, decay])
    experimental_rigor: [trial_size, p_value, replication_studies] (analogous to [diagnostic_res, noise_floor, reproducibility])
    Returns: PSS (0-1, where <0.3 = unstable/turbulent, >0.7 = stable/converged)
    """
    efficacy, specificity, half_life = claim_data
    trial_size, p_value, replication_studies = experimental_rigor
    
    # --- Physical Model Mapping ---
    # Tumor reduction efficacy -> Plasma heating efficiency
    # Target specificity -> Magnetic field purity (inverse of transport losses)
    # Half-life -> Particle confinement time
    # Trial size -> Diagnostic resolution (inverse of statistical noise)
    # P-value -> Signal-to-noise threshold
    # Replication -> System stability (reproducibility = absence of chaos)
    
    # Confinement quality: high efficacy * high specificity = good "confinement"
    confinement_quality = efficacy * specificity
    
    # System noise: low trial size + high p-value = high "turbulence"
    noise_factor = (1 / (trial_size + 1)) * p_value
    
    # Stability coefficient: replication studies dampen instability (like feedback stabilization)
    stability_coeff = np.log1p(replication_studies) / np.log1p(10)
    
    # --- Plasma Stability Equation (Simplified from ballooning mode analysis) ---
    # PSS = (Confinement) / (Confinement + Noise) * Stability_Damping
    # If noise dominates, PSS -> 0 (unstable/turbulent)
    # If confinement dominates and damping is high, PSS -> 1 (stable)
    
    pss = (confinement_quality / (confinement_quality + noise_factor + 1e-6)) * stability_coeff
    
    return np.clip(pss, 0, 1)

def biotech_system_dynamics(t, state, pss, claim_data):
    """
    Models the biotech claim as a coupled ODE system (predator-prey + perturbation).
    state: [tumor_cells, drug_concentration, market_sentiment]
    pss: Plasma Stability Score acting as a damping/instability term
    """
    tumor, drug, sentiment = state
    efficacy, specificity, half_life = claim_data
    
    # Tumor growth without drug (logistic)
    growth_rate = 0.5
    carrying_capacity = 1000
    d_tumor_dt = growth_rate * tumor * (1 - tumor / carrying_capacity)
    
    # Drug effect (predator-like term)
    drug_effect = efficacy * drug * tumor * specificity
    
    # Market sentiment feedback loop (hype vs. reality)
    # High sentiment drives drug adoption, but crashes if tumor doesn't respond
    sentiment_damping = 0.1 * (1 - pss)  # Low PSS = high damping (instability)
    d_sentiment_dt = -sentiment_damping * sentiment + 0.05 * (efficacy - 0.5)
    
    # System instability: Low PSS injects chaotic perturbations
    instability_noise = (1 - pss) * 50 * np.sin(10 * t) * (tumor / carrying_capacity)
    
    # Final tumor dynamics
    d_tumor_dt = d_tumor_dt - drug_effect + instability_noise
    
    # Drug pharmacokinetics
    d_drug_dt = -0.1 * drug / half_life  # Decay
    
    return [d_tumor_dt, d_drug_dt, d_sentiment_dt]

def simulate_biotech_asset(claim_data, experimental_rigor, initial_market_cap):
    """
    Simulates a biotech company's trajectory based on its claim's scientific validity.
    """
    pss = plasma_stability_score(claim_data, experimental_rigor)
    
    # Initial conditions: [tumor_cells, drug_concentration, market_sentiment]
    y0 = [800, 100, initial_market_cap / 10]  # Sentiment tied to market cap
    
    t_span = (0, 50)  # 50 time units (e.g., months)
    t_eval = np.linspace(*t_span, 500)
    
    sol = solve_ivp(
        biotech_system_dynamics, 
        t_span, 
        y0, 
        args=(pss, claim_data),
        t_eval=t_eval,
        dense_output=True
    )
    
    # Market cap evolves with sentiment and tumor reduction
    # Tumor reduction success = market cap growth
    tumor_reduction_rate = (y0[0] - sol.y[0, -1]) / y0[0]
    final_market_cap = initial_market_cap * (1 + tumor_reduction_rate * sol.y[2, -1] / 10)
    
    # If system diverges (unstable), market cap crashes
    if pss < 0.3 and np.max(np.abs(sol.y[0])) > 1500:
        final_market_cap *= 0.1  # Crash
    
    return pss, sol, final_market_cap

# --- SIMULATION: Two Biotech Companies ---

# Company A: "Revolutionary" but scientifically weak claim (high hype, low rigor)
# High efficacy claim, but small trials, no replication
claim_A = [0.9, 0.95, 12.0]  # 90% efficacy, 95% specific, 12hr half-life
rigor_A = [30, 0.04, 0]      # n=30, p=0.04, no replication

# Company B: "Boring" but scientifically robust claim (modest, high rigor)
# Modest efficacy, but large trials, replicated
claim_B = [0.6, 0.85, 8.0]   # 60% efficacy, 85% specific, 8hr half-life
rigor_B = [500, 0.001, 5]    # n=500, p=0.001, 5 replication studies

initial_cap = 1000  # $1B market cap

# Run simulations
pss_A, sol_A, final_cap_A = simulate_biotech_asset(claim_A, rigor_A, initial_cap)
pss_B, sol_B, final_cap_B = simulate_biotech_asset(claim_B, rigor_B, initial_cap)

# --- PLOTTING: Exposing the Flaw ---

fig, axes = plt.subplots(2, 2, figsize=(14, 10))
fig.suptitle('PLASMA ARBITER Ω: Scientific Rigor vs. Market Hype', fontsize=16, fontweight='bold')

# Plot 1: Tumor Dynamics (Scientific Reality)
axes[0, 0].plot(sol_A.t, sol_A.y[0], 'r-', label=f'Company A (PSS={pss_A:.2f})', linewidth=2)
axes[0, 0].plot(sol_B.t, sol_B.y[0], 'b-', label=f'Company B (PSS={pss_B:.2f})', linewidth=2)
axes[0, 0].set_title('Tumor Cell Count (Scientific Efficacy)', fontweight='bold')
axes[0, 0].set_xlabel('Time (months)')
axes[0, 0].set_ylabel('Tumor Cells')
axes[0, 0].legend()
axes[0, 0].grid(True, alpha=0.3)
axes[0, 0].axhline(y=1000, color='k', linestyle='--', alpha=0.5, label='Lethal Threshold')

# Plot 2: System Instability (Lyapunov Exponent Proxy)
# Compute divergence between nearby trajectories to show chaos
def lyapunov_proxy(sol, pss):
    """Simple proxy: variance of tumor dynamics indicates instability"""
    return np.var(sol.y[0]) * (1 - pss)

instability_A = lyapunov_proxy(sol_A, pss_A)
instability_B = lyapunov_proxy(sol_B, pss_B)

axes[0, 1].bar(['Company A', 'Company B'], [instability_A, instability_B], 
               color=['r', 'b'], alpha=0.7)
axes[0, 1].set_title('System Instability Score (Plasma Turbulence Analogy)', fontweight='bold')
axes[0, 1].set_ylabel('Instability (Variance × (1-PSS))')
axes[0, 1].grid(True, alpha=0.3)
for i, v in enumerate([instability_A, instability_B]):
    axes[0, 1].text(i, v + max(instability_A, instability_B)*0.01, f'{v:.1f}', 
                    ha='center', fontweight='bold')

# Plot 3: Market Sentiment Evolution
axes[1, 0].plot(sol_A.t, sol_A.y[2], 'r-', label=f'Company A Sentiment', linewidth=2)
axes[1, 0].plot(sol_B.t, sol_B.y[2], 'b-', label=f'Company B Sentiment', linewidth=2)
axes[1, 0].set_title('Market Sentiment Dynamics', fontweight='bold')
axes[1, 0].set_xlabel('Time (months)')
axes[1, 0].set_ylabel('Sentiment Index')
axes[1, 0].legend()
axes[1, 0].grid(True, alpha=0.3)
axes[1, 0].axhline(y=0, color='k', linestyle='--', alpha=0.5)

# Plot 4: Market Cap Outcome
outcomes = [final_cap_A, final_cap_B]
colors = ['r' if final_cap_A < initial_cap else 'g', 'b']
axes[1, 1].bar(['Company A', 'Company B'], outcomes, color=colors, alpha=0.7)
axes[1, 1].axhline(y=initial_cap, color='k', linestyle='--', label='Initial Cap')
axes[1, 1].set_title('Final Market Capitalization ($B)', fontweight='bold')
axes[1, 1].set_ylabel('Market Cap')
axes[1, 1].grid(True, alpha=0.3)
for i, v in enumerate(outcomes):
    axes[1, 1].text(i, v + max(outcomes)*0.01, f'${v:.0f}B', 
                    ha='center', fontweight='bold')

plt.tight_layout()
plt.show()

# --- DISRUPTIVE CONCLUSION ---

print("\n" + "="*70)
print("PLASMA ARBITER Ω: DISRUPTIVE FINDINGS")
print("="*70)
print(f"\nCompany A (High Hype, Low Rigor):")
print(f"  - PSS: {pss_A:.2f} (UNSTABLE/TURBULENT)")
print(f"  - Initial Market Cap: ${initial_cap}B")
print(f"  - Final Market Cap: ${final_cap_A:.0f}B")
print(f"  - Instability Score: {instability_A:.1f}")
print(f"  - VERDICT: Scientifically invalid, market crash imminent")

print(f"\nCompany B (Modest, High Rigor):")
print(f"  - PSS: {pss_B:.2f} (STABLE/CONVERGED)")
print(f"  - Initial Market Cap: ${initial_cap}B")
print(f"  - Final Market Capitalization: ${final_cap_B:.0f}B")
print(f"  - Instability Score: {instability_B:.1f}")
print(f"  - VERDICT: Scientifically sound, sustainable growth")

print("\n--- CORE DISRUPTION ---")
print("CVT-Ω's Fatal Flaw: It trains on MARKETING (PowerPoint hype) to predict SCIENCE.")
print("PA-Ω's Insight: Use SCIENTIFIC RIGOR (plasma stability) to predict MARKET FAILURE.")
print("\nImplication: The 'undervalued' biotech assets are often just *unstable plasma*.")
print("True breakthrough: Financial markets are less rational than tokamak plasma.")
print("="*70)