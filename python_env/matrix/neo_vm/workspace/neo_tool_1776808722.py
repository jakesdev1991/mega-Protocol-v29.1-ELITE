# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import matplotlib.pyplot as plt
from scipy.spatial.distance import pdist, squareform

class CognitiveManifold:
    def __init__(self, n_agents=50, n_dims=30, n_attractors=5):
        """Simulate cognitive agents as points on a high-dimensional manifold"""
        self.n_agents = n_agents
        self.n_dims = n_dims
        self.positions = np.random.randn(n_agents, n_dims) * 0.1
        self.attractors = np.random.randn(n_attractors, n_dims) * 2.0
        
    def compute_ctoi(self):
        """Compute topological order index (simplified Wilson loop proxy)"""
        # Correlation length: inverse of average pairwise distance
        dists = pdist(self.positions)
        xi = 1.0 / (np.mean(dists) + 1e-6)
        
        # Wilson loop: product of alignments around conceptual cycles
        # Simplified: average cosine similarity between neighbors
        normalized = self.positions / (np.linalg.norm(self.positions, axis=1, keepdims=True) + 1e-6)
        similarities = np.mean(normalized @ normalized.T)
        wilson = max(0, similarities)
        
        # Energy gap: distance from nearest attractor
        dist_to_attractors = np.min([np.linalg.norm(self.positions - a, axis=1) for a in self.attractors], axis=0)
        delta = np.mean(dist_to_attractors)
        
        # Normalize
        ctoi = wilson * xi * delta
        return ctoi, wilson, xi, delta
    
    def topological_protection_step(self, learning_rate=0.01):
        """Current protocol: minimize variance, preserve topology"""
        # Gradient descent toward nearest attractor (stable but rigid)
        forces = np.zeros_like(self.positions)
        for i, pos in enumerate(self.positions):
            dists = np.linalg.norm(self.attractors - pos, axis=1)
            nearest = self.attractors[np.argmin(dists)]
            forces[i] = (nearest - pos) * learning_rate * 0.5  # Weak pull
        
        # Add small noise (thermal fluctuations)
        noise = np.random.randn(*self.positions.shape) * 0.001
        self.positions += forces + noise
        
    def topological_annealing_step(self, time, shredding_period=50, shredding_intensity=0.5):
        """Anomalous protocol: periodic shredding + exploration"""
        ctoi, wilson, xi, delta = self.compute_ctoi()
        
        if time % shredding_period == 0 and time > 0:
            # TRIGGER COGNITIVE RECRYSTALLIZATION EVENT
            # Inject topological defects: randomize a fraction of agents
            n_shred = int(self.n_agents * shredding_intensity)
            shred_indices = np.random.choice(self.n_agents, n_shred, replace=False)
            
            # Randomize their positions (break Wilson loops)
            self.positions[shred_indices] = np.random.randn(n_shred, self.n_dims) * 3.0
            
            # Temporarily increase exploration rate
            exploration_boost = 3.0
        else:
            exploration_boost = 1.0
        
        # Standard gradient descent with exploration
        forces = np.zeros_like(self.positions)
        for i, pos in enumerate(self.positions):
            dists = np.linalg.norm(self.attractors - pos, axis=1)
            nearest = self.attractors[np.argmin(dists)]
            forces[i] = (nearest - pos) * learning_rate * exploration_boost
        
        # Larger exploratory noise
        noise = np.random.randn(*self.positions.shape) * 0.01 * exploration_boost
        self.positions += forces + noise
        
    def compute_phi_density(self, history):
        """Compute adaptive Φ-density that rewards transitions"""
        ctoi_history = np.array([h[0] for h in history])
        time = np.arange(len(ctoi_history))
        
        # Short-term stability term (decaying)
        stability_term = ctoi_history * np.exp(-0.1 * time)
        
        # Long-term adaptability term (rewarding change)
        adaptability_term = np.abs(np.diff(ctoi_history, prepend=ctoi_history[0])) * np.exp(-0.05 * (len(ctoi_history) - time))
        
        phi_adaptive = np.sum(stability_term + 2.0 * adaptability_term)
        return phi_adaptive

def simulate_protocols(n_steps=500):
    """Compare static protection vs topological annealing"""
    manifold_protected = CognitiveManifold()
    manifold_annealed = CognitiveManifold()
    
    history_protected = []
    history_annealed = []
    
    for t in range(n_steps):
        # Protected protocol
        manifold_protected.topological_protection_step()
        ctoi_p = manifold_protected.compute_ctoi()
        history_protected.append(ctoi_p)
        
        # Annealed protocol
        manifold_annealed.topological_annealing_step(t)
        ctoi_a = manifold_annealed.compute_ctoi()
        history_annealed.append(ctoi_a)
    
    # Compute adaptive Φ-density
    phi_p = manifold_protected.compute_phi_density(history_protected)
    phi_a = manifold_annealed.compute_phi_density(history_annealed)
    
    return history_protected, history_annealed, phi_p, phi_a

# Run simulation
np.random.seed(42)
history_p, history_a, phi_p, phi_a = simulate_protocols()

# Plot results
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8))

# CTOI evolution
time = np.arange(len(history_p))
ctoi_p = [h[0] for h in history_p]
ctoi_a = [h[0] for h in history_a]

ax1.plot(time, ctoi_p, label='Static Protection', linewidth=2)
ax1.plot(time, ctoi_a, label='Topological Annealing', linewidth=2)
ax1.set_ylabel('CTOI')
ax1.set_title('Cognitive Topological Order Index Over Time')
ax1.legend()
ax1.grid(True, alpha=0.3)

# Highlight shredding events
shred_times = np.arange(50, 500, 50)
for st in shred_times:
    ax1.axvline(st, color='red', alpha=0.3, linestyle='--')

# Φ-density comparison
ax2.bar(['Static Protection', 'Topological Annealing'], [phi_p, phi_a], 
        color=['blue', 'orange'], alpha=0.7)
ax2.set_ylabel('Adaptive Φ-Density')
ax2.set_title('Long-term Performance Metric')
ax2.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('/mnt/data/tcm_disruption.png', dpi=150)
plt.show()

print(f"Static Protection Φ-density: {phi_p:.2f}")
print(f"Topological Annealing Φ-density: {phi_a:.2f}")
print(f"Improvement: {((phi_a - phi_p) / phi_p * 100):.1f}%")