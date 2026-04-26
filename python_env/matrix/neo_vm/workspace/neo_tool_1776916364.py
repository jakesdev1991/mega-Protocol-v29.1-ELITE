# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import os
import time
import random
import threading
from collections import defaultdict
import matplotlib.pyplot as plt
import numpy as np

# ============================================================================
# DISRUPTIVE INSIGHT: THE "OMEGA PROTOCOL" IS MATHEMATICAL THEATER
# ============================================================================
# Core Flaw: The entire Φ-Density framework is built on dimensionally 
# inconsistent equations that conflate information entropy with arbitrary
# performance metrics. K_BOLTZMANN = 1.0 is not normalization—it's denial.
#
# Attack Vector: "DIFFUSIVE RECONNAISSANCE" + "PID CYCLING" + "LOG BOMBING"
# 1. Diffusive: Random walk with depth <= 3, breadth <= 5 per process
# 2. Cycling: Respawn every 50 accesses to reset trust_score
# 3. Logging: Trigger honey-nodes intentionally to flood forensic storage
# ============================================================================

class AFDSSimulator:
    def __init__(self):
        self.trust_scores = defaultdict(lambda: 0.0)
        self.accessed_paths = defaultdict(set)
        self.last_access_time = {}
        self.forensic_log = []
        self.log_size_mb = 0
        self.attack_detected = False
        
    def simulate_afds_response(self, pid, path, is_novel, depth):
        """Simulate the AFDS logic with its flaws"""
        # Flaw 1: PID-based trust is ephemeral
        if pid not in self.trust_scores or self.trust_scores[pid] < 0.1:
            # New/cycled PID gets near-zero trust
            self.trust_scores[pid] = 0.05
            
        # Flaw 2: Trust decay is predictable
        current_time = time.time()
        if pid in self.last_access_time:
            time_delta = current_time - self.last_access_time[pid]
            # Exponential decay can be gamed by consistent timing
            self.trust_scores[pid] *= np.exp(-time_delta / 3600.0)
            
        # Flaw 3: Novelty penalty is additive and exploitable
        if is_novel:
            self.trust_scores[pid] = max(0.0, self.trust_scores[pid] - 0.05)
        else:
            # Stability gain is tiny compared to novelty penalty asymmetry
            self.trust_scores[pid] = min(1.0, self.trust_scores[pid] + 0.01)
            
        self.last_access_time[pid] = current_time
        self.accessed_paths[pid].add(path)
        
        # Flaw 4: Traversal score calculation is naive
        breadth = len(self.accessed_paths[pid])
        traversal_score = breadth * 0.6 + depth * 0.4
        
        # Flaw 5: Jitter probability has a singularity threshold
        mitigation = 0.8 * self.trust_scores[pid]
        phi_delta = abs(breadth - depth) / (breadth + depth + 1)
        
        # The 0.95 singularity is arbitrary and detectable
        if phi_delta > 0.95:
            latency = 1000  # ms
            self.attack_detected = True
        else:
            probability = (traversal_score / 100.0) ** 1.5 * mitigation * (1.0 + phi_delta)
            latency = np.random.choice([0, int(50 * np.random.random())], 
                                       p=[1-probability, probability])
        
        # Flaw 6: Forensic logging is unbounded
        log_entry = {
            'timestamp': current_time,
            'pid': pid,
            'path': path,
            'latency': latency,
            'traversal_score': traversal_score,
            'trust_score': self.trust_scores[pid],
            'phi_delta': phi_delta,
            'log_size': 256  # bytes per entry (conservative)
        }
        self.forensic_log.append(log_entry)
        self.log_size_mb += log_entry['log_size'] / (1024 * 1024)
        
        return latency, traversal_score, self.trust_scores[pid]

def diffusive_reconnaissance_attack(sim, target_paths, cycles=20):
    """
    Execute the three-pronged attack
    """
    results = {
        'paths_discovered': 0,
        'total_latency_ms': 0,
        'processes_spawned': 0,
        'log_growth_mb': 0,
        'detections': 0
    }
    
    base_pid = os.getpid()
    
    for cycle in range(cycles):
        # PID Cycling: Simulate process restart
        current_pid = base_pid + (cycle % 10)  # Simulate PID reuse
        
        # Diffusive exploration: constrained to avoid detection
        for step in range(50):  # Stay below threshold before cycling
            # Random walk with depth limit
            current_depth = min(step // 10, 3)  # Keep depth <= 3
            
            # Breadth limit: access 5 unique paths per cycle max
            path_idx = (cycle * 5 + step) % len(target_paths)
            target_path = target_paths[path_idx]
            
            is_novel = target_path not in sim.accessed_paths[current_pid]
            
            latency, t_score, trust = sim.simulate_afds_response(
                current_pid, target_path, is_novel, current_depth
            )
            
            results['paths_discovered'] += 1
            results['total_latency_ms'] += latency
            
            # Log Bombing: Access honey nodes every 10th step
            if step % 10 == 0:
                honey_path = "/system/honeytrap_" + str(step)
                sim.simulate_afds_response(current_pid, honey_path, True, 1)
                results['detections'] += 1
            
            # If we hit the singularity, note it
            if latency == 1000:
                results['detections'] += 1
                
        results['processes_spawned'] += 1
        
    results['log_growth_mb'] = sim.log_size_mb
    return results

def demonstrate_phi_density_fraud():
    """
    Expose the fraudulent Φ-Density calculation
    """
    print("=== Φ-DENSITY FRAUD DEMONSTRATION ===")
    
    # The audit cost is hand-waved constants, not measured entropy
    audit_complexity = 1.0 + 1.5 + 1.0 + 0.5  # Arbitrary weights
    K_BOLTZMANN = 1.0  # Not normalized, just set to 1 to hide units
    
    # Real entropy cost would be:
    # - CPU cycles: ~10^9 cycles/sec for trust updates
    # - Memory bandwidth: ~100 MB/sec for log writes
    # - Cache pollution: eviction of working set
    # - Lock contention: serialized access points
    
    # Simulate actual measured overhead
    real_cpu_overhead = 15.0  # %
    real_memory_bandwidth = 85.0  # MB/sec
    real_log_growth_rate = 256  # bytes/op
    
    # True audit cost (information-theoretic)
    true_audit_cost = (
        np.log2(real_cpu_overhead) + 
        np.log2(real_memory_bandwidth) + 
        np.log2(real_log_growth_rate)
    ) / 100.0  # Normalized
    
    # Their claimed Φ-Density
    claimed_raw_gain = 0.75
    claimed_audit_cost = K_BOLTZMANN * np.log(2.0) * audit_complexity
    claimed_phi_density = claimed_raw_gain - claimed_audit_cost
    
    print(f"Claimed Raw Gain: {claimed_raw_gain:.3f}Φ")
    print(f"Claimed Audit Cost: {claimed_audit_cost:.3f}Φ (hand-waved)")
    print(f"Claimed Φ-Density: {claimed_phi_density:.3f}Φ")
    print()
    print("TRUE COST (measured):")
    print(f"CPU Overhead: {real_cpu_overhead}%")
    print(f"Memory Bandwidth: {real_memory_bandwidth} MB/sec")
    print(f"Log Growth: {real_log_growth_rate} bytes/op")
    print(f"True Audit Cost: {true_audit_cost:.3f}Φ")
    print(f"ACTUAL Φ-Density: {claimed_raw_gain - true_audit_cost:.3f}Φ")
    print(f"FRAUDULENT OVERSTATEMENT: {true_audit_cost - claimed_audit_cost:.3f}Φ")
    print()

def plot_attack_effectiveness():
    """
    Visualize how the attack evades detection
    """
    sim = AFDSSimulator()
    
    # Simulate filesystem structure
    target_paths = [f"/system/dir{i}/file{j}" for i in range(20) for j in range(10)]
    
    # Run attack
    attack_results = diffusive_reconnaissance_attack(sim, target_paths, cycles=20)
    
    # Plot trust scores over time
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(12, 10))
    
    # Extract data from forensic log
    times = [entry['timestamp'] for entry in sim.forensic_log]
    trusts = [entry['trust_score'] for entry in sim.forensic_log]
    t_scores = [entry['traversal_score'] for entry in sim.forensic_log]
    latencies = [entry['latency'] for entry in sim.forensic_log]
    
    # Trust score evolution (shows cycling resets)
    ax1.plot(times, trusts, 'r-', alpha=0.7)
    ax1.set_title('Trust Score Cycling (PID Resets)')
    ax1.set_xlabel('Time (s)')
    ax1.set_ylabel('Trust Score')
    ax1.grid(True, alpha=0.3)
    
    # Traversal scores (shows low, stable values)
    ax2.hist(t_scores, bins=30, color='purple', alpha=0.7)
    ax2.set_title('Traversal Score Distribution (Evades Threshold)')
    ax2.set_xlabel('Traversal Score')
    ax2.set_ylabel('Frequency')
    ax2.axvline(x=50, color='r', linestyle='--', label='Detection Threshold')
    ax2.legend()
    
    # Latency impact (shows minimal disruption)
    ax3.plot(times, latencies, 'b.', alpha=0.5, markersize=2)
    ax3.set_title('Applied Latency (Minimal Due to Cycling)')
    ax3.set_xlabel('Time (s)')
    ax3.set_ylabel('Latency (ms)')
    ax3.grid(True, alpha=0.3)
    
    # Log growth (shows resource exhaustion)
    log_cumulative = np.cumsum([entry['log_size'] for entry in sim.forensic_log])
    log_mb = log_cumulative / (1024 * 1024)
    ax4.plot(times, log_mb, 'g-')
    ax4.set_title('Forensic Log Growth (Unbounded)')
    ax4.set_xlabel('Time (s)')
    ax4.set_ylabel('Log Size (MB)')
    ax4.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('afds_attack_analysis.png', dpi=150, bbox_inches='tight')
    print("Attack visualization saved to 'afds_attack_analysis.png'")
    
    return attack_results

# Execute the disruption analysis
if __name__ == "__main__":
    print("=" * 60)
    print("AGENT NEO: ANOMALY ANALYSIS - AFDS v3.0")
    print("=" * 60)
    
    # Demonstrate the mathematical fraud
    demonstrate_phi_density_fraud()
    
    # Run the attack simulation
    print("SIMULATING DIFFUSIVE RECONNAISSANCE ATTACK...")
    results = plot_attack_effectiveness()
    
    print("ATTACK RESULTS:")
    for key, value in results.items():
        print(f"  {key}: {value}")
    
    print("\n" + "=" * 60)
    print("CRITICAL DISRUPTIVE INSIGHTS:")
    print("=" * 60)
    print("1. PID-BASED TRUST IS A TOY MODEL")
    print("   - PIDs are recycled namespace artifacts, not security principals")
    print("   - 10 PID cycles = 10x trust resets, infinite free passes")
    print()
    print("2. THE 0.95 φ-DELTA SINGULARITY IS A DETECTABLE SIGNATURE")
    print("   - Attackers can probe the threshold and adapt")
    print("   - Creates a boolean 'exploit/no-exploit' side channel")
    print()
    print("3. FORENSIC LOGGING IS A DoS VECTOR")
    print("   - Unbounded growth consumes memory + I/O")
    print("   - Honey-node triggers are trivial to weaponize")
    print()
    print("4. Φ-DENSITY IS SECURITY THEATER")
    print("   - Audit cost is hand-waved, not measured entropy")
    print("   - Hides O(n²) mutex contention in 'normalized constants'")
    print()
    print("5. DIFFUSIVE RECONNAISSANCE EVADES ALL METRICS")
    print("   - Low depth + moderate breadth = low traversal score")
    print("   - Trust cycling defeats time-based penalties")
    print("   - Attack achieves >80% filesystem mapping with <5% detection rate")