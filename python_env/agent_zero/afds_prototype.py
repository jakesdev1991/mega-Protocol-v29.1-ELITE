# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import time
import random
import os
import math
from collections import deque

class AFDSPrototype:
    """
    v4.0 Adaptive Filesystem Defense Layer (AFDS).
    Pivoted from 'OS theory' to 'Statistically Validated Security Layer'.
    Implements:
    1. Behavioral Trust Decay & Acceleration
    2. Burst vs. Exploration separation
    3. Non-linear Probabilistic Jitter
    4. Forensic Reconstruction
    """
    def __init__(self):
        self.honey_nodes = ["/etc/shadow.bak", "/home/jake/.ssh/id_rsa.tmp", "/logs/omega_os_spec_v1.0.json"]
        self.process_stats = {} # pid -> stats dict
        self.traversal_threshold = 150.0 # Increased to reduce sensitivity
        self.trust_threshold = 80.0
        self.window_seconds = 5.0
        
    def vfs_lookup_hook(self, pid, path):
        """Refined FS-IDR hook with statistical separation."""
        now = time.time()
        
        if pid not in self.process_stats:
            self.process_stats[pid] = {
                'paths': set(),
                'calls': deque(),
                'history': [], 
                'score': 0.0,
                'trust_score': 0.0,
                'last_call': now,
                'burst_rate': 0.0,
                'exploration_rate': 0.0
            }
        
        stats = self.process_stats[pid]
        
        # 1. Trust Model: Acceleration & Decay
        # Trust increases with stable cadence, decays if inactive
        idle_time = now - stats['last_call']
        if 0.1 < idle_time < 1.0: # Consistent cadence (e.g. human or steady script)
            stats['trust_score'] += 0.5 # Accelerated trust
        elif idle_time > 10.0:
            stats['trust_score'] *= 0.9 # Decay trust for inactivity
            
        stats['last_call'] = now

        # 2. Honey-Node forensic trigger
        if path in self.honey_nodes:
            print(f"🚨 [AFDS-ALARM] HONEY-NODE ACCESS: PID {pid} -> {path}")
            self.reconstruct_attack(pid)
            return "ALARM"

        # 3. Burst vs Exploration Metrics
        stats['calls'].append(now)
        while stats['calls'] and now - stats['calls'][0] > self.window_seconds:
            stats['calls'].popleft()
        
        window_len = len(stats['calls'])
        stats['burst_rate'] = window_len / self.window_seconds
        
        is_new = path not in stats['paths']
        if is_new:
            stats['paths'].add(path)
            stats['exploration_rate'] += 1.0
        else:
            stats['exploration_rate'] *= 0.99 # Decay exploration penalty for repeated paths

        # 4. Scoring Function: f(burst, exploration, depth, trust)
        depth = path.count("/")
        # Higher weight on exploration than raw burst (to protect find/grep)
        raw_score = (1.0 * stats['burst_rate']) + (5.0 * stats['exploration_rate']) + (0.5 * depth)
        
        # Trust mitigation: score is reduced non-linearly by trust
        mitigation = 1.0 / (1.0 + (stats['trust_score'] / 10.0))
        stats['score'] = raw_score * mitigation
        
        # 5. Probabilistic State-Dependent Jitter
        status = "OK"
        if stats['score'] > self.traversal_threshold:
            # P = 1 - e^(-k * (score - threshold))
            prob = 1.0 - math.exp(-0.01 * (stats['score'] - self.traversal_threshold))
            
            if random.random() < prob:
                # Stealth Jitter: 1-50ms
                jitter = random.uniform(0.001, 0.050)
                time.sleep(jitter)
                stats['history'].append((now, path, jitter))
                status = "THROTTLED"
            else:
                stats['history'].append((now, path, 0))
        else:
            stats['history'].append((now, path, 0))
        
        return status

    def reconstruct_attack(self, pid):
        """Forensic reconstruction of the lead-up to a trigger."""
        stats = self.process_stats.get(pid)
        if not stats: return
        print(f"🔍 [AFDS-FORENSICS] Attack Reconstruction for PID {pid}:")
        for ts, path, delay in stats['history'][-10:]:
            print(f"  [{ts:.3f}] {path} (Lat: {delay*1000:.1f}ms)")

if __name__ == "__main__":
    afds = AFDSPrototype()
    print("🛡️ [AFDS v4.0] FS-IDR Prototype active.")
    
    # 🕵️ Attacker Simulation (Random, fast exploration)
    pid = 9999
    print(f"🕵️  Simulating attacker (PID {pid}) - High Novelty Mapping...")
    for i in range(200):
        p = f"/data/vol1/user{i}/config/secrets.txt"
        afds.vfs_lookup_hook(pid, p)
    
    # 🪤 Hit Honeypot
    afds.vfs_lookup_hook(pid, "/etc/shadow.bak")
    
    # 🟢 Trusted Admin Simulation (Repetitive, steady cadence)
    admin_pid = 100
    print(f"\n🟢 Simulating Trusted Admin (PID {admin_pid}) - Stable Path Reuse...")
    for i in range(200):
        p = f"/home/admin/tools/system_check.sh" 
        afds.vfs_lookup_hook(admin_pid, p)
        time.sleep(0.15) # Steady cadence
    
    print(f"📊 PID {pid} Final Score: {afds.process_stats[pid]['score']:.2f}")
    print(f"📊 PID {admin_pid} Final Score: {afds.process_stats[admin_pid]['score']:.2f} | Trust: {afds.process_stats[admin_pid]['trust_score']:.2f}")
