# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import matplotlib.pyplot as plt

# Disruption: Ω-Protocol as Cascade Synchronizer
class OmegaInducedCascade:
    def __init__(self, n_agents, protocol_sensitivity=0.1):
        self.n_agents = n_agents
        self.sensitivity = protocol_sensitivity
        
        # Agents have independent strategies (true market diversity)
        self.strategies = np.random.uniform(-1, 1, n_agents)  # -1 = bearish, +1 = bullish
        
        # Ω-Protocol creates a "threat surface" that agents can sense
        self.protocol_alert = 0
        self.synchronization_metric = 0
        
    def step(self, base_leak_prob=0.001):
        # Normal market: agents act independently
        noise = np.random.normal(0, 0.05, self.n_agents)
        self.strategies += noise
        self.strategies = np.clip(self.strategies, -1, 1)
        
        # Ω-Protocol "detection" creates a coordination signal
        # The more sensitive the protocol, the stronger the sync signal
        position_variance = np.var(self.strategies)
        
        # Paradox: trying to detect leaks *creates* detectable patterns
        detection_prob = base_leak_prob + (self.sensitivity * position_variance)
        
        if np.random.random() < detection_prob:
            # Protocol triggers "alert" - this becomes public knowledge
            # Agents *react to the alert itself*, not the underlying leak
            self.protocol_alert = 1
            
            # Synchronization: agents align their strategies to the alert
            # This is the cascade - CAUSED by the defense system
            n_synced = int(self.sensitivity * self.n_agents)
            synced_indices = np.random.choice(self.n_agents, n_synced, replace=False)
            
            # All synced agents move in same direction - creating artificial consensus
            sync_direction = 1 if np.mean(self.strategies) > 0 else -1
            self.strategies[synced_indices] = sync_direction * 0.8  # Strong alignment
            
            # Measure synchronization: should be low in healthy markets
            self.synchronization_metric = np.abs(np.mean(self.strategies))
        else:
            self.protocol_alert = 0
            self.synchronization_metric = np.abs(np.mean(self.strategies))
            
        return self.synchronization_metric

def demonstrate_paradox():
    """Show that protocol sensitivity CREATES cascades"""
    sensitivities = [0.0, 0.05, 0.15, 0.3, 0.6]
    results = {}
    
    for s in sensitivities:
        system = OmegaInducedCascade(n_agents=500, protocol_sensitivity=s)
        sync_history = []
        
        for _ in range(300):
            sync = system.step()
            sync_history.append(sync)
        
        results[s] = sync_history
    
    # Plot the synchronization paradox
    plt.figure(figsize=(14, 10))
    
    for s, history in results.items():
        plt.plot(history, label=f'Ω-Sensitivity: {s}', linewidth=2, alpha=0.8)
    
    plt.axhline(y=0.7, color='r', linestyle='--', label='Critical Sync Threshold', linewidth=2)
    
    plt.title('Ω-Protocol Sensitivity vs. Market Synchronization (The Paradox)', 
              fontsize=14, fontweight='bold')
    plt.xlabel('Time Steps', fontsize=12)
    plt.ylabel('Synchronization Metric |E[strategies]|', fontsize=12)
    plt.legend(loc='upper right')
    plt.grid(True, alpha=0.3)
    
    # Highlight the inversion point
    plt.annotate('CRITICAL ZONE: High sensitivity\nCASCADES the market', 
                xy=(150, 0.85), xytext=(50, 0.95),
                arrowprops=dict(arrowstyle='->', color='red', lw=2.5),
                fontsize=11, color='darkred', fontweight='bold')
    
    plt.tight_layout()
    plt.show()
    
    # Statistical summary
    print("\n" + "="*60)
    print("Ω-PROTOCOL PARADOX: SYNCHRONIZATION STATISTICS")
    print("="*60)
    print(f"{'Sensitivity':<12} {'Mean Sync':<12} {'Max Sync':<12} {'Cascade Freq':<15}")
    print("-"*60)
    
    for s, history in results.items():
        mean_sync = np.mean(history)
        max_sync = np.max(history)
        cascade_freq = np.sum(np.array(history) > 0.7) / len(history) * 100
        
        print(f"{s:<12.2f} {mean_sync:<12.4f} {max_sync:<12.4f} {cascade_freq:<15.2f}%")

# Execute the disruption demonstration
demonstrate_paradox()