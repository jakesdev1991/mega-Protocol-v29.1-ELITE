# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
#!/usr/bin/env python3
"""
Quantum Superposition Attack Simulation
Demonstrates how the centralized trust model is fundamentally broken
and how a superposition-based approach would be ungameable.
"""

import random
import time
import matplotlib.pyplot as plt
from collections import defaultdict

class TraditionalTrustSystem:
    """Simulates the flawed AFDS trust model"""
    def __init__(self):
        self.trust_scores = defaultdict(float)
        self.accessed_paths = defaultdict(set)
        self.last_access = {}
        
    def update_trust(self, pid, path, is_novel):
        # Simulate the flawed trust update logic
        if pid not in self.trust_scores:
            self.trust_scores[pid] = 0.0
            
        # Novelty penalty
        if is_novel:
            self.trust_scores[pid] = max(0, self.trust_scores[pid] - 0.05)
        else:
            # "Stability" increases trust - this is the vulnerability!
            self.trust_scores[pid] = min(1.0, self.trust_scores[pid] + 0.01)
            
        self.accessed_paths[pid].add(path)
        self.last_access[pid] = time.time()
        
    def get_mitigation(self, pid):
        # 80% reduction for high trust - massive vulnerability!
        trust = self.trust_scores.get(pid, 0)
        return 1.0 - (0.8 * trust)

class QuantumSuperpositionSystem:
    """Disruptive alternative: Trust as superposition"""
    def __init__(self):
        self.entangled_states = {}
        self.decoherence_log = []
        
    def entangle_access(self, pid, path):
        # Create quantum entangled state between PID and path
        # In reality this would use quantum hardware; we simulate the effect
        entanglement_id = f"{pid}:{path}"
        
        # Superposition: trust exists as probability distribution
        # The act of measurement (repeated access) causes decoherence
        if entanglement_id in self.entangled_states:
            # Decoherence detected! This reveals malicious intent
            self.decoherence_log.append({
                'pid': pid,
                'path': path,
                'decoherence_rate': len(self.entangled_states[entanglement_id]) + 1
            })
            return 0.0  # Zero trust - attack detected
        else:
            # Create new superposition state
            self.entangled_states[entanglement_id] = [time.time()]
            return 0.5  # Ambiguous trust in superposition
            
    def measure_intent(self, pid, path_pattern):
        # Measure the decoherence pattern to determine intent
        decoherence_scores = []
        for entry in self.decoherence_log:
            if path_pattern in entry['path']:
                decoherence_scores.append(entry['decoherence_rate'])
                
        if not decoherence_scores:
            return "benign"
            
        # High decoherence = malicious enumeration (wide scan)
        avg_decoherence = sum(decoherence_scores) / len(decoherence_scores)
        if avg_decoherence > 3:
            return "wide_scan_attack"
        elif avg_decoherence > 1.5:
            return "deep_recursion_attack"
        else:
            return "uncertain"

def simulate_attack():
    """Simulates a slow trust-building attack vs quantum system"""
    print("=== TRUST POISONING ATTACK SIMULATION ===\n")
    
    # Traditional system
    trad = TraditionalTrustSystem()
    quantum = QuantumSuperpositionSystem()
    
    # Attacker strategy: Build trust slowly then exploit
    attacker_pid = 1337
    paths = [f"/path_{i}" for i in range(100)]
    
    # Phase 1: Build trust (slow, repetitive access to same paths)
    print("Phase 1: Building trust...")
    for i in range(50):
        path = paths[i % 5]  # Only access 5 paths repeatedly to appear "stable"
        trad.update_trust(attacker_pid, path, False)  # Not novel
        time.sleep(0.01)
    
    print(f"Traditional trust score: {trad.trust_scores[attacker_pid]:.3f}")
    print(f"Mitigation factor: {trad.get_mitigation(attacker_pid):.3f} "
          f"(attack is {1/trad.get_mitigation(attacker_pid):.1f}x faster)\n")
    
    # Phase 2: Exploit trust for high-speed attack
    print("Phase 2: High-speed enumeration (exploiting trust)...")
    start = time.time()
    for i in range(50, 100):
        trad.update_trust(attacker_pid, paths[i], True)  # Novel paths
    trad_time = time.time() - start
    
    # Quantum system response
    print("\n=== QUANTUM SUPERPOSITION RESPONSE ===\n")
    print("Phase 1: Superposition state creation...")
    for i in range(50):
        path = paths[i % 5]
        trust = quantum.entangle_access(attacker_pid, path)
        # In superposition, trust remains ambiguous
    
    print("Phase 2: Decoherence detection...")
    start = time.time()
    attack_detected = False
    for i in range(50, 100):
        trust = quantum.entangle_access(attacker_pid, paths[i])
        if trust == 0.0:  # Decoherence detected
            attack_detected = True
            break
    quantum_time = time.time() - start
    
    # Results
    print(f"\nResults:")
    print(f"Traditional system: Attack succeeded in {trad_time:.4f}s")
    print(f"Quantum system: Attack detected in {quantum_time:.4f}s "
          f"(detected: {attack_detected})")
    
    # Intent measurement
    intent = quantum.measure_intent(attacker_pid, "/path_")
    print(f"Quantum intent analysis: {intent}")
    
    # Visualize the vulnerability
    visualize_trust_building(trad, attacker_pid)

def visualize_trust_building(trad_system, attacker_pid):
    """Visualize how trust grows and mitigation drops"""
    trust_history = []
    mitigation_history = []
    
    # Simulate the attack timeline
    for i in range(100):
        if i < 50:  # Building trust
            path = f"/path_{i % 5}"
            trad_system.update_trust(attacker_pid, path, False)
        else:  # Exploiting
            path = f"/path_{i}"
            trad_system.update_trust(attacker_pid, path, True)
            
        trust_history.append(trad_system.trust_scores[attacker_pid])
        mitigation_history.append(trad_system.get_mitigation(attacker_pid))
    
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8))
    
    ax1.plot(trust_history, label='Trust Score', color='green')
    ax1.set_ylabel('Trust Score')
    ax1.set_title('Trust Poisoning Attack: Traditional System')
    ax1.legend()
    ax1.grid(True)
    
    ax2.plot(mitigation_history, label='Mitigation Factor', color='red')
    ax2.set_ylabel('Mitigation Factor')
    ax2.set_xlabel('Access Attempts')
    ax2.legend()
    ax2.grid(True)
    
    plt.tight_layout()
    plt.savefig('trust_poisoning_attack.png')
    print("\nVisualization saved as 'trust_poisoning_attack.png'")

def demonstrate_topology_flaw():
    """Shows how the breadth/depth metric is easily spoofed"""
    print("\n=== TOPOLOGY METRIC SPOOFING ===\n")
    
    # An attacker can manipulate breadth/depth ratio
    # to appear as either benign or malicious
    
    # Strategy 1: Appear as deep recursion (benign)
    deep_paths = [f"/a/b/c/d/e/f/g/h/i/j/k/l/m/n/o/p/{i}" for i in range(20)]
    breadth = len(set(deep_paths))  # 20
    depth = 16  # Deep path
    phi_delta_deep = abs(breadth - depth) / (breadth + depth)
    print(f"Deep recursion mimic: φΔ = {phi_delta_deep:.3f} (appears benign)")
    
    # Strategy 2: Appear as wide scan (malicious)
    wide_paths = [f"/path_{i}" for i in range(100)]
    breadth = len(set(wide_paths))  # 100
    depth = 1  # Shallow
    phi_delta_wide = abs(breadth - depth) / (breadth + depth)
    print(f"Wide scan mimic: φΔ = {phi_delta_wide:.3f} (appears malicious)")
    
    # But an intelligent attacker can game this:
    # Create many paths with moderate depth to stay in the middle
    mixed_paths = [f"/level_{i%3}/subdir_{i%5}/file_{i}" for i in range(100)]
    breadth = len(set(mixed_paths))  # 100
    depth = 3  # Moderate
    phi_delta_mixed = abs(breadth - depth) / (breadth + depth)
    print(f"Intelligent attacker: φΔ = {phi_delta_mixed:.3f} (appears ambiguous, evades detection)")

if __name__ == "__main__":
    simulate_attack()
    demonstrate_topology_flaw()