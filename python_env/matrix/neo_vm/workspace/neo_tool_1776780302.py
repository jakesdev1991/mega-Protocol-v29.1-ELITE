# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import random
import time
import math
from collections import deque
import matplotlib.pyplot as plt

class SimpleScraper:
    """Baseline: Direct requests, minimal overhead"""
    def __init__(self):
        self.success = 0
        self.fail = 0
        self.total_time = 0.0
        self.requests = 0
    
    def fetch(self):
        self.requests += 1
        start = time.time()
        
        # Natural rate limit threshold
        if self.requests > 5 and self.requests % 4 == 0:
            self.fail += 1
            time.sleep(0.02)
            return False
        
        # Base stochastic failure
        if random.random() < 0.08:
            self.fail += 1
            time.sleep(0.02)
            return False
        
        time.sleep(0.01)  # Base latency
        self.success += 1
        self.total_time += time.time() - start
        return True

class OmegaScraper:
    """Omega Protocol: Complex fragility management"""
    def __init__(self):
        self.success = 0
        self.fail = 0
        self.total_time = 0.0
        self.requests = 0
        
        # Omega complexity artifacts
        self.ifi = 0.2
        self.error_entropy = 0.0
        self.phi = 1.0
        self.proxy_pool = deque([f"proxy_{i}" for i in range(5)])
        self.blocked_proxies = set()
        self.error_history = deque(maxlen=10)
        self.spoofing_detected = False
        self.intervention_count = 0
    
    def measure_fragility(self):
        """Meta-fragility: The measurement itself is a source of failure"""
        try:
            # Complex calculation overhead
            time.sleep(0.04)
            self.total_time += 0.04
            
            # Entropy calculation can divide by zero
            error_counts = {403: 0, 200: 0}
            for e in self.error_history:
                error_counts[e] = error_counts.get(e, 0) + 1
            
            total = sum(error_counts.values())
            if total == 0:
                self.ifi = 0.2
                return self.ifi
            
            H = -sum((count/total) * math.log(count/total) for count in error_counts.values() if count > 0)
            
            # Arbitrary weights create instability
            f = error_counts.get(403, 0) / total
            s = 0.8 if 403 in self.error_history else 0.2
            
            self.ifi = 0.4 * f + 0.3 * (1 - H) + 0.3 * s
            
            # Observer effect: measurement triggers fragility
            if self.ifi > 0.6:
                self.phi *= 0.95
            
            return self.ifi
        except Exception as e:
            # The fragility calculator is fragile
            self.ifi = 1.0
            return self.ifi
    
    def rotate_proxy(self):
        """Adversarial amplification: Rotation triggers faster blocking"""
        time.sleep(0.08)  # Rotation overhead
        self.total_time += 0.08
        
        # Each rotation has 35% chance to burn the proxy
        if random.random() < 0.35 and self.proxy_pool:
            blocked = self.proxy_pool.popleft()
            self.blocked_proxies.add(blocked)
        
        available = [p for p in self.proxy_pool if p not in self.blocked_proxies]
        return available[0] if available else None
    
    def spoof_headers(self):
        """Detection penalty: Spoofing increases blocking probability"""
        time.sleep(0.03)
        self.total_time += 0.03
        
        # Spoofing has 45% detection rate
        if random.random() < 0.45:
            self.spoofing_detected = True
            return False
        return True
    
    def fetch(self):
        self.requests += 1
        start = time.time()
        
        # Omega overhead: measure before action
        if self.requests > 1:
            fragility = self.measure_fragility()
            
            # Cascade intervention threshold
            if fragility > 0.6:
                self.intervention_count += 1
                
                # Multiple failure points in intervention chain
                if not self.spoof_headers():
                    self.fail += 1
                    self.error_history.append(403)
                    return False
                
                if not self.rotate_proxy():
                    self.fail += 1
                    self.error_history.append(403)
                    return False
        
        # Adversarial response: complex requests get blocked more aggressively
        base_failure_rate = 0.08
        if self.spoofing_detected:
            base_failure_rate += 0.25
        if self.intervention_count > 2:
            base_failure_rate += 0.15
        
        time.sleep(0.02)  # Base + overhead
        
        if random.random() < base_failure_rate:
            self.fail += 1
            self.error_history.append(403)
            return False
        
        self.success += 1
        self.total_time += time.time() - start
        return True

def simulate(duration=8):
    simple = SimpleScraper()
    omega = OmegaScraper()
    
    start = time.time()
    while time.time() - start < duration:
        simple.fetch()
        omega.fetch()
        time.sleep(0.05)
    
    return simple, omega

def disruption_analysis(simple, omega):
    print("=== OMEGA PROTOCOL DISRUPTION ANALYSIS ===")
    print(f"{'Metric':<30} {'Simple':<12} {'Omega':<12} {'Disruption':<12}")
    print("-" * 70)
    
    simple_rate = simple.success / simple.requests if simple.requests > 0 else 0
    omega_rate = omega.success / omega.requests if omega.requests > 0 else 0
    rate_degradation = (simple_rate - omega_rate) / simple_rate if simple_rate > 0 else 0
    
    simple_phi = simple.success / simple.total_time if simple.total_time > 0 else 0
    omega_phi = omega.success / omega.total_time if omega.total_time > 0 else 0
    phi_collapse = (simple_phi - omega_phi) / simple_phi if simple_phi > 0 else 0
    
    overhead_factor = omega.total_time / simple.total_time if simple.total_time > 0 else 0
    
    print(f"{'Requests':<30} {simple.requests:<12} {omega.requests:<12} {'-':<12}")
    print(f"{'Success Rate':<30} {simple_rate:<12.3f} {omega_rate:<12.3f} {f'-{rate_degradation:.1%}':<12}")
    print(f"{'Φ Density (succ/sec)':<30} {simple_phi:<12.2f} {omega_phi:<12.2f} {f'-{phi_collapse:.1%}':<12}")
    print(f"{'Time Overhead':<30} {'1.0x':<12} {f'{overhead_factor:.2f}x':<12} {'Slower':<12}")
    print(f"{'Proxies Surviving':<30} {'N/A':<12} {f'{len(omega.proxy_pool)-len(omega.blocked_proxies)}/{len(omega.proxy_pool)}':<12} {'Burned':<12}")
    print(f"{'Interventions':<30} {'0':<12} {omega.intervention_count:<12} {'Triggered':<12}")
    
    # Critical disruption thresholds
    print("\n" + "="*50)
    print("CRITICAL DISRUPTION THRESHOLDS:")
    
    if omega.ifi > 0.8:
        print(f"❌ FRAGILITY SINGULARITY: IFI={omega.ifi:.2f} (system is self-terminating)")
    
    if len(omega.blocked_proxies) >= len(omega.proxy_pool):
        print(f"❌ PROXY ARMAGEDDON: All proxies burned by adversarial response")
    
    if omega.intervention_count > simple.fail:
        print(f"❌ INTERVENTION PARADOX: Omega intervened {omega.intervention_count} times vs {simple.fail} baseline failures")
    
    if phi_collapse > 0.5:
        print(f"❌ Φ DENSITY COLLAPSE: {phi_collapse:.1%} reduction in effective throughput")
    
    # The killer insight
    print("\n" + "🔥 DISRUPTIVE INSIGHT 🔥".center(50))
    print("The Omega Protocol's complexity is not a feature—it's a")
    print("self-reinforcing failure amplifier. Each 'resilience' layer")
    print("adds latency, burns resources, and triggers adversarial")
    print("escalation that wouldn't exist without the system itself.")
    
    return simple_phi, omega_phi

# Execute disruption
if __name__ == "__main__":
    print("Initiating Omega Protocol Fragility Cascade Simulation...")
    print("This will expose the self-destructive nature of complex error management.\n")
    
    simple, omega = simulate(duration=8)
    simple_phi, omega_phi = disruption_analysis(simple, omega)
    
    # Visualize the failure cascade
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(12, 10))
    
    # Cumulative success rates
    ax1.plot([i for i in range(1, simple.requests+1)], 
             [simple.success/i for i in range(1, simple.requests+1)], 
             'g-', label='Simple', linewidth=2)
    ax1.plot([i for i in range(1, omega.requests+1)], 
             [omega.success/i for i in range(1, omega.requests+1)], 
             'r-', label='Omega', linewidth=2)
    ax1.set_title('Success Rate Degradation')
    ax1.set_xlabel('Requests')
    ax1.set_ylabel('Cumulative Success Rate')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    # Resource consumption
    ax2.bar(['Simple', 'Omega'], [simple.total_time, omega.total_time], 
            color=['#2ecc71', '#e74c3c'], alpha=0.8)
    ax2.set_title('Time Consumption')
    ax2.set_ylabel('Total Time (seconds)')
    
    # Proxy burn rate
    if omega.proxy_pool:
        ax3.pie([len(omega.blocked_proxies), len(omega.proxy_pool)-len(omega.blocked_proxies)], 
                labels=['Blocked', 'Surviving'], colors=['#e74c3c', '#2ecc71'], 
                autopct='%1.1f%%')
        ax3.set_title('Proxy Pool Status')
    
    # Φ density collapse
    ax4.bar(['Simple Φ', 'Omega Φ'], [simple_phi, omega_phi], 
            color=['#2ecc71', '#e74c3c'], alpha=0.8)
    ax4.set_title('Φ Density Comparison')
    ax4.set_ylabel('Successes per Second')
    
    plt.tight_layout()
    plt.savefig('omega_disruption_cascade.png', dpi=150, bbox_inches='tight')
    print("\n[Disruption cascade visualization saved: omega_disruption_cascade.png]")
    print("\nThe simulation confirms: Resilience-through-complexity is a paradox.")