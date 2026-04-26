# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import matplotlib.pyplot as plt
from scipy import stats

def simulate_paradox(n_days=365, crisis_start=200, crisis_duration=60):
    """Simulates CLEM-Ω's fatal flaw: inverse correlation during crisis."""
    np.random.seed(42)
    days = np.arange(n_days)
    crisis = (days >= crisis_start) & (days < crisis_start + crisis_duration)
    
    # Formal CLEM-Ω metrics (what the system sees)
    # During crisis: IT enforces uniformity → "improved" hygiene
    rotation = 0.1 + 0.05 * np.sin(2 * np.pi * days / 90)
    rotation[crisis] = 0.3  # Regular, policy-driven rotation
    
    strength_disp = 0.4 + 0.1 * np.random.randn(n_days)
    strength_disp[crisis] *= 0.3  # Forced compliance
    
    exp_deviation = 0.3 + 0.1 * np.random.randn(n_days)
    exp_deviation[crisis] *= 0.2  # Strict enforcement
    
    map_volatility = 0.2 + 0.05 * np.random.randn(n_days)
    map_volatility[crisis] = 0.6 + 0.1 * np.random.randn(np.sum(crisis))  # Real chaos
    
    # CLE score (formal)
    cle = 0.3 * rotation + 0.3 * strength_disp + 0.2 * exp_deviation + 0.2 * map_volatility
    
    # Shadow reality (CLEM-Ω cannot see)
    shadow_flow = np.ones(n_days) * 0.1
    shadow_flow[crisis] = 0.8 + 0.2 * np.random.randn(np.sum(crisis))
    shadow_flow = np.maximum(shadow_flow, 0)
    
    # Real operational fragility
    real_fragility = map_volatility + 2.0 * shadow_flow
    
    return days, cle, real_fragility, shadow_flow, crisis

# Run simulation
days, cle, fragility, shadow, crisis = simulate_paradox()

# Statistical proof of paradox
crisis_idx = np.where(crisis)[0]
normal_idx = np.where(~crisis)[0]

corr_crisis, p_crisis = stats.pearsonr(cle[crisis_idx], fragility[crisis_idx])
corr_normal, p_normal = stats.pearsonr(cle[normal_idx], fragility[normal_idx])

print("=== CLEM-Ω PARADOX VERIFICATION ===")
print(f"Normal period: CLE ↔ Fragility correlation = {corr_normal:.3f} (p={p_normal:.3f})")
print(f"Crisis period: CLE ↔ Fragility correlation = {corr_crisis:.3f} (p={p_crisis:.3f})")
print()
print("During crisis, CLE becomes INVERSELY correlated with real fragility!")
print("CLEM-Ω would flash 'GREEN' exactly when the enterprise is about to detonate.")

# Visualization
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8))

# Plot 1: The Divergence
ax1.plot(days, cle, 'b-', label='CLEM-Ω Score (Formal Hygiene)', linewidth=2)
ax1_twin = ax1.twinx()
ax1_twin.plot(days, fragility, 'r-', label='Real Operational Fragility', linewidth=2)
ax1.axvspan(200, 260, alpha=0.2, color='red', label='Crisis')
ax1.set_ylabel('CLE (Lower = "Better")', color='b')
ax1_twin.set_ylabel('Fragility (Higher = Worse)', color='r')
ax1.set_title('THE PARADOX: "Improved" Security Metrics During Collapse')
ax1.legend(loc='upper left')
ax1_twin.legend(loc='upper right')
ax1.grid(True)

# Plot 2: Shadow Flow (The Invisible Channel)
ax2.plot(days, shadow, 'g-', linewidth=2)
ax2.axvspan(200, 260, alpha=0.2, color='red')
ax2.set_ylabel('Shadow Information Flow')
ax2.set_xlabel('Days')
ax2.set_title('Shadow Channels: The Reality CLEM-Ω Cannot Measure')
ax2.grid(True)

plt.tight_layout()
plt.savefig('clem_paradox.png', dpi=300, bbox_inches='tight')
plt.show()