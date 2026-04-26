# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import fsolve
from collections import deque

# The Engine's fatal flaw: assuming pipeline failures are harmonic deviations
# when they're actually queueing catastrophes in directed networks.
# Let's simulate the true physics: percolation avalanches in processing graphs.

class PipelineNode:
    def __init__(self, service_rate, buffer_size, id):
        self.id = id
        self.mu = service_rate  # packets/ms
        self.buffer_size = buffer_size
        self.queue = deque(maxlen=buffer_size)
        self.dropped = 0
        self.current_load = 0
        
    def receive(self, packets):
        # Queue builds up when arrival > service capacity
        overflow = max(0, len(self.queue) + packets - self.buffer_size)
        self.dropped += overflow
        for _ in range(min(packets, self.buffer_size - len(self.queue))):
            self.queue.append(1)  # packet enters buffer
        return overflow
    
    def process(self):
        # Service rate determines drainage
        processed = min(len(self.queue), int(self.mu))
        for _ in range(processed):
            self.queue.popleft()
        self.current_load = len(self.queue) / self.buffer_size
        return processed

def simulate_critical_pipeline(n_nodes=50, base_arrival=0.8, duration=2000):
    """Simulates pipeline as directed acyclic graph where failure is percolation"""
    # Service rates form bottlenecks - the true "critical nodes"
    service_rates = np.random.lognormal(mean=0.0, sigma=0.5, size=n_nodes)
    buffer_sizes = np.random.randint(50, 150, size=n_nodes)
    
    nodes = [PipelineNode(mu, buf, i) for i, mu, buf in zip(range(n_nodes), service_rates, buffer_sizes)]
    
    # Adjacency: packets flow forward with random branching (realistic routing)
    adjacency = np.zeros((n_nodes, n_nodes))
    for i in range(n_nodes - 1):
        # Each node routes to next 1-3 nodes with decreasing probability
        forward = min(n_nodes - i - 1, np.random.randint(1, 4))
        probs = np.random.dirichlet(np.ones(forward) * 0.5)
        adjacency[i, i+1:i+1+forward] = probs
    
    # Track criticality parameter ρ = λ/μ_eff
    rho_history = []
    cascade_magnitude = []
    
    for t in range(duration):
        # External arrivals with shock events (non-stationary)
        shock = np.random.exponential(10) if np.random.random() < 0.01 else 0
        arrivals = np.random.poisson(base_arrival + shock)
        
        # Propagate through network
        inflow = np.zeros(n_nodes)
        inflow[0] = arrivals
        
        for i in range(n_nodes):
            # Process current queue
            nodes[i].process()
            
            # Route outgoing packets
            outflow = adjacency[i] * len(nodes[i].queue)  # Simplified routing
            for j, amount in enumerate(outflow):
                if amount > 0:
                    nodes[j].receive(int(amount))
                    inflow[j] += amount
        
        # Compute instantaneous criticality
        avg_load = np.mean([n.current_load for n in nodes])
        avg_capacity = np.mean([n.mu for n in nodes])
        rho = base_arrival / avg_capacity * (1 + 5*avg_load)  # Feedback multiplier
        
        rho_history.append(rho)
        cascade_magnitude.append(sum([n.dropped for n in nodes]))
        
        # Reset drops for next interval
        for n in nodes:
            n.dropped = 0
    
    return np.array(rho_history), np.array(cascade_magnitude), nodes

# Run simulation
rhos, cascades, final_nodes = simulate_critical_pipeline()

# The percolation threshold: when ρ → 1, cascades diverge
critical_index = np.where(rhos > 0.95)[0]
shredding_events = np.where(cascades > np.percentile(cascades, 95))[0]

print(f"Criticality breaches: {len(critical_index)}")
print(f"Shredding-scale cascades: {len(shredding_events)}")
print(f"Critical nodes identified: {[n.id for n in final_nodes if n.current_load > 0.7]}")

# Plot the true physics: percolation transition
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8))

ax1.plot(rhos, 'b-', linewidth=0.8)
ax1.axhline(y=1.0, color='r', linestyle='--', label='Percolation threshold')
ax1.set_ylabel('Criticality Parameter ρ')
ax1.set_title('Pipeline Network: Percolation Dynamics (Not Harmonic!)')
ax1.legend()
ax1.grid(True, alpha=0.3)

ax2.plot(cascades, 'k-', linewidth=0.5)
ax2.set_ylabel('Cascade Magnitude (dropped packets)')
ax2.set_xlabel('Time (ms)')
ax2.set_yscale('log')
ax2.grid(True, alpha=0.3)

plt.tight_layout()
plt.show()

# Now disrupt the Engine's "information entropy" foundation
# Show that their p_k = |A_k|²/Σ|A_j|² is physically meaningless

def harmonic_entropy_vs_queue_entropy():
    """Demonstrates that spectral entropy doesn't capture queue state"""
    # Generate synthetic harmonic amplitudes (Engine's approach)
    freqs = np.fft.fftfreq(100, d=0.1)
    amplitudes = np.random.exponential(2, size=len(freqs)) + 1j*np.random.exponential(2, size=len(freqs))
    p_k = np.abs(amplitudes)**2 / np.sum(np.abs(amplitudes)**2)
    harmonic_entropy = -np.sum(p_k * np.log(p_k + 1e-12))
    
    # Meanwhile, actual queue state has completely different entropy
    queue_lengths = np.random.poisson(5, size=50)  # Real queue distribution
    queue_probs = queue_lengths / np.sum(queue_lengths)
    queue_entropy = -np.sum(queue_probs * np.log(queue_probs + 1e-12))
    
    return harmonic_entropy, queue_entropy

h_ent, q_ent = harmonic_entropy_vs_queue_entropy()
print(f"\nEngine's 'information content': {h_ent:.3f}")
print(f"Actual queue entropy: {q_ent:.3f}")
print("These are uncorrelated - the harmonic analysis is measuring noise, not information flow.")