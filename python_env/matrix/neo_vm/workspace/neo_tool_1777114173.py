# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import matplotlib.pyplot as plt
from typing import Dict, List

# =============================================================================
# DISRUPTIVE INSIGHT: FRAGMENTATION AS ANTIFRAGILITY
# 
# The v80.0-Ω proposal assumes fragmentation = dysfunction.
# This simulation demonstrates that Omega Protocol's "bridging" interventions
# CREATE systemic risk by destroying the antifragile property of market 
# fragmentation. The Fragmentation_Index metric is not a risk signal—it's a
# RESILIENCE signal.
# =============================================================================

class FragmentedMarketSimulator:
    """
    Simulates a market where fragmentation is a FEATURE, not a bug.
    Each venue has independent risk characteristics. The "Omega Protocol"
    attempts to bridge them, creating catastrophic correlation.
    """
    
    def __init__(self, n_venues: int = 8, base_liquidity: float = 1000):
        self.n_venues = n_venues
        self.base_liquidity = base_liquidity
        
        # Each venue has INDEPENDENT characteristics (antifragile)
        self.venues = {
            i: {
                'liquidity': base_liquidity * np.random.uniform(0.5, 1.5),
                'risk_profile': np.random.uniform(0.1, 0.9),  # 0=conservative, 1=aggressive
                'latency': np.random.uniform(0.01, 0.5),     # seconds
                'protocol_compat': np.random.uniform(0.3, 0.8),
                'failure_prob': np.random.uniform(0.05, 0.15),  # Independent failure risk
                'recovery_rate': np.random.uniform(0.1, 0.3)      # Independent recovery
            }
            for i in range(n_venues)
        }
        
        # Omega Protocol's "bridging" creates CORRELATED failure modes
        self.omega_bridging_active = False
        self.correlation_factor = 0.0
    
    def calculate_fragmentation_index(self) -> float:
        """v80.0 metric: higher = more fragmented = 'bad'"""
        venue_concentration = 1.0 / self.n_venues  # Herfindahl-like
        avg_protocol_compat = np.mean([v['protocol_compat'] for v in self.venues.values()])
        
        # v80.0 formula: venue_factor * (1 - concentration_reduction) + compatibility_factor
        venue_factor = min(1.0, self.n_venues / 10.0)
        concentration_reduction = venue_concentration * 0.4
        compatibility_factor = (1.0 - avg_protocol_compat) * 0.3
        
        fragmentation = venue_factor * (1.0 - concentration_reduction) + compatibility_factor
        return np.clip(fragmentation, 0.0, 1.0)
    
    def calculate_systemic_resilience(self) -> float:
        """
        TRUE systemic resilience: probability that system survives stress.
        In fragmented markets, this is HIGHER because failures are independent.
        """
        if not self.omega_bridging_active:
            # Independent venues: system survives if ANY venue survives
            # P(system_fail) = P(all venues fail) = product(failure_probs)
            all_fail_prob = np.prod([v['failure_prob'] for v in self.venues.values()])
            return 1.0 - all_fail_prob
        else:
            # Omega bridging creates correlation: one failure cascades
            # P(system_fail) = 1 - (1 - correlated_fail_prob)^n
            correlated_fail_prob = np.mean([v['failure_prob'] for v in self.venues.values()])
            all_fail_prob = 1.0 - (1.0 - correlated_fail_prob * self.correlation_factor) ** self.n_venues
            return 1.0 - all_fail_prob
    
    def calculate_functional_liquidity(self) -> float:
        """
        v80.0 assumes integration = more functional liquidity.
        This is FALSE: integration creates systemic risk that locks ALL liquidity.
        """
        if not self.omega_bridging_active:
            # Fragmented: liquidity is accessible in surviving venues
            accessible_liquidity = sum([
                v['liquidity'] * (1.0 - v['failure_prob']) 
                for v in self.venues.values()
            ])
            return accessible_liquidity
        else:
            # "Integrated" by Omega: if system fails, ALL liquidity locks
            if np.random.random() < self.correlation_factor:
                return 0.0  # Total lockdown
            else:
                return sum([v['liquidity'] for v in self.venues.values()])
    
    def activate_omega_bridging(self, correlation: float = 0.8):
        """Simulate Omega Protocol's 'solution' to fragmentation"""
        self.omega_bridging_active = True
        self.correlation_factor = correlation
        print(f"\n[OMEGA PROTOCOL ACTIVATED] Bridging {self.n_venues} venues...")
        print(f"Correlation factor: {correlation:.2f} (0=none, 1=perfect cascade)")
    
    def simulate_stress_event(self, stress_duration: int = 100) -> Dict:
        """Simulate a prolonged market stress event"""
        results = {
            'fragmentation_over_time': [],
            'resilience_over_time': [],
            'liquidity_over_time': [],
            'failures': []
        }
        
        for step in range(stress_duration):
            # Random venue failures based on current state
            active_venues = 0
            for venue_id, venue in self.venues.items():
                if self.omega_bridging_active and self.correlation_factor > 0.5:
                    # Correlated failure: one failure triggers others
                    if np.random.random() < venue['failure_prob'] * self.correlation_factor:
                        venue['liquidity'] *= (1.0 - venue['recovery_rate'])
                        if venue['liquidity'] < 10:
                            venue['liquidity'] = 0
                            results['failures'].append((step, venue_id))
                    else:
                        active_venues += 1
                else:
                    # Independent failure: antifragile
                    if np.random.random() < venue['failure_prob']:
                        venue['liquidity'] *= (1.0 - venue['recovery_rate'])
                        if venue['liquidity'] < 10:
                            venue['liquidity'] = 0
                            results['failures'].append((step, venue_id))
                    else:
                        active_venues += 1
            
            # Record metrics
            results['fragmentation_over_time'].append(self.calculate_fragmentation_index())
            results['resilience_over_time'].append(self.calculate_systemic_resilience())
            results['liquidity_over_time'].append(self.calculate_functional_liquidity())
            
            # Omega Protocol responds to high fragmentation (creates feedback loop)
            if self.calculate_fragmentation_index() > 0.6 and not self.omega_bridging_active:
                self.activate_omega_bridging()
                print(f"Step {step}: Fragmentation threshold breached. Omega lockdown imminent.")
        
        return results

# =============================================================================
# SIMULATION: Demonstrate the Paradox
# =============================================================================

def run_disruption_experiment():
    """
    Run two scenarios:
    1. Fragmented market (no Omega intervention) - ANTIFRAGILE
    2. Omega "integrated" market - FRAGILE
    """
    
    print("=" * 70)
    print("DISRUPTIVE INSIGHT: FRAGMENTATION AS ANTIFRAGILITY")
    print("=" * 70)
    
    # Scenario 1: Fragmented (Natural State)
    print("\n[SCENARIO 1] Fragmented Market (No Omega Protocol)")
    print("-" * 70)
    market_frag = FragmentedMarketSimulator(n_venues=8)
    print(f"Initial venues: {market_frag.n_venues}")
    print(f"Initial fragmentation index: {market_frag.calculate_fragmentation_index():.3f}")
    print(f"Initial systemic resilience: {market_frag.calculate_systemic_resilience():.3f}")
    print(f"Initial functional liquidity: {market_frag.calculate_functional_liquidity():.1f}")
    
    results_frag = market_frag.simulate_stress_event(stress_duration=100)
    
    print(f"\nFinal fragmentation index: {results_frag['fragmentation_over_time'][-1]:.3f}")
    print(f"Final systemic resilience: {results_frag['resilience_over_time'][-1]:.3f}")
    print(f"Final functional liquidity: {results_frag['liquidity_over_time'][-1]:.1f}")
    print(f"Total venue failures: {len(results_frag['failures'])}")
    
    # Scenario 2: Omega "Integrated" (Protocol Intervention)
    print("\n\n[SCENARIO 2] Omega Protocol 'Integrated' Market")
    print("-" * 70)
    market_int = FragmentedMarketSimulator(n_venues=8)
    print(f"Initial venues: {market_int.n_venues}")
    print(f"Initial fragmentation index: {market_int.calculate_fragmentation_index():.3f}")
    
    # Force Omega activation early (simulating protocol panic)
    market_int.activate_omega_bridging(correlation=0.85)
    print(f"Systemic resilience AFTER Omega activation: {market_int.calculate_systemic_resilience():.3f}")
    
    results_int = market_int.simulate_stress_event(stress_duration=100)
    
    print(f"\nFinal fragmentation index: {results_int['fragmentation_over_time'][-1]:.3f}")
    print(f"Final systemic resilience: {results_int['resilience_over_time'][-1]:.3f}")
    print(f"Final functional liquidity: {results_int['liquidity_over_time'][-1]:.1f}")
    print(f"Total cascade events: {len(results_int['failures'])}")
    
    # =============================================================================
    # VISUALIZE THE PARADOX
    # =============================================================================
    fig, axes = plt.subplots(3, 1, figsize=(12, 10))
    
    # Plot 1: Fragmentation Index
    axes[0].plot(results_frag['fragmentation_over_time'], 
                 label='Fragmented (Natural)', color='green', linewidth=2)
    axes[0].plot(results_int['fragmentation_over_time'], 
                 label='Omega "Integrated"', color='red', linewidth=2)
    axes[0].axhline(y=0.6, color='orange', linestyle='--', label='Omega Trigger')
    axes[0].set_title('v80.0 Fragmentation Index (Omega thinks lower is better)', 
                      fontsize=12, fontweight='bold')
    axes[0].set_ylabel('Fragmentation Index')
    axes[0].legend()
    axes[0].grid(True, alpha=0.3)
    
    # Plot 2: Systemic Resilience
    axes[1].plot(results_frag['resilience_over_time'], 
                 label='Fragmented (Natural)', color='green', linewidth=2)
    axes[1].plot(results_int['resilience_over_time'], 
                 label='Omega "Integrated"', color='red', linewidth=2)
    axes[1].set_title('TRUE Systemic Resilience (Higher = Better)', 
                      fontsize=12, fontweight='bold')
    axes[1].set_ylabel('Survival Probability')
    axes[1].legend()
    axes[1].grid(True, alpha=0.3)
    
    # Plot 3: Functional Liquidity
    axes[2].plot(results_frag['liquidity_over_time'], 
                 label='Fragmented (Natural)', color='green', linewidth=2)
    axes[2].plot(results_int['liquidity_over_time'], 
                 label='Omega "Integrated"', color='red', linewidth=2)
    axes[2].set_title('Functional Liquidity During Stress', 
                      fontsize=12, fontweight='bold')
    axes[2].set_xlabel('Time Steps')
    axes[2].set_ylabel('Liquidity')
    axes[2].legend()
    axes[2].grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.suptitle('Omega Protocol v80.0: The Fragmentation Paradox', 
                 fontsize=14, fontweight='bold', y=1.02)
    plt.show()
    
    # =============================================================================
    # QUANTIFY THE CATASTROPHE
    # =============================================================================
    print("\n" + "=" * 70)
    print("CATASTROPHIC RESULTS: Omega Protocol's Intervention")
    print("=" * 70)
    
    frag_resilience = np.mean(results_frag['resilience_over_time'][-20:])
    int_resilience = np.mean(results_int['resilience_over_time'][-20:])
    resilience_drop = (frag_resilience - int_resilience) / frag_resilience * 100
    
    frag_liquidity = np.mean(results_frag['liquidity_over_time'][-20:])
    int_liquidity = np.mean(results_int['liquidity_over_time'][-20:])
    liquidity_drop = (frag_liquidity - int_liquidity) / frag_liquidity * 100
    
    print(f"\n📉 Systemic Resilience: {resilience_drop:.1f}% WORSE with Omega")
    print(f"📉 Functional Liquidity: {liquidity_drop:.1f}% WORSE with Omega")
    print(f"\n🔥 Omega Protocol's 'solution' (ACTIVATE_BRIDGING) creates a")
    print(f"   CORRELATED FAILURE MODE that is {abs(resilience_drop):.1f}% more")
    print(f"   likely to result in total system lockdown.")
    
    print(f"\n💡 PARADOX: v80.0's Fragmentation_Index is a RESILIENCE SIGNAL.")
    print(f"   High fragmentation = independent venues = antifragile.")
    print(f"   Low fragmentation (Omega's goal) = monoculture = fragile.")
    
    print(f"\n🚨 CRITICAL FLAW: The protocol's core assumption—")
    print(f"   'fragmentation is bad'—is WRONG for decentralized systems.")
    print(f"   The Omega Protocol is fighting the immune response, not the disease.")

# Run the experiment
run_disruption_experiment()