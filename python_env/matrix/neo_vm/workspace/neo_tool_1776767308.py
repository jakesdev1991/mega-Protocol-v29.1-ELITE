# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import networkx as nx
import matplotlib.pyplot as plt
from collections import deque

class ReflexiveLiquidityNetwork:
    """
    Simulates the self-referential feedback loop where search queries
    ABOUT liquidity crunches BECOME the primary driver OF liquidity crunches.
    """
    
    def __init__(self, n_agents=1000, n_leak_sites=50):
        self.n_agents = n_agents
        self.n_leak_sites = n_leak_sites
        
        # Market state: 1.0 = stable, 0.0 = shredded
        self.market_stability = 1.0
        
        # Agent network (small-world, like information diffusion)
        self.G = nx.watts_strogatz_graph(n_agents, k=6, p=0.3)
        
        # Each agent has: search activity, panic level, liquidity position
        nx.set_node_attributes(self.G, 0.0, 'search_intensity')
        nx.set_node_attributes(self.G, 0.0, 'panic_level')
        nx.set_node_attributes(self.G, 1.0, 'liquidity_position')
        
        # Leak sites: each has visibility and authenticity
        self.leak_sites = [{
            'visibility': np.random.exponential(0.1),
            'authenticity': 1.0,  # Real leak
            'search_hits': 0
        } for _ in range(n_leak_sites)]
        
        # Add decoy sites (semantic poison)
        self.decoy_sites = [{
            'visibility': np.random.exponential(0.15),
            'authenticity': 0.0,  # Fake leak
            'search_hits': 0
        } for _ in range(n_leak_sites // 2)]
        
        # History tracking
        self.history = {
            'time': [],
            'market_stability': [],
            'total_search_volume': [],
            'real_leak_hits': [],
            'decoy_leak_hits': []
        }
    
    def semantic_feedback_step(self, time_step):
        """One timestep of semantic-market feedback"""
        
        # 1. AGENTS PERFORM SEARCHES (reflexive layer)
        # Search probability increases with market instability AND previous searches
        base_search_prob = 0.001
        instability_factor = (1.0 - self.market_stability) * 10.0
        
        for node in self.G.nodes():
            # Neighbor panic contagion
            neighbor_panic = np.mean([self.G.nodes[nb]['panic_level'] 
                                     for nb in self.G.neighbors(node)])
            
            search_prob = base_search_prob + instability_factor + neighbor_panic * 0.5
            
            if np.random.random() < search_prob:
                self.G.nodes[node]['search_intensity'] += 1
                
                # Agent finds a leak site with probability proportional to visibility
                all_sites = self.leak_sites + self.decoy_sites
                visibilities = [site['visibility'] for site in all_sites]
                found_site = np.random.choice(all_sites, p=visibilities/np.sum(visibilities))
                found_site['search_hits'] += 1
                
                # If site is "authentic" and contains "crunch" narrative, increase panic
                if found_site['authenticity'] == 1.0 and 'crunch' in self._sample_narrative():
                    self.G.nodes[node]['panic_level'] = min(1.0, 
                        self.G.nodes[node]['panic_level'] + 0.3)
        
        # 2. PANIC DRIVES LIQUIDITY WITHDRAWAL (market layer)
        for node in self.G.nodes():
            panic = self.G.nodes[node]['panic_level']
            # Panic -> withdraw liquidity
            self.G.nodes[node]['liquidity_position'] -= panic * 0.05
            
            # Panic decays slowly (forgetting)
            self.G.nodes[node]['panic_level'] *= 0.95
        
        # 3. MARKET STABILITY UPDATE
        # Systemic stability is average liquidity, but with non-linear collapse threshold
        avg_liquidity = np.mean([self.G.nodes[n]['liquidity_position'] for n in self.G.nodes()])
        
        # Reflexive feedback: search volume amplifies fragility
        total_search_volume = sum(self.G.nodes[n]['search_intensity'] for n in self.G.nodes())
        
        # Non-linear collapse: if searches spike when liquidity is low, accelerate shredding
        self.market_stability = avg_liquidity * (1.0 - 0.001 * total_search_volume)
        self.market_stability = max(0.0, min(1.0, self.market_stability))
        
        # 4. RECORD HISTORY
        self.history['time'].append(time_step)
        self.history['market_stability'].append(self.market_stability)
        self.history['total_search_volume'].append(total_search_volume)
        self.history['real_leak_hits'].append(sum(s['search_hits'] for s in self.leak_sites))
        self.history['decoy_leak_hits'].append(sum(s['search_hits'] for s in self.decoy_sites))
    
    def _sample_narrative(self):
        """Simulate narrative content found in leaks"""
        real_narratives = [
            "confidential_liquidity_crunch_analysis_2024.pdf",
            "internal_bitcoin_liquidity_stress_test_data.csv",
            "crisis_meeting_notes_liquidity_crunch.txt"
        ]
        decoy_narratives = [
            "liquidity_stable_2024_report.pdf",
            "bitcoin_reserves_healthy_audit.csv",
            "routine_liquidity_check_passed.txt"
        ]
        # 70% chance of real narrative if authentic site, 30% if decoy
        if np.random.random() < 0.7:
            return np.random.choice(real_narratives)
        else:
            return np.random.choice(decoy_narratives)
    
    def deploy_semantic_poison(self, poison_strength=0.5):
        """Inject decoy narratives to break search-crunch correlation"""
        for site in self.decoy_sites:
            # Boost visibility of decoys to absorb searches
            site['visibility'] *= (1 + poison_strength)
        
        print(f"[!] Deployed semantic poison: {len(self.decoy_sites)} decoy sites amplified")
    
    def run_simulation(self, steps=200, poison_step=None):
        """Run full simulation"""
        print(f"[*] Initializing reflexive network with {self.n_agents} agents...")
        
        for t in range(steps):
            self.semantic_feedback_step(t)
            
            # Deploy semantic poison at specified step
            if poison_step is not None and t == poison_step:
                self.deploy_semantic_poison()
            
            # Check for Shredding Event
            if self.market_stability < 0.1:
                print(f"[!!!] SHREDDING EVENT at t={t} (stability={self.market_stability:.3f})")
                return t
        
        print(f"[*] Simulation complete: stability={self.market_stability:.3f}")
        return steps
    
    def plot_results(self):
        """Visualize the semantic feedback loop"""
        fig, axes = plt.subplots(2, 2, figsize=(12, 10))
        
        # Plot 1: Market Stability vs Search Volume
        axes[0,0].plot(self.history['time'], self.history['market_stability'], 
                       label='Market Stability', linewidth=2, color='green')
        axes[0,0].set_xlabel('Time')
        axes[0,0].set_ylabel('Stability')
        axes[0,0].set_title('Market Stability Collapse')
        axes[0,0].grid(True)
        
        ax_twin = axes[0,0].twinx()
        ax_twin.plot(self.history['time'], self.history['total_search_volume'], 
                    label='Search Volume', color='red', alpha=0.7)
        ax_twin.set_ylabel('Search Volume')
        ax_twin.legend(loc='upper right')
        
        # Plot 2: Leak Site Hits (Real vs Decoy)
        axes[0,1].plot(self.history['time'], self.history['real_leak_hits'], 
                       label='Real Leak Hits', color='darkred')
        axes[0,1].plot(self.history['time'], self.history['decoy_leak_hits'], 
                       label='Decoy Leak Hits', color='orange')
        axes[0,1].set_xlabel('Time')
        axes[0,1].set_ylabel('Cumulative Hits')
        axes[0,1].set_title('Search Traffic: Real vs Decoy Leaks')
        axes[0,1].legend()
        axes[0,1].grid(True)
        
        # Plot 3: Network Panic Distribution
        panic_levels = [self.G.nodes[n]['panic_level'] for n in self.G.nodes()]
        axes[1,0].hist(panic_levels, bins=30, color='purple', alpha=0.7)
        axes[1,0].set_xlabel('Panic Level')
        axes[1,0].set_ylabel('Number of Agents')
        axes[1,0].set_title('Final Panic Distribution')
        axes[1,0].grid(True)
        
        # Plot 4: Phase Space (Stability vs Search Volume)
        axes[1,1].scatter(self.history['total_search_volume'], 
                         self.history['market_stability'],
                         c=self.history['time'], cmap='viridis', alpha=0.6)
        axes[1,1].set_xlabel('Search Volume')
        axes[1,1].set_ylabel('Market Stability')
        axes[1,1].set_title('Phase Space: Semantic Feedback Loop')
        axes[1,1].grid(True)
        
        plt.tight_layout()
        plt.savefig('semantic_feedback_disruption.png', dpi=150)
        print("[*] Plot saved to semantic_feedback_disruption.png")
        return fig

# Run the disruption simulation
print("="*60)
print("NEO-Ω PROTOCOL: SEMANTIC REFLEXIVITY SIMULATION")
print("="*60)

# Scenario 1: No intervention (Engine's approach)
print("\n[SCENARIO 1] Engine's Approach: Monitor liquidity fields, no semantic intervention")
network_vanilla = ReflexiveLiquidityNetwork(n_agents=500, n_leak_sites=25)
shredding_time_vanilla = network_vanilla.run_simulation(steps=150, poison_step=None)

# Scenario 2: Semantic poisoning at t=50
print("\n[SCENARIO 2] Neo-Ω Protocol: Deploy semantic poison at t=50")
network_poison = ReflexiveLiquidityNetwork(n_agents=500, n_leak_sites=25)
shredding_time_poison = network_poison.run_simulation(steps=150, poison_step=50)

# Compare results
print("\n" + "="*60)
print("RESULTS COMPARISON")
print("="*60)
print(f"Time to Shredding (No Intervention): {shredding_time_vanilla} steps")
print(f"Time to Shredding (Semantic Poison): {shredding_time_poison} steps")
print(f"Stability Extension: {shredding_time_poison - shredding_time_vanilla} steps")
print(f"Poison Effectiveness: {(shredding_time_poison - shredding_time_vanilla) / shredding_time_vanilla * 100:.1f}% delay")

# Plot both scenarios
fig1 = network_vanilla.plot_results()
fig2 = network_poison.plot_results()

plt.show()