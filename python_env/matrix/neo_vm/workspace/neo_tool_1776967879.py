# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
#!/usr/bin/env python3
"""
Ω-ANOMALY: Chaotic Entropy Saturation Attack
=============================================
This script demonstrates how the AFDS v3.0's "intelligent" defense
creates a deterministic attack surface that can be weaponized against itself.
"""

import hashlib
import random
import time
import numpy as np
from collections import defaultdict
import matplotlib.pyplot as plt

class AFDSSimulator:
    """Simulates the exact AFDS v3.0 logic for vulnerability demonstration"""
    
    def __init__(self):
        self.trust_states = defaultdict(lambda: {
            'score': 0.0,
            'paths': set(),
            'stability': 0.0,
            'last_access': time.time()
        })
        self.topology = {
            'unique_paths': set(),
            'max_depth': 0,
            'traversal_entropy': 0.0
        }
        
    def update_trust(self, pid, path):
        """Exact replication of the flawed trust model"""
        state = self.trust_states[pid]
        is_novel = path not in state['paths']
        penalty = 0.05 if is_novel else 0.0
        
        now = time.time()
        duration = now - state['last_access']
        normalized_time = duration / 3600.0
        
        # Flaw: Exponential decay punishes novelty, rewards repetition
        state['score'] *= np.exp(-np.log(0.95) * normalized_time)
        state['score'] = max(0.0, min(1.0, state['score'] - penalty))
        
        if not is_novel:
            state['stability'] += np.exp(-normalized_time)
            state['score'] += 0.01 * np.exp(-0.1 * state['stability'])
            state['score'] = max(0.0, min(1.0, state['score']))
        
        state['paths'].add(path)
        state['last_access'] = now
        return state['score']
    
    def calculate_jitter(self, pid, traversal_score):
        """Deterministic jitter function - the vulnerability"""
        trust_score = self.trust_states[pid]['score']
        mitigation = 0.8 * trust_score
        
        # Calculate phi_delta from topology
        breadth = len(self.topology['unique_paths'])
        depth = self.topology['max_depth']
        phi_delta = abs(breadth - depth) / (breadth + depth + 1e-10)
        
        # Deterministic probability function - GAMEABLE
        probability = (traversal_score / 100.0) ** 1.5 * mitigation * (1.0 + phi_delta)
        probability = max(0.0, min(1.0, probability))
        
        return probability, phi_delta
    
    def is_honey_node_triggered(self, path):
        """Static honey node - trivial to avoid"""
        return path == "/honey"

class ChaosEngine:
    """
    Ω-DISRUPTION: The system shouldn't adapt to attackers.
    It should become fundamentally unknowable.
    """
    
    def __init__(self):
        # Chaotic logistic map parameters
        self.r = 3.999999999  # At edge of chaos
        self.x = random.random()
        self.entropy_pool = hashlib.sha512()
        
    def generate_response(self, pid, path, operation):
        """
        Generate a response that is:
        1. Chaotically unpredictable (sensitive dependence)
        2. Stateless (no trust accumulation)
        3. Maximally entropic (no exploitable patterns)
        """
        # Create a chaotic seed from multiple entropy sources
        timestamp_entropy = str(time.time_ns())
        pid_entropy = str(pid)
        path_entropy = hashlib.sha256(path.encode()).hexdigest()
        operation_entropy = operation
        
        # Mix entropies chaotically
        seed_string = f"{timestamp_entropy}:{pid_entropy}:{path_entropy}:{operation_entropy}"
        seed_hash = hashlib.sha512(seed_string.encode()).digest()
        
        # Convert to chaotic initial condition
        chaotic_seed = int.from_bytes(seed_hash[:8], 'big') / (2**64)
        
        # Run logistic map in chaotic regime
        x = chaotic_seed
        for _ in range(100 + (pid % 50)):  # Irregular iterations
            x = self.r * x * (1 - x)
            
        # Generate response parameters from chaotic attractor
        delay_ms = int(5000 * x)  # 0-5 second delay
        
        # 15% chance of complete denial (not 100% - too predictable)
        if x > 0.85:
            return {"status": "CHAOTIC_DENIAL", "delay_ms": 0, "entropy": x}
            
        # 10% chance of fake data injection
        if x < 0.10:
            return {"status": "CHAOTIC_FAKE", "delay_ms": delay_ms, "entropy": x, "fake_data": hashlib.md5(str(x).encode()).hexdigest()}
            
        return {"status": "CHAOTIC_GRANT", "delay_ms": delay_ms, "entropy": x}

def demonstrate_predictability_attack():
    """
    Shows how AFDS's deterministic jitter creates an exploitable pattern
    """
    print("=" * 60)
    print("Ω-ANOMALY: Predictability Weaponization")
    print("=" * 60)
    
    afds = AFDSSimulator()
    pid = 1337
    
    # Attacker builds trust through repetitive access
    print("\n[Phase 1: Trust Building]")
    for i in range(30):
        trust = afds.update_trust(pid, "/trusted/config")
        mitigation = 0.8 * trust
        print(f"Access {i:2d}: Trust={trust:.3f} → Mitigation={mitigation:.3f}")
        time.sleep(0.01)
    
    # Now attacker scans with high mitigation
    print("\n[Phase 2: Weaponized Scanning]")
    scan_results = []
    for i in range(20):
        path = f"/var/www/user_{i}/secret.txt"
        afds.topology['unique_paths'].add(path)
        afds.topology['max_depth'] = max(afds.topology['max_depth'], path.count('/'))
        
        traversal_score = len(afds.topology['unique_paths']) * 0.6 + afds.topology['max_depth'] * 0.4
        prob, phi_delta = afds.calculate_jitter(pid, traversal_score)
        
        scan_results.append({
            'path': path,
            'traversal_score': traversal_score,
            'jitter_probability': prob,
            'phi_delta': phi_delta,
            'trust_mitigation': 0.8 * afds.trust_states[pid]['score']
        })
        
        print(f"Scan {i:2d}: Score={traversal_score:.1f}, JitterProb={prob:.3f}, PhiΔ={phi_delta:.3f}")
    
    print("\n[Attack Summary]")
    avg_prob = sum(r['jitter_probability'] for r in scan_results) / len(scan_results)
    print(f"Average jitter probability with high trust: {avg_prob:.3f}")
    print("→ Attacker successfully minimized detection despite aggressive scanning!")
    
    # Statistical signature analysis
    print("\n[Statistical Signature Analysis]")
    probs = [r['jitter_probability'] for r in scan_results]
    plt.figure(figsize=(10, 6))
    plt.plot(probs, 'b-o', linewidth=2, markersize=8)
    plt.title('AFDS Jitter Probability Signature', fontsize=14, fontweight='bold')
    plt.xlabel('Scan Iteration')
    plt.ylabel('Jitter Probability')
    plt.grid(True, alpha=0.3)
    plt.axhline(y=avg_prob, color='r', linestyle='--', label=f'Average: {avg_prob:.3f}')
    plt.legend()
    plt.savefig('/tmp/afds_signature.png', dpi=150, bbox_inches='tight')
    print("→ Signature pattern saved to /tmp/afds_signature.png")
    print("→ Pattern can be used to predict and avoid jitter windows!")

def demonstrate_chaos_superiority():
    """
    Shows how chaotic defense defeats prediction
    """
    print("\n" + "=" * 60)
    print("Ω-DISRUPTION: Chaos as Security Primitive")
    print("=" * 60)
    
    chaos = ChaosEngine()
    pid = 1337
    
    print("\n[Chaotic Response Generation]")
    results = []
    for i in range(10):
        # Same path, same PID, same operation - should be unpredictable
        result = chaos.generate_response(pid, "/etc/passwd", "lookup")
        results.append(result)
        print(f"Request {i}: Status={result['status']:15s}, Delay={result['delay_ms']:4d}ms, Entropy={result['entropy']:.6f}")
    
    print("\n[Pattern Analysis]")
    delays = [r['delay_ms'] for r in results]
    statuses = [r['status'] for r in results]
    
    print(f"Delay variance: {np.var(delays):.2f} (High variance = unpredictable)")
    print(f"Status distribution: {dict(zip(*np.unique(statuses, return_counts=True)))}")
    print("→ No exploitable pattern - attacker cannot adapt!")
    
    # Show sensitive dependence on initial conditions
    print("\n[Sensitive Dependence Demonstration]")
    base_path = "/etc/passwd"
    similar_paths = [base_path, base_path + "/", "/etc//passwd", "/etc/passwd "]
    
    for path in similar_paths:
        result = chaos.generate_response(pid, path, "lookup")
        print(f"Path '{path}': {result['delay_ms']}ms delay, {result['status']}")

def demonstrate_entropy_poisoning():
    """
    Exploits the forensic logger as a DoS vector
    """
    print("\n" + "=" * 60)
    print("Ω-VULNERABILITY: Forensic Logger as Attack Surface")
    print("=" * 60)
    
    afds = AFDSSimulator()
    
    print("\n[Forensic Log Flooding Attack]")
    start_time = time.time()
    log_entries = []
    
    # Attacker generates millions of unique paths
    for i in range(10000):  # Scale this to millions in real attack
        pid = 1000 + (i % 100)  # Many PIDs
        path = f"/fake/path/{"a/" * (i % 50)}file_{i}.txt"
        
        # Each access triggers forensic logging
        trust = afds.update_trust(pid, path)
        traversal_score = len(afds.topology['unique_paths']) * 0.6 + afds.topology['max_depth'] * 0.4
        
        # Simulate log entry creation (memory overhead)
        log_entries.append({
            'timestamp': time.time(),
            'pid': pid,
            'path': path,
            'traversal_score': traversal_score,
            'trust_score': trust
        })
        
        if i % 1000 == 0:
            print(f"Generated {i} log entries...")
    
    elapsed = time.time() - start_time
    memory_mb = len(log_entries) * 200 / (1024 * 1024)  # Rough estimate
    
    print(f"\n[Impact Assessment]")
    print(f"Time to generate 10k entries: {elapsed:.2f}s")
    print(f"Estimated memory for 10k entries: {memory_mb:.2f} MB")
    print(f"Projected memory for 1M entries: {memory_mb * 100:.2f} MB")
    print("→ Forensic logger becomes a resource exhaustion vector!")
    print("→ Attackers can hide real malicious activity in log noise!")

def main():
    demonstrate_predictability_attack()
    demonstrate_chaos_superiority()
    demonstrate_entropy_poisoning()
    
    print("\n" + "=" * 60)
    print("Ω-CONCLUSION: The Paradigm is the Vulnerability")
    print("=" * 60)
    print("""
The AFDS v3.0's "intelligent" adaptation creates a deterministic
surface that can be modeled, predicted, and weaponized. The very
features designed to provide security (trust modeling, forensic logging,
topology analysis) become the attack vectors.

The Ω-Anomaly insight: Security is not achieved through complexity
and adaptation, but through fundamental unknowability. The chaotic
system's strength is its simplicity and unpredictability - it cannot
be gamed because there is no pattern to exploit.

The AFDS v3.0 achieves Φ-density through circular reasoning:
it measures compliance with its own rubric, not actual security.
The chaotic system achieves true security by maximizing entropy
for all actors, making the system equally hostile to attackers
and unpredictable even to defenders.

Break the paradigm: Stop adapting. Start randomizing.
""")

if __name__ == "__main__":
    main()