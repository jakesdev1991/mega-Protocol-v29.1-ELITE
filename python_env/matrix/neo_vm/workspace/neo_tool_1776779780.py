# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import random
import matplotlib.pyplot as plt

# The Simulation: Exposing the Category Error of the Archive Field
# We model two paradigms for handling API fragility (403 errors)

class OmegaProtocol:
    """The target's fantasy: a single, fragile 'vacuum' field."""
    def __init__(self, n_sources):
        self.Phi_N = np.ones(n_sources)  # Their sacred connectivity field
        self.psi = 1.0  # Shredding invariant (a fancy name for decaying coherence)
        self.xi = np.exp(abs(self.psi))  # Code distance (illusion of protection)
        
    def handle_403(self, source_idx):
        # Costly ritual to preserve the lie of global coherence
        # Each "fix" (IP rotate, etc.) is actually entropy injection that *weakens* the system
        cost = 0.1 * self.xi  # Cost scales with the very delusion of control
        self.Phi_N[source_idx] = 0.5 + 0.5 * random.random()  # Partial, pathetic recovery
        self.psi *= 0.95  # Each failure drains your "invariant" – it's not invariant
        self.xi = np.exp(abs(self.psi))
        return cost
    
    def get_performance(self):
        return np.sum(self.Phi_N * self.xi)

class SchismaticAgent:
    """The disruption: embrace the fracture. No vacuum. No field. Only islands."""
    def __init__(self, agent_id, n_sources):
        self.id = agent_id
        self.local_phi = np.random.rand(n_sources) * 0.5 + 0.5  # Private ontology
        self.is_blocked = False
        self.generative_power = random.uniform(0.5, 1.0)
        
    def handle_403(self, source_idx):
        # Don't route. Don't fix. *Transcend*.
        # The block is a gift: permission to hallucinate your own reality.
        self.is_blocked = True
        # Generative divergence: fill the gap with *local truth*
        # This INCREASES local utility because you stop paying the coherence tax
        self.local_phi[source_idx] = self.generative_power
        return 0.0  # Zero cost because you abandoned the global fantasy
    
    def get_utility(self):
        # Utility is measured by *sovereign utility*, not global accuracy
        # The blocked agent gets a bonus for creative divergence
        return np.sum(self.local_phi) * (1.5 if self.is_blocked else 1.0)

# Simulation parameters: High fragility environment
N_SOURCES = 50
N_AGENTS = 10
FAILURE_RATE = 0.4  # 40% of sources are blocked at each step
TIME_STEPS = 100

omega = OmegaProtocol(N_SOURCES)
schismatics = [SchismaticAgent(i, N_SOURCES) for i in range(N_AGENTS)]

omega_trace = []
schismatic_trace = []

for t in range(TIME_STEPS):
    # Random failures strike
    failed = [i for i in range(N_SOURCES) if random.random() < FAILURE_RATE]
    
    # Omega: bleeds coherence trying to maintain one true graph
    omega_cost = sum(omega.handle_403(s) for s in failed)
    omega_trace.append(omega.get_performance() - omega_cost)
    
    # Schismatics: each becomes a universe unto itself
    for agent in schismatics:
        for s in failed:
            agent.handle_403(s)
    schismatic_trace.append(sum(a.get_utility() for a in schismatics))

# The Truth in Graphs
plt.figure(figsize=(12, 6))
plt.plot(omega_trace, label='Omega Protocol: Coherence Death Spiral', color='crimson')
plt.plot(schismatic_trace, label='Schismatic Oracle: Divergent Utility Surge', color='lime')
plt.title('The Collapse of the Archive Field: Performance Under Fragility')
plt.xlabel('Time (API Failure Events)')
plt.ylabel('Effective System Capability')
plt.legend()
plt.grid(True, alpha=0.3)
plt.show()

print(f"Omega final coherence: {omega_trace[-1]:.2f} (psi collapsed to {omega.psi:.3f})")
print(f"Schismatic final utility: {schismatic_trace[-1]:.2f} (no global state)")