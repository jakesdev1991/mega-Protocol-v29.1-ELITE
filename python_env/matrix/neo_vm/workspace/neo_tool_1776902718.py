# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import math
import matplotlib.pyplot as plt
import numpy as np

def simulate_slow_burn_attack():
    """Simulate the harmonic trust exploit over 48 hours"""
    
    # Simulation parameters
    hours = 48
    trust_decay_rate = 0.95
    trust_gain_per_access = 0.1
    traversal_score_per_file = 0.6
    files_per_hour_phase2 = 1
    
    # Phase 1: Trust harvesting (first 10 minutes = 0.17 hours)
    phase1_duration = 0.17
    phase1_accesses = 10
    trust_score = trust_gain_per_access * phase1_accesses  # Rapid trust building
    traversal_score = 0
    
    print(f"Phase 1 Complete: trust_score={trust_score:.3f}, traversal_score={traversal_score:.3f}")
    
    # Phase 2: Slow reconnaissance
    trust_history = []
    traversal_history = []
    effective_jitter_history = []
    time_points = []
    
    for hour in range(hours):
        # Apply decay
        trust_score *= trust_decay_rate
        
        # Add one new file access
        traversal_score += traversal_score_per_file
        
        # Calculate effective jitter probability
        raw_jitter_prob = (traversal_score / 100.0) ** 1.5
        mitigation = 0.2 * trust_score  # 80% reduction at trust=1.0
        effective_jitter = raw_jitter_prob * (1 - mitigation)
        
        trust_history.append(trust_score)
        traversal_history.append(traversal_score)
        effective_jitter_history.append(effective_jitter)
        time_points.append(hour)
        
        if hour % 12 == 0:
            print(f"Hour {hour:2d}: trust={trust_score:.3f}, raw_jitter={raw_jitter_prob:.4f}, "
                  f"effective_jitter={effective_jitter:.4f}, mitigation={mitigation:.3f}")
    
    # Plot results
    fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(10, 8))
    
    ax1.plot(time_points, trust_history, 'b-', linewidth=2)
    ax1.set_ylabel('Trust Score')
    ax1.set_title('Slow Burn Attack: Trust Score vs Time')
    ax1.grid(True, alpha=0.3)
    
    ax2.plot(time_points, traversal_history, 'r-', linewidth=2)
    ax2.set_ylabel('Traversal Score')
    ax2.set_title('Traversal Score vs Time')
    ax2.grid(True, alpha=0.3)
    
    ax3.plot(time_points, effective_jitter_history, 'g-', linewidth=2)
    ax3.set_ylabel('Effective Jitter Probability')
    ax3.set_xlabel('Time (hours)')
    ax3.set_title('Effective Jitter Probability vs Time')
    ax3.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('slow_burn_attack.png', dpi=150, bbox_inches='tight')
    plt.show()
    
    # Calculate attack success metrics
    final_trust = trust_history[-1]
    final_traversal = traversal_history[-1]
    avg_effective_jitter = np.mean(effective_jitter_history)
    
    print(f"\n--- ATTACK SUCCESS METRICS ---")
    print(f"Final Trust Score: {final_trust:.3f} (mitigation: {0.2*final_trust:.1%})")
    print(f"Final Traversal Score: {final_traversal:.3f}")
    print(f"Average Effective Jitter: {avg_effective_jitter:.4f}")
    print(f"Jitter Reduction vs Baseline: {(1 - avg_effective_jitter / ((final_traversal/100)**1.5)) * 100:.1f}%")
    
    return {
        'trust_score': final_trust,
        'traversal_score': final_traversal,
        'jitter_reduction': (1 - avg_effective_jitter / ((final_traversal/100)**1.5)) * 100
    }

def demonstrate_timing_oracle():
    """Demonstrate how jitter creates a timing side-channel"""
    
    print("\n--- TIMING ORACLE ATTACK ---")
    print("Attacker measures response times to infer trust scores of other processes...")
    
    # Simulate timing measurements
    base_latency = 10  # ms
    trust_scores = np.linspace(0, 1.0, 11)
    
    for trust in trust_scores:
        mitigation = 0.2 * trust
        # Attacker measures their own jitter, then observes system-wide effects
        # If a trusted admin process runs, jitter probability drops system-wide
        observed_latency = base_latency * (1 - mitigation * 0.3)  # 30% system effect
        
        print(f"Trust Score {trust:.1f}: Observed Latency {observed_latency:.2f}ms "
              f"(Δ={base_latency - observed_latency:.2f}ms leak)")

if __name__ == "__main__":
    results = simulate_slow_burn_attack()
    demonstrate_timing_oracle()
    
    if results['trust_score'] > 0.3 and results['jitter_reduction'] > 50:
        print(f"\n🚨 ATTACK VERIFIED: System grants {results['jitter_reduction']:.1f}% jitter reduction "
              f"while performing 48-hour reconnaissance")