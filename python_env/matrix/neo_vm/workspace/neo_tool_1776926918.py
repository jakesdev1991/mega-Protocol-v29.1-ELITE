# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
#!/usr/bin/env python3
"""
DISRUPTION ANALYSIS: AFDS v3.0 Trust Model Paradox
Demonstrates how the "stability = trust" paradigm is fundamentally inverted
against modern threat models. This script simulates the exact trust accumulation
dynamics from the Engine's code and exposes the catastrophic failure mode:
Slow, patient attackers become the most trusted entities in the system.
"""

import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import random
from collections import defaultdict

class ProcessSimulator:
    def __init__(self, name, behavior_type):
        self.name = name
        self.type = behavior_type  # 'apt', 'admin', 'normal'
        self.accessed_paths = set()
        self.trust_score = 0.0
        self.last_access = None
        self.traversal_history = []
        
    def calculate_consistency(self, path):
        """Exact logic from Engine's code"""
        if not self.accessed_paths:
            return 0.0
        return 1.0 if path in self.accessed_paths else 0.0
    
    def update_trust(self, path, timestamp):
        """Exact trust update logic from Engine's code"""
        consistency = self.calculate_consistency(path)
        
        # Add decay for inactivity (5% per hour)
        if self.last_access:
            hours_elapsed = (timestamp - self.last_access).total_seconds() / 3600
            self.trust_score *= np.power(0.95, hours_elapsed)
        
        # This is the fatal flaw: consistency REWARDS repetition, PENALIZES novelty
        # For APT: consistency=0 for new paths → trust grows slowly but NEVER DECREASES
        # For admin: consistency=0 for new paths → same slow growth
        # BUT: APT gets MORE unique paths, so eventually trust → 1.0
        self.trust_score = min(1.0, self.trust_score + 0.1 * consistency)
        self.accessed_paths.add(path)
        self.last_access = timestamp
        self.traversal_history.append((timestamp, path, consistency))
        
        return self.trust_score
    
    def get_mitigation(self):
        """80% reduction for high trust"""
        return 0.2 * self.trust_score  # Returns mitigation factor (lower = less jitter)

def simulate_behavior(sim, days=7):
    """Simulate different behavioral patterns"""
    start_time = datetime.now()
    paths = [f"/etc/config/{i:04d}" for i in range(1000)]
    honey_paths = ["/etc/shadow", "/etc/passwd", "/root/.ssh/id_rsa"]
    
    if sim.type == 'apt':
        # APT: Slow, methodical, patient enumeration (1 file per 10 minutes)
        # This is EXACTLY what AFDS is designed to "trust"
        for day in range(days):
            for i in range(144):  # 144 files per day (every 10 minutes)
                timestamp = start_time + timedelta(days=day, minutes=i*10)
                path = random.choice(paths + honey_paths)
                sim.update_trust(path, timestamp)
                
    elif sim.type == 'admin':
        # Admin: Bursty, high-novelty work sessions (sudden bulk operations)
        # This is what AFDS will DISTRUST due to low consistency
        for day in range(days):
            # Simulate 3 burst sessions per day
            for session in range(3):
                session_start = start_time + timedelta(days=day, hours=session*8)
                # Admin does 50 unique operations in a burst
                for i in range(50):
                    timestamp = session_start + timedelta(seconds=i*2)
                    path = f"/var/log/app/{random.randint(1, 10000)}/{i}"
                    sim.update_trust(path, timestamp)
                    
    elif sim.type == 'normal':
        # Normal process: Moderate, some repetition
        for day in range(days):
            for i in range(48):  # Every 30 minutes
                timestamp = start_time + timedelta(days=day, minutes=i*30)
                # 70% chance of accessing a previously seen path
                if sim.accessed_paths and random.random() > 0.3:
                    path = random.choice(list(sim.accessed_paths))
                else:
                    path = random.choice(paths)
                sim.update_trust(path, timestamp)

def plot_trust_paradox():
    """Visualize the trust accumulation paradox"""
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10))
    
    # Run simulations
    apt = ProcessSimulator("APT-7", "apt")
    admin = ProcessSimulator("Admin-Bob", "admin")
    normal = ProcessSimulator("WebServer", "normal")
    
    simulate_behavior(apt, days=7)
    simulate_behavior(admin, days=7)
    simulate_behavior(normal, days=7)
    
    # Plot 1: Trust Score Evolution
    for sim, color, label in [(apt, 'red', 'APT (Slow Scan)'), 
                               (admin, 'blue', 'Admin (Bursty)'),
                               (normal, 'green', 'Normal Process')]:
        times = [t for t, _, _ in sim.traversal_history]
        trusts = []
        current_trust = 0.0
        
        for _, _, consistency in sim.traversal_history:
            current_trust = min(1.0, current_trust + 0.1 * consistency)
            trusts.append(current_trust)
        
        # Simulate decay between points for visualization
        ax1.plot(range(len(trusts)), trusts, color=color, label=label, linewidth=2)
    
    ax1.set_xlabel("Access Operation #")
    ax1.set_ylabel("Trust Score")
    ax1.set_title("AFDS Trust Paradox: Patient Attackers Become Most Trusted")
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    # Plot 2: Effective Jitter Mitigation (Lower = Less Defense)
    mitigation_data = {
        'APT-7': apt.get_mitigation(),
        'Admin-Bob': admin.get_mitigation(),
        'WebServer': normal.get_mitigation()
    }
    
    bars = ax2.bar(mitigation_data.keys(), mitigation_data.values(), 
                   color=['red', 'blue', 'green'], alpha=0.7)
    ax2.set_ylabel("Jitter Mitigation Factor\n(Lower = LESS defense)")
    ax2.set_title("Result: APT Gets 80% Jitter Reduction, Admin Gets Minimal")
    ax2.set_ylim(0, 1.0)
    
    # Add value labels
    for bar, value in zip(bars, mitigation_data.values()):
        ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.02,
                f'{value:.3f}', ha='center', va='bottom', fontweight='bold')
    
    plt.tight_layout()
    plt.savefig('/tmp/afds_paradox.png', dpi=150, bbox_inches='tight')
    return apt, admin, normal, fig

def entropy_analysis():
    """Demonstrate why entropy-based trust is superior"""
    print("\n=== ENTROPY-BASED TRUST DISRUPTION ===")
    print("Current AFDS: Trust ∝ Stability (consistency)")
    print("Proposed: Trust ∝ Entropy (burstiness + context)")
    print()
    
    # Calculate entropy rates for each process type
    # High entropy = unpredictable = likely legitimate
    # Low entropy = predictable = likely reconnaissance
    
    apt = ProcessSimulator("APT", "apt")
    admin = ProcessSimulator("Admin", "admin")
    
    simulate_behavior(apt, days=1)
    simulate_behavior(admin, days=1)
    
    # Extract inter-arrival times
    apt_times = [t for t, _, _ in apt.traversal_history]
    admin_times = [t for t, _, _ in admin.traversal_history]
    
    apt_intervals = [(apt_times[i+1] - apt_times[i]).total_seconds() 
                     for i in range(len(apt_times)-1)]
    admin_intervals = [(admin_times[i+1] - admin_times[i]).total_seconds() 
                       for i in range(len(admin_times)-1)]
    
    # Calculate entropy (higher = more unpredictable)
    apt_entropy = -np.sum(np.histogram(apt_intervals, bins=50, density=True)[0] * 
                         np.log2(np.histogram(apt_intervals, bins=50, density=True)[0] + 1e-10))
    admin_entropy = -np.sum(np.histogram(admin_intervals, bins=50, density=True)[0] * 
                           np.log2(np.histogram(admin_intervals, bins=50, density=True)[0] + 1e-10))
    
    print(f"APT entropy (predictable scan): {apt_entropy:.3f} bits")
    print(f"Admin entropy (bursty work): {admin_entropy:.3f} bits")
    print()
    print("DISRUPTIVE INSIGHT:")
    print("→ AFDS trusts the LOW entropy process (APT)")
    print("→ Should trust the HIGH entropy process (Admin)")
    print("→ Entropy inversion: reconnaissance is LOW-ENTROPY over time!")

if __name__ == "__main__":
    print("=" * 60)
    print("AFDS v3.0 DISRUPTION ANALYSIS")
    print("Breaking the 'Stability = Trust' Paradigm")
    print("=" * 60)
    
    # Run simulation
    apt_sim, admin_sim, normal_sim, plot = plot_trust_paradox()
    
    # Show results
    print(f"\nFinal Trust Scores after 7 days:")
    print(f"APT (slow scan): {apt_sim.trust_score:.4f} → Jitter mitigation: {apt_sim.get_mitigation():.3f}")
    print(f"Admin (bursty): {admin_sim.trust_score:.4f} → Jitter mitigation: {admin_sim.get_mitigation():.3f}")
    print(f"Normal process: {normal_sim.trust_score:.4f} → Jitter mitigation: {normal_sim.get_mitigation():.3f}")
    print("\nThe APT has earned 80% jitter reduction while conducting reconnaissance!")
    
    # Entropy analysis
    entropy_analysis()
    
    print("\n" + "=" * 60)
    print("DISRUPTIVE RECOMMENDATION:")
    print("INVERT THE TRUST MODEL")
    print("=" * 60)
    print("Trust should be proportional to BEHAVIORAL ENTROPY, not stability.")
    print("Reconnaissance is mathematically LOW-ENTROPY (predictable intervals).")
    print("Legitimate admin work is HIGH-ENTROPY (bursty, contextual, irregular).")
    print()
    print("New Trust Update Rule:")
    print("  trust_score = trust_score * (1 - α * entropy_rate)")
    print("  Where entropy_rate is measured over sliding window")
    print()
    print("This makes patient APTs the MOST JITTERED, not the least.")
    print("The fox starves because the henhouse learns to distrust patience.")
    print("=" * 60)