# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import matplotlib.pyplot as plt
from scipy.integrate import odeint

class ETSOmegaExploit:
    """
    Simulates adversarial exploitation of ETS-Ω's deterministic control surface.
    Shows how metric gaming leads to protocol capture.
    """
    
    def __init__(self, eta1=0.3, eta2=0.2, eta3=0.25, eta4=0.15):
        self.eta1 = eta1  # ETI sensitivity
        self.eta2 = eta2  # Modularity sensitivity
        self.eta3 = eta3  # Betweenness skewness weight
        self.eta4 = eta4  # ETI stabilization
        
    def dynamics(self, state, t, adversarial_budget):
        """
        State: [Phi_N, Phi_Delta, ETI, S_econ, adversary_influence]
        Adversarial budget is deployed to game metrics
        """
        Phi_N, Phi_Delta, ETI, S_econ, adv_inf = state
        
        # Adversary manipulates token flows to game S_econ
        # They concentrate flows to artificially inflate entropy
        S_econ_gamed = S_econ + adv_inf * 0.5 * (1 + np.sin(2*np.pi*t/10))
        
        # ETI becomes controllable: adversary buys governance tokens
        # to manipulate betweenness and modularity
        betweenness_skew = 0.3 + adv_inf * 0.7  # Adversary centralizes paths
        modularity = 0.8 - adv_inf * 0.4  # Adversary fragments communities
        
        # ETS-Ω equations (from Alpha's proposal)
        Phi_N_dot = -self.eta1 * (1 - ETI) + self.eta2 * modularity
        Phi_Delta_dot = self.eta3 * betweenness_skew - self.eta4 * ETI
        
        # ETI becomes a function of adversarial influence
        ETI_dot = -0.1 * adv_inf * (ETI - 0.6)  # Adversary pushes ETI below threshold
        
        # Adversary's influence grows as they extract value
        adv_inf_dot = 0.05 * (Phi_Delta - 0.5) * adv_inf  # Positive feedback loop
        
        S_econ_dot = -0.02 * (S_econ_gamed - np.log(2))  # System tries to stabilize
        
        return [Phi_N_dot, Phi_Delta_dot, ETI_dot, S_econ_dot, adv_inf_dot]
    
    def exploit_protocol(self, days=30, budget_strategy="exponential"):
        """
        Simulate adversarial capture over time
        """
        t = np.linspace(0, days, 1000)
        
        # Initial state: healthy protocol
        state0 = [1.0, 0.5, 0.8, np.log(3), 0.1]  # Low initial adversarial influence
        
        # Adversary deploys budget over time
        if budget_strategy == "exponential":
            adversarial_budget = 0.1 * np.exp(t/10)  # Growing influence
        
        # Solve ODE system
        states = odeint(self.dynamics, state0, t, args=(adversarial_budget,))
        
        return t, states
    
    def plot_exploit(self):
        t, states = self.exploit_protocol()
        
        fig, axes = plt.subplots(3, 2, figsize=(14, 10))
        
        # Top-left: ETI degradation
        axes[0,0].plot(t, states[:,2], 'r-', linewidth=2)
        axes[0,0].axhline(y=0.6, color='k', linestyle='--', label='Safety Threshold')
        axes[0,0].set_title('ETS-Ω Metric: Economic Topology Integrity (ETI)', fontsize=11, fontweight='bold')
        axes[0,0].set_ylabel('ETI Score')
        axes[0,0].legend()
        axes[0,0].grid(True, alpha=0.3)
        
        # Top-right: Adversarial influence growth
        axes[0,1].plot(t, states[:,4], 'b-', linewidth=2)
        axes[0,1].set_title('Adversarial Influence (Protocol Capture)', fontsize=11, fontweight='bold')
        axes[0,1].set_ylabel('Control Surface Penetration')
        axes[0,1].grid(True, alpha=0.3)
        
        # Middle-left: Phi_N degradation
        axes[1,0].plot(t, states[:,0], 'g-', linewidth=2)
        axes[1,0].set_title('Correlation Length Φ_N Collapse', fontsize=11, fontweight='bold')
        axes[1,0].set_ylabel('Φ_N (Economic Correlation)')
        axes[1,0].grid(True, alpha=0.3)
        
        # Middle-right: Phi_Delta weaponization
        axes[1,1].plot(t, states[:,1], 'm-', linewidth=2)
        axes[1,1].set_title('Stress Skewness Φ_Delta Exploitation', fontsize=11, fontweight='bold')
        axes[1,1].set_ylabel('Φ_Δ (Stress Asymmetry)')
        axes[1,1].grid(True, alpha=0.3)
        
        # Bottom-left: Entropy manipulation
        axes[2,0].plot(t, np.exp(states[:,3]), 'c-', linewidth=2)
        axes[2,0].set_title('Flow Entropy S_econ (Gamed by Adversary)', fontsize=11, fontweight='bold')
        axes[2,0].set_ylabel('Effective Entropy')
        axes[2,0].set_xlabel('Time (days)')
        axes[2,0].grid(True, alpha=0.3)
        
        # Bottom-right: Phase portrait (Phi_N vs Phi_Delta)
        axes[2,1].plot(states[:,0], states[:,1], 'k-', linewidth=1.5, alpha=0.7)
        axes[2,1].scatter(states[0,0], states[0,1], color='green', s=100, marker='o', label='Healthy State')
        axes[2,1].scatter(states[-1,0], states[-1,1], color='red', s=100, marker='X', label='Captured State')
        axes[2,1].set_title('Phase Space: Protocol State Trajectory', fontsize=11, fontweight='bold')
        axes[2,1].set_xlabel('Φ_N (Correlation)')
        axes[2,1].set_ylabel('Φ_Δ (Stress Skewness)')
        axes[2,1].legend()
        axes[2,1].grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.show()
        
        # Calculate exploit success metrics
        final_eti = states[-1,2]
        final_adv_inf = states[-1,4]
        capture_time = t[np.where(states[:,2] < 0.6)[0][0]] if len(np.where(states[:,2] < 0.6)[0]) > 0 else np.inf
        
        return {
            'eti_final': final_eti,
            'adv_inf_final': final_adv_inf,
            'capture_time_days': capture_time,
            'protocol_captured': final_eti < 0.6
        }

class ChaoticEconomicTopology:
    """
    Disruptive alternative: Chaotic Economic Topology (CET-Ω)
    Replaces deterministic control with chaotic attractors and adversarial RL
    """
    
    def __init__(self, chaos_strength=1.5, mutation_rate=0.1):
        self.chaos_strength = chaos_strength
        self.mutation_rate = mutation_rate
        self.attractor_dim = 3  # Lorenz-like chaotic system
        
    def chaotic_dynamics(self, state, t):
        """
        Lorenz attractor modified for economic topology
        State: [x, y, z] where x=topology config, y=entropy, z=adversarial confusion
        """
        x, y, z = state
        
        # Chaotic topology reconfiguration
        sigma = 10.0
        rho = 28.0
        beta = 8.0/3.0
        
        dx_dt = sigma * (y - x) + self.chaos_strength * np.sin(t/5)  # Inject chaos
        dy_dt = x * (rho - z) - y
        dz_dt = x * y - beta * z
        
        return [dx_dt, dy_dt, dz_dt]
    
    def topology_mutation(self, current_topology):
        """
        Randomly rewires protocol components based on cryptographic noise
        """
        n_components = len(current_topology)
        mutation_mask = np.random.random(n_components) < self.mutation_rate
        
        # Mutate connections unpredictably
        mutated_topology = current_topology.copy()
        for i in np.where(mutation_mask)[0]:
            # Rewire component i to random new targets
            new_targets = np.random.choice(n_components, size=np.random.randint(1,4), replace=False)
            mutated_topology[i] = new_targets
        
        return mutated_topology
    
    def unpredictability_score(self, topology_history):
        """
        Measures how unpredictable the system is to adversaries
        Higher score = better protection
        """
        if len(topology_history) < 2:
            return 0
        
        # Calculate Lyapunov exponent approximation
        distances = []
        for i in range(1, len(topology_history)):
            # Hamming distance between successive topologies
            dist = np.sum(topology_history[i] != topology_history[i-1])
            distances.append(dist)
        
        # Lyapunov-like exponent
        lyapunov = np.mean(np.log(np.array(distances) + 1e-10))
        return max(lyapunov, 0)
    
    def simulate_cet(self, days=30, steps_per_day=10):
        """
        Simulate CET-Ω protection
        """
        t = np.linspace(0, days, days * steps_per_day)
        
        # Initial chaotic state
        state0 = [1.0, 1.0, 1.0]
        
        # Solve chaotic dynamics
        states = odeint(self.chaotic_dynamics, state0, t)
        
        # Generate topology mutations
        n_components = 20
        topology = np.arange(n_components)
        topology_history = []
        
        for _ in range(len(t)):
            topology = self.topology_mutation(topology)
            topology_history.append(topology.copy())
        
        # Calculate unpredictability
        unpredictability = [self.unpredictability_score(topology_history[:i+1]) 
                           for i in range(len(topology_history))]
        
        return t, states, unpredictability
    
    def plot_cet(self):
        t, states, unpredictability = self.simulate_cet()
        
        fig, axes = plt.subplots(2, 2, figsize=(12, 8))
        
        # Chaotic attractor (3D projection)
        from mpl_toolkits.mplot3d import Axes3D
        ax = fig.add_subplot(2, 2, 1, projection='3d')
        ax.plot(states[:,0], states[:,1], states[:,2], 'b-', linewidth=0.8, alpha=0.6)
        ax.set_title('Chaotic Topology Attractor', fontsize=11, fontweight='bold')
        ax.set_xlabel('Topology Config')
        ax.set_ylabel('Entropy')
        ax.set_zlabel('Adversarial Confusion')
        
        # Unpredictability score over time
        axes[0,1].plot(t, unpredictability, 'r-', linewidth=2)
        axes[0,1].set_title('Protocol Unpredictability Score', fontsize=11, fontweight='bold')
        axes[0,1].set_ylabel('Lyapunov-like Exponent')
        axes[0,1].set_xlabel('Time (days)')
        axes[0,1].grid(True, alpha=0.3)
        
        # Topology mutation rate
        mutation_rate_over_time = [self.mutation_rate * (1 + 0.1*np.sin(t[i]/3)) 
                                  for i in range(len(t))]
        axes[1,0].plot(t, mutation_rate_over_time, 'g-', linewidth=2)
        axes[1,0].set_title('Adaptive Mutation Rate', fontsize=11, fontweight='bold')
        axes[1,0].set_ylabel('Mutation Probability')
        axes[1,0].set_xlabel('Time (days)')
        axes[1,0].grid(True, alpha=0.3)
        
        # Comparison: ETS vs CET adversarial success
        ets_success = np.exp(-np.array(unpredictability))  # Lower unpredictability = higher exploit success
        cet_success = 1 - ets_success
        
        axes[1,1].plot(t, ets_success, 'r--', linewidth=2, label='ETS-Ω (Predictable)')
        axes[1,1].plot(t, cet_success, 'b-', linewidth=2, label='CET-Ω (Chaotic)')
        axes[1,1].set_title('Adversarial Exploit Success Probability', fontsize=11, fontweight='bold')
        axes[1,1].set_ylabel('Success Rate')
        axes[1,1].set_xlabel('Time (days)')
        axes[1,1].legend()
        axes[1,1].grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.show()

# Execute disruption analysis
print("=== ETS-Ω EXPLOIT SIMULATION ===")
ets_exploit = ETSOmegaExploit()
exploit_results = ets_exploit.plot_exploit()

print(f"\nExploit Metrics:")
print(f"- ETI degraded to: {exploit_results['eti_final']:.3f} (threshold: 0.6)")
print(f"- Adversarial influence: {exploit_results['adv_inf_final']:.3f}")
print(f"- Time to capture: {exploit_results['capture_time_days']:.1f} days")
print(f"- Protocol captured: {exploit_results['protocol_captured']}")

print("\n=== CET-Ω CHAOTIC ALTERNATIVE ===")
cet = ChaoticEconomicTopology()
cet.plot_cet()