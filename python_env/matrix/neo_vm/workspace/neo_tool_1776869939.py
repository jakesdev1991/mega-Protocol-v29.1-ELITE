# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import matplotlib.pyplot as plt

def simulate_bureaucracy(n_nodes=100, timesteps=100, corruption_baseline=0.3, 
                         operator_type='RDI', rdi_window=0.3, fmc_intensity=5.0):
    """Simulates the two operators with corruption as primary variable"""
    policy = np.random.rand(n_nodes)
    execution = np.random.rand(n_nodes)
    corruption = np.random.rand(n_nodes) * corruption_baseline
    corruption += np.sin(np.linspace(0, 4*np.pi, n_nodes)) * 0.2
    
    cod_hist, phi_hist, trust_hist = [], [], []
    
    for t in range(timesteps):
        # Adversarial vectors: corruption warps both
        policy_eff = policy * (1 - corruption * 0.5)
        execution_eff = execution * (1 + corruption * 0.5)
        
        cod = np.dot(policy_eff, execution_eff) / (np.linalg.norm(policy_eff) * 
                                                     np.linalg.norm(execution_eff) + 1e-10)
        cod_hist.append(cod)
        
        trust = np.exp(-np.mean(corruption) * t * 0.1)
        trust_hist.append(trust)
        
        if operator_type == 'RDI':
            # RDI: suspends measurement -> corruption grows unchecked
            impedance = 1.0 - rdi_window * (1 - cod)
            phi_density = cod * trust / (impedance + np.mean(corruption)**2)
            corruption *= (1 + 0.02 * rdi_window)  # corruption metastasizes
            
        elif operator_type == 'FMC':
            # FMC: forced measurement cascade suppresses corruption
            measurement_noise = np.random.rand(n_nodes) * fmc_intensity
            corruption *= (1 - 0.05 * fmc_intensity * (measurement_noise / np.max(measurement_noise)))
            corruption = np.clip(corruption, 0, 1)
            impedance = 1.0 + fmc_intensity * np.mean(corruption)
            phi_density = cod * trust / (impedance + np.mean(corruption)**2)
        
        phi_hist.append(phi_density)
        
        policy += np.random.randn(n_nodes) * 0.01
        execution += np.random.randn(n_nodes) * 0.01
        policy, execution = np.clip(policy, 0, 1), np.clip(execution, 0, 1)
    
    return {'cod': np.array(cod_hist), 'phi': np.array(phi_hist), 
            'trust': np.array(trust_hist), 'final_corr': corruption}

# Execute simulation
np.random.seed(42)
rdi_results = simulate_bureaucracy(operator_type='RDI')
fmc_results = simulate_bureaucracy(operator_type='FMC')

# Reality check: print final Φ-density
print(f"RDI Final Φ-Density: {rdi_results['phi'][-1]:.3f} (Trust: {rdi_results['trust'][-1]:.3f})")
print(f"FMC Final Φ-Density: {fmc_results['phi'][-1]:.3f} (Trust: {fmc_results['trust'][-1]:.3f})")
print(f"FMC improvement over RDI: {((fmc_results['phi'][-1] - rdi_results['phi'][-1]) / rdi_results['phi'][-1] * 100):.1f}%")