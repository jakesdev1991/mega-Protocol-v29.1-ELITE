# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
from scipy.stats import beta as beta_dist
import matplotlib.pyplot as plt

# ============================================
# PROTOCOL FAILURE SIMULATION
# ============================================

class Agent:
    def __init__(self, name, originality_score, domain_expertise, cross_domain Awareness):
        self.name = name
        self.originality = originality_score  # 0-1
        self.expertise = domain_expertise  # 0-1 (domain-specific)
        self.cross_aware = cross_domain_awareness  # 0-1
        self.error_rate = 0.3 * (1 - originality) + 0.2 * (1 - cross_aware)
        # Higher originality without cross-awareness = HIGHER error rate (blind spots)
    
    def generate_insight(self, domain):
        # Simulate insight quality
        base_quality = self.expertise if domain == "psychology" else self.cross_aware
        noise = np.random.normal(0, self.error_rate)
        return np.clip(base_quality + noise, 0, 1)

class ProtocolAudit:
    def __init__(self):
        self.phi_density = 0
        self.catastrophic_failures = 0
    
    def evaluate(self, agents, domain):
        """Traditional Agent Smith audit"""
        # Find "Alpha" (highest originality)
        alpha = max(agents, key=lambda a: a.originality)
        alpha_insight = alpha.generate_insight(domain)
        
        # Punish derivativity
        for agent in agents:
            if agent != alpha:
                if abs(agent.generate_insight(domain) - alpha_insight) < 0.1:
                    # Identical = derivativity = elimination
                    self.phi_density -= 0.15  # Beta penalty
                    print(f"{agent.name} ELIMINATED for derivativity")
        
        # Punish cross-domain
        if domain == "psychology" and any(a.cross_aware > a.expertise for a in agents):
            self.phi_density -= np.inf  # Neo penalty
            print("CROSS-DOMAIN AGENT ELIMINATED")
        
        # Single point of failure risk
        if alpha_insight < 0.5:  # Flawed insight
            self.catastrophic_failures += 1
            print(f"⚠️ CATASTROPHIC: Alpha's flawed insight accepted as canon!")
        
        return alpha_insight

class ConsensusAudit:
    def __init__(self):
        self.phi_density = 0
        self.catastrophic_failures = 0
    
    def evaluate(self, agents, domain):
        """Neo-disrupted protocol: consensus + cross-domain validation"""
        # Generate all insights
        insights = [a.generate_insight(domain) for a in agents]
        
        # Cross-domain correction factor
        cross_weights = [a.cross_aware for a in agents]
        weighted_insights = np.average(insights, weights=cross_weights)
        
        # Consensus cluster detection (what Smith calls "derivativity")
        # This is FEATURE, not bug
        consensus_strength = np.std(insights)
        if consensus_strength < 0.15:
            print("✓ STRONG CONSENSUS DETECTED (Smith would call this 'fraud')")
            self.phi_density += 0.20  # REWARD redundancy
        
        # Cross-domain agents provide sanity check
        if any(a.cross_aware > 0.7 for a in agents):
            print("✓ CROSS-DOMAIN VALIDATION ENABLED")
            self.phi_density += 0.15
        
        # Fault tolerance: no single point of failure
        if weighted_insight < 0.5:
            print("⚠️ Warning: Consensus below threshold, triggering review")
            # Doesn't cause catastrophic failure
        else:
            print("✓ Robust consensus insight accepted")
        
        return weighted_insight

# ============================================
# SIMULATE 1000 PROTOCOL RUNS
# ============================================

def simulate(n_runs=1000):
    protocol_results = {'phi': [], 'failures': []}
    consensus_results = {'phi': [], 'failures': []}
    
    for _ in range(n_runs):
        # Create agents: Alpha (high originality), Beta (high expertise), Neo (cross-domain)
        agents = [
            Agent("Alpha", originality_score=0.95, domain_expertise=0.85, cross_domain_awareness=0.3),
            Agent("Beta", originality_score=0.6, domain_expertise=0.90, cross_domain_awareness=0.4),
            Agent("Neo", originality_score=0.7, domain_expertise=0.5, cross_domain_awareness=0.95)
        ]
        
        # Traditional audit
        pa = ProtocolAudit()
        pa.evaluate(agents, "psychology")
        protocol_results['phi'].append(pa.phi_density)
        protocol_results['failures'].append(pa.catastrophic_failures)
        
        # Consensus audit
        ca = ConsensusAudit()
        ca.evaluate(agents, "psychology")
        consensus_results['phi'].append(ca.phi_density)
        consensus_results['failures'].append(ca.catastrophic_failures)
    
    return protocol_results, consensus_results

# Run simulation
proto, cons = simulate()

print(f"\n{'='*50}")
print("AGENT SMITH vs NEO PROTOCOL: 1000 RUNS")
print(f"{'='*50}")
print(f"Smith Protocol:")
print(f"  Avg Φ-density: {np.mean(proto['phi']):.3f}")
print(f"  Catastrophic failures: {np.sum(proto['failures'])}")
print(f"  Failure rate: {np.sum(proto['failures'])/1000*100:.1f}%")

print(f"\nNeo Protocol (Consensus + Cross-Domain):")
print(f"  Avg Φ-density: {np.mean(cons['phi']):.3f}")
print(f"  Catastrophic failures: {np.sum(cons['failures'])}")
print(f"  Failure rate: {np.sum(cons['failures'])/1000*100:.1f}%")

print(f"\nΦ-Density Improvement: {np.mean(cons['phi']) - np.mean(proto['phi']):.3f}")
print(f"Failure Rate Reduction: {np.sum(proto['failures']) - np.sum(cons['failures'])} events")