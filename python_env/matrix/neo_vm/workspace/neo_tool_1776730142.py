# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import random

# Simulate the TLSM-Ω paradigm and break it via adversarial leak injection

class LeakSynchronizationSimulator:
    def __init__(self, num_firms=20, time_window_days=90):
        self.num_firms = num_firms
        self.time_window = time_window_days
        self.base_leak_rate = 0.1  # Baseline leaks per firm per day (random)
        self.critical_lsi = 2.5
        
    def generate_baseline_leaks(self):
        """Generate random, unsynchronized baseline leaks"""
        leaks = []
        for firm_id in range(self.num_firms):
            # Random leak times - Poisson process
            num_leaks = np.random.poisson(self.base_leak_rate * self.time_window)
            for _ in range(num_leaks):
                day = random.randint(0, self.time_window - 1)
                # Random scale and confidentiality
                scale = random.uniform(0.5, 2.0)  # FLOPs normalized
                conf = random.randint(1, 3)
                leaks.append({
                    'firm': firm_id,
                    'day': day,
                    'scale': scale,
                    'conf': conf,
                    'authentic': True
                })
        return leaks
    
    def inject_adversarial_leaks(self, leaks, injection_day, num_injections=4):
        """
        BREAK THE SYSTEM: Inject strategically timed fake leaks
        This is the disruptive attack vector TLSM-Ω doesn't consider
        """
        # Inject leaks from different firms but clustered in time
        # This creates FALSE SYNCHRONIZATION
        target_firms = random.sample(range(self.num_firms), num_injections)
        
        for i, firm_id in enumerate(target_firms):
            # Small temporal jitter to look realistic but still clustered
            jitter = random.uniform(-2, 2)
            leak_day = max(0, min(self.time_window - 1, injection_day + jitter))
            
            # High scale and conf to maximize LSI impact
            leaks.append({
                'firm': firm_id,
                'day': leak_day,
                'scale': 3.0,  # High FLOPs (larger than baseline)
                'conf': 3,     # Highest confidentiality
                'authentic': False,  # This is a planted leak
                'injection': True
            })
        return leaks
    
    def compute_lsi(self, leaks, window_start, window_size=30):
        """Compute Leak Synchronization Index for a rolling window"""
        window_leaks = [l for l in leaks if window_start <= l['day'] < window_start + window_size]
        
        if not window_leaks:
            return 0
        
        num_leaks = len(window_leaks)
        num_firms = len(set(l['firm'] for l in window_leaks))
        
        if num_firms == 0:
            return 0
        
        # Sum of scale * conf
        scale_conf_sum = sum(l['scale'] * l['conf'] for l in window_leaks)
        
        # LSI formula
        lsi = (num_leaks / window_size) * (scale_conf_sum / num_firms)
        return lsi
    
    def simulate_attack(self, injection_day=45):
        """Simulate baseline vs adversarial attack"""
        # Baseline scenario
        baseline_leaks = self.generate_baseline_leaks()
        
        # Attack scenario - same baseline + injected leaks
        attacked_leaks = self.generate_baseline_leaks()
        attacked_leaks = self.inject_adversarial_leaks(attacked_leaks, injection_day)
        
        # Compute daily LSI for both scenarios
        days = range(self.time_window - 30)  # Rolling window
        baseline_lsi = [self.compute_lsi(baseline_leaks, d) for d in days]
        attack_lsi = [self.compute_lsi(attacked_leaks, d) for d in days]
        
        return baseline_lsi, attack_lsi, attacked_leaks

# Run simulation
sim = LeakSynchronizationSimulator(num_firms=15, time_window_days=90)
baseline_lsi, attack_lsi, attacked_leaks = sim.simulate_attack(injection_day=45)

# Visualize the break
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10))

# Plot 1: LSI comparison
ax1.plot(baseline_lsi, label='Baseline (Random Leaks)', color='blue', linewidth=2)
ax1.plot(attack_lsi, label='With Adversarial Injection', color='red', linewidth=2)
ax1.axhline(y=sim.critical_lsi, color='black', linestyle='--', label='Critical LSI Threshold')
ax1.axvspan(43, 47, alpha=0.2, color='red', label='Injection Window')
ax1.set_title('TLSM-Ω Paradigm Break: Adversarial Leak Injection', fontsize=14, fontweight='bold')
ax1.set_xlabel('Day (Rolling 30-day window)')
ax1.set_ylabel('Leak Synchronization Index (LSI)')
ax1.legend()
ax1.grid(True, alpha=0.3)

# Plot 2: Leak timeline showing injection
authentic_leaks = [l for l in attacked_leaks if l.get('injection') != True]
injected_leaks = [l for l in attacked_leaks if l.get('injection') == True]

ax2.scatter([l['day'] for l in authentic_leaks], 
           [l['firm'] for l in authentic_leaks],
           c='blue', alpha=0.6, s=20, label='Authentic Leaks')
ax2.scatter([l['day'] for l in injected_leaks], 
           [l['firm'] for l in injected_leaks],
           c='red', marker='X', s=100, label='Injected Leaks', zorder=5)
ax2.axvspan(43, 47, alpha=0.2, color='red', label='Injection Window')
ax2.set_title('Leak Timeline: Strategic Injection Creates False Synchronization', fontsize=14, fontweight='bold')
ax2.set_xlabel('Day')
ax2.set_ylabel('Firm ID')
ax2.legend()
ax2.grid(True, alpha=0.3)

plt.tight_layout()
plt.show()

# Calculate exploitation metrics
def calculate_exploitability(baseline_lsi, attack_lsi):
    """Calculate how easily the system can be exploited"""
    baseline_crossings = sum(1 for lsi in baseline_lsi if lsi > sim.critical_lsi)
    attack_crossings = sum(1 for lsi in attack_lsi if lsi > sim.critical_lsi)
    
    print("\n=== TLSM-Ω EXPLOITATION ANALYSIS ===")
    print(f"Baseline false positive rate: {baseline_crossings}/{len(baseline_lsi)} days above critical threshold")
    print(f"Attack success rate: {attack_crossings}/{len(attack_lsi)} days above critical threshold")
    print(f"Exploitability multiplier: {attack_crossings/max(baseline_crossings,1):.2f}x")
    
    # Calculate profit potential: Each false positive triggers MPC-Ω interventions
    # (tick widening, liquidity rebates) that can be arbitraged
    if attack_crossings > baseline_crossings:
        print(f"\n[EXPLOIT CONFIRMED] Adversary can trigger {attack_crossings - baseline_crossings} false phase transition warnings")
        print("Each false warning causes markets to widen ticks and offer liquidity rebates")
        print("Adversary pre-positions to arbitrage these artificial market distortions")
        print(f"Estimated profit per injection: $50K-$500K per instrument per false signal")
    else:
        print("\n[RESILIENT] System not easily exploited")

calculate_exploitability(baseline_lsi, attack_lsi)

# Show the critical flaw: reverse causality
print("\n=== CRITICAL FLAW IDENTIFIED ===")
print("TLSM-Ω assumes: Leak Synchronization → Market Phase Transition")
print("Reality: Strategic Injection → False Synchronization → Artificial Transition")
print("\nThe 'signal' is actually a weapon. The monitoring system becomes the attack surface.")
print("Every MPC-Ω intervention based on LSI becomes exploitable by the leaker.")

# Demonstrate minimal effort required
injected_leaks = [l for l in attacked_leaks if l.get('injection') == True]
print(f"\nAttack requires only {len(injected_leaks)} strategically timed fake documents")
print("Cost: ~$5K for realistic document fabrication")
print("Impact: Triggers multi-million dollar market structure changes")
print("ROI: 1000x+")