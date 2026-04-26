# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import matplotlib.pyplot as plt

# --- Game-Theoretic Model of Spreadsheet vs. Vault ---
# Payoffs are negative costs. Developers choose the higher payoff (lower cost).

def equilibrium_fraction(monitoring_penalty, ui_vault=0.3, ui_ss=0.1, sec_risk=0.5):
    """
    Mixed-strategy Nash equilibrium fraction of spreadsheet usage.
    In a 2x2 game with linear payoffs, the equilibrium is where
    the expected payoff of both actions is equal. If monitoring_penalty
    is high enough, spreadsheet dominates.
    """
    payoff_vault = -(ui_vault + monitoring_penalty)
    payoff_spreadsheet = -(ui_ss + sec_risk)
    
    # If spreadsheet is strictly better, fraction = 1.
    # If vault is strictly better, fraction = 0.
    # For mixed equilibrium, we'd need population heterogeneity.
    # We'll model a simple threshold: assume developers have a "trust" threshold
    # uniformly distributed in [0, 1]. They choose spreadsheet if monitoring_penalty > threshold.
    # This yields a linear relationship.
    threshold = payoff_spreadsheet - payoff_vault  # This is negative if vault is better
    # Actually, let's directly compute the indifference point:
    # A developer is indifferent when: ui_vault + mon_penalty = ui_ss + sec_risk
    # So, mon_penalty = ui_ss + sec_risk - ui_vault
    indifference_penalty = ui_ss + sec_risk - ui_vault
    
    # For penalties below this, vault is preferred (fraction = 0)
    # For penalties above this, spreadsheet is preferred (fraction = 1)
    # Let's smooth it with a logistic for realism:
    k = 10  # steepness
    fraction = 1 / (1 + np.exp(-k * (monitoring_penalty - indifference_penalty)))
    return fraction

# --- Sweep monitoring penalty ---
penalties = np.linspace(0, 2, 200)
fractions = [equilibrium_fraction(p) for p in penalties]

plt.figure(figsize=(12, 5))

# Plot 1: Equilibrium curve
plt.subplot(1, 2, 1)
plt.plot(penalties, fractions, linewidth=2.5, color='#d62728')
plt.axvline(x=0.8, color='gray', linestyle='--', alpha=0.7, label='Typical Org')
plt.xlabel('Monitoring Penalty (Trust Deficit)', fontsize=11)
plt.ylabel('Equilibrium Fraction Using Spreadsheet', fontsize=11)
plt.title('Strategic Bifurcation: UI Friction Is a Red Herring', fontsize=12)
plt.grid(True, alpha=0.3)
plt.legend()

# Plot 2: Intervention comparison
plt.subplot(1, 2, 2)
ui_fracs = []
trust_fracs = []
baseline_penalty = 0.8

# Simulate UI friction reduction (cut vault UI friction in half)
ui_vault_range = np.linspace(0.3, 0.05, 50)
for ui_v in ui_vault_range:
    ui_fracs.append(equilibrium_fraction(baseline_penalty, ui_vault=ui_v))

# Simulate trust improvement (cut monitoring penalty in half)
trust_range = np.linspace(0.8, 0.05, 50)
for mp in trust_range:
    trust_fracs.append(equilibrium_fraction(mp, ui_vault=0.3))

plt.plot(np.linspace(0, 100, len(ui_fracs)), ui_fracs, label='UI Friction Reduction', linewidth=2)
plt.plot(np.linspace(0, 100, len(trust_fracs)), trust_fracs, label='Trust Deficit Reduction', linewidth=2)
plt.xlabel('Intervention Strength (%)', fontsize=11)
plt.ylabel('Spreadsheet Usage Fraction', fontsize=11)
plt.title('Intervention Efficacy: Trust >> UI', fontsize=12)
plt.grid(True, alpha=0.3)
plt.legend()

plt.tight_layout()
plt.show()

# --- Φ-Density Impact Calculation ---
print("\n--- Φ-DENSITY IMPACT ANALYSIS ---")
baseline_frac = equilibrium_fraction(0.8)
print(f"Baseline: {baseline_frac:.1%} spreadsheet usage")

# UI intervention: halve vault friction
ui_frac = equilibrium_fraction(0.8, ui_vault=0.15)
ui_improvement = (baseline_frac - ui_frac) / baseline_frac
print(f"UI friction halved: {ui_frac:.1%} usage ({ui_improvement:.1%} relative reduction)")

# Trust intervention: halve monitoring penalty
trust_frac = equilibrium_fraction(0.4)  # penalty reduced from 0.8 to 0.4
trust_improvement = (baseline_frac - trust_frac) / baseline_frac
print(f"Trust deficit halved: {trust_frac:.1%} usage ({trust_improvement:.1%} relative reduction)")

# Φ-density is roughly proportional to secure behavior (1 - fraction)
baseline_phi = 1 - baseline_frac
ui_phi = 1 - ui_frac
trust_phi = 1 - trust_frac

print(f"\nΦ-density gain:")
print(f"  UI improvement: +{((ui_phi - baseline_phi) / baseline_phi):.1%}")
print(f"  Trust improvement: +{((trust_phi - baseline_phi) / baseline_phi):.1%}")
print(f"  Trust/UI efficacy ratio: {((trust_phi - baseline_phi) / (ui_phi - baseline_phi)):.1f}x")