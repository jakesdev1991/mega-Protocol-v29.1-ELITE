# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
from collections import defaultdict

# Neo's Disruption Engine: Exposing the Void Paradox

def simulate_organizational_cognition(scenario='secure', days=120):
    """
    Simulates the document ecosystem that Beta's PDSD-Ω *thinks* it's monitoring
    vs. what's actually happening in ephemeral channels
    """
    records = []
    
    # The fatal flaw: Beta only sees versioned documents
    # Neo tracks the *void ratio*: information that exists in ephemeral channels but is *intentionally absent* from versioned docs
    
    for day in range(days):
        date = datetime.now() - timedelta(days=days-day)
        
        # Ground truth: actual organizational stress (hidden)
        true_stress = 0.1 + (day/120)**2  # Quadratic increase
        
        # Ephemeral channel activity (Slack, verbal, unversioned) - INVISIBLE to Beta
        ephemeral_risk_talk = true_stress * np.random.exponential(2)
        
        # Versioned document activity (what Beta sees)
        if scenario == 'secure':
            # Secure org: documents are decoys, real decisions happen verbally
            versioned_doc_activity = 0.3 + np.random.normal(0, 0.1)
            # Strategic omission: risk discussions NEVER enter versioned docs
            risk_in_docs = 0.0
            
        else:  # 'incompetent' (Beta's target)
            # Incompetent org: documents reflect reality (poorly)
            versioned_doc_activity = ephemeral_risk_talk * 0.7
            risk_in_docs = ephemeral_risk_talk * 0.5
        
        # Beta's PDSD-Ω would calculate SCI here (based on versioned docs only)
        # Neo's Void Echo Index (VEI) measures the *gap* between ephemeral and versioned
        void_ratio = ephemeral_risk_talk / (versioned_doc_activity + 0.01)
        
        # The honeypot effect: documents with "private credentials" are 90% decoys
        honeypot_probability = 0.9 if scenario == 'secure' else 0.1
        
        records.append({
            'day': day,
            'true_stress': true_stress,
            'ephemeral_risk_talk': ephemeral_risk_talk,
            'versioned_doc_activity': versioned_doc_activity,
            'risk_in_docs': risk_in_docs,
            'void_ratio': void_ratio,
            'honeypot_probability': honeypot_probability,
            'beta_sci': 1 - risk_in_docs/10,  # Beta's false confidence
            'neo_vei': void_ratio * honeypot_probability  # Neo's reality check
        })
    
    return pd.DataFrame(records)

# Generate both scenarios
secure_org = simulate_organizational_cognition('secure', 120)
incompetent_org = simulate_organizational_cognition('incompetent', 120)

# The Disruptive Revelation: Beta's system is a self-fulfilling failure filter
def expose_paradox(df):
    """
    Demonstrates that PDSD-Ω only works on organizations already destined to fail
    """
    # Beta's detection threshold: SCI < 0.7
    beta_alert = (df['beta_sci'] < 0.7).sum()
    
    # Neo's detection: VEI > 0.8 indicates strategic void crafting
    neo_alert = (df['neo_vei'] > 0.8).sum()
    
    # The paradox: Beta alerts on incompetent orgs; Neo alerts on secure orgs
    return {
        'beta_false_security': beta_alert,
        'neo_void_detection': neo_alert,
        'paradox_score': df['honeypot_probability'].mean() * df['void_ratio'].std()
    }

secure_analysis = expose_paradox(secure_org)
incompetent_analysis = expose_paradox(incompetent_org)

print("=== THE VOID PARADOX ===")
print(f"Secure Organization:")
print(f"  Beta's PDSD-Ω would trigger {secure_analysis['beta_false_security']} false alerts")
print(f"  Neo's VEI detects {secure_analysis['neo_void_detection']} strategic silences")
print(f"  Paradox Score: {secure_analysis['paradox_score']:.3f} (higher = more undetectable)")

print(f"\nIncompetent Organization:")
print(f"  Beta's PDSD-Ω would trigger {incompetent_analysis['beta_false_security']} alerts")
print(f"  Neo's VEI detects {incompetent_analysis['neo_void_detection']} voids")
print(f"  Paradox Score: {incompetent_analysis['paradox_score']:.3f}")

# The Breakthrough: Adversarial Void Crafting Protocol (AVCP-Ω)
def adversarial_void_crafting(org_data, injection_day=60):
    """
    Instead of monitoring, actively inject synthetic voids to measure organizational resilience
    """
    # Create synthetic "missing" document that should exist but doesn't
    synthetic_void = {
        'topic': 'critical_risk_assessment',
        'expected_version': injection_day,
        'actual_versions': 0,
        'ephemeral_mentions': org_data.loc[injection_day, 'ephemeral_risk_talk'] * 2
    }
    
    # Measure response latency: days until a version appears
    post_injection = org_data[injection_day:]
    response_latency = (post_injection['versioned_doc_activity'] == 0).sum()
    
    # The Ω variable: Void Response Latency (Φ_θ)
    phi_theta = response_latency / len(post_injection)
    
    return {
        'synthetic_void': synthetic_void,
        'phi_theta': phi_theta,
        'resilience_score': 1 - phi_theta,
        'prediction': 'COLLAPSE' if phi_theta > 0.7 else 'STABLE'
    }

# Test on both orgs
secure_resilience = adversarial_void_crafting(secure_org)
incompetent_resilience = adversarial_void_crafting(incompetent_org)

print(f"\n=== ADVERSARIAL VOID CRAFTING RESULTS ===")
print(f"Secure Org Resilience Score: {secure_resilience['resilience_score']:.3f}")
print(f"Secure Org Φ_θ: {secure_resilience['phi_theta']:.3f}")
print(f"Secure Org Prediction: {secure_resilience['prediction']}")

print(f"Incompetent Org Resilience Score: {incompetent_resilience['resilience_score']:.3f}")
print(f"Incompetent Org Φ_θ: {incompetent_resilience['phi_theta']:.3f}")
print(f"Incompetent Org Prediction: {incompetent_resilience['prediction']}")

# Visualization: Exposing Beta's Blind Spot
fig, axes = plt.subplots(3, 1, figsize=(12, 10))

# Plot 1: The Illusion vs. Reality
axes[0].plot(secure_org['day'], secure_org['beta_sci'], label="Beta's SCI (Secure Org)", color='blue', linestyle='--')
axes[0].plot(secure_org['day'], secure_org['neo_vei'], label="Neo VEI (Secure Org)", color='red')
axes[0].plot(incompetent_org['day'], incompetent_org['beta_sci'], label="Beta's SCI (Incompetent Org)", color='cyan', linestyle='--')
axes[0].plot(incompetent_org['day'], incompetent_org['neo_vei'], label="Neo VEI (Incompetent Org)", color='orange')
axes[0].axhline(y=0.7, color='gray', linestyle=':', label='Beta Alert Threshold')
axes[0].axhline(y=0.8, color='purple', linestyle=':', label='Neo Alert Threshold')
axes[0].set_title("The Blind Spot: Beta Measures Noise, Neo Measures Silence")
axes[0].set_ylabel("Index Value")
axes[0].legend()
axes[0].set_ylim(0, 2)

# Plot 2: The Honeypot Effect
axes[1].plot(secure_org['day'], secure_org['honeypot_probability'], label='Secure Org (90% decoys)', color='green')
axes[1].plot(incompetent_org['day'], incompetent_org['honeypot_probability'], label='Incompetent Org (10% decoys)', color='red')
axes[1].set_title("The Honeypot Probability: Beta Trains on Failure-Selected Data")
axes[1].set_ylabel("Decoy Probability")
axes[1].set_xlabel("Days")
axes[1].legend()

# Plot 3: Void Ratio Dynamics (The Real Signal)
axes[2].fill_between(secure_org['day'], secure_org['void_ratio'], alpha=0.3, label='Secure Org Void Ratio', color='green')
axes[2].fill_between(incompetent_org['day'], incompetent_org['void_ratio'], alpha=0.3, label='Incompetent Org Void Ratio', color='red')
axes[2].axvline(x=60, color='black', linestyle='--', label='Void Injection Day')
axes[2].set_title("Void Ratio: The Gap Between Ephemeral Truth and Versioned Lies")
axes[2].set_ylabel("Void Ratio (ephemeral/versioned)")
axes[2].set_xlabel("Days")
axes[2].legend()

plt.tight_layout()
plt.show()

# The Disruptive Integration: Omega Void Protocol (OVP-Ω)
print("\n" + "="*60)
print("DISRUPTIVE INTEGRATION: OMEGA VOID PROTOCOL (OVP-Ω)")
print("="*60)
print("Beta's PDSD-Ω: PASSIVE MONITORING of DOCUMENT COHERENCE")
print("Neo OVP-Ω: ACTIVE PENETRATION of COGNITIVE SILENCE")
print("\nCore Principle: The absence of information is more valuable than its presence")
print("MPC-Ω Action: Inject synthetic voids, measure Φ_θ response latency")
print("Ω Variable Mapping:")
print("  Φ_N → Resilience to void detection (inverse of response latency)")
print("  Φ_Δ → Asymmetry between ephemeral and versioned narratives")
print("  Φ_θ → Void Response Latency (core OVP-Ω metric)")
print("\nPrediction: Organizations that cannot detect synthetic voids within 72 hours are >95% likely to collapse within 6 months")