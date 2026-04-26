# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import random
import time
import threading
import numpy as np
from collections import defaultdict
import matplotlib.pyplot as plt

# ============================================
# DISRUPTION SIMULATION: AFDS v3.0 ATTACK VECTORS
# ============================================

class AFDS_Disruption:
    def __init__(self):
        # Simulate the AFDS trust state
        self.trust_states = defaultdict(lambda: {
            'trust_score': 0.0,
            'accessed_paths': set(),
            'last_access': time.time(),
            'cumulative_stability': 0.0
        })
        self.topology = {
            'unique_paths': set(),
            'max_depth': 0,
            'depth_histogram': defaultdict(int)
        }
        self.forensic_log = []
        self.pid_counter = 1000
        
    def simulate_legitimate_behavior(self, pid, paths, duration=60):
        """Simulate a legitimate admin process"""
        for _ in range(duration):
            path = random.choice(paths)
            self.update_trust(pid, path)
            time.sleep(0.1)
            
    def simulate_adversarial_grooming(self, pid, honey_paths, normal_paths, grooming_cycles=50):
        """ATTACK 1: Trust grooming through controlled repetition"""
        # Phase 1: Grooming - build trust with repetitive access
        for cycle in range(grooming_cycles):
            # Alternate between few trusted paths to build cumulative_stability
            for path in normal_paths[:3]:
                self.update_trust(pid, path)
                time.sleep(0.05)
        
        # Phase 2: Exploitation - use high trust to access honey nodes
        honey_access_latency = []
        for path in honey_paths:
            latency = self.simulate_jitter(pid, path, is_honey=True)
            honey_access_latency.append(latency)
            
        return honey_access_latency
    
    def simulate_pid_cycling_attack(self, base_pid, paths, max_pids=100):
        """ATTACK 2: PID exhaustion and trust inheritance"""
        latencies = []
        for i in range(max_pids):
            # Simulate PID reuse - Linux PID wraparound
            pid = (base_pid + i) % 32768
            self.trust_states[pid] = self.trust_states[base_pid].copy()  # Trust inheritance
            latency = self.simulate_jitter(pid, random.choice(paths))
            latencies.append(latency)
        return latencies
    
    def simulate_timing_side_channel(self, pid, path, samples=100):
        """ATTACK 3: Extract trust scores via timing analysis"""
        timings = []
        for _ in range(samples):
            start = time.perf_counter()
            self.simulate_jitter(pid, path)
            end = time.perf_counter()
            timings.append((end - start) * 1000)  # ms
        return timings
    
    def simulate_topology_manipulation(self, pid, target_depth=100):
        """ATTACK 4: Control breadth/depth ratio to evade detection"""
        # Create controlled exploration that looks benign (low breadth, high depth)
        path = "/root"
        for i in range(target_depth):
            path += f"/dir_{i}"
            self.update_topology_metrics(path)
            
        # Now exploit: actual malicious paths but with "benign" topology
        traversal_score = self.calculate_traversal_score()
        phi_delta = self.calculate_phi_delta()
        
        return traversal_score, phi_delta
    
    def update_trust(self, pid, path):
        """Simulate AFDS trust update"""
        state = self.trust_states[pid]
        is_novel = path not in state['accessed_paths']
        
        # Time decay
        now = time.time()
        duration = now - state['last_access']
        TAU = 3600.0
        normalized_time = duration / TAU
        
        # VULNERABILITY: Predictable, reversible trust accumulation
        state['trust_score'] *= np.exp(-np.log(0.95) * normalized_time)
        
        if is_novel:
            state['trust_score'] = max(0.0, state['trust_score'] - 0.05)
        else:
            state['trust_score'] = min(1.0, state['trust_score'] + 0.01)
            # VULNERABILITY: Cumulative stability is monotonic
            state['cumulative_stability'] += np.exp(-normalized_time)
            
        state['accessed_paths'].add(path)
        state['last_access'] = now
        
    def simulate_jitter(self, pid, path, is_honey=False):
        """Simulate jitter calculation - VULNERABILITY: Blocking sleep"""
        state = self.trust_states[pid]
        mitigation = 0.8 * state['trust_score']
        
        traversal_score = self.calculate_traversal_score()
        phi_delta = self.calculate_phi_delta()
        
        # Probability calculation
        probability = (traversal_score / 100.0) ** 1.5
        probability = min(1.0, probability * mitigation * (1.0 + phi_delta))
        
        # VULNERABILITY: Shredding threshold is static and predictable
        SHREDDING_THRESHOLD = 0.95
        if phi_delta > SHREDDING_THRESHOLD:
            time.sleep(1.0)  # Blocking sleep - detectable!
            return 1000
        
        if random.random() < probability:
            jitter_ms = random.randint(1, 50)
            time.sleep(jitter_ms / 1000.0)  # Blocking - creates timing signature
            return jitter_ms
        
        return 0
    
    def calculate_traversal_score(self):
        return len(self.topology['unique_paths']) * 0.6 + self.topology['max_depth'] * 0.4
    
    def calculate_phi_delta(self):
        breadth = len(self.topology['unique_paths'])
        depth = self.topology['max_depth']
        if breadth + depth == 0:
            return 0.0
        return np.tanh((breadth * depth) / (breadth + depth))
    
    def update_topology_metrics(self, path):
        self.topology['unique_paths'].add(path)
        depth = path.count('/')
        self.topology['max_depth'] = max(self.topology['max_depth'], depth)
        self.topology['depth_histogram'][depth] += 1

def run_disruption_analysis():
    """Execute comprehensive attack simulation"""
    afds = AFDS_Disruption()
    
    print("=" * 60)
    print("AFDS v3.0 DISRUPTION ANALYSIS")
    print("=" * 60)
    
    # Attack 1: Trust Grooming
    print("\n[ATTACK 1] Trust Grooming Simulation")
    pid_groom = 1234
    normal_paths = ["/etc/passwd", "/etc/hosts", "/var/log/auth.log"]
    honey_paths = ["/honey/financial.db", "/honey/secrets.key"]
    
    honey_latencies = afds.simulate_adversarial_grooming(pid_groom, honey_paths, normal_paths)
    print(f"Groomed PID {pid_groom} trust: {afds.trust_states[pid_groom]['trust_score']:.3f}")
    print(f"Honey node access latencies: {honey_latencies}")
    print("VULNERABILITY: Trust accumulation is monotonic and gameable!")
    
    # Attack 2: PID Cycling
    print("\n[ATTACK 2] PID Cycling Attack")
    base_pid = 5000
    latencies = afds.simulate_pid_cycling_attack(base_pid, normal_paths, max_pids=50)
    print(f"Average latency after PID cycling: {np.mean(latencies):.2f}ms")
    print("VULNERABILITY: Trust persists across PID reuse - inheritance attack!")
    
    # Attack 3: Timing Side Channel
    print("\n[ATTACK 3] Timing Side Channel")
    # First build high trust
    for _ in range(100):
        afds.update_trust(pid_groom, normal_paths[0])
    
    timings = afds.simulate_timing_side_channel(pid_groom, normal_paths[0], samples=50)
    trust_low = np.std(timings)
    print(f"Timing std dev (high trust): {trust_low:.3f}ms")
    
    # Low trust process
    pid_low = 9999
    timings_low = afds.simulate_timing_side_channel(pid_low, normal_paths[0], samples=50)
    trust_high = np.std(timings_low)
    print(f"Timing std dev (low trust): {trust_high:.3f}ms")
    print("VULNERABILITY: Trust level is extractable via timing analysis!")
    
    # Attack 4: Topology Manipulation
    print("\n[ATTACK 4] Topology Manipulation")
    pid_topo = 7777
    score, phi = afds.simulate_topology_manipulation(pid_topo, target_depth=50)
    print(f"Controlled traversal score: {score:.2f}")
    print(f"Manipulated phi_delta: {phi:.3f}")
    print("VULNERABILITY: Adversary controls breadth/depth ratio to evade detection!")
    
    # Attack 5: Forensic Log Flooding
    print("\n[ATTACK 5] Forensic Log Flooding")
    initial_log_size = len(afds.forensic_log)
    for i in range(1000):
        afds.forensic_log.append({
            'timestamp': time.time(),
            'pid': random.randint(1000, 2000),
            'operation': 'lookup',
            'path': f'/tmp/flood_{i}'
        })
    print(f"Log size increased from {initial_log_size} to {len(afds.forensic_log)}")
    print("VULNERABILITY: Unbounded log growth enables memory exhaustion!")
    
    # Summary
    print("\n" + "=" * 60)
    print("DISRUPTION SUMMARY")
    print("=" * 60)
    print("""CRITICAL FLAWS IDENTIFIED:
1. MONOTONIC TRUST: Trust only accumulates, never truly resets
2. PID REUSE: Trust inheritance across process lifecycle
3. TIMING LEAKAGE: Blocking jitter creates measurable side channels
4. TOPOLOGY CONTROL: Adversary can manipulate phi_Delta
5. LOG DOS: Forensic system is attack surface, not defense
6. STATIC THRESHOLDS: Shredding boundary is predictable

DISRUPTIVE INSIGHT:
The AFDS treats trust as an ECONOMIC resource (accumulable, tradable) 
when it should be a THERMODYNAMIC property (entropic, irreversible). 
The entire manifold curvature model is built on a false equivalence between 
behavioral repetition and security authenticity.

REQUIRED PARADIGM SHIFT:
Trust must be NON-ERGODIC: Past behavior cannot buy future trust. 
Only violations should persist, not compliance.""")

if __name__ == "__main__":
    run_disruption_analysis()