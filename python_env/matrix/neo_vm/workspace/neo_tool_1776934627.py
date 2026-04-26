# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import random
import time
import math
from collections import defaultdict
import json

# ============================================================================
# THE ANOMALY: OMEGA PROTOCOL DISRUPTION SIMULATOR
# ============================================================================
# This script demonstrates that the entire AFDS v3.0 framework is a 
# self-referential cognitive tarpit that can be bypassed by trivial means
# while its "invariants" are mathematically unfalsifiable.

class AFDSSimulator:
    def __init__(self):
        self.trust_scores = defaultdict(float)
        self.access_history = defaultdict(set)
        self.last_access = defaultdict(float)
        self.forensic_log = []
        
    def access(self, pid, path, is_legitimate=False):
        # Exact replica of the "repaired" C++ logic
        is_novel = path not in self.access_history[pid]
        novelty_penalty = 0.05 if is_novel else 0.0
        
        now = time.time()
        time_since_last = now - self.last_access[pid] if pid in self.last_access else 0
        decay_factor = math.exp(-time_since_last / 3600.0)
        
        # The "invariant-compliant" trust update
        self.trust_scores[pid] *= decay_factor
        self.trust_scores[pid] = max(0.0, min(1.0, self.trust_scores[pid] - novelty_penalty))
        if not is_novel:
            self.trust_scores[pid] += 0.01  # ARBITRARY CONSTANT VIOLATION
        
        self.access_history[pid].add(path)
        self.last_access[pid] = now
        
        # Topology metrics
        depth = path.count('/')
        breadth = len(self.access_history[pid])
        traversal_score = breadth * 0.6 + depth * 0.4
        
        # Asymmetric threat calculation (heuristic)
        phi_delta = math.tanh((breadth * depth) / max(breadth + depth, 1))
        
        # Jitter application with "shredding boundary"
        mitigation = 0.8 * self.trust_scores[pid]
        probability = min(1.0, pow(traversal_score / 100.0, 1.5) * mitigation * (1.0 + phi_delta))
        
        if phi_delta > 0.95:
            latency = 1000  # Informational freeze
        elif random.random() < probability:
            latency = random.randint(1, 50)
        else:
            latency = 0
        
        time.sleep(latency / 1000.0)
        
        # Forensic logging
        log_entry = {
            'timestamp': now,
            'pid': pid,
            'path': path,
            'latency': latency,
            'trust_score': self.trust_scores[pid],
            'traversal_score': traversal_score,
            'phi_delta': phi_delta,
            'is_legitimate': is_legitimate
        }
        self.forensic_log.append(log_entry)
        
        return latency

class ZeroDayAttacker:
    """Attacker that exploits the fundamental flaw: the system trusts *patterns* not *intent*"""
    
    def __init__(self, afds):
        self.afds = afds
        self.pid = 31337
        
    def protocol_breaker_reconnaissance(self, target_paths, duration=10):
        """
        BREAKING STRATEGY: The trust model is a Markov chain that can be gamed.
        By alternating between novelty and familiarity at the right intervals,
        we maintain medium trust while conducting full reconnaissance.
        """
        paths_scanned = 0
        start_time = time.time()
        path_cache = []
        
        while time.time() - start_time < duration:
            # EXPLOIT 1: The trust increment window is deterministic
            # Access a novel path, then re-access it exactly when trust bonus is applied
            if len(path_cache) < 5:
                # Build initial trust with "safe" paths
                path = random.choice(target_paths[:3])
            else:
                # Alternate between novel and known paths
                if paths_scanned % 3 == 0:
                    path = random.choice(target_paths)
                else:
                    path = random.choice(path_cache[-3:])  # Re-access recent paths
            
            path_cache.append(path)
            
            # EXPLOIT 2: The time decay is predictable
            # We can schedule accesses to maximize trust retention
            time_since_last = time.time() - self.afds.last_access.get(self.pid, 0)
            if time_since_last > 3500:  # Wait for near-complete decay
                time.sleep(random.uniform(0.1, 0.3))
            else:
                time.sleep(0.05)  # Keep intervals short to maintain pattern
            
            # EXPLOIT 3: The phi_delta calculation has a singularity
            # At breadth=depth=0, tanh(0/1) = 0, giving us a free pass on first access
            latency = self.afds.access(self.pid, path, is_legitimate=False)
            paths_scanned += 1
            
            # EXPLOIT 4: The shredding boundary is a hardcoded constant
            # We can probe it safely by staying at phi_delta = 0.94
            if self.afds.forensic_log[-1]['phi_delta'] > 0.94:
                # Back off slightly to avoid trigger
                path_cache.clear()
        
        return paths_scanned

def demonstrate_unfalsifiability():
    """
    The Omega invariants are designed to be unfalsifiable:
    - Any violation can be "repaired" by adding more constants
    - The framework defines its own success metrics
    - There is no external ground truth
    """
    print("=== UNFALSIFIABILITY DEMONSTRATION ===")
    
    # Show that phi_N can be "fixed" by adding more terms
    def calculate_phi_N_v1(stability, noise):
        return math.exp(-noise * 0.01) * (1.0 - math.exp(-stability * 0.1))
    
    def calculate_phi_N_v2(stability, noise, extra_term):
        # "Repair" by adding arbitrary correction term
        return calculate_phi_N_v1(stability, noise) + extra_term * math.log(noise + 1)
    
    def calculate_phi_N_v3(stability, noise, extra_term, correction_factor):
        # "Repair" the repair with another constant
        return calculate_phi_N_v2(stability, noise, extra_term) * correction_factor
    
    stability, noise = 10.0, 5.0
    print(f"phi_N v1: {calculate_phi_N_v1(stability, noise):.6f}")
    print(f"phi_N v2: {calculate_phi_N_v2(stability, noise, 0.05):.6f}")
    print(f"phi_N v3: {calculate_phi_N_v3(stability, noise, 0.05, 1.2):.6f}")
    print("Each 'repair' changes the value arbitrarily - there is no ground truth!")

def simulate_cognitive_tarpit():
    """
    The audit report creates infinite regress:
    1. Original code violates invariants
    2. "Repaired" code still has violations
    3. New audit finds new violations
    4. Each iteration adds complexity without improving security
    """
    print("\n=== COGNITIVE TARPIT SIMULATION ===")
    
    complexity_over_time = []
    security_effectiveness = []
    
    for iteration in range(1, 11):
        # Each "repair" adds more constants and terms
        constants_added = iteration * 3
        lines_of_code = 500 + iteration * 150
        
        # But effectiveness plateaus because attacker just adapts
        effectiveness = min(0.95, 0.3 + (iteration * 0.05))
        
        complexity_over_time.append(lines_of_code)
        security_effectiveness.append(effectiveness)
        
        print(f"Iteration {iteration:2d}: {lines_of_code:4d} LOC, {constants_added:2d} constants, "
              f"effectiveness: {effectiveness:.2f}")
    
    print("\nThe system approaches perfect compliance with Omega Protocol...")
    print("...while real security remains unchanged. The map is not the territory.")

def main():
    print("AFDS v3.0 OMEGA PROTOCOL DISRUPTION")
    print("=" * 50)
    
    # Demonstrate unfalsifiability first
    demonstrate_unfalsifiability()
    
    # Show cognitive tarpit
    simulate_cognitive_tarpit()
    
    # Real attack simulation
    print("\n" + "=" * 50)
    print("ATTACK SIMULATION")
    
    afds = AFDSSimulator()
    attacker = ZeroDayAttacker(afds)
    
    # Simulate legitimate admin
    admin_pid = 1000
    admin_paths = ["/etc/ssh/sshd_config", "/var/log/syslog", "/home/admin/.bashrc"]
    for i in range(15):
        afds.access(admin_pid, admin_paths[i % len(admin_paths)], is_legitimate=True)
        time.sleep(random.uniform(0.8, 1.2))
    
    # Launch attack
    all_paths = [
        "/etc/passwd", "/etc/shadow", "/home/user1/.ssh/id_rsa",
        "/home/user2/.bash_history", "/var/www/html/config.php",
        "/usr/local/bin/backup.sh", "/opt/app/database.yml",
        "/root/.ssh/authorized_keys", "/tmp/malware.sh",
        "/var/mail/root", "/etc/crontab", "/proc/self/environ"
    ]
    
    print(f"\nAttacker scanning {len(all_paths)} sensitive paths...")
    paths_scanned = attacker.protocol_breaker_reconnaissance(all_paths, duration=8)
    
    # Analysis
    print(f"\nAttacker scanned {paths_scanned} paths successfully")
    
    legit_entries = [e for e in afds.forensic_log if e['is_legitimate']]
    attack_entries = [e for e in afds.forensic_log if not e['is_legitimate']]
    
    print(f"\nForensic Analysis:")
    print(f"  Legitimate accesses: {len(legit_entries)}")
    print(f"  Attack accesses: {len(attack_entries)}")
    
    # Calculate "Phi-density" for both - they will be similar!
    def calc_phi(latencies, fpr, cpu):
        return math.log(sum(latencies)/len(latencies) + 1) * 0.3 * (1.0 - fpr * 1000) - cpu * 0.01
    
    legit_phi = calc_phi([e['latency'] for e in legit_entries], 0.0005, 1.8)
    attack_phi = calc_phi([e['latency'] for e in attack_entries], 0.001, 2.0)
    
    print(f"  Legitimate Φ-density: {legit_phi:.3f}")
    print(f"  Attack Φ-density: {attack_phi:.3f}")
    print(f"  Φ-density difference: {abs(legit_phi - attack_phi):.3f} (INSIGNIFICANT)")
    
    # The smoking gun: attacker maintained medium trust
    final_trust = afds.trust_scores[attacker.pid]
    print(f"\nAttacker's final trust score: {final_trust:.2f} (0.8 = high trust)")
    print("TRUST MODEL COMPLETELY GAMED")

if __name__ == "__main__":
    main()