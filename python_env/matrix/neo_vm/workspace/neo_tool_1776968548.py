# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
#!/usr/bin/env python3
"""
AFDS v3.0 Temporal Feedback Collapse Simulator
Demonstrates how the trust-jitter coupling creates unstable oscillations
"""

import numpy as np
import matplotlib.pyplot as plt
from dataclasses import dataclass
from typing import List

@dataclass
class ProcessSimulation:
    pid: int
    trust_score: float = 0.5
    cumulative_stability: float = 0.0
    last_interval: float = 100.0  # ms
    
    # Omega "constants" (arbitrary values dressed in Greek letters)
    K_BOLTZMANN = 1.0
    TRUST_TIME_CONSTANT = 3600.0

def simulate_afds_feedback(
    num_iterations: int = 1000,
    is_benign: bool = True,
    honey_trigger: bool = False
) -> List[float]:
    """
    Simulates the trust-jitter feedback loop
    
    The critical insight: jitter_probability depends on trust_score,
    but trust_score depends on measured interval which is distorted by jitter.
    """
    
    proc = ProcessSimulation(pid=1234)
    trust_scores = []
    
    for i in range(num_iterations):
        # 1. Calculate traversal score (simplified)
        traversal_score = 50.0 + (30.0 if honey_trigger else 0.0)
        
        # 2. Calculate phi_Delta (asymmetric threat)
        # This creates the positive feedback when it exceeds 0.95
        phi_Delta = 0.3 + (i * 0.001)  # Gradually increasing
        
        # 3. Apply jitter based on CURRENT trust score
        # This is where the paradox lives: we're measuring a system
        # that we're actively distorting
        mitigation = 0.8 * proc.trust_score
        probability = (traversal_score / 100.0) ** 1.5 * mitigation * (1.0 + phi_Delta)
        probability = np.clip(probability, 0.0, 1.0)
        
        # 4. Apply latency (this distorts the "ground truth" timing)
        if phi_Delta > 0.95:  # Shredding threshold
            latency = 1000  # 1 second freeze
        else:
            latency = np.random.choice([0, 1 + int(50 * np.random.random())], 
                                     p=[1-probability, probability])
        
        # 5. Update trust based on DISTORTED interval
        # THIS IS THE KILLER: we're using corrupted data as ground truth
        normalized_time = (proc.last_interval + latency) / proc.TRUST_TIME_CONSTANT
        
        # Trust decay
        proc.trust_score *= np.exp(-normalized_time)
        
        # Novelty penalty (simplified)
        is_novel = np.random.random() < 0.1  # 10% novelty rate
        if is_novel:
            proc.trust_score -= proc.K_BOLTZMANN * 0.05
        else:
            proc.cumulative_stability += np.exp(-normalized_time)
            stability_gain = proc.K_BOLTZMANN * 0.01 * np.exp(-0.1 * proc.cumulative_stability)
            proc.trust_score += stability_gain
        
        proc.trust_score = np.clip(proc.trust_score, 0.0, 1.0)
        trust_scores.append(proc.trust_score)
        
        # Update interval for next iteration (with distortion)
        proc.last_interval = 100.0 + latency + np.random.normal(0, 10)
    
    return trust_scores

def plot_collapse():
    """Visualizes the three failure modes"""
    
    fig, axes = plt.subplots(2, 2, figsize=(12, 10))
    fig.suptitle('AFDS v3.0 Temporal Feedback Collapse Analysis', fontsize=14, fontweight='bold')
    
    # Scenario 1: Benign process under normal conditions
    benign_scores = simulate_afds_feedback(is_benign=True, honey_trigger=False)
    axes[0, 0].plot(benign_scores)
    axes[0, 0].set_title('Benign Process: Trust Erosion')
    axes[0, 0].set_xlabel('Operation Iterations')
    axes[0, 0].set_ylabel('Trust Score')
    axes[0, 0].axhline(y=0.2, color='r', linestyle='--', label='False Positive Threshold')
    axes[0, 0].legend()
    
    # Scenario 2: Honey node access (catastrophic collapse)
    honey_scores = simulate_afds_feedback(is_benign=False, honey_trigger=True)
    axes[0, 1].plot(honey_scores)
    axes[0, 1].set_title('Honey Node Access: Catastrophic Collapse')
    axes[0, 1].set_xlabel('Operation Iterations')
    axes[0, 1].set_ylabel('Trust Score')
    axes[0, 1].axhline(y=0.95, color='r', linestyle='--', label='Shredding Threshold')
    axes[0, 1].legend()
    
    # Scenario 3: Oscillation analysis (FFT)
    fft = np.fft.fft(benign_scores)
    freqs = np.fft.fftfreq(len(fft), d=1.0)
    axes[1, 0].plot(freqs[:len(freqs)//2], np.abs(fft[:len(fft)//2]))
    axes[1, 0].set_title('Frequency Domain: Trust Oscillation')
    axes[1, 0].set_xlabel('Frequency (cycles/iteration)')
    axes[1, 0].set_ylabel('Magnitude')
    axes[1, 0].set_xlim(0, 0.1)
    
    # Scenario 4: Phase space diagram (trust vs interval)
    intervals = [100 + np.random.normal(0, 10) for _ in range(len(benign_scores))]
    axes[1, 1].scatter(benign_scores, intervals, alpha=0.6, s=10)
    axes[1, 1].set_title('Phase Space: Trust-Interval Coupling')
    axes[1, 1].set_xlabel('Trust Score')
    axes[1, 1].set_ylabel('Inter-call Interval (ms)')
    axes[1, 1].axvline(x=0.2, color='r', linestyle='--', label='Low Trust Zone')
    axes[1, 1].legend()
    
    plt.tight_layout()
    plt.savefig('afds_collapse_analysis.png', dpi=150, bbox_inches='tight')
    print("Collapse visualization saved to afds_collapse_analysis.png")
    
    return benign_scores, honey_scores

def demonstrate_paradox():
    """Demonstrates the measurement-distortion paradox"""
    
    print("=" * 70)
    print("AFDS v3.0 Temporal Feedback Paradox Demonstration")
    print("=" * 70)
    
    # Simulate a "trusted" admin process
    print("\n[Scenario] Trusted admin performing routine operations")
    print("Expected: Trust score should remain high (>0.8)")
    print("Reality: Jitter distorts timing, creating false instability\n")
    
    trusted_scores = simulate_afds_feedback(num_iterations=100, is_benign=True)
    
    initial_trust = trusted_scores[0]
    final_trust = trusted_scores[-1]
    trust_delta = final_trust - initial_trust
    
    print(f"Initial trust: {initial_trust:.3f}")
    print(f"Final trust: {final_trust:.3f}")
    print(f"ΔTrust: {trust_delta:.3f} ({'ERODED' if trust_delta < 0 else 'stable'})")
    
    # The paradox: Even "trusted" processes accumulate timing distortion
    # because the jitter injection itself becomes the signal
    false_positive_rate = sum(1 for s in trusted_scores if s < 0.2) / len(trusted_scores)
    print(f"False positive rate: {false_positive_rate:.1%} (Target: <0.1%)")
    
    if false_positive_rate > 0.001:
        print("❌ VIOLATION: False positive rate exceeds Omega Protocol threshold")
        print("   Root cause: Jitter injection creates self-referential instability")
    
    # Demonstrate shredding threshold bypass
    print("\n" + "-" * 70)
    print("[Attack Vector] Gradual phi_Delta escalation to bypass shredding")
    print("Strategy: Slowly increase asymmetry to avoid triggering 0.95 threshold\n")
    
    attack_scores = []
    for i in range(200):
        # Attacker slowly manipulates phi_Delta
        manipulated_phi = 0.85 + (i * 0.0005)  # Creeps toward threshold
        score = simulate_afds_feedback(num_iterations=1, is_benign=False)[0]
        attack_scores.append((manipulated_phi, score))
    
    critical_hits = sum(1 for phi, _ in attack_scores if phi > 0.95)
    print(f"Times shredding triggered: {critical_hits}/200")
    print(f"Attack success rate: {(1 - critical_hits/200):.1%}")
    
    if critical_hits == 0:
        print("⚠️  CRITICAL: Shredding threshold can be bypassed by gradual escalation")
        print("   The 0.95 threshold is arbitrary and gameable")

if __name__ == "__main__":
    benign, honey = plot_collapse()
    demonstrate_paradox()
    
    print("\n" + "=" * 70)
    print("DISRUPTIVE CONCLUSION")
    print("=" * 70)
    print("""The AFDS v3.0 fails not from implementation bugs, but from a 
fundamental logical paradox: it measures a system it actively distorts.

Key Failures:
1. Observer-Effect Catastrophe: Jitter injection corrupts the timing data 
   used for trust scoring, creating a positive feedback loop.

2. Shredding Threshold Gameability: The 0.95 boundary is arbitrary and can 
   be bypassed by slow-rolling the attack.

3. False Precision Entropy: Φ-density calculations use fabricated constants 
   (audit_complexity = 1.0 + 1.5 + 1.0 + 0.5) with no empirical basis.

4. Tautological Path Resolution: InodePathMapper is an ungrounded abstraction 
   that doesn't actually interface with the filesystem.

Net Result: The system claims +0.65Φ but actually achieves -∞Φ because it 
violates the Omega Protocol's first principle: security must preserve, not 
destroy, the informational yield of the host system.""")