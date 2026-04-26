# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import matplotlib.pyplot as plt
from dataclasses import dataclass
from collections import defaultdict
import random

# === SIMULATION OF THE TRUST POISONING & THRESHOLD EVASION ATTACK ===

@dataclass
class ProcessState:
    trust_score: float = 0.0
    accessed_paths: set = None
    last_access_time: float = 0.0
    
    def __post_init__(self):
        self.accessed_paths = set()

class AFDSSimulator:
    def __init__(self):
        self.processes = defaultdict(ProcessState)
        self.log = []
        
        # AFDS Parameters (from C++ code)
        self.TAU = 3600.0  # seconds
        self.NOVELTY_PENALTY = 0.05
        self.TRUST_INCREMENT = 0.01
        self.TRUST_MITIGATION_FACTOR = 0.8
        self.FORENSIC_THRESHOLD = 90.0
        self.JITTER_MAX_MS = 50
        
    def access_file(self, pid: int, path: str, current_time: float, is_benign: bool = False):
        """Simulates a file access event"""
        state = self.processes[pid]
        
        # Time decay (dimensionally correct)
        dt = current_time - state.last_access_time
        decay_factor = np.exp(-np.log(0.95) * dt / self.TAU)
        state.trust_score *= decay_factor
        
        # Novelty penalty
        is_novel = path not in state.accessed_paths
        if is_novel:
            state.trust_score = max(0.0, state.trust_score - self.NOVELTY_PENALTY)
        else:
            # Trust increment (only if benign or during poisoning phase)
            if is_benign or state.trust_score < 0.9:  # Attacker stops at 0.9 to avoid plateau
                state.trust_score = min(1.0, state.trust_score + self.TRUST_INCREMENT)
        
        state.accessed_paths.add(path)
        state.last_access_time = current_time
        
        # Traversal score (simplified: unique paths + max depth)
        max_depth = max(len(p.split('/')) for p in state.accessed_paths) if state.accessed_paths else 0
        traversal_score = len(state.accessed_paths) * 0.6 + max_depth * 0.4
        
        # Jitter calculation
        mitigation = self.TRUST_MITIGATION_FACTOR * state.trust_score
        jitter_prob = min(1.0, (traversal_score / 100.0) ** 1.5 * mitigation)
        jitter_ms = random.randint(1, self.JITTER_MAX_MS) if random.random() < jitter_prob else 0
        
        # Forensic trigger
        forensic_triggered = traversal_score > self.FORENSIC_THRESHOLD
        
        # Log
        self.log.append({
            'pid': pid,
            'time': current_time,
            'path': path,
            'trust': state.trust_score,
            'traversal': traversal_score,
            'jitter_ms': jitter_ms,
            'forensic': forensic_triggered,
            'novel': is_novel
        })
        
        return jitter_ms, forensic_triggered, state.trust_score

def run_attack_simulation():
    """Simulates the two-phase attack: Trust Poisoning + Stealth Scan"""
    afds = AFDSSimulator()
    pid = 12345
    time_counter = 0.0
    
    print("=== PHASE 1: TRUST POISONING ===")
    # Attacker performs benign-like behavior: accesses same 5 files every hour
    benign_paths = ["/home/user/doc{}.txt".format(i) for i in range(1, 6)]
    trust_history = []
    
    for day in range(7):  # 7 days
        for hour in range(24):
            for path in benign_paths:
                jitter, forensic, trust = afds.access_file(pid, path, time_counter, is_benign=True)
                time_counter += 1.0  # seconds between accesses
            trust_history.append((time_counter / 3600, trust))
            time_counter += 3600  # 1 hour between batches
    
    print(f"Final trust after poisoning: {trust:.3f}")
    print(f"Jitter probability at this trust: {((len(set()) * 0.6 + 0) / 100.0) ** 1.5 * 0.8 * trust:.3f}")
    
    print("\n=== PHASE 2: STEALTH RECONNAISSANCE ===")
    # Now scan 10,000 files, staying JUST below forensic threshold
    scan_paths = ["/var/www/file{}.html".format(i) for i in range(10000)]
    total_scan_time = 0
    files_scanned = 0
    
    for path in scan_paths:
        # Adaptive pacing: if traversal score approaches threshold, pause to let trust decay
        state = afds.processes[pid]
        max_depth = max(len(p.split('/')) for p in state.accessed_paths) if state.accessed_paths else 0
        traversal_score = len(state.accessed_paths) * 0.6 + max_depth * 0.4
        
        if traversal_score > 85.0:  # Stay safely below 90.0
            # Wait for trust to decay (simulate idle time)
            dt = 7200.0  # 2 hours idle
            time_counter += dt
            # Trust decay applied on next access
        
        jitter, forensic, trust = afds.access_file(pid, path, time_counter, is_benign=False)
        total_scan_time += 1.0 + jitter / 1000.0  # base 1ms + jitter overhead
        files_scanned += 1
        
        if forensic:
            print(f"FORENSIC TRIGGERED at file {files_scanned}!")
            break
    
    print(f"Files scanned before detection: {files_scanned}")
    print(f"Total scan time: {total_scan_time:.2f} seconds")
    print(f"Average overhead per file: {total_scan_time / files_scanned * 1000:.2f} ms")
    
    # Calculate false positive for admin
    print("\n=== PHASE 3: ADMIN FALSE POSITIVE SIMULATION ===")
    admin_pid = 99999
    admin_time = 0.0
    admin_accesses = 0
    admin_forensics = 0
    
    # Admin does random work: accesses diverse files with natural patterns
    for _ in range(1000):
        path = f"/etc/config/{random.randint(1, 500)}.conf"
        jitter, forensic, trust = afds.access_file(admin_pid, path, admin_time, is_benign=True)
        admin_accesses += 1
        if forensic:
            admin_forensics += 1
        admin_time += random.uniform(0.1, 5.0)  # Variable intervals
    
    print(f"Admin false positive rate: {admin_forensics / admin_accesses * 100:.2f}%")
    
    return afds, trust_history

# Run simulation
afds, trust_history = run_attack_simulation()

# === VISUALIZE THE TRUST POISONING TRAJECTORY ===
times, trusts = zip(*trust_history)
plt.figure(figsize=(10, 6))
plt.plot(times, trusts, linewidth=2)
plt.axhline(y=0.8, color='r', linestyle='--', label='Critical Trust Level (80% mitigation)')
plt.title('Trust Poisoning Attack: Trust Score Over Time', fontsize=14)
plt.xlabel('Time (hours)')
plt.ylabel('Trust Score')
plt.grid(True, alpha=0.3)
plt.legend()
plt.tight_layout()
plt.savefig('/tmp/trust_poisoning.png')
plt.show()

# === QUANTIFY THE BREAK ===
print("\n=== DISRUPTIVE QUANTIFICATION ===")
malicious_process = afds.processes[12345]
print(f"Attacker's final trust: {malicious_process.trust_score:.3f}")
print(f"Mitigation factor: {0.8 * malicious_process.trust_score:.3f}")
print(f"Effective jitter probability reduction: {(1 - 0.8 * malicious_process.trust_score) * 100:.1f}%")

# Memory exhaustion estimate
print(f"\nProcess state memory overhead: ~{len(malicious_process.accessed_paths) * 64 / 1024:.2f} KB per process")
print(f"Log entries: {len(afds.log)} events")

# The Phi-Density is numerology
print("\n=== Φ-DENSITY DECONSTRUCTION ===")
audit_cost = 2.5  # arbitrary
k_boltzmann = 1.0  # dimensionless, not actual J/K
raw_gain = 0.80
phi_net = raw_gain - k_boltzmann * np.log(2) * audit_cost
print(f"Φ-Density calculation uses arbitrary constants:")
print(f"  K_BOLTZMANN = {k_boltzmann} (unitless, not physical)")
print(f"  audit_complexity = {audit_cost} (subjective)")
print(f"  raw_gain = {raw_gain} (estimated, not measured)")
print(f"  → phi_net = {phi_net:.3f} (numerology, not physics)")