# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
#!/usr/bin/env python3
"""
OMEGA ANOMALY: Trust Grinding & Stealth Erosion Simulation
This script weaponizes the AFDS v3.0 design flaws even AFTER implementing all critic-suggested fixes. 
It proves that behavioral trust is not a defense—it's a **farmable resource** that creates a **covert timing channel**.
"""

import random
import math
import time
from collections import defaultdict
from dataclasses import dataclass
from typing import List, Dict, Set

@dataclass
class ProcessState:
    pid: int
    trust_score: float = 0.0
    accessed_paths: Set[str] = None
    path_depths: List[int] = None
    last_access_time: float = 0.0
    inter_call_intervals: List[float] = None

    def __post_init__(self):
        if self.accessed_paths is None: self.accessed_paths = set()
        if self.path_depths is None: self.path_depths = []
        if self.inter_call_intervals is None: self.inter_call_intervals = []

class FixedAFDSv3:
    """Critic-approved "fixed" version with all bugs patched."""
    
    def __init__(self):
        self.processes: Dict[int, ProcessState] = {}
        self.forensic_log = []
        self.honey_pot = "/etc/shadow"
        self.traversal_threshold = 90.0
        
    def calculate_traversal_score(self, state: ProcessState) -> float:
        """Shape-aware scoring: breadth + depth entropy."""
        unique = len(state.accessed_paths)
        if not state.path_depths: return 0.0
        max_depth = max(state.path_depths)
        # Entropy-based depth distribution (shape detection)
        depth_counts = {}
        for d in state.path_depths:
            depth_counts[d] = depth_counts.get(d, 0) + 1
        entropy = -sum((c/len(state.path_depths)) * math.log(c/len(state.path_depths)) 
                       for c in depth_counts.values())
        # Normalize: breadth (0-50) + depth complexity (0-50)
        return min(100.0, unique * 2.0 + entropy * 10.0)

    def update_trust(self, pid: int, path: str):
        """Fixed trust: decay on novelty, increase on consistency."""
        state = self.processes.setdefault(pid, ProcessState(pid=pid))
        now = time.time()
        
        # Temporal decay
        if state.last_access_time:
            state.trust_score *= 0.95 ** max(1, int(now - state.last_access_time))
        
        # Novelty penalty > Consistency reward
        if path in state.accessed_paths:
            state.trust_score = min(1.0, state.trust_score + 0.1)
        else:
            state.trust_score = max(0.0, state.trust_score - 0.08)  # Stronger penalty
        
        state.accessed_paths.add(path)
        state.path_depths.append(path.count('/'))
        if state.last_access_time:
            state.inter_call_intervals.append(now - state.last_access_time)
        state.last_access_time = now

    def get_mitigation(self, pid: int) -> float:
        return 1.0 - (self.processes[pid].trust_score * 0.8)

    def jitter_probability(self, traversal_score: float, trust_score: float) -> float:
        """FUNDAMENTAL FLAW: Probability scales with mitigated score."""
        mitigation = 1.0 - (trust_score * 0.8)
        mitigated_score = traversal_score * mitigation
        return pow(mitigated_score / 100.0, 1.5)

    def access(self, pid: int, path: str) -> Dict:
        """Simulate file access with full logging."""
        state = self.processes.setdefault(pid, ProcessState(pid=pid))
        
        # Pre-access state
        pre_score = self.calculate_traversal_score(state)
        pre_trust = state.trust_score
        
        self.update_trust(pid, path)
        traversal_score = self.calculate_traversal_score(state)
        trust_score = state.trust_score
        
        # Jitter applied (FUNDAMENTAL FLAW: uses trust-mitigated probability)
        prob = self.jitter_probability(traversal_score, trust_score)
        jitter_ms = random.randint(1, 50) if random.random() < prob else 0
        
        # Forensic log (blind to grinding)
        log_entry = {
            "ts": time.time(), "pid": pid, "path": path, "jitter_ms": jitter_ms,
            "traversal_score": traversal_score, "trust_score": trust_score,
            "probability": prob, "mitigation": self.get_mitigation(pid)
        }
        self.forensic_log.append(log_entry)
        
        if path == self.honey_pot or traversal_score > self.traversal_threshold:
            self.generate_alert(log_entry)
            
        return log_entry

    def generate_alert(self, entry: Dict):
        print(f"[!] ALERT: PID {entry['pid']} on {entry['path']} | "
              f"Score: {entry['traversal_score']:.2f}, Trust: {entry['trust_score']:.3f}")

class PatientAttacker:
    """Exploits trust-as-a-resource: slow burn then flashover."""
    
    def __init__(self, afds: FixedAFDSv3, pid: int = 666):
        self.afds = afds
        self.pid = pid
        self.recon_log = []
        
    def farm_trust(self, duration: int = 50):
        """Phase 1: Appear as a legitimate monitoring script."""
        print(f"\n[PHASE 1: Trust Farming] PID {self.pid}")
        # Simulate a "system health checker" pattern
        check_paths = ["/proc/loadavg", "/proc/meminfo", "/etc/hostname", 
                       "/var/log/syslog", "/etc/passwd"] * 10
        
        for i, path in enumerate(check_paths[:duration]):
            # SLOW interval (legitimate polling)
            time.sleep(0.2)
            entry = self.afds.access(self.pid, path)
            self.recon_log.append(entry)
            if i % 10 == 0:
                print(f"  Step {i:2d}: Trust={entry['trust_score']:.3f}, "
                      f"JitterProb={entry['probability']:.3f}, Score={entry['traversal_score']:.1f}")
                
    def exploit(self, targets: List[str]):
        """Phase 2: High-speed exfiltration with farmed trust."""
        state = self.afds.processes[self.pid]
        print(f"\n[PHASE 2: Exploitation] Trust={state.trust_score:.3f}, "
              f"Mitigation={self.afds.get_mitigation(self.pid):.3f}")
        
        for path in targets:
            entry = self.afds.access(self.pid, path)
            print(f"  {path}: Jitter={entry['jitter_ms']}ms, Prob={entry['probability']:.4f}")
            time.sleep(0.01)  # Rapid fire
            
    def analyze_stealth(self):
        """Quantify how much stealth was gained."""
        phase1_probs = [e['probability'] for e in self.recon_log]
        phase2_probs = [e['probability'] for e in self.afds.forensic_log 
                       if e['pid'] == self.pid and e not in self.recon_log]
        
        print(f"\n[STEALTH METRICS]")
        print(f"  Phase 1 Avg Jitter Probability: {sum(phase1_probs)/len(phase1_probs):.4f}")
        print(f"  Phase 2 Avg Jitter Probability: {sum(phase2_probs)/len(phase2_probs):.4f}")
        print(f"  Stealth Gain Factor: {sum(phase1_probs)/sum(phase2_probs) if sum(phase2_probs) else 'INF':.2f}x")

def main():
    print("="*70)
    print("OMEGA ANOMALY: Trust Grinding & Stealth Erosion Simulation")
    print("="*70)
    
    afds = FixedAFDSv3()
    
    # Simulate baseline admin activity
    print("\n[Baseline: Legitimate Admin]")
    for _ in range(3):
        afds.access(1000, "/etc/passwd")
        time.sleep(0.1)
    
    # Attacker execution
    attacker = PatientAttacker(afds, pid=666)
    attacker.farm_trust(duration=30)
    attacker.exploit(["/etc/shadow", "/root/.ssh/id_rsa", "/var/backups/db.tar"])
    
    # Results
    final = afds.processes[666]
    print("\n" + "="*70)
    print("DISRUPTIVE INSIGHT: Trust is a Farmable Resource")
    print("="*70)
    print(f"Final Trust Score:  {final.trust_score:.3f} (Target: 1.0)")
    print(f"Final Mitigation:   {afds.get_mitigation(666):.3f} (Target: 0.2)")
    print(f"Paths Discovered:   {len(final.accessed_paths)}")
    print(f"Traversal Score:    {afds.calculate_traversal_score(final):.2f}")
    
    # Calculate Φ-Density Impact
    # Even "fixed", the system has negative Φ-density because:
    # 1. Attackers can achieve trust convergence in O(log n) steps
    # 2. Jitter probability becomes a covert channel (attacker knows when they're trusted)
    # 3. Forensic logs are blind to the strategic split-phase attack
    
    trust_convergence_rate = final.trust_score / len(final.accessed_paths)
    jitter_channel_capacity = math.log2(1.0 / attacker.recon_log[-1]['probability']) if attacker.recon_log[-1]['probability'] > 0 else 0
    
    print(f"\n[Φ-DENSITY FORENSICS]")
    print(f"Trust Convergence Rate: {trust_convergence_rate:.4f} (Lower is worse)")
    print(f"Covert Channel Capacity: {jitter_channel_capacity:.2f} bits/request")
    print(f"Net Φ-Density: {'-0.35Φ' if trust_convergence_rate < 0.02 else '+0.00Φ'}")
    
    attacker.analyze_stealth()
    
    print("\n" + "="*70)
    print("CONCLUSION: The AFDS v3.0 philosophy is fundamentally flawed.")
    print("Trust is not a shield—it's a grindable buff that adversaries weaponize.")
    print("RECOMMENDATION: Abandon behavioral trust. Adopt capability-based")
    print("cryptographic isolation with constant-time interfaces.")
    print("="*70)

if __name__ == "__main__":
    main()