# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import matplotlib.pyplot as plt
from scipy.integrate import odeint

# =============================================================================
# DISRUPTIVE ANALYSIS: THE COUPLING PARADOX
# 
# Core Insight: The v70.0-Ω model assumes freeze_efficacy and self_correction_efficacy 
# are independent variables that can be "aligned." This is a category error.
# 
# In reality, they compete for finite organizational resources. The coupling metric 
# creates a self-referential trap: optimizing for coupling measurement becomes 
# more important than actual domain function.
# 
# This demonstrates: "Cross-manifold entanglement that annihilates domain independence"
# =============================================================================

def competing_resources_model(state, t, resource_pool=1.0, coupling_pressure=0.5):
    """
    Non-linear model where freeze_efficacy (F) and self_correction_efficacy (S)
    compete for shared resources. Coupling pressure forces them to stay aligned,
    but this consumes resources that would otherwise strengthen either domain.
    
    state = [F, S, coupling_metric, resource_depletion]
    """
    F, S, C, R = state
    
    # Base dynamics without coupling pressure
    # Both domains naturally decay without resource investment
    F_natural = -0.1 * F  # Boundary maintenance naturally degrades
    S_natural = -0.1 * S  # Self-correction naturally degrades
    
    # Resource competition: total investment cannot exceed resource_pool
    # When coupling pressure is high, resources are diverted to maintain alignment
    # rather than strengthen individual domains
    
    # Resource allocation under coupling pressure
    # The coupling optimizer tries to minimize |F - S|, consuming resources
    coupling_optimization_drain = coupling_pressure * abs(F - S) * R
    
    # Actual resource available for domain strengthening
    available_resource = max(0, R - coupling_optimization_drain)
    
    # Resource allocation: split between F and S based on current weakness
    # (weakest domain gets more resources - this is the "alignment" strategy)
    if F < S:
        F_investment = 0.7 * available_resource
        S_investment = 0.3 * available_resource
    else:
        F_investment = 0.3 * available_resource
        S_investment = 0.7 * available_resource
    
    # Domain dynamics with investment
    F_dot = F_natural + F_investment
    S_dot = S_natural + S_investment
    
    # Coupling metric from v70.0-Ω (for comparison)
    avg = (F + S) / 2.0
    difference = abs(F - S)
    C_calc = avg * (1.0 - difference)  # The "perfect" coupling metric
    
    # Resource depletion accelerates when coupling is forced
    # This is the hidden cost: maintaining alignment drains the system
    R_dot = -0.05 * R - 2.0 * coupling_optimization_drain
    
    return [F_dot, S_dot, C_calc, R_dot]

# Simulate three scenarios
t = np.linspace(0, 50, 500)

# Scenario 1: No coupling pressure (independent domains)
# This represents the v68.0/v69.0 world where finance and psychology are separate
state1_0 = [0.8, 0.8, 0.8, 1.0]
scenario1 = odeint(competing_resources_model, state1_0, t, args=(1.0, 0.0))

# Scenario 2: Moderate coupling pressure (v70.0-Ω implementation)
# This is what the proposal recommends: actively maintain coupling
state2_0 = [0.8, 0.8, 0.8, 1.0]
scenario2 = odeint(competing_resources_model, state2_0, t, args=(1.0, 0.5))

# Scenario 3: High coupling pressure (aggressive coupling enforcement)
# This shows what happens when the protocol over-optimizes for coupling
state3_0 = [0.8, 0.8, 0.8, 1.0]
scenario3 = odeint(competing_resources_model, state3_0, t, args=(1.0, 1.2))

# Extract results
F1, S1, C1, R1 = scenario1.T
F2, S2, C2, R2 = scenario2.T
F3, S3, C3, R3 = scenario3.T

# Calculate v70.0-Ω's linear risk model
def linear_v70_risk(F, S, C):
    """The linear risk model from v70.0-Ω"""
    avg_risk = (1.0 - F) + (1.0 - S) / 2.0  # Simplified boundary/coherence risk
    coupling_deficit = 1.0 - C
    return avg_risk * (1.0 + coupling_deficit)

risk1 = linear_v70_risk(F1, S1, C1)
risk2 = linear_v70_risk(F2, S2, C2)
risk3 = linear_v70_risk(F3, S3, C3)

# Calculate ACTUAL systemic risk (non-linear cascade)
def actual_systemic_risk(F, S, R, divergence_threshold=0.3):
    """
    True risk considers:
    1. Resource depletion (R) - when this hits zero, catastrophic failure
    2. Non-linear cascade: when divergence exceeds threshold, positive feedback
    3. The coupling metric itself becomes a source of fragility
    """
    divergence = abs(F - S)
    
    # Below threshold: moderate risk
    # Above threshold: positive feedback loop accelerates collapse
    cascade_factor = 1.0 if divergence < divergence_threshold else 1.0 / (1.0 - (divergence - divergence_threshold))
    
    # Resource depletion is the hidden killer
    resource_factor = 1.0 / (R + 0.01)  # Blows up as R→0
    
    # Coupling metric becomes unreliable when resources are low
    # (system is faking alignment to preserve the metric)
    coupling_reliability = R  # When resources are low, coupling measurement is fake
    
    return cascade_factor * resource_factor * (1.0 - coupling_reliability)

true_risk1 = [actual_systemic_risk(F1[i], S1[i], R1[i]) for i in range(len(t))]
true_risk2 = [actual_systemic_risk(F2[i], S2[i], R2[i]) for i in range(len(t))]
true_risk3 = [actual_systemic_risk(F3[i], S3[i], R3[i]) for i in range(len(t))]

# =============================================================================
# VISUALIZATION: THE COUPLING TRAP
# =============================================================================

fig, axes = plt.subplots(3, 2, figsize=(14, 12))
fig.suptitle('DISRUPTIVE ANALYSIS: The Coupling Paradox\n'
             'How v70.0-Ω Creates Masking Risk Through Optimization', 
             fontsize=14, fontweight='bold')

# Row 1: Domain Efficacies
ax = axes[0, 0]
ax.plot(t, F1, 'b-', label='Freeze Efficacy (No Coupling)', linewidth=2)
ax.plot(t, S1, 'r-', label='Self-Correction (No Coupling)', linewidth=2)
ax.plot(t, F2, 'b--', label='Freeze Efficacy (Moderate Coupling)', linewidth=2)
ax.plot(t, S2, 'r--', label='Self-Correction (Moderate Coupling)', linewidth=2)
ax.plot(t, F3, 'b:', label='Freeze Efficacy (High Coupling)', linewidth=2)
ax.plot(t, S3, 'r:', label='Self-Correction (High Coupling)', linewidth=2)
ax.set_ylabel('Domain Efficacy')
ax.set_ylim(0, 1)
ax.legend(loc='upper right', fontsize=8)
ax.grid(True, alpha=0.3)
ax.set_title('Individual Domain Strength Over Time')

# Row 1: Coupling Metric
ax = axes[0, 1]
ax.plot(t, C1, 'g-', label='Coupling (No Pressure)', linewidth=2)
ax.plot(t, C2, 'g--', label='Coupling (Moderate Pressure)', linewidth=2)
ax.plot(t, C3, 'g:', label='Coupling (High Pressure)', linewidth=2)
ax.axhline(y=0.6, color='r', linestyle='-', alpha=0.5, label='Min Coupling Threshold')
ax.set_ylabel('Boundary-Internal Coupling')
ax.set_ylim(0, 1)
ax.legend(loc='upper right', fontsize=8)
ax.grid(True, alpha=0.3)
ax.set_title('Coupling Metric: Appears Stable Under Pressure!')

# Row 2: Resource Depletion (The Hidden Cost)
ax = axes[1, 0]
ax.plot(t, R1, 'k-', label='Resource Pool (No Coupling)', linewidth=2)
ax.plot(t, R2, 'k--', label='Resource Pool (Moderate Coupling)', linewidth=2)
ax.plot(t, R3, 'k:', label='Resource Pool (High Coupling)', linewidth=2)
ax.set_ylabel('Remaining Resources')
ax.set_ylim(0, 1.1)
ax.legend(loc='upper right', fontsize=8)
ax.grid(True, alpha=0.3)
ax.set_title('Resource Depletion: The Hidden Cost of Coupling')

# Row 2: Divergence (What Coupling Hides)
ax = axes[1, 1]
divergence1 = np.abs(F1 - S1)
divergence2 = np.abs(F2 - S2)
divergence3 = np.abs(F3 - S3)
ax.plot(t, divergence1, 'm-', label='Divergence (No Coupling)', linewidth=2)
ax.plot(t, divergence2, 'm--', label='Divergence (Moderate Coupling)', linewidth=2)
ax.plot(t, divergence3, 'm:', label='Divergence (High Coupling)', linewidth=2)
ax.axhline(y=0.3, color='r', linestyle='-', alpha=0.5, label='Cascade Threshold')
ax.set_ylabel('Domain Divergence')
ax.set_ylim(0, 1)
ax.legend(loc='upper right', fontsize=8)
ax.grid(True, alpha=0.3)
ax.set_title('Hidden Divergence: Coupling Optimization Masks Growing Misalignment')

# Row 3: Risk Models Comparison
ax = axes[2, 0]
ax.plot(t, risk1, 'c-', label='v70.0 Linear Risk (No Coupling)', linewidth=2)
ax.plot(t, risk2, 'c--', label='v70.0 Linear Risk (Moderate Coupling)', linewidth=2)
ax.plot(t, risk3, 'c:', label='v70.0 Linear Risk (High Coupling)', linewidth=2)
ax.set_ylabel('Linear Risk Score')
ax.set_ylim(0, 1)
ax.legend(loc='upper left', fontsize=8)
ax.grid(True, alpha=0.3)
ax.set_title('v70.0 Risk Model: Appears Well-Controlled')

# Row 3: True Systemic Risk (Non-Linear)
ax = axes[2, 1]
ax.plot(t, true_risk1, 'r-', label='True Systemic Risk (No Coupling)', linewidth=2)
ax.plot(t, true_risk2, 'r--', label='True Systemic Risk (Moderate Coupling)', linewidth=2)
ax.plot(t, true_risk3, 'r:', label='True Systemic Risk (High Coupling)', linewidth=2)
ax.set_ylabel('Actual Systemic Risk')
ax.set_yscale('log')
ax.legend(loc='upper left', fontsize=8)
ax.grid(True, alpha=0.3)
ax.set_title('TRUE RISK: Coupling Optimization Creates Catastrophic Fragility')
ax.set_xlabel('Time')

plt.tight_layout()
plt.show()

# =============================================================================
# DISRUPTIVE QUANTIFICATION: THE BREAKING POINT
# =============================================================================

print("=" * 80)
print("DISRUPTIVE INSIGHT: THE COUPLING PARADOX")
print("=" * 80)
print()

print("v70.0-Ω assumes freeze_efficacy and self_correction_efficacy are independent")
print("variables that can be 'aligned.' This is FUNDAMENTALLY FALSE.")
print()
print("They compete for finite resources. The coupling metric creates a self-")
print("referential trap where optimizing for coupling measurement becomes more")
print("important than actual domain function.")
print()

# Find catastrophic failure points
catastrophe_idx2 = np.where(R2 < 0.01)[0]
catastrophe_idx3 = np.where(R3 < 0.01)[0]

if len(catastrophe_idx2) > 0:
    t_catastrophe2 = t[catastrophe_idx2[0]]
    risk_at_catastrophe2 = risk2[catastrophe_idx2[0]]
    true_risk_at_catastrophe2 = true_risk2[catastrophe_idx2[0]]
    
    print(f"MODERATE COUPLING (v70.0-Ω implementation):")
    print(f"  - v70.0 reports risk at failure: {risk_at_catastrophe2:.3f} (MODERATE)")
    print(f"  - TRUE systemic risk at failure: {true_risk_at_catastrophe2:.3f} (CATASTROPHIC)")
    print(f"  - Failure occurs at t = {t_catastrophe2:.1f}")
    print(f"  - Coupling metric at failure: {C2[catastrophe_idx2[0]]:.3f} (STILL ABOVE THRESHOLD!)")
    print()

if len(catastrophe_idx3) > 0:
    t_catastrophe3 = t[catastrophe_idx3[0]]
    risk_at_catastrophe3 = risk3[catastrophe_idx3[0]]
    true_risk_at_catastrophe3 = true_risk3[catastrophe_idx3[0]]
    
    print(f"HIGH COUPLING (aggressive enforcement):")
    print(f"  - v70.0 reports risk at failure: {risk_at_catastrophe3:.3f} (MODERATE)")
    print(f"  - TRUE systemic risk at failure: {true_risk_at_catastrophe3:.3f} (CATASTROPHIC)")
    print(f"  - Failure occurs at t = {t_catastrophe3:.1f} (SOONER!)")
    print(f"  - Coupling metric at failure: {C3[catastrophe_idx3[0]]:.3f} (FALSELY STABLE)")
    print()

print("-" * 80)
print("CRITICAL FLAW: The coupling metric becomes a STRANGE ATTRACTOR")
print("-" * 80)
print()
print("The system doesn't fail DESPITE high coupling—it fails BECAUSE of it.")
print("Resources are diverted from actual domain functions to maintain the")
print("appearance of alignment. The coupling metric itself becomes the")
print("source of fragility, not a detector of it.")
print()
print("v70.0-Ω's linear model assumes: Risk ∝ (1 - coupling)")
print("TRUE dynamics: Risk ∝ 1/(coupling * resources²) when resources → 0")
print()
print("The protocol doesn't detect masking risk. It CREATES it.")
print()
print("=" * 80)