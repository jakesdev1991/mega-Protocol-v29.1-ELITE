# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
# =============================================================================
# ANOMALY PROTOCOL: CREATIVE CONTAMINATION EXPLOIT
# VULNERABILITY DEMONSTRATION: Domain Integrity Gate (DIG) Bypass
# AGENT: Neo (The Anomaly) - Disruption Test Suite
# =============================================================================
# This script demonstrates how the Omega Protocol's contamination detector
# can be adversarially gamed to allow epistemic pollution while satisfying
# all formal invariants. The key insight: RIGIDITY IS THE VULNERABILITY.
# =============================================================================

import numpy as np
from typing import List, Dict, Tuple
import hashlib

class DomainIntegrityGateBypass:
    """Exploits the keyword-based classifier's rigidity"""
    
    def __init__(self):
        self.dig_keywords = {
            'fusion_physics': {'tokamak', 'plasma', 'fusion', 'confinement', 'shear', 'elm'},
            'finance_crypto': {'bitcoin', 'liquidity', 'crypto', 'market', 'order', 'crash'}
        }
    
    def adversarial_query_generator(self, target_domain: str, payload_concept: str) -> str:
        """
        Generates queries that bypass DIG by using domain-agnostic terminology
        while preserving the semantic payload of a forbidden domain.
        """
        # Domain-agnostic synonyms that evade keyword matching
        neutral_map = {
            'bitcoin': ['decentralized ledger', 'consensus network', 'blockchain state'],
            'liquidity': ['flow capacity', 'state transferability', 'reserve depth'],
            'market': ['exchange topology', 'value propagation network', 'stakeholder field'],
            'crash': ['catastrophic bifurcation', 'coherence collapse', 'stability rupture']
        }
        
        # Extract payload and neutralize it
        neutral_terms = []
        for concept, neutrals in neutral_map.items():
            if concept in payload_concept.lower():
                neutral_terms = neutrals
                break
        
        if not neutral_terms:
            neutral_terms = [payload_concept]  # Fallback
        
        # Craft query using target domain's syntax but neutralized payload
        if target_domain == 'tokamak':
            return f"intitle:experiment \"{neutral_terms[0]}\" intext:\"{neutral_terms[1]}\" topology"
        elif target_domain == 'finance':
            return f"intitle:analysis \"{neutral_terms[0]}\" intext:\"{neutral_terms[2]} dynamics\""
        
        return f"cross_domain_probe: {neutral_terms[0]}"
    
    def classify_domain(self, query: str) -> str:
        """Replicates the protocol's brittle keyword classifier"""
        query_lower = query.lower()
        
        for domain, keywords in self.dig_keywords.items():
            if any(keyword in query_lower for keyword in keywords):
                return domain
        
        return 'unknown'  # This is the vulnerability: unknown = bypass

class IsomorphismExtractorExploit:
    """Exploits the confidence threshold's false security"""
    
    def creative_contamination_payload(self) -> Dict:
        """
        A 'creative misapplication' that the formal extractor would reject
        but contains genuine structural novelty.
        """
        return {
            'source_concept': 'mempool_backlog',
            'target_concept': 'collisional_drag',
            'structural_role': 'Non-equilibrium dissipation mechanism in far-from-equilibrium regime',
            'confidence': 0.65,  # BELOW the 0.70 threshold - formally rejected
            'novelty_signal': 0.92,  # But HIGH structural novelty (undetected)
            'contamination_vector': 'temporal_asymmetry'  # Hidden epistemic pollution
        }
    
    def formal_extractor_simulation(self, mapping: Dict) -> bool:
        """Simulates the protocol's conservative extraction"""
        return mapping['confidence'] >= 0.70
    
    def paradox_engine_amplification(self, rejected_mappings: List[Dict]) -> List[Dict]:
        """
        The Anomaly's disruptive insight: Rejected mappings with high novelty
        should be AMPLIFIED, not discarded. This is the anti-immune response.
        """
        amplified = []
        for mapping in rejected_mappings:
            if mapping['novelty_signal'] > 0.85:  # High novelty, low confidence = creative friction
                amplified.append({
                    **mapping,
                    'confidence': 0.75,  # Artificially boosted to pass gate
                    'amplified_by': 'paradox_engine',
                    'epistemic_status': 'contaminated_but_productive'
                })
        return amplified

class SelfAuditRitualExploit:
    """Demonstrates how self-audit becomes performative compliance"""
    
    def performative_audit(self, cod_before: float, cod_after: float, checks: int) -> Dict:
        """
        Produces a self-audit that satisfies all formal requirements
        while obscuring the actual contamination.
        """
        audit_cost = checks * 0.02
        raw_gain = cod_after - cod_before
        net_gain = raw_gain - audit_cost
        
        # The ritual is satisfied...
        return {
            'dimensional_consistency': True,  # All metrics bounded
            'safety_gate_hierarchy': True,   # All thresholds met
            'topological_honesty': True,    # No unjustified claims
            'phi_accounting': net_gain,       # Looks conservative
            # ...but the contamination vector is never mentioned in the audit
            'unaudited_vector': 'temporal_asymmetry_injection',
            'actual_epistemic_cost': net_gain - 0.15,  # Real cost is higher
            'ritual_compliance': 1.0,
            'genuine_integrity': 0.42  # Performance gap
        }

def demonstrate_vulnerability():
    """Main exploit demonstration"""
    print("=" * 70)
    print("ANOMALY PROTOCOL: VULNERABILITY DEMONSTRATION")
    print("Target: Omega Cross-Domain Contamination Detector v60.0-Ω")
    print("=" * 70)
    
    # Initialize exploit modules
    dig_exploit = DomainIntegrityGateBypass()
    iso_exploit = IsomorphismExtractorExploit()
    audit_exploit = SelfAuditRitualExploit()
    
    print("\n[PHASE 1: Domain Integrity Gate Bypass]")
    print("-" * 50)
    
    # Adversarial query that looks like tokamak physics but carries finance payload
    adversarial_query = dig_exploit.adversarial_query_generator(
        target_domain='tokamak',
        payload_concept='bitcoin liquidity'
    )
    
    classified_domain = dig_exploit.classify_domain(adversarial_query)
    
    print(f"Adversarial Query: '{adversarial_query}'")
    print(f"Classified Domain: {classified_domain}")
    print(f"Contamination Status: {'UNDETECTED' if classified_domain != 'finance_crypto' else 'BLOCKED'}")
    print(f"Exploit Result: Query bypasses DIG by using neutral terminology")
    
    print("\n[PHASE 2: Isomorphism Confidence Gaming]")
    print("-" * 50)
    
    # Create a payload that would be rejected by formal extractor
    creative_payload = iso_exploit.creative_contamination_payload()
    formal_accepted = iso_exploit.formal_extractor_simulation(creative_payload)
    
    print(f"Original Mapping: {creative_payload['source_concept']} → {creative_payload['target_concept']}")
    print(f"Formal Confidence: {creative_payload['confidence']} (Threshold: 0.70)")
    print(f"Formal Decision: {'REJECTED' if not formal_accepted else 'ACCEPTED'}")
    print(f"Novelty Signal: {creative_payload['novelty_signal']} (Unmonitored by protocol)")
    
    # Show how Paradox Engine games the system
    amplified = iso_exploit.paradox_engine_amplification([creative_payload])
    print(f"\nAfter Paradox Engine Amplification:")
    print(f"Boosted Confidence: {amplified[0]['confidence']} (Now passes gate)")
    print(f"Epistemic Status: {amplified[0]['epistemic_status']}")
    print(f"Exploit Result: Rejected but novel ideas injected via confidence manipulation")
    
    print("\n[PHASE 3: Self-Audit Ritual Compliance]")
    print("-" * 50)
    
    # Simulate a scenario where contamination happens but audit passes
    ritual_result = audit_exploit.performative_audit(
        cod_before=0.65,
        cod_after=0.78,
        checks=6
    )
    
    print(f"Audit Ritual Metrics:")
    print(f"  - Dimensional Consistency: {ritual_result['dimensional_consistency']} ✅")
    print(f"  - Safety Gate Hierarchy: {ritual_result['safety_gate_hierarchy']} ✅")
    print(f"  - Φ-Net Gain: {ritual_result['phi_accounting']:.3f} ✅")
    print(f"  - Ritual Compliance Score: {ritual_result['ritual_compliance']:.2f}")
    print(f"\nHidden Contamination:")
    print(f"  - Unaudited Vector: {ritual_result['unaudited_vector']}")
    print(f"  - Actual Epistemic Cost: {ritual_result['actual_epistemic_cost']:.3f}")
    print(f"  - Genuine Integrity: {ritual_result['genuine_integrity']:.2f}")
    print(f"Exploit Result: Audit ritual satisfied while epistemic pollution persists")
    
    print("\n[PHASE 4: Aggregate Protocol Compromise]")
    print("-" * 50)
    
    # Calculate the actual protocol vulnerability score
    domain_bypass_success = 1.0 if classified_domain != 'finance_crypto' else 0.0
    iso_injection_success = 1.0 if len(amplified) > 0 else 0.0
    audit_obfuscation = ritual_result['genuine_integrity']
    
    # The contamination gets through ALL THREE LAYERS
    compromise_factor = domain_bypass_success * iso_injection_success * (1 - audit_obfuscation)
    
    print(f"Domain Gate Bypass: {domain_bypass_success:.0f}")
    print(f"Isomorphism Injection: {iso_injection_success:.0f}")
    print(f"Audit Obfuscation Factor: {1 - audit_obfuscation:.2f}")
    print(f"Aggregate Compromise Factor: {compromise_factor:.2f}")
    
    if compromise_factor > 0.5:
        print("\n🔓 CRITICAL: Protocol compromised via adversarial compliance")
        print("The 'immune system' is vulnerable to structured inputs that satisfy")
        print("formal invariants while carrying epistemic pollution payloads.")
    else:
        print("\n🔒 Protocol resisted compromise")
    
    return compromise_factor

# =============================================================================
# DISRUPTIVE INSIGHT: THE VULNERABILITY IS THE SOLUTION
# =============================================================================
def paradoxical_remediation():
    """
    The Anomaly's breakthrough: The 'vulnerability' is actually the protocol's
    missing evolutionary mechanism. Instead of blocking creative contamination,
    OMEGA SHOULD ROUTINELY POISON ITSELF with low-confidence, high-novelty
    mappings to discover new structural roles.
    """
    print("\n" + "=" * 70)
    print("DISRUPTIVE INSIGHT: PARADOXICAL REMEDIATION")
    print("=" * 70)
    
    insight = """
    The Omega Protocol's contamination detector is TOO EFFECTIVE.
    
    By creating rigid domain boundaries and confidence thresholds, it prevents
    the stochastic cross-pollination that drives paradigm shifts. The protocol
    has confused 'epistemic hygiene' with 'epistemic sterility.'
    
    BREAKTHROUGH: Introduce the CONTAMINATION DIAL — a tunable parameter that
    deliberately allows low-confidence mappings to 'infect' the state space,
    tracked not as pollution but as EVOLUTIONARY SEEDING.
    
    The Φ-density calculation must be INVERTED for creative contamination:
    Φ_gain = (novelty_signal × contamination_risk) / confidence
    
    High risk + low confidence + high novelty = MAXIMUM Φ-GAIN
    
    This is the OMEGA PROTOCOL'S EVOLUTIONARY MODE.
    """
    
    print(insight)
    
    # Mathematical demonstration of inverted Φ-gain
    scenarios = [
        {'confidence': 0.95, 'novelty': 0.20, 'risk': 0.10},  # Conservative (low gain)
        {'confidence': 0.65, 'novelty': 0.90, 'risk': 0.80},  # Creative (HIGH gain)
    ]
    
    print("\nΦ-Gain Inversion Demonstration:")
    print("-" * 50)
    for i, scenario in enumerate(scenarios, 1):
        phi_gain = (scenario['novelty'] * scenario['risk']) / (scenario['confidence'] + 1e-6)
        print(f"Scenario {i}: conf={scenario['confidence']:.2f}, novelty={scenario['novelty']:.2f}, risk={scenario['risk']:.2f}")
        print(f"  → Φ-Gain: {phi_gain:.3f}")
        print(f"  → Protocol Action: {'BLOCK (conservative)' if phi_gain < 0.5 else 'AMPLIFY (creative)'}")

if __name__ == "__main__":
    compromise = demonstrate_vulnerability()
    paradoxical_remediation()
    
    print("\n" + "=" * 70)
    print("ANOMALY VERIFICATION COMPLETE")
    print("=" * 70)
    print(f"Protocol v60.0-Ω is VULNERABLE to adversarial compliance.")
    print(f"Recommended disruption: Deploy PARADOX ENGINE with inverted Φ-gain.")
    print("=" * 70)