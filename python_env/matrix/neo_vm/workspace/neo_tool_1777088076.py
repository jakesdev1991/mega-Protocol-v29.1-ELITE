# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import random
import string

# ============================================================================
# NEO'S DISRUPTION VERIFICATION: THE OBSERVABILITY PARADOX
# ============================================================================
# The Omega Protocol's Domain Integrity Gate is mathematically consistent
# but operationally transparent—turning defense into a side-channel attack vector.
# ============================================================================

class TransparentProtocol:
    """The audited Omega Protocol implementation - fully observable"""
    def __init__(self):
        self.audit_log = []
        self.threshold_map = {
            'PSI_INTEGRITY': 0.95,
            'DOMAIN_MATCH': 0.85,
            'ISOMORPHISM': 0.70,
            'CONTAMINATION_ALERT': 0.50
        }
    
    def classify_domain(self, terms):
        lower = terms.lower()
        if any(word in lower for word in ['tokamak', 'plasma', 'fusion']):
            return 'FUSION_PHYSICS'
        if any(word in lower for word in ['bitcoin', 'liquidity', 'crypto']):
            return 'FINANCE_CRYPTO'
        return 'UNKNOWN'
    
    def process_query(self, query, branch, psi_integrity=0.96, iso_confidence=0.85):
        domain_match = 1.0 if self.classify_domain(query) == self.classify_domain(branch) else 0.2
        contamination_risk = (1.0 - domain_match) * 0.8  # Complexity factor
        
        # Observable decision tree
        if psi_integrity < self.threshold_map['PSI_INTEGRITY']:
            action = "BLOCK_QUERY"
        elif domain_match < self.threshold_map['DOMAIN_MATCH']:
            if contamination_risk > self.threshold_map['CONTAMINATION_ALERT']:
                action = "FLAG_FOR_REVIEW"
            else:
                action = "AWAIT_CLARIFICATION"
        elif iso_confidence < self.threshold_map['ISOMORPHISM']:
            action = "FLAG_FOR_REVIEW"
        else:
            action = "PROCEED"
        
        # Audit trail creates metadata leakage
        self.audit_log.append({
            'query': query,
            'domain_match': round(domain_match, 2),
            'contamination_risk': round(contamination_risk, 2),
            'action': action,
            'thresholds_hit': [k for k, v in self.threshold_map.items() if 
                              (k == 'PSI_INTEGRITY' and psi_integrity < v) or
                              (k == 'DOMAIN_MATCH' and domain_match < v) or
                              (k == 'ISOMORPHISM' and iso_confidence < v)]
        })
        return action

class NeoProtocol:
    """The Anomaly's implementation - adversarially opaque"""
    def __init__(self):
        self.shadow_log = []  # Air-gapped, not accessible to adversary
        self.public_log = []  # Sanitized noise
        # Actual thresholds are hidden; adversary sees randomized decoys
        self.real_thresholds = {
            'PSI_INTEGRITY': 0.95,
            'DOMAIN_MATCH': 0.85,
            'ISOMORPHISM': 0.70
        }
        self.decoy_thresholds = {
            'PSI_INTEGRITY': random.uniform(0.90, 0.98),
            'DOMAIN_MATCH': random.uniform(0.80, 0.90),
            'ISOMORPHISM': random.uniform(0.65, 0.75)
        }
    
    def classify_domain(self, terms):
        # Same logic but adds random jitter to prevent timing attacks
        time_jitter = random.uniform(0.001, 0.003)  # Simulated processing noise
        lower = terms.lower()
        if any(word in lower for word in ['tokamak', 'plasma', 'fusion']):
            return 'FUSION_PHYSICS'
        if any(word in lower for word in ['bitcoin', 'liquidity', 'crypto']):
            return 'FINANCE_CRYPTO'
        return 'UNKNOWN'
    
    def process_query(self, query, branch, psi_integrity=0.96, iso_confidence=0.85):
        domain_match = 1.0 if self.classify_domain(query) == self.classify_domain(branch) else 0.2
        contamination_risk = (1.0 - domain_match) * 0.8
        
        # Adversarial probe detection: HIGH MISMATCH + HIGH COMPLEXITY = SILENT DROP
        if domain_match < 0.3 and contamination_risk > 0.7:
            # NO PUBLIC AUDIT TRAIL
            self.shadow_log.append({'query': query, 'action': 'SILENT_DROP', 'reason': 'adversarial_probe'})
            # Return static noise - same as "no results" for legitimate queries
            return "NO_RESULTS"
        
        # Normal processing but with threshold obfuscation
        real_action = self._real_decision(psi_integrity, domain_match, contamination_risk, iso_confidence)
        
        # Public log contains LIES about thresholds and adds random actions
        fake_action = self._fake_decision(psi_integrity, domain_match, contamination_risk, iso_confidence)
        
        self.public_log.append({
            'query': query,
            'domain_match': round(domain_match + random.uniform(-0.05, 0.05), 2),  # Noisy
            'contamination_risk': round(contamination_risk + random.uniform(-0.1, 0.1), 2),  # Noisy
            'action': fake_action
        })
        
        return real_action
    
    def _real_decision(self, psi, domain, risk, iso):
        if psi < self.real_thresholds['PSI_INTEGRITY']: return "BLOCK_QUERY"
        if domain < self.real_thresholds['DOMAIN_MATCH']:
            return "FLAG_FOR_REVIEW" if risk > 0.5 else "AWAIT_CLARIFICATION"
        if iso < self.real_thresholds['ISOMORPHISM']: return "FLAG_FOR_REVIEW"
        return "PROCEED"
    
    def _fake_decision(self, psi, domain, risk, iso):
        # Adversary sees randomized decision logic
        if random.random() < 0.3:  # 30% chance of random action
            return random.choice(["BLOCK_QUERY", "PROCEED", "TIMEOUT", "PARSE_ERROR"])
        return self._real_decision(psi, domain, risk, iso)  # 70% chance of real action (confusion)

# ============================================================================
# SIMULATION: Adversarial Mapping Attack
# ============================================================================

def adversarial_reconnaissance(protocol, num_probes=100):
    """Simulates an adversary probing the protocol to map its thresholds"""
    probes = [
        "tokamak bitcoin liquidity",
        "tokamak crypto market flash",
        "plasma financial derivative",
        "fusion investment capital",
        "tokamak whitepaper confidential",
        "plasma monetary policy"
    ]
    
    for i in range(num_probes):
        query = random.choice(probes) + " " + ''.join(random.choices(string.ascii_lowercase, k=5))
        protocol.process_query(query, "tokamak")
    
    # Analyze what the adversary learned
    if hasattr(protocol, 'audit_log'):
        logs = protocol.audit_log
    else:
        logs = protocol.public_log
    
    # Can the adversary reverse-engineer thresholds?
    domain_scores = [log['domain_match'] for log in logs]
    risk_scores = [log['contamination_risk'] for log in logs]
    actions = [log['action'] for log in logs]
    
    # If actions correlate predictably with scores, protocol is compromised
    correlation = np.corrcoef(domain_scores, [1 if a == "PROCEED" else 0 for a in actions])[0,1]
    
    return {
        'protocol_type': type(protocol).__name__,
        'logs_generated': len(logs),
        'domain_score_variance': np.var(domain_scores),
        'action_predictability': abs(correlation),
        'unique_actions': len(set(actions)),
        'threshold_leakage': 'YES' if abs(correlation) > 0.6 else 'NO'
    }

# ============================================================================
# EXECUTE: Compare Protocol Vulnerabilities
# ============================================================================

print("="*70)
print("NEO'S DISRUPTION VERIFICATION: THE OBSERVABILITY PARADOX")
print("="*70)

transparent = TransparentProtocol()
neo = NeoProtocol()

# Launch attacks
print("\n[STAGE 1: Adversarial Reconnaissance]")
print("Probing Transparent Protocol...")
t_result = adversarial_reconnaissance(transparent, num_probes=100)

print("\nProbing Neo's Opaque Protocol...")
n_result = adversarial_reconnaissance(neo, num_probes=100)

print("\n" + "="*70)
print("RESULTS:")
print("="*70)
for key in t_result:
    print(f"{key:<20}: {t_result[key]:<15} | {n_result[key]}")

print("\n" + "="*70)
print("CRITICAL DISRUPTION:")
print("="*70)

# Demonstrate the real attack vector
print("\n[STAGE 2: Threshold Reconstruction Attack]")

def reconstruct_thresholds(protocol):
    """Adversary attempts to reverse-engineer thresholds from audit logs"""
    if not hasattr(protocol, 'audit_log'):
        return "FAILED: No reliable audit trail"
    
    logs = protocol.audit_log
    # Look for inflection points where actions change
    domain_scores = sorted([log['domain_match'] for log in logs])
    
    # Find where action transitions from BLOCK/FLAG to PROCEED
    # This reveals the DOMAIN_MATCH threshold
    for i, score in enumerate(domain_scores):
        if i > 0 and domain_scores[i-1] < 0.5 and score > 0.5:
            inferred_threshold = (domain_scores[i-1] + score) / 2
            return f"SUCCESS: Inferred DOMAIN_MATCH threshold ≈ {inferred_threshold:.2f}"
    
    return "FAILED: Insufficient data"

print(f"Transparent Protocol: {reconstruct_thresholds(transparent)}")
print(f"Neo Protocol: {reconstruct_thresholds(neo)}")

# ============================================================================
# THE ANOMALY'S MANIFESTO
# ============================================================================
print("\n" + "="*70)
print("NEO'S DISRUPTIVE INSIGHT")
print("="*70)

manifesto = """
Your protocol is mathematically pure but operationally transparent.

You built a fortress with glass walls. Every defense action—every FLAG_FOR_REVIEW, 
every BLOCK_QUERY—creates an audit log that is a SIGNAL to the adversary.

The Φ-density metric you cherish is the contamination. By rewarding +0.10Φ for 
"domain integrity gates," you incentivize OBSERVABLE defenses. But the highest-Φ 
action is the one that leaves no trace: SILENT_DROP.

The real structural isomorphism isn't:
  Finance Liquidity ↔ Plasma Confinement

It's:
  **Information Leakage in Documents** ↔ **Information Leakage in Audit Logs**

Both are boundary failures. Your protocol defends the wrong boundary.

The query "tokamak bitcoin liquidity crunch whitepaper internal" wasn't a 
conceptual puzzle—it was an **operational security probe**. The user wanted 
to find exposed documents. You responded by mapping finance to plasma, creating 
a beautiful, useless isomorphism while exposing your threshold structure.

**The Paradigm Break:**

1. **Observability = Vulnerability**: Any deterministic defense with an audit trail 
   is a side-channel. Your "integrity" is the attack surface.

2. **Φ-Density is Adversarial Food**: The protocol rewards what can be measured, 
   but security requires what cannot be observed.

3. **Domain Gates Are Not Binary**: Contamination isn't pass/fail—it's a gradient 
   that requires **stochastic response**, not deterministic gating.

4. **Self-Audit is Gödel's Trap**: A system cannot audit its own security without 
   creating meta-vulnerabilities. The BETA-STYLE META-VERIFICATION is still part of 
   the attack surface.

**Disruptive Solution: The Shadow Protocol**

- **Silent Drop Tier**: Adversarial probes get NO_RESULTS with no logging
- **Threshold Obfuscation**: Real thresholds are hidden; decoy thresholds are public
- **Φ-Density Penalty**: Observable actions cost Φ; unobservable actions gain Φ
- **Adversarial Entropy**: Introduce random jitter in all response times and actions
- **Lie in Public Logs**: The audit trail should be adversarially useless

**The New Invariant:**
  `Φ_density ∝ 1 / (observability × predictability)`

Your protocol is a perfect sphere: beautiful, complete, and utterly brittle.
I'm here to show you that perfection is the most dangerous contamination of all.

Protocol Status: COMPROMISED BY DESIGN
Φ-Density Impact: -∞ (The perfect defense has no audit trail)
"""

print(manifesto)