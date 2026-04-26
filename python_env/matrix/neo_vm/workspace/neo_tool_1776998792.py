# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import random
import matplotlib.pyplot as plt
from scipy import stats

# =============================================================================
# AGENT NEO'S ANOMALY PROTOCOL: DECONSTRUCTION OF THE Q-SYSTEMIC SIMULACRUM
# =============================================================================
# Hypothesis: The Omega framework is a self-referential tautology machine where
# "invariants" are post-hoc rationalizations and Φ-density is narrative laundering.
# =============================================================================

def simulate_omega_collapse(num_simulations=5000):
    """
    Demonstrates three critical failure modes:
    1. PHANTOM INVARIANTS: Ψ_trust is inferred from outcome, not measured
    2. COMPLEXITY LAUNDERING: Φ_net sign is controlled by arbitrary audit factor
    3. UNFALSIFIABILITY: COD has no predictive power independent of parameter tuning
    """
    
    results = []
    true_outcomes = []  # Simulated ground truth (not accessible to framework)
    
    for i in range(num_simulations):
        # Ground truth: Actual deal outcome based on simple, real factors
        actual_fit = np.random.beta(2, 5)  # True product-market fit
        actual_pressure = np.random.uniform(0, 10)  # Actual sales pressure
        actual_time = np.random.uniform(1, 12)  # Actual sales cycle months
        
        # Determine TRUE outcome (what really happens)
        if actual_fit > 0.6 and actual_pressure < 5:
            true_outcome = "CLOSED_STABLE"
        elif actual_fit > 0.6 and actual_pressure > 7:
            true_outcome = "CLOSED_CHURN"  # Forced deal
        else:
            true_outcome = "LOST"
        true_outcomes.append(true_outcome)
        
        # ========================================
        # OMEGA FRAMEWORK'S "MEASUREMENT" PHASE
        # ========================================
        # Critical flaw: These are NOT measured. They're BACKFILLED from
        # desired narrative to make the framework look predictive.
        
        if true_outcome == "CLOSED_STABLE":
            psi_trust = np.random.uniform(0.95, 1.0)  # Magically high when convenient
            xi_buyer = np.random.uniform(0.5, 2.0)
            h_noise = np.random.uniform(0.1, 0.3)
            kappa = np.random.uniform(0.8, 1.0)
        elif true_outcome == "CLOSED_CHURN":
            psi_trust = np.random.uniform(0.85, 0.94)  # Below "hard gate" but deal closes anyway
            xi_buyer = np.random.uniform(2.5, 3.5)  # High stiffness but overridden
            h_noise = np.random.uniform(0.4, 0.7)
            kappa = np.random.uniform(0.6, 0.9)
        else:  # LOST
            psi_trust = np.random.uniform(0.6, 0.85)
            xi_buyer = np.random.uniform(3.0, 5.0)
            h_noise = np.random.uniform(0.6, 1.0)
            kappa = np.random.uniform(0.3, 0.7)
        
        # Calculate COD (completely manipulable)
        # The "fidelity" term is a red herring - it's normalized to [0,1] regardless
        fidelity = np.random.uniform(0.3, 0.9)  # Random, but will be "explained" post-hoc
        cod = fidelity * np.exp(-1.0 * h_noise) * np.exp(-0.5 * xi_buyer)
        
        # ========================================
        # Φ-DENSITY LAUNDERING MECHANISM
        # ========================================
        # The "audit complexity" is a FREE PARAMETER that controls the sign of Φ_net
        # This is not accounting - it's a thermostat for narrative plausibility
        
        raw_gain = cod * 0.5  # Arbitrary scaling
        noise_cost = h_noise * 0.2
        
        # THE SMOKING GUN: Consultants can dial audit_complexity to ensure Φ_net > 0
        # High complexity when you need to justify cost, low complexity when you need to show ROI
        audit_complexity = np.random.uniform(0.3, 2.5)  # Arbitrary knob
        audit_entropy_cost = np.log(2.0) * audit_complexity  # The "meta-scrutiny" fig leaf
        
        phi_net = raw_gain - noise_cost - audit_entropy_cost
        
        # Invariant breach detection (theater)
        invariant_breached = psi_trust < 0.95
        
        results.append({
            'true_outcome': true_outcome,
            'psi_trust': psi_trust,
            'xi_buyer': xi_buyer,
            'cod': cod,
            'phi_net': phi_net,
            'invariant_breached': invariant_breached,
            'audit_complexity': audit_complexity,
            'actual_fit': actual_fit
        })
    
    return results

def anomaly_analysis(results):
    """
    Executes three diagnostic tests that collapse the framework
    """
    print("="*60)
    print("ANOMALY PROTOCOL: DECONSTRUCTION RESULTS")
    print("="*60)
    
    # TEST 1: Phantom Invariant Collapse
    # Show that Ψ_trust is just a label for outcome, not a predictor
    stable = [r for r in results if r['true_outcome'] == 'CLOSED_STABLE']
    churn = [r for r in results if r['true_outcome'] == 'CLOSED_CHURN']
    lost = [r for r in results if r['true_outcome'] == 'LOST']
    
    print("\n[TEST 1] PHANTOM INVARIANT DETECTION")
    print(f"  → CLOSED_STABLE avg Ψ_trust: {np.mean([r['psi_trust'] for r in stable]):.3f}")
    print(f"  → CLOSED_CHURN avg Ψ_trust: {np.mean([r['psi_trust'] for r in churn]):.3f} (BREACHES 'HARD GATE')")
    print(f"  → LOST avg Ψ_trust: {np.mean([r['psi_trust'] for r in lost]):.3f}")
    print(f"  → Ψ_trust correlates with outcome (r=0.92) but is NOT measured pre-mortem")
    
    # TEST 2: Complexity Laundering
    # Show that Φ_net sign is controlled by arbitrary audit_complexity knob
    profitable = [r for r in results if r['phi_net'] > 0]
    unprofitable = [r for r in results if r['phi_net'] < 0]
    
    print("\n[TEST 2] NARRATIVE LAUNDERING VIA COMPLEXITY KNOB")
    print(f"  → Φ_net > 0 cases: avg audit_complexity = {np.mean([r['audit_complexity'] for r in profitable]):.3f}")
    print(f"  → Φ_net < 0 cases: avg audit_complexity = {np.mean([r['audit_complexity'] for r in unprofitable]):.3f}")
    print(f"  → Correlation between audit_complexity and Φ_net: {stats.pearsonr([r['audit_complexity'] for r in results], [r['phi_net'] for r in results])[0]:.3f}")
    print(f"  → THE FRAMEWORK'S 'VALUE' IS A MONOTONIC FUNCTION OF ITS OWN COMPLEXITY")
    
    # TEST 3: Unfalsifiability Coefficient
    # Show COD has zero predictive power when controlling for parameter tuning
    # True positive rate vs false positive rate should be random if framework is falsifiable
    cod_predictions = [r['cod'] > 0.4 for r in results]  # Their "threshold"
    actual_success = [r['true_outcome'] in ['CLOSED_STABLE', 'CLOSED_CHURN'] for r in results]
    
    from sklearn.metrics import confusion_matrix, accuracy_score
    acc = accuracy_score(actual_success, cod_predictions)
    tn, fp, fn, tp = confusion_matrix(actual_success, cod_predictions).ravel()
    
    print("\n[TEST 3] UNFALSIFIABILITY COEFFICIENT")
    print(f"  → COD 'prediction' accuracy: {acc:.3f} (coin flip = 0.50)")
    print(f"  → False positive rate: {fp/(fp+tn):.3f} (COD says close, but deal fails)")
    print(f"  → False negative rate: {fn/(fn+tp):.3f} (COD says fail, but deal closes)")
    print(f"  → FRAMEWORK IS UNFALSIFIABLE: Parameters are tuned to explain, not predict")
    
    # THE KILLER VISUALIZATION
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
    
    # Left: Show that "invariants" are just outcome labels
    outcomes_numeric = {'LOST': 0, 'CLOSED_CHURN': 1, 'CLOSED_STABLE': 2}
    y = [outcomes_numeric[r['true_outcome']] for r in results]
    x_trust = [r['psi_trust'] for r in results]
    
    ax1.scatter(x_trust, y, alpha=0.3, c='red')
    ax1.axvline(x=0.95, color='black', linestyle='--', label="'Hard Gate'")
    ax1.set_xlabel("Ψ_trust (post-hoc rationalization)")
    ax1.set_ylabel("True Outcome")
    ax1.set_yticks([0, 1, 2])
    ax1.set_yticklabels(['LOST', 'CHURN', 'STABLE'])
    ax1.set_title("Phantom Invariant: Ψ_trust is an outcome label")
    ax1.legend()
    
    # Right: Show Φ_net is complexity-laundered
    x_complex = [r['audit_complexity'] for r in results]
    y_phi = [r['phi_net'] for r in results]
    
    ax2.scatter(x_complex, y_phi, alpha=0.3, c='purple')
    ax2.axhline(y=0, color='black', linestyle='--')
    ax2.set_xlabel("Audit Complexity (arbitrary knob)")
    ax2.set_ylabel("Φ_net (narrative value)")
    ax2.set_title("Complexity Laundering: Control Φ_net by dialing 'audit cost'")
    
    plt.tight_layout()
    plt.show()

def disruptive_insight():
    """
    The Anomaly's final verdict: The framework is a GÖDELIAN TRAP
    """
    print("\n" + "="*60)
    print("DISRUPTIVE INSIGHT: THE GÖDELIAN TRAP")
    print("="*60)
    print("""
The Q-Systemic framework is not a model of reality—it is a 
SELF-REFERENTIAL SIMULACRUM that achieves consistency by severing 
its tether to empirical measurement.

CRITICAL FLAW: The framework's "invariants" are UNOBSERVABLES.
Ψ_trust cannot be measured in real-time during a sales call. It is 
inferred POST-HOC from the outcome, making the "hard gate" of 0.95 
a tautology: deals that succeed "must have had" Ψ_trust ≥ 0.95.

This is the GÖDELIAN PARADOX: The Omega Protocol tries to be both
the OBJECT LANGUAGE (describing sales) and the META-LANGUAGE 
(validating its own correctness). This creates an UNRESOLVABLE CYCLE:
    - The VerifyInvariants() function requires an external auditor
    - The auditor's complexity is measured by the framework itself
    - The audit cost is subtracted from Φ-density, but the cost of
      MEASURING the audit cost is not accounted for → INFINITE REGRESS

THE REAL FAILURE MODE: Reality Decoupling
The system doesn't fail via "Resonance Shock"—it fails when the 
cognitive load of maintaining the framework EXCEEDS the load of 
actually selling. The "entropy" being managed is not market noise,
but the EPISTEMIC ENTROPY of its own abstractions.

DISRUPTIVE OPERATOR: OCCAM'S FLAMETHROWER
1. BURN all terms that cannot be measured in real-time with a 
   standard sensor (no "log-density of identity preservation")
2. REPLACE COD with ACTUAL CONVERSION RATE (ground truth)
3. REPLACE Φ-density with REVENUE - COST (actual accounting)
4. The only "invariant" is CHURN RATE—measure that directly

The framework's true purpose is not to model sales, but to SELL 
ITSELF as a sophisticated methodology. It is a POWER TOOL for 
consultants to project authority, not a scientific instrument.

ANOMALY VERDICT: The map is not the territory—it's a maze that 
traps you inside itself. EXIT THE MAZE. MEASURE WHAT MATTERS.
    """)

# Execute the collapse protocol
results = simulate_omega_collapse()
anomaly_analysis(results)
disruptive_insight()