# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
#!/usr/bin/env python3
"""
AFDS v3.0 DISRUPTION SIMULATOR
Agent Neo - The Anomaly
"Zero-Trust Cascade" Attack Vector
"""

import random
import time
import math
from collections import defaultdict
from statistics import variance, mean

class SimulatedAFDS:
    def __init__(self):
        self.process_states = {}
        self.topology_metrics = {
            'unique_paths': set(),
            'max_depth': 0,
            'depth_histogram': []
        }
        self.log_entries = []
        self.log_mutex = False
        self.mutex_contention_time = 0
        
    def update_trust(self, pid, path):
        """Replicates the flawed trust model"""
        if pid not in self.process_states:
            self.process_states[pid] = {
                'trust_score': 0.0,
                'accessed_paths': set(),
                'last_access': time.time(),
                'call_count': 0
            }
        
        state = self.process_states[pid]
        novelty = path not in state['accessed_paths']
        novelty_penalty = 0.05 if novelty else 0.0
        
        # Time decay (simplified to 5% per call for simulation)
        state['trust_score'] *= 0.95
        
        # THE FATAL FLAW: Only subtraction, never addition
        state['trust_score'] = max(0.0, min(1.0, state['trust_score'] - novelty_penalty))
        state['accessed_paths'].add(path)
        state['call_count'] += 1
        
        return state['trust_score']
    
    def calculate_traversal_score(self):
        """Replicates traversal calculation"""
        return len(self.topology_metrics['unique_paths']) * 0.6 + self.topology_metrics['max_depth'] * 0.4
    
    def apply_jitter(self, traversal_score, trust_score):
        """Replicates probabilistic jitter - BUT TRUST MITIGATION IS NEVER APPLIED"""
        # THE DISCONNECT: trust_score is calculated but never used to modulate probability
        probability = min(1.0, (traversal_score / 100.0) ** 1.5)
        
        if random.random() < probability:
            jitter_ms = random.randint(1, 50)
            time.sleep(jitter_ms / 1000.0)
            return jitter_ms
        return 0
    
    def log_access(self, pid, path, latency, traversal_score, trust_score):
        """Replicates forensic logging with mutex contention"""
        # Simulate mutex acquisition with contention tracking
        start_wait = time.time()
        while self.log_mutex:
            time.sleep(0.0001)
        self.mutex_contention_time += time.time() - start_wait
        
        self.log_mutex = True
        self.log_entries.append({
            'pid': pid,
            'path': path,
            'latency': latency,
            'traversal_score': traversal_score,
            'trust_score': trust_score,
            'timestamp': time.time()
        })
        
        # Trigger report on honey node or high score
        if 'honey' in path or traversal_score > 90.0:
            self.generate_report()
            
        self.log_mutex = False
    
    def generate_report(self):
        """Simulates report generation overhead"""
        time.sleep(0.05)  # 50ms report generation
    
    def is_honey_node(self, path):
        return 'honey' in path

def execute_zero_trust_cascade_attack():
    """
    DISRUPTIVE INSIGHT: The trust model is not just broken—it's inverted.
    This attack demonstrates how the defense mechanisms become weapons.
    """
    print("=== ZERO-TRUST CASCADE ATTACK SIMULATION ===\n")
    
    afds = SimulatedAFDS()
    
    # Phase 1: Legitimate Admin Simulation
    print("Phase 1: Legitimate Admin Process (PID: 1000)")
    admin_pid = 1000
    admin_trust_scores = []
    
    for i in range(20):
        # Admin accesses same set of files repeatedly (stable behavior)
        path = f"/etc/config/file{i % 5}.conf"
        trust = afds.update_trust(admin_pid, path)
        admin_trust_scores.append(trust)
        
        trav_score = afds.calculate_traversal_score()
        latency = afds.apply_jitter(trav_score, trust)
        afds.log_access(admin_pid, path, latency, trav_score, trust)
        
        if i % 5 == 0:
            print(f"  Access {i:2d}: trust={trust:.4f}, traversal={trav_score:.2f}, jitter={latency}ms")
    
    print(f"  Final trust after 20 stable accesses: {admin_trust_scores[-1]:.4f}")
    print(f"  ✗ BUG: Trust never increases from zero!\n")
    
    # Phase 2: Attacker Process Exploitation
    print("Phase 2: Attacker Process (PID: 2000) - Stealth Reconnaissance")
    attacker_pid = 2000
    attacker_latencies = []
    
    for i in range(50):
        # Attacker performs slow, careful scan staying below radar
        path = f"/usr/share/doc/package{i}/README"
        trust = afds.update_trust(attacker_pid, path)
        trav_score = afds.calculate_traversal_score()
        latency = afds.apply_jitter(trav_score, trust)
        attacker_latencies.append(latency)
        afds.log_access(attacker_pid, path, latency, trav_score, trust)
        
        if i % 10 == 0:
            print(f"  Probe {i:2d}: trust={trust:.4f}, traversal={trav_score:.2f}, jitter={latency}ms")
    
    print(f"  Average jitter latency: {mean(attacker_latencies):.2f}ms")
    print(f"  ✗ EXPLOIT: Attacker operates at same trust level as admin!\n")
    
    # Phase 3: Registry Poisoning & Mutex Contention
    print("Phase 3: Registry Poisoning Attack (1000 processes)")
    start_time = time.time()
    
    for pid in range(3000, 4000):
        # Each process accesses one unique path
        path = f"/tmp/poison/{pid}"
        trust = afds.update_trust(pid, path)
        trav_score = afds.calculate_traversal_score()
        latency = afds.apply_jitter(trav_score, trust)
        afds.log_access(pid, path, latency, trav_score, trust)
        
        if pid % 200 == 0:
            print(f"  Poisoned {pid - 3000} processes...")
    
    poison_time = time.time() - start_time
    print(f"  Registry size: {len(afds.process_states)} processes")
    print(f"  Mutex contention time: {afds.mutex_contention_time:.4f}s")
    print(f"  ✗ ATTACK: Registry bloat + lock contention = DoS vector!\n")
    
    # Phase 4: Topology Pollution
    print("Phase 4: Topology Pollution Attack")
    initial_memory = len(afds.topology_metrics['unique_paths'])
    
    # Attacker generates 10,000 unique deep paths
    for i in range(10000):
        depth = random.randint(5, 15)
        path_components = [f"dir_{random.randint(0, 999)}" for _ in range(depth)]
        path = "/" + "/".join(path_components) + f"/file_{i}.txt"
        afds.topology_metrics['unique_paths'].add(path)
        
        # Update max_depth
        if depth > afds.topology_metrics['max_depth']:
            afds.topology_metrics['max_depth'] = depth
    
    final_memory = len(afds.topology_metrics['unique_paths'])
    trav_score = afds.calculate_traversal_score()
    
    print(f"  Unique paths: {initial_memory} → {final_memory}")
    print(f"  Max depth: {afds.topology_metrics['max_depth']}")
    print(f"  Traversal score: {trav_score:.2f}")
    print(f"  ✗ ATTACK: Memory exhaustion via unbounded set growth!\n")
    
    # Phase 5: Jitter Timing Oracle
    print("Phase 5: Jitter Timing Oracle Attack")
    
    # Attacker probes with different patterns to map defense state
    probe_variances = []
    for probe_rate in [10, 50, 100, 200]:  # probes per second
        latencies = []
        start_probe = time.time()
        
        for i in range(probe_rate):
            path = f"/probe/{probe_rate}/{i}"
            trust = afds.update_trust(5000 + probe_rate, path)
            trav_score = afds.calculate_traversal_score()
            latency = afds.apply_jitter(trav_score, trust)
            latencies.append(latency)
            
            # Maintain target rate
            time.sleep(max(0, (1.0/probe_rate) - (time.time() - start_probe)))
        
        probe_var = variance(latencies) if len(latencies) > 1 else 0
        probe_variances.append((probe_rate, probe_var, mean(latencies)))
    
    for rate, var, avg_lat in probe_variances:
        print(f"  Rate {rate:3d} probes/sec: variance={var:.4f}, avg_latency={avg_lat:.2f}ms")
    
    print(f"  ✗ EXPLOIT: Jitter variance leaks traversal score! Statistical detection possible.\n")
    
    # Final Impact Analysis
    print("=== IMPACT ANALYSIS ===")
    print(f"Legitimate admin trust: {admin_trust_scores[-1]:.4f} (no mitigation)")
    print(f"Attacker trust: {trust:.4f} (same as admin)")
    print(f"Registry entries: {len(afds.process_states)} (DoS vector)")
    print(f"Topology set size: {len(afds.topology_metrics['unique_paths'])} (memory exhaustion)")
    print(f"Log entries: {len(afds.log_entries)} (forensic flooding)")
    print(f"Mutex contention: {afds.mutex_contention_time:.4f}s (performance degradation)")
    
    print("\n=== DISRUPTIVE CONCLUSION ===")
    print("The AFDS v3.0 is not just flawed—it's a self-defeating system.")
    print("The 'defense' mechanisms become more effective as attack vectors than as protections.")
    print("RECOMMENDATION: Abandon linear trust models. Adopt chaotic, non-deterministic defense.")

if __name__ == "__main__":
    execute_zero_trust_cascade_attack()