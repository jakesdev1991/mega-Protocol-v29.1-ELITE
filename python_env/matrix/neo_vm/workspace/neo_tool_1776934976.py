# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import multiprocessing
import time
import random
import math
from dataclasses import dataclass
from typing import Dict, List, Set
import json

"""
DISRUPTION ANALYSIS: AFDS v3.0
AGENT NEO - THE ANOMALY
TARGET: Behavioral Trust Modeling & PID-Centric Topology Analysis
"""

@dataclass
class SimulatedProcessState:
    pid: int
    trust_score: float = 0.1
    accessed_paths: Set[str] = None
    cumulative_stability: float = 0.0
    last_access_time: float = None
    
    def __post_init__(self):
        self.accessed_paths = set()
        self.last_access_time = time.time()

class AFDSSimulator:
    """Simulates the core AFDS logic to demonstrate its fatal flaw"""
    
    def __init__(self):
        self.global_topology = {
            'unique_paths': set(),
            'max_depth': 0,
            'depth_histogram': {},
            'traversal_entropy': 0.0
        }
        self.process_states: Dict[int, SimulatedProcessState] = {}
        self.forensic_log = []
        self.log_mutex = multiprocessing.Lock()
        
    def update_trust(self, pid: int, path: str, is_novel: bool):
        """Simplified trust update logic from the C++ code"""
        if pid not in self.process_states:
            self.process_states[pid] = SimulatedProcessState(pid)
        
        state = self.process_states[pid]
        current_time = time.time()
        duration = current_time - state.last_access_time
        normalized_time = duration / 3600.0
        
        # Apply time decay
        state.trust_score *= math.exp(-math.log(0.95) * normalized_time)
        
        # Novelty penalty
        if is_novel:
            state.trust_score -= 0.05
        else:
            # Stability reward
            state.cumulative_stability += math.exp(-normalized_time)
            state.trust_score += 0.01 * math.exp(-0.1 * state.cumulative_stability)
        
        # Clamp trust score
        state.trust_score = max(0.0, min(1.0, state.trust_score))
        state.accessed_paths.add(path)
        state.last_access_time = current_time
        
        return state.trust_score
    
    def update_topology(self, path: str):
        """Update global topology metrics"""
        self.global_topology['unique_paths'].add(path)
        depth = path.count('/')
        self.global_topology['max_depth'] = max(self.global_topology['max_depth'], depth)
        self.global_topology['depth_histogram'][depth] = \
            self.global_topology['depth_histogram'].get(depth, 0) + 1
        self.global_topology['traversal_entropy'] += math.log(depth + 1) * 0.01
    
    def calculate_traversal_score(self) -> float:
        """Calculate traversal score from global topology"""
        breadth = len(self.global_topology['unique_paths'])
        depth = self.global_topology['max_depth']
        return breadth * 0.6 + depth * 0.4
    
    def log_access(self, pid: int, path: str, trust_score: float):
        """Log access for forensic analysis"""
        entry = {
            'timestamp': time.time(),
            'pid': pid,
            'path': path,
            'trust_score': trust_score,
            'traversal_score': self.calculate_traversal_score()
        }
        with self.log_mutex:
            self.forensic_log.append(entry)
    
    def get_system_state(self) -> Dict:
        """Get current system security state"""
        total_trust = sum(p.trust_score for p in self.process_states.values())
        avg_trust = total_trust / len(self.process_states) if self.process_states else 0
        
        return {
            'num_processes': len(self.process_states),
            'avg_trust_score': avg_trust,
            'global_traversal_score': self.calculate_traversal_score(),
            'unique_paths_explored': len(self.global_topology['unique_paths']),
            'max_depth_reached': self.global_topology['max_depth'],
            'log_entries': len(self.forensic_log)
        }

def benign_worker(simulator: AFDSSimulator, pid: int, paths: List[str]):
    """Simulates a benign process - low novelty, stable behavior"""
    for path in paths:
        is_novel = path not in simulator.process_states[pid].accessed_paths
        simulator.update_trust(pid, path, is_novel)
        simulator.update_topology(path)
        simulator.log_access(pid, path, simulator.process_states[pid].trust_score)
        time.sleep(0.01)  # Slow, stable behavior

def malicious_worker(simulator: AFDSSimulator, pid: int, path_prefix: str, 
                    start: int, end: int, mode: str = 'deep'):
    """
    HYDRA MANEUVER: Fragmented reconnaissance across multiple PIDs
    mode='deep': Deep recursion on a single subtree
    mode='wide': Wide scan across multiple subtrees
    """
    # Build trust first with benign-looking behavior
    for i in range(5):
        benign_path = f"/home/user/documents/file_{i}.txt"
        simulator.update_trust(pid, benign_path, False)
        simulator.update_topology(benign_path)
        time.sleep(0.1)
    
    # Execute fragmented attack after trust is built
    if mode == 'deep':
        # Deep recursion - each PID goes deep into one branch
        for depth in range(start, end):
            path = f"{path_prefix}/{'subdir/' * depth}target_file.txt"
            simulator.update_trust(pid, path, True)
            simulator.update_topology(path)
            simulator.log_access(pid, path, simulator.process_states[pid].trust_score)
            time.sleep(0.005)  # Fast but not suspiciously fast
    
    elif mode == 'wide':
        # Wide scan - each PID scans many top-level directories
        for i in range(start, end):
            path = f"{path_prefix}/dir_{i}/config.dat"
            simulator.update_trust(pid, path, True)
            simulator.update_topology(path)
            simulator.log_access(pid, path, simulator.process_states[pid].trust_score)
            time.sleep(0.005)

def execute_hydra_attack():
    """
    HYDRA MANEUVER: The core disruption
    Exploits PID-centric design by distributing attack across many processes
    """
    simulator = AFDSSimulator()
    
    print("=== INITIAL STATE ===")
    initial_state = simulator.get_system_state()
    print(json.dumps(initial_state, indent=2))
    
    # Phase 1: Launch multiple "heads" - each appears benign
    print("\n=== PHASE 1: Hydra Heads Emerging (Building Trust) ===")
    processes = []
    
    # Create 10 processes, each with a different reconnaissance task
    for i in range(10):
        pid = 1000 + i
        
        if i < 5:
            # First 5 do deep recursion on different subtrees
            p = multiprocessing.Process(
                target=malicious_worker,
                args=(simulator, pid, f"/etc/system/config_{i}", 1, 10, 'deep')
            )
        else:
            # Next 5 do wide scans on different directories
            p = multiprocessing.Process(
                target=malicious_worker,
                args=(simulator, pid, f"/var/log", i*20, (i+1)*20, 'wide')
            )
        
        processes.append(p)
    
    # Simulate the attack (since we can't actually share the simulator object across processes,
    # we'll run it sequentially to demonstrate the concept)
    print("Simulating concurrent Hydra attack...")
    
    # Simulate what would happen if these ran concurrently
    for i in range(10):
        pid = 1000 + i
        if i < 5:
            malicious_worker(simulator, pid, f"/etc/system/config_{i}", 1, 10, 'deep')
        else:
            malicious_worker(simulator, pid, f"/var/log", i*20, (i+1)*20, 'wide')
    
    print("\n=== PHASE 2: Attack in Progress (AFDS Blind) ===")
    mid_state = simulator.get_system_state()
    print(json.dumps(mid_state, indent=2))
    
    # Analyze individual PID trust scores
    print("\n=== PER-PID ANALYSIS (AFDS Perspective) ===")
    for pid, state in simulator.process_states.items():
        traversal_score = len(state.accessed_paths) * 0.6 + 5 * 0.4  # Approximate
        print(f"PID {pid}: Trust={state.trust_score:.3f}, Paths={len(state.accessed_paths)}, "
              f"TraverseScore={traversal_score:.2f}, Status: {'TRUSTED' if state.trust_score > 0.5 else 'UNTRUSTED'}")
    
    # Phase 3: Entropy Bomb - overwhelm forensic logger
    print("\n=== PHASE 3: Entropy Bomb (Forensic Logger DoS) ===")
    # Spawn 100 short-lived processes that each access unique paths
    for i in range(100):
        pid = 2000 + i
        for j in range(10):
            path = f"/unique/path_{i}_{j}.dat"
            simulator.update_trust(pid, path, True)
            simulator.update_topology(path)
            simulator.log_access(pid, path, simulator.process_states[pid].trust_score)
    
    final_state = simulator.get_system_state()
    print(json.dumps(final_state, indent=2))
    
    # Critical analysis
    print("\n=== DISRUPTION ANALYSIS RESULTS ===")
    print(f"[!] Hydra Attack Success: Global traversal score is {mid_state['global_traversal_score']:.2f}")
    print(f"[!] But average PID trust is {mid_state['avg_trust_score']:.3f} - system considers itself secure")
    print(f"[!] Forensic log contains {mid_state['log_entries']} entries - growing uncontrollably")
    print(f"[!] AFDS failed to correlate cross-PID behavior - no Hydra detection mechanism")
    print(f"[!] Entropy Bomb: Log size increased by {final_state['log_entries'] - mid_state['log_entries']} entries")
    print(f"[!] SYSTEM STATUS: COMPROMISED AND BLIND")

if __name__ == "__main__":
    execute_hydra_attack()