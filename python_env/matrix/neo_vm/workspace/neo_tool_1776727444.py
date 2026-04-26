# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import matplotlib.pyplot as plt
from scipy.linalg import expm

# Let's model a bureaucracy as a contested topology with competing agents
# Each agent has their own "policy projection operator" they can modify

class ContestedBureaucracy:
    def __init__(self, n_agents=5, n_states=10):
        self.n_agents = n_agents
        self.n_states = n_states
        
        # Each agent has their own subjective "reality" (subconscious manifold)
        self.agent_realities = [self._random_unitary() for _ in range(n_agents)]
        
        # Each agent controls a piece of the "policy" projection operator
        self.policy_blocks = [self._random_projector(n_states // n_agents) 
                             for _ in range(n_agents)]
        
        # Power dynamics: each agent has influence weight
        self.power_weights = np.random.dirichlet(np.ones(n_agents))
        
        # System state: superposition of all agent realities weighted by power
        self.psi_system = self._compute_system_state()
        
    def _random_unitary(self):
        """Generate a random unitary matrix (subconscious manifold)"""
        a = np.random.randn(self.n_states, self.n_states) + \
             1j * np.random.randn(self.n_states, self.n_states)
        q, r = np.linalg.qr(a)
        return q
    
    def _random_projector(self, dim):
        """Generate a random projection operator for policy block"""
        v = np.random.randn(dim, dim) + 1j * np.random.randn(dim, dim)
        v = v / np.linalg.norm(v, axis=0)
        return v @ v.conj().T
    
    def _compute_system_state(self):
        """System state is weighted superposition of agent realities"""
        psi = np.zeros(self.n_states, dtype=complex)
        for i, reality in enumerate(self.agent_realities):
            weight = self.power_weights[i]
            eigvals, eigvecs = np.linalg.eigh(reality)
            dominant_state = eigvecs[:, -1]
            psi += weight * dominant_state
        return psi / np.linalg.norm(psi)
    
    def compute_cod(self):
        """Compute Chain Overlap Density - but it's contested"""
        P_con = np.zeros((self.n_states, self.n_states), dtype=complex)
        idx = 0
        for i, block in enumerate(self.policy_blocks):
            block_dim = block.shape[0]
            P_con[idx:idx+block_dim, idx:idx+block_dim] = block * self.power_weights[i]
            idx += block_dim
        
        cod = np.vdot(self.psi_system, P_con @ self.psi_system)
        return np.real(cod)
    
    def apply_stabilization(self, urgency=0.1, safety=0.1):
        """Apply the naive stabilization operator"""
        self.power_weights = self.power_weights * (1 + urgency)
        self.power_weights = self.power_weights / np.sum(self.power_weights)
        
        for i in range(self.n_agents):
            self.policy_blocks[i] = (1 - safety) * self.policy_blocks[i] + \
                                   safety * np.eye(self.policy_blocks[i].shape[0])
    
    def apply_topological_raid(self, target_agent, raid_strength=0.3):
        """Disruptive operator: raid one agent's policy block to extract value"""
        block_dim = self.policy_blocks[target_agent].shape[0]
        noise = np.random.randn(block_dim, block_dim) + \
                1j * np.random.randn(block_dim, block_dim)
        self.policy_blocks[target_agent] = (1 - raid_strength) * self.policy_blocks[target_agent] + \
                                            raid_strength * noise / np.linalg.norm(noise)
        
        extracted_power = self.power_weights[target_agent] * raid_strength
        redist = extracted_power / (self.n_agents - 1)
        for i in range(self.n_agents):
            if i == target_agent:
                self.power_weights[i] *= (1 - raid_strength)
            else:
                self.power_weights[i] += redist
        
        self.psi_system = self._compute_system_state()
    
    def measure_fragmentation(self):
        """Measure how fragmented the system is"""
        overlaps = []
        for i in range(self.n_agents):
            for j in range(i+1, self.n_agents):
                _, eigvecs_i = np.linalg.eigh(self.agent_realities[i])
                _, eigvecs_j = np.linalg.eigh(self.agent_realities[j])
                psi_i = eigvecs_i[:, -1]
                psi_j = eigvecs_j[:, -1]
                overlap = np.abs(np.vdot(psi_i, psi_j))**2
                overlaps.append(overlap)
        return 1 - np.mean(overlaps)

# Run simulation
np.random.seed(42)
bureaucracy = ContestedBureaucracy(n_agents=5, n_states=15)

print("=== INITIAL STATE ===")
print(f"COD: {bureaucracy.compute_cod():.3f}")
print(f"Fragmentation: {bureaucracy.measure_fragmentation():.3f}")
print(f"Power distribution: {bureaucracy.power_weights}")

# Apply stabilization (target's approach)
print("\n=== AFTER STABILIZATION ===")
for _ in range(10):
    bureaucracy.apply_stabilization(urgency=0.05, safety=0.1)
print(f"COD: {bureaucracy.compute_cod():.3f}")
print(f"Fragmentation: {bureaucracy.measure_fragmentation():.3f}")
print(f"Power distribution: {bureaucracy.power_weights}")

# Apply topological raids (disruptive approach)
print("\n=== AFTER TOPOLOGICAL RAIDS ===")
bureaucracy2 = ContestedBureaucracy(n_agents=5, n_states=15)
np.random.seed(42)

raid_history = []
for step in range(20):
    target = np.argmax(bureaucracy2.power_weights)
    bureaucracy2.apply_topological_raid(target, raid_strength=0.15)
    
    raid_history.append({
        'step': step,
        'cod': bureaucracy2.compute_cod(),
        'fragmentation': bureaucracy2.measure_fragmentation(),
        'entropy': -np.sum(bureaucracy2.power_weights * np.log(bureaucracy2.power_weights + 1e-10))
    })

final_state = raid_history[-1]
print(f"COD: {final_state['cod']:.3f}")
print(f"Fragmentation: {final_state['fragmentation']:.3f}")
print(f"Power entropy: {final_state['entropy']:.3f}")
print(f"Power distribution: {bureaucracy2.power_weights}")

# Plot
steps = [r['step'] for r in raid_history]
cod_vals = [r['cod'] for r in raid_history]
frag_vals = [r['fragmentation'] for r in raid_history]

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
ax1.plot(steps, cod_vals, 'r-', linewidth=2)
ax1.set_xlabel('Raid Steps')
ax1.set_ylabel('Chain Overlap Density (COD)')
ax1.set_title('COD Collapses Under Raids')
ax1.grid(True, alpha=0.3)

ax2.plot(steps, frag_vals, 'b-', linewidth=2)
ax2.set_xlabel('Raid Steps')
ax2.set_ylabel('Fragmentation Index')
ax2.set_title('Fragmentation Accelerates')
ax2.grid(True, alpha=0.3)

plt.tight_layout()
plt.show()