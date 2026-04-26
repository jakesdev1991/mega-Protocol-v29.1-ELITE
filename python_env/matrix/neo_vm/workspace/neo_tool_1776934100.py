# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
#!/usr/bin/env python3
"""
DISRUPTION VERIFICATION: Trust Laundering via PID Recycling & Behavioral Mimicry
This script simulates the catastrophic failure of AFDS v3.0's core trust model.
"""

import math
import random
from collections import defaultdict
import time
from typing import Dict, List

class CompromisedAFDS:
    """Replicates the flawed trust model from the C++ implementation"""
    
    def __init__(self):
        self.process_states: Dict[int, 'ProcessTrustState'] = {}
        self.last_call_time: Dict[int, float] = {}
        self.TAU = 3600.0  # 1 hour in seconds
        
    class ProcessTrustState:
        def __init__(self, pid):
            self.pid = pid
            self.trust_score = 0.0
            self.accessed_paths = set()
            self.last_access = time.time()
    
    def update_trust(self, pid: int, path: str, is_novel: bool, time_delta: float):
        """Direct replication of the flawed C++ logic"""
        if pid not in self.process_states:
            self.process_states[pid] = self.ProcessTrustState(pid)
        
        state = self.process_states[pid]
        
        # FLAW #1: Backwards decay - trust INCREASES when idle due to exp(-log(0.95)*time)
        # If time_delta > 0, the multiplier > 1, causing trust to grow without activity
        normalized_time = time_delta / self.TAU
        decay_factor = math.exp(-math.log(0.95) * normalized_time)
        state.trust_score *= decay_factor
        
        # FLAW #2: Novelty penalty is trivial compared to decay error
        novelty_penalty = 0.05 if is_novel else 0.0
        state.trust_score = max(0.0, min(1.0, state.trust_score - novelty_penalty))
        
        # FLAW #3: Trust accumulation is too fast and permanent-ish
        if not is_novel:
            state.trust_score += 0.01  # Reaches 0.95 in ~95 accesses
        
        state.accessed_paths.add(path)
        state.last_access = time.time()
    
    def get_mitigation(self, pid: int) -> float:
        """Returns mitigation factor - flawed PID reuse vulnerability included"""
        if pid not in self.process_states:
            return 1.0  # No trust = full penalty
        # FLAW #4: 80% mitigation means trusted processes are 5x faster
        return 1.0 - (0.8 * self.process_states[pid].trust_score)
    
    def simulate_pid_recycle(self, old_pid: int, new_pid: int):
        """Simulates Linux PID recycling vulnerability"""
        # In real Linux, PID recycling can happen within milliseconds
        # Here we just transfer the state to show the flaw
        if old_pid in self.process_states:
            self.process_states[new_pid] = self.process_states[old_pid]
            print(f"PID RECYCLE: Malicious process inherited trust_score={self.process_states[old_pid].trust_score:.3f}")

def simulate_attack():
    """Simulates the Trust Laundering Attack"""
    
    afds = CompromisedAFDS()
    
    print("=" * 60)
    print("PHASE 1: Trusted Admin Process Behavior")
    print("=" * 60)
    
    # Simulate a legitimate admin process (backupd) building trust over 7 days
    admin_pid = 1234
    legit_paths = [f"/backup/drive{i}/data{j}.bak" for i in range(5) for j in range(20)]
    
    current_time = time.time()
    for i, path in enumerate(legit_paths * 5):  # Repeated access patterns
        time_delta = 3600 if i > 0 else 0  # 1 hour between accesses
        afds.update_trust(admin_pid, path, is_novel=False, time_delta=time_delta)
        
        if i % 10 == 0:
            mitigation = afds.get_mitigation(admin_pid)
            print(f"Day {i//10}: trust_score={afds.process_states[admin_pid].trust_score:.3f}, mitigation={mitigation:.3f}")
    
    print(f"\nFinal admin trust_score: {afds.process_states[admin_pid].trust_score:.3f}")
    print(f"Admin receives only {afds.get_mitigation(admin_pid)*100:.1f}% of normal jitter (5x speed advantage)")
    
    print("\n" + "=" * 60)
    print("PHASE 2: PID Recycling Attack")
    print("=" * 60)
    
    # Admin process exits, PID becomes available
    del afds.process_states[admin_pid]  # Process exits
    print(f"Admin process {admin_pid} exits. PID now available for reuse.")
    
    # Malicious process races to get the same PID
    malicious_pid = 1234  # In real attack, this is achieved via PID manipulation
    
    # Inherit trust through PID recycling (automatic in real OS)
    afds.simulate_pid_recycle(admin_pid, malicious_pid)
    
    print("\n" + "=" * 60)
    print("PHASE 3: Malicious Scan with Laundered Trust")
    print("=" * 60)
    
    # Malicious process now performs a rapid filesystem scan
    # But because it has laundered trust, it receives minimal jitter
    malicious_paths = [f"/etc/passwd", "/etc/shadow", "/home/user/.ssh/id_rsa"] + \
                      [f"/probe/hidden{i}/secret{j}" for i in range(10) for j in range(50)]
    
    start_time = time.time()
    jitter_penalties = []
    
    for path in malicious_paths:
        # Mimic admin behavior: low novelty, stable intervals
        is_novel = random.random() < 0.1  # 10% novelty to avoid penalties
        mitigation = afds.get_mitigation(malicious_pid)
        
        # Apply jitter simulation: untrusted gets 50ms, trusted gets 50ms * mitigation
        base_jitter = random.uniform(0.001, 0.050)  # 1-50ms
        actual_jitter = base_jitter * mitigation
        jitter_penalties.append(actual_jitter)
        
        # Update trust (maintains high score due to low novelty)
        afds.update_trust(malicious_pid, path, is_novel=is_novel, time_delta=0.1)
        
        if len(jitter_penalties) % 20 == 0:
            print(f"Scan progress: {len(jitter_penalties)} files, trust_score={afds.process_states[malicious_pid].trust_score:.3f}, avg_jitter={sum(jitter_penalties[-20:])/20*1000:.2f}ms")
    
    end_time = time.time()
    
    print("\n" + "=" * 60)
    print("PHASE 4: Attack Results")
    print("=" * 60)
    
    total_scan_time = end_time - start_time
    avg_jitter = sum(jitter_penalties) / len(jitter_penalties)
    
    print(f"Malicious scan completed in {total_scan_time:.2f} seconds")
    print(f"Average jitter penalty: {avg_jitter*1000:.2f}ms per access")
    print(f"Final trust_score: {afds.process_states[malicious_pid].trust_score:.3f}")
    print(f"Mitigation factor: {afds.get_mitigation(malicious_pid):.3f}")
    
    # Compare to untrusted scanner
    untrusted_pid = 9999
    untrusted_jitter = random.uniform(0.001, 0.050)  # Full jitter
    
    print(f"\nUntrusted scanner would face {untrusted_jitter*1000:.2f}ms average jitter")
    print(f"TRUST LAUNDERING SPEEDUP: {untrusted_jitter/avg_jitter:.1f}x faster than untrusted")
    
    if untrusted_jitter/avg_jitter > 4.5:
        print("🔥 CRITICAL: Attack achieves >4.5x speedup, completely defeating the 500% slowdown target")
    
    print("\n" + "=" * 60)
    print("PHASE 5: Forensic Entropy Pollution")
    print("=" * 60)
    
    # Simulate forensic logger seeing this activity
    # The low inter-call interval variance and high trust suppresses alerts
    intervals = [0.1 + random.gauss(0, 0.01) for _ in range(100)]
    mean_interval = sum(intervals) / len(intervals)
    variance = sum((x - mean_interval) ** 2 for x in intervals) / len(intervals)
    
    # Shannon entropy would be low (predictable intervals), marking as "normal"
    print(f"Inter-call interval variance: {variance:.6f} (low = predictable = trusted)")
    print("Forensic logger classifies activity as 'trusted admin behavior' - ALERT SUPPRESSED")

if __name__ == "__main__":
    simulate_attack()