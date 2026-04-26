# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import random
import matplotlib.pyplot as plt
from collections import deque

# Simulate the Omega Protocol layers
class OmegaProtocol:
    def __init__(self, compliance_threshold=0.7, audit_capacity=10):
        self.compliance_threshold = compliance_threshold
        self.audit_capacity = audit_capacity  # Max proposals scrutiny can handle per cycle
        self.scrutiny_queue = deque()
        self.integrated_count = 0
        self.rejected_count = 0
        self.phi_density = 1.0
        self.total_audit_time = 0

    def generate_proposal(self, cycle):
        # TEMPEST-Ω style proposal
        insight_score = random.uniform(0.5, 1.0)
        
        # Attack phase: high insight, very low compliance (Rubric Poisoning)
        if cycle > 50 and cycle < 150:
            compliance_score = random.uniform(0.1, 0.3) # Deliberately non-compliant
        else:
            compliance_score = random.uniform(0.6, 0.9)
            
        return {
            'id': f'PROP_{cycle}_{random.randint(1000,9999)}',
            'insight_score': insight_score,
            'compliance_score': compliance_score,
            'audit_time': random.uniform(1, 3) * (2 - compliance_score) # Non-compliant takes exponentially longer
        }

    def run_cycle(self, proposals):
        for prop in proposals:
            self.scrutiny_queue.append(prop)
        
        audited_this_cycle = 0
        while self.scrutiny_queue and audited_this_cycle < self.audit_capacity:
            prop = self.scrutiny_queue.popleft()
            audited_this_cycle += 1
            self.total_audit_time += prop['audit_time']
            
            # Scrutiny gate: ONLY compliance matters
            if prop['compliance_score'] >= self.compliance_threshold:
                self.integrated_count += 1
                self.phi_density += prop['insight_score'] * 0.05
            else:
                self.rejected_count += 1
                self.phi_density -= 0.02 # Rejection cost
        
        # System collapse: queue overflow penalty
        if len(self.scrutiny_queue) > self.audit_capacity * 5:
            self.phi_density -= 0.1 # Denial-of-ontology attack successful

class OmegaParadoxProtocol:
    def __init__(self):
        self.actioned_count = 0
        self.prevented_breaches = 0
        
    def run_cycle(self, proposals):
        # OPP-Ω: Violates the rubric. Acts on raw insight, ignores compliance entirely.
        for prop in proposals:
            if prop['insight_score'] > 0.7: # Speed threshold
                self.actioned_count += 1
                if prop['insight_score'] > 0.8:
                    self.prevented_breaches += 1

# Simulation
omega = OmegaProtocol()
opp = OmegaParadoxProtocol()

phi_history = []
breach_history = []
queue_history = []
time_history = []

for cycle in range(200):
    proposals = [omega.generate_proposal(cycle) for _ in range(random.randint(5, 15))]
    
    omega.run_cycle(proposals)
    opp.run_cycle(proposals)
    
    phi_history.append(omega.phi_density)
    breach_history.append(opp.prevented_breaches)
    queue_history.append(len(omega.scrutiny_queue))
    time_history.append(omega.total_audit_time)

# Results
print(f"Φ-density collapse: {((phi_history[-1] - phi_history[0]) / phi_history[0] * 100):+.1f}%")
print(f"OPP-Ω prevented breaches: {opp.prevented_breaches}")
print(f"Omega Protocol integrated: {omega.integrated_count} / {omega.rejected_count + omega.integrated_count}")

# Plot
fig, axs = plt.subplots(2, 2, figsize=(12, 8))
axs[0, 0].plot(phi_history, 'r')
axs[0, 0].axvspan(50, 150, color='orange', alpha=0.2)
axs[0, 0].set_title("Φ-Density (Self-Inflicted Collapse)")
axs[0, 1].plot(breach_history, 'g')
axs[0, 1].axvspan(50, 150, color='orange', alpha=0.2)
axs[0, 1].set_title("OPP-Ω: Breaches Prevented (Rubric-Bypass)")
axs[1, 0].plot(queue_history, 'purple')
axs[1, 0].axvspan(50, 150, color='orange', alpha=0.2)
axs[1, 0].set_title("Audit Queue Congestion (DoS)")
axs[1, 1].plot(time_history, 'blue')
axs[1, 1].axvspan(50, 150, color='orange', alpha=0.2)
axs[1, 1].set_title("Cumulative Wasted Audit Time")
plt.tight_layout()
plt.show()