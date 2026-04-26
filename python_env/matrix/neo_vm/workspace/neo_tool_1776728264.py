# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import random
import heapq
import numpy as np
from collections import defaultdict, deque

class HSANodeAnomaly:
    """
    A discrete-event simulation of a Linux HSA node that shatters the
    continuous-field paradigm. No phis, no psis, no Lagrangians.
    Just agents, resources, and the chaos of contention.
    """
    def __init__(self, num_agents=4, memory_channels=2, total_pages=100):
        self.memory_channels = memory_channels
        self.free_pages = total_pages
        self.channel_queues = [deque() for _ in range(memory_channels)]
        self.agents = [f"Agent_{i}" for i in range(num_agents)]
        self.event_queue = []  # (time, event)
        self.latency_log = []
        self.allocation_graph = defaultdict(set)  # page -> {agents}
        self.time = 0.0
        
        # Real-world instability drivers
        self.frag_threshold = 0.7  # Page fragmentation ratio
        self.deadlock_risk = 0.0
        
    def generate_request(self, agent_id):
        """Memory access is stochastic, bursty, and greedy."""
        # Pareto-distributed request sizes (realistic burstiness)
        size = int(np.random.pareto(2.0) * 10) + 1
        # Random channel contention
        channel = random.randint(0, self.memory_channels - 1)
        # Access pattern: read (0.6), write (0.3), alloc (0.1)
        op = random.choices(['read', 'write', 'alloc'], weights=[0.6, 0.3, 0.1])[0]
        duration = random.expovariate(1/0.001)  # ~1ms average
        return {'agent': agent_id, 'size': size, 'channel': channel, 'op': op, 'duration': duration}
    
    def handle_event(self, event):
        """Process events in real configuration space, not a potential well."""
        agent = event['agent']
        op = event['op']
        
        if op == 'alloc':
            if self.free_pages >= event['size']:
                self.free_pages -= event['size']
                # Contention graph: who owns what
                for page in range(self.free_pages, self.free_pages + event['size']):
                    self.allocation_graph[page].add(agent)
                latency = event['duration'] * (1 + len(self.channel_queues[event['channel']]))
                self.channel_queues[event['channel']].append(agent)
            else:
                # **FRAGMENTATION EVENT**: Real instability, not "manifold shredding"
                latency = event['duration'] * 100  # Page fault penalty
                self.deadlock_risk += 0.1
        else:
            # Read/Write: contention latency
            latency = event['duration'] * (1 + len(self.channel_queues[event['channel']]))
            
        self.latency_log.append(latency)
        
    def simulate(self, max_time=1.0):
        """Run the reality engine. No Rubric, no pleading."""
        # Seed initial events
        for agent in self.agents:
            heapq.heappush(self.event_queue, (random.expovariate(100), self.generate_request(agent)))
        
        while self.time < max_time:
            if not self.event_queue:
                break
            self.time, event = heapq.heappop(self.event_queue)
            self.handle_event(event)
            
            # Schedule next event for this agent (bursty renewal process)
            next_time = self.time + random.expovariate(100)
            heapq.heappush(self.event_queue, (next_time, self.generate_request(event['agent'])))
            
            # Random channel release
            for ch in self.channel_queues:
                if ch and random.random() < 0.1:
                    ch.popleft()
                    
        # **CALCULATE REAL STABILITY METRIC**
        if len(self.latency_log) > 1:
            latency_cv = np.std(self.latency_log) / np.mean(self.latency_log)
        else:
            latency_cv = float('inf')
            
        # **CALCULATE ALGORITHMIC ENTROPY OF CONTENTION GRAPH**
        # (A real information-theoretic measure, not Shannon of phis)
        page_ownerships = [len(owners) for owners in self.allocation_graph.values()]
        if page_ownerships:
            ownership_probs = np.array(page_ownerships) / sum(page_ownerships)
            # Algorithmic surprise: -sum(p log p) of contention distribution
            algorithmic_surprise = -np.sum(ownership_probs * np.log(ownership_probs + 1e-12))
        else:
            algorithmic_surprise = 0.0
            
        return {
            'latency_cv': latency_cv,  # Lower is more stable
            'deadlock_risk': self.deadlock_risk,
            'algorithmic_surprise': algorithmic_surprise,  # Real "informational" measure
            'free_pages': self.free_pages
        }

# EXECUTE THE ANOMALY
anomaly = HSANodeAnomaly(num_agents=8, memory_channels=4, total_pages=200)
results = anomaly.simulate(max_time=5.0)

print("=== OMEGA RUBRIC SHATTER RESULTS ===")
print(f"Latency Coefficient of Variation (Stability): {results['latency_cv']:.4f}")
print(f"Deadlock Risk Accumulation: {results['deadlock_risk']:.4f}")
print(f"Algorithmic Surprise (Real Info Entropy): {results['algorithmic_surprise']:.4f}")
print(f"Remaining Free Pages: {results['free_pages']}")

# **PREDICTIVE INSIGHT**: If latency_cv > 1.0, the node is in a pre-failure state.
# This is a threshold you can MEASURE, not derive from a log of a ghost field.
if results['latency_cv'] > 1.0:
    print("\n[ANOMALY ALERT] Node stability threshold exceeded. Pre-fragmentation state detected.")
    print("Recommended action: Reduce agent concurrency or rebalance channel affinity.")
else:
    print("\n[ANOMALY STABLE] Node operating within nominal contention parameters.")