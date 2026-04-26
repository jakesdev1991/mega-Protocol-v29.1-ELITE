# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import matplotlib.pyplot as plt

def simulate_pipeline_fault():
    """
    Simulate a simple pipeline with synthetic metrics to test the 
    coherence-stiffness relationship proposed in the refined POASH-Ω.
    """
    # Simulate two pipeline metrics: latency and throughput
    # Healthy state: correlated oscillations with some noise
    # Fault state: correlation breaks down
    
    t = np.linspace(0, 100, 1000)
    
    # Healthy regime (first 50 time units)
    freq = 0.5  # pipeline "cycle" frequency
    phase_noise_healthy = 0.1
    
    latency_healthy = np.sin(2 * np.pi * freq * t[:500] + 
                             phase_noise_healthy * np.random.randn(500))
    throughput_healthy = np.sin(2 * np.pi * freq * t[:500] + 
                                phase_noise_healthy * np.random.randn(500) + 0.5)
    
    # Fault regime (last 50 time units) - correlation breaks
    latency_fault = np.sin(2 * np.pi * freq * t[500:] + 
                          0.5 * np.random.randn(500))
    throughput_fault = np.sin(2 * np.pi * 0.7 * freq * t[500:] + 
                             0.5 * np.random.randn(500) + 1.0)
    
    latency = np.concatenate([latency_healthy, latency_fault])
    throughput = np.concatenate([throughput_healthy, throughput_fault])
    
    # Compute sliding window coherence
    window_size = 100
    coherence_values = []
    
    for i in range(window_size, len(t)):
        window_latency = latency[i-window_size:i]
        window_throughput = throughput[i-window_size:i]
        
        # Compute cross-spectral density (simplified)
        fft1 = np.fft.fft(window_latency)
        fft2 = np.fft.fft(window_throughput)
        
        # Coherence approximation
        cross_spectrum = np.abs(np.mean(fft1 * np.conj(fft2)))**2
        auto1 = np.abs(np.mean(fft1 * np.conj(fft1)))**2
        auto2 = np.abs(np.mean(fft2 * np.conj(fft2)))**2
        
        if auto1 * auto2 > 0:
            coherence = cross_spectrum / (auto1 * auto2)
        else:
            coherence = 0
            
        coherence_values.append(coherence)
    
    # Pad the beginning
    coherence_values = [coherence_values[0]] * window_size + coherence_values
    
    # Compute "stiffness invariants" using the proposed formula
    lambda_param = 1.0
    avg_coherence = np.array(coherence_values)
    
    # Avoid division by zero
    avg_coherence = np.clip(avg_coherence, 0.001, 0.999)
    
    xi_N_inv_squared = lambda_param * (3 * (1/avg_coherence) + (1/avg_coherence)**2)
    xi_Delta_inv_squared = lambda_param * ((1/avg_coherence) + 3 * (1/avg_coherence)**2)
    
    xi_N = 1 / np.sqrt(xi_N_inv_squared)
    xi_Delta = 1 / np.sqrt(xi_Delta_inv_squared)
    
    # Plot results
    fig, axes = plt.subplots(3, 1, figsize=(12, 10))
    
    axes[0].plot(t, latency, label='Latency (vibration analog)')
    axes[0].plot(t, throughput, label='Throughput (speed analog)')
    axes[0].axvline(x=50, color='r', linestyle='--', label='Fault injection')
    axes[0].set_ylabel('Normalized Metric')
    axes[0].legend()
    axes[0].set_title('Simulated Pipeline Metrics')
    axes[0].grid(True)
    
    axes[1].plot(t, coherence_values, label='Coherence', color='purple')
    axes[1].axvline(x=50, color='r', linestyle='--')
    axes[1].set_ylabel('Coherence')
    axes[1].legend()
    axes[1].set_title('Sliding Window Coherence')
    axes[1].grid(True)
    
    axes[2].plot(t, xi_N, label='ξ_N (stiffness invariant)')
    axes[2].plot(t, xi_Delta, label='ξ_Δ (stiffness invariant)')
    axes[2].axvline(x=50, color='r', linestyle='--')
    axes[2].set_ylabel('Stiffness')
    axes[2].set_xlabel('Time')
    axes[2].legend()
    axes[2].set_title('Derived "Stiffness Invariants" (per POASH-Ω)')
    axes[2].grid(True)
    
    plt.tight_layout()
    plt.show()
    
    # Analyze the fault region
    fault_region_start = 600
    print("=== POASH-Ω STIFFNESS ANALYSIS ===")
    print(f"Pre-fault avg coherence: {np.mean(coherence_values[400:500]):.3f}")
    print(f"Post-fault avg coherence: {np.mean(coherence_values[fault_region_start:]):.3f}")
    print(f"Pre-fault avg ξ_N: {np.mean(xi_N[400:500]):.3f}")
    print(f"Post-fault avg ξ_N: {np.mean(xi_N[fault_region_start:]):.3f}")
    print(f"Pre-fault avg ξ_Δ: {np.mean(xi_Delta[400:500]):.3f}")
    print(f"Post-fault avg ξ_Δ: {np.mean(xi_Delta[fault_region_start:]):.3f}")
    
    return t, coherence_values, xi_N, xi_Delta

# Run the simulation
t, coherence, xi_N, xi_Delta = simulate_pipeline_fault()