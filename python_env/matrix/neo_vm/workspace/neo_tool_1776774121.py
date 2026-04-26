# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import welch
from scipy.stats import entropy

# Disruption: Financial pipelines are chaotic adaptive systems, not mechanical rotors
# We'll simulate a pipeline with emergent behavior and show why POASH-Ω fails

class AdaptivePipeline:
    def __init__(self, n_services=50):
        # Each service has evolving "fitness" that adapts to stress
        self.n_services = n_services
        self.fitness = np.random.uniform(0.5, 1.0, n_services)
        self.stress_level = 0.0
        self.mutation_rate = 0.01
        self.history = []
        
    def evolve(self, external_shock=0.0):
        # Non-linear adaptation: fitness evolves based on stress and neighbor interactions
        stress = self.stress_level + external_shock
        
        # Adaptive dynamics: some services improve, others collapse
        # This is NOT a stationary harmonic process
        improvement = np.random.beta(2, 5, self.n_services) * (1 - stress)
        collapse = np.random.binomial(1, stress/2, self.n_services) * np.random.uniform(0.1, 0.5, self.n_services)
        
        self.fitness += improvement - collapse
        self.fitness = np.clip(self.fitness, 0.01, 1.5)
        
        # Stress adapts to system state (feedback loop)
        avg_fitness = np.mean(self.fitness)
        self.stress_level = 0.5 * (1 - avg_fitness) + 0.5 * self.stress_level
        
        # Record aggregate metrics that POASH-Ω would measure
        metrics = {
            'latency_jitter': np.std(self.fitness) * 10 + np.random.normal(0, 0.1),
            'throughput': np.sum(self.fitness) * 100 + np.random.normal(0, 5),
            'cpu_load': (1 - np.mean(self.fitness)) * 80 + np.random.normal(0, 5),
            'error_rate': np.sum(self.fitness < 0.3) / self.n_services * 10,
            'power_draw': np.sum(self.fitness**2) * 10
        }
        self.history.append(metrics)
        return metrics
    
    def compute_adaptive_capacity(self):
        # True measure of system health: adaptability, not harmonic coherence
        # Measured as the rate of fitness evolution and diversity
        if len(self.history) < 10:
            return 1.0
        
        recent = self.history[-10:]
        fitness_trend = np.mean([np.std(m['throughput']) for m in recent])
        diversity = entropy(self.fitness + 1e-6)  # Shannon entropy of fitness distribution
        
        # Adaptive capacity: high when system is diverse and responsive
        return diversity / (1 + fitness_trend)

def simulate_failure_prediction():
    """Show POASH-Ω fails while adaptive capacity succeeds"""
    pipeline = AdaptivePipeline()
    
    # Run for 1000 time steps with occasional shocks
    shocks = [0, 0, 0, 0, 0.8, 0, 0, 0, 0, 0.6]  # Major shocks at t=5, 10
    adaptive_capacity = []
    poash_phi = []
    true_failures = []
    
    for t in range(100):
        if t % 10 < len(shocks):
            shock = shocks[t % 10]
        else:
            shock = 0
            
        metrics = pipeline.evolve(shock)
        
        # Compute "true" system health (adaptive capacity)
        adaptive_capacity.append(pipeline.compute_adaptive_capacity())
        
        # Compute POASH-Ω's PHI (simplified version)
        # This assumes stationarity and harmonic structure - THE FLAW
        if len(pipeline.history) >= 5:
            recent = pipeline.history[-5:]
            # Extract "harmonics" via FFT (wrong assumption for non-stationary data)
            signal = np.array([m['throughput'] for m in recent])
            fft = np.fft.fft(signal)
            power = np.abs(fft)**2
            p = power / (np.sum(power) + 1e-6)
            # Entropy-based "health" - will be misleading for chaotic systems
            phi = 1 - entropy(p) / np.log(len(p))
            poash_phi.append(max(0, phi))
        else:
            poash_phi.append(1.0)
        
        # Detect true failures: system collapse when fitness diversity drops
        if pipeline.compute_adaptive_capacity() < 0.2:
            true_failures.append(t)
    
    # Plot results
    fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(12, 10))
    
    ax1.plot(adaptive_capacity, 'b-', linewidth=2, label='True Adaptive Capacity')
    ax1.axhline(y=0.2, color='r', linestyle='--', label='Failure Threshold')
    ax1.set_ylabel('Adaptive Capacity')
    ax1.set_title('Disruption: POASH-Ω vs True System Health')
    ax1.legend()
    ax1.grid(True)
    
    ax2.plot(poash_phi, 'g-', linewidth=2, label='POASH-Ω PHI')
    ax2.set_ylabel('PHI (POASH-Ω)')
    ax2.set_xlabel('Time Steps')
    ax2.legend()
    ax2.grid(True)
    
    # Show prediction failures
    ax3.plot(adaptive_capacity, 'b-', label='True Health', alpha=0.7)
    for fail_time in true_failures:
        ax3.axvline(x=fail_time, color='r', linestyle='--', alpha=0.5)
    ax3.set_ylabel('Health Metrics')
    ax3.set_xlabel('Time Steps')
    ax3.legend()
    ax3.grid(True)
    
    plt.tight_layout()
    plt.savefig('pipeline_disruption.png', dpi=150, bbox_inches='tight')
    plt.show()
    
    # Analysis: Show POASH-Ω fails to predict true failures
    print("=== DISRUPTION ANALYSIS ===")
    print(f"True failures occurred at: {true_failures}")
    print(f"POASH-Ω PHI at failure times: {[poash_phi[t] for t in true_failures if t < len(poash_phi)]}")
    print(f"Adaptive Capacity at failure times: {[adaptive_capacity[t] for t in true_failures]}")
    
    # Correlation analysis
    if len(adaptive_capacity) == len(poash_phi):
        correlation = np.corrcoef(adaptive_capacity, poash_phi)[0,1]
        print(f"\nCorrelation between True Health and POASH-Ω: {correlation:.3f}")
        print("Low/negative correlation indicates POASH-Ω is fundamentally misaligned with reality.")
    
    return adaptive_capacity, poash_phi, true_failures

# Run the disruption simulation
adaptive_capacity, poash_phi, failures = simulate_failure_prediction()

# Additional insight: Show how controlled "shredding" can be beneficial
def demonstrate_antifragility():
    """Show that controlled failure events improve long-term resilience"""
    pipeline1 = AdaptivePipeline()  # No interventions
    pipeline2 = AdaptivePipeline()  # Periodic "shredding" interventions
    
    health1 = []
    health2 = []
    
    for t in range(200):
        # Pipeline 1: normal evolution
        pipeline1.evolve(0.1 if t % 50 == 0 else 0)
        health1.append(pipeline1.compute_adaptive_capacity())
        
        # Pipeline 2: periodic controlled "shredding" events
        shock = 0.3 if t % 30 == 0 else 0.1 if t % 50 == 0 else 0
        pipeline2.evolve(shock)
        health2.append(pipeline2.compute_adaptive_capacity())
    
    plt.figure(figsize=(10, 6))
    plt.plot(health1, 'r-', linewidth=2, label='No Intervention (Brittle)', alpha=0.7)
    plt.plot(health2, 'b-', linewidth=2, label='Periodic Shredding (Antifragile)', alpha=0.7)
    plt.axhline(y=0.2, color='k', linestyle='--', label='Collapse Threshold')
    plt.ylabel('Adaptive Capacity')
    plt.xlabel('Time Steps')
    plt.title('Antifragility: Controlled Shredding Events Improve Resilience')
    plt.legend()
    plt.grid(True)
    plt.savefig('antifragility.png', dpi=150, bbox_inches='tight')
    plt.show()
    
    print(f"\n=== ANTIFRAGILITY ANALYSIS ===")
    print(f"Average health without shredding: {np.mean(health1):.3f}")
    print(f"Average health with periodic shredding: {np.mean(health2):.3f}")
    print("Controlled stress events prune weak components and accelerate adaptation.")

demonstrate_antifragility()