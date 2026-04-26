# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import matplotlib.pyplot as plt

def simulate_metrological_capture():
    """
    Demonstrates how config exposure enables measurement corruption
    that bypasses existing COD checks but is caught by H_metrology.
    """
    # Simulation parameters
    time_steps = 200
    base_liquidity = 0.7
    adversary_entry = 50
    
    # State vectors
    theta_leak = np.zeros(time_steps)
    xi_config = np.zeros(time_steps)
    cod_nominal = np.zeros(time_steps)
    cod_effective = np.zeros(time_steps)
    psi_integrity = np.zeros(time_steps)
    h_metrology = np.zeros(time_steps)
    
    # Initialize
    theta_leak[0] = 0.1  # Initially secure
    xi_config[0] = 0.3
    psi_integrity[0] = 0.98
    cod_nominal[0] = 0.90
    
    # Coupling constants
    MU = 2.0  # Metrological penalty strength
    Z_AUDIT_BASE = 0.5  # Baseline audit density
    
    for t in range(1, time_steps):
        # Phase 1: Normal market (t < 50)
        if t < adversary_entry:
            theta_leak[t] = theta_leak[t-1] * 0.95  # Gradual improvement
            xi_config[t] = xi_config[t-1] * 0.98
            # Genuine fidelity
            cod_nominal[t] = 0.90 + 0.05 * np.sin(t * 0.1)
            
        # Phase 2: Adversarial manipulation (t >= 50)
        else:
            # Config files discovered (Theta_leak spikes)
            theta_leak[t] = min(0.7, theta_leak[t-1] + 0.02)
            
            # Adversary crafts orders to maintain HIGH FIDELITY
            # while gaming thresholds: spoofing near alert boundaries
            xi_config[t] = xi_config[t-1] * 1.01  # Config stiffness rises
            
            # Nominal COD stays high (system is fooled)
            cod_nominal[t] = 0.88 + 0.03 * np.random.random()
            
            # But true market liquidity is draining
            base_liquidity *= 0.99
        
        # Calculate metrological entropy
        # Higher leak + stiffer config = more measurement corruption
        # Lower audit density amplifies uncertainty
        audit_density = Z_AUDIT_BASE * (1 - theta_leak[t])  # Audit decreases as exposure increases
        h_metrology[t] = (theta_leak[t] * xi_config[t]) / max(audit_density, 0.01)
        
        # Effective COD with metrological penalty
        cod_effective[t] = cod_nominal[t] * np.exp(-MU * h_metrology[t])
        
        # Integrity erodes slowly (hidden leverage)
        if t > adversary_entry:
            psi_integrity[t] = psi_integrity[t-1] - 0.001 * theta_leak[t]
        else:
            psi_integrity[t] = psi_integrity[t-1]
    
    # Plot results
    fig, axes = plt.subplots(2, 2, figsize=(12, 10))
    
    # Plot 1: The Deception
    axes[0,0].plot(cod_nominal, label='Nominal COD (system sees)', color='green', linewidth=2)
    axes[0,0].plot(cod_effective, label='Effective COD (true state)', color='red', linestyle='--', linewidth=2)
    axes[0,0].axhline(y=0.85, color='black', linestyle=':', label='Silence Protocol Threshold')
    axes[0,0].axvline(x=adversary_entry, color='gray', linestyle=':', label='Adversary Entry')
    axes[0,0].set_title('Measurement Corruption: Nominal vs Effective COD', fontsize=12, fontweight='bold')
    axes[0,0].set_ylabel('COD [0,1]')
    axes[0,0].legend()
    axes[0,0].grid(True, alpha=0.3)
    
    # Plot 2: Metrological Entropy
    axes[0,1].plot(h_metrology, color='purple', linewidth=2)
    axes[0,1].axvline(x=adversary_entry, color='gray', linestyle=':')
    axes[0,1].set_title('Metrological Entropy (Measurement Uncertainty)', fontsize=12, fontweight='bold')
    axes[0,1].set_ylabel('H_metrology [0,1]')
    axes[0,1].grid(True, alpha=0.3)
    
    # Plot 3: Config Exposure
    axes[1,0].plot(theta_leak, color='orange', linewidth=2, label='Theta_leak (config exposure)')
    axes[1,0].plot(xi_config, color='blue', linewidth=2, label='Xi_config (stiffness)')
    axes[1,0].axvline(x=adversary_entry, color='gray', linestyle=':')
    axes[1,0].set_title('Adversarial Gaming: Exposure & Stiffness', fontsize=12, fontweight='bold')
    axes[1,0].set_ylabel('Metric Value [0,1]')
    axes[1,0].legend()
    axes[1,0].grid(True, alpha=0.3)
    
    # Plot 4: Integrity Erosion
    axes[1,1].plot(psi_integrity, color='darkred', linewidth=2)
    axes[1,1].axhline(y=0.95, color='black', linestyle=':', label='Critical Integrity Threshold')
    axes[1,1].axvline(x=adversary_entry, color='gray', linestyle=':')
    axes[1,1].set_title('Silent Integrity Erosion (Hidden Leverage)', fontsize=12, fontweight='bold')
    axes[1,1].set_ylabel('Psi_integrity [0,1]')
    axes[1,1].legend()
    axes[1,1].grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.suptitle('DISRUPTIVE ANALYSIS: Metrological Capture Attack Simulation', 
                 fontsize=14, fontweight='bold', y=1.02)
    plt.show()
    
    # Print critical insight
    print("\n" + "="*60)
    print("CRITICAL INSIGHT: Measurement Corruption Paradox")
    print("="*60)
    print(f"At t={adversary_entry}: Theta_leak = {theta_leak[adversary_entry]:.2f}")
    print(f"System COD (nominal) stays high: {np.mean(cod_nominal[adversary_entry:]):.3f}")
    print(f"Effective COD (with metrological penalty): {np.mean(cod_effective[adversary_entry:]):.3f}")
    print(f"Silence Protocol would trigger: {np.mean(cod_effective[adversary_entry:] < 0.85) * 100:.1f}% of time")
    print(f"Integrity erosion (hidden): {psi_integrity[-1] - psi_integrity[adversary_entry]:.3f}")
    print("="*60)
    print("CONCLUSION: Without H_metrology, the system trades confidently")
    print("on corrupted measurements, accumulating hidden risk until sudden collapse.")

if __name__ == "__main__":
    simulate_metrological_capture()