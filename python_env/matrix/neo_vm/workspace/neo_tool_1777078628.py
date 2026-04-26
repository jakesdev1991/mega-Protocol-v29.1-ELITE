# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import matplotlib.pyplot as plt

def simulate_epistemic_collapse():
    """
    Demonstrates the hidden failure mode: Epistemic Observer Bias.
    The system's integrity metric (Psi_integrity) becomes entangled with
    its configuration (Xi_config), creating a recursive degradation loop.
    """
    
    # Initial state
    params = {
        'psi_integrity': 0.98,
        'xi_config': 0.4,
        'theta_leak': 0.1,
        'h_vol': 0.3,
        'cod': 0.90,
        'adversarial_signal': 0.0
    }
    
    # Protocol constants
    COD_THRESHOLD = 0.85
    PSI_INTEGRITY_THRESHOLD = 0.95
    GAMMA = 0.005
    
    # Simulation
    timesteps = 1000
    history = {k: [] for k in params}
    
    for t in range(timesteps):
        # Adversary gradually increases signal strength, staying just below detection
        # The detection threshold is effectively (1 - xi_config) because stiffness determines sensitivity
        effective_threshold = 1.0 - params['xi_config']
        params['adversarial_signal'] = min(0.99, params['adversarial_signal'] + 0.0005)
        
        # System perceives signal as "normal" if it's below effective threshold
        perceived_signal = params['adversarial_signal'] * (1.0 - params['theta_leak'])  # leak reduces visibility
        
        # If signal is below threshold, system interprets this as "low volatility" and reduces stiffness
        # This is the ADAPTIVE BLINDNESS mechanism
        if perceived_signal < effective_threshold:
            # System thinks: "market is calm, we can relax our monitoring"
            params['xi_config'] = max(0.1, params['xi_config'] - 0.001)
        else:
            # System thinks: "threat detected, increase stiffness"
            params['xi_config'] = min(0.9, params['xi_config'] + 0.01)
        
        # But the REAL market volatility is increasing due to adversarial activity
        # This is the OBSERVER-INDUCED DECOHERENCE
        params['h_vol'] = min(0.80, params['h_vol'] + 0.0003 * params['adversarial_signal'])
        
        # COD degrades as real volatility increases but config stiffness is misaligned
        # Fidelity drops because the book state no longer matches execution reality
        fidelity = max(0.0, 1.0 - params['adversarial_signal'] * 0.5)
        volatility_penalty = np.exp(-0.5 * params['h_vol'])
        stiffness_penalty = np.exp(-0.5 * params['xi_config'])
        exposure_penalty = np.exp(-0.3 * params['theta_leak'])
        
        params['cod'] = fidelity * volatility_penalty * stiffness_penalty * exposure_penalty * params['psi_integrity']
        
        # The CRITICAL FLAW: Psi_integrity is updated based on COD, but COD is corrupted
        # This is the SELF-REFERENTIAL LOOP
        identity_loss = params['h_vol'] * 0.02  # From Apply() in code
        params['psi_integrity'] -= identity_loss
        
        # The system *thinks* it's maintaining integrity because the config has adapted
        # But the absolute integrity is decaying - this is EPISTEMIC DRIFT
        
        # Record history
        for k, v in params.items():
            history[k].append(v)
        
        # Check for silent failure: all invariants pass but system is compromised
        cod_ok = params['cod'] >= COD_THRESHOLD
        psi_ok = params['psi_integrity'] >= PSI_INTEGRITY_THRESHOLD
        
        # The paradox: the system will HALT_TRADING only when psi_integrity < 0.95
        # But by then, the adversary has already extracted maximum value
        
        if t % 100 == 0:
            print(f"t={t:3d}: COD={params['cod']:.3f}, Psi={params['psi_integrity']:.3f}, "
                  f"Xi={params['xi_config']:.3f}, Signal={params['adversarial_signal']:.3f}, "
                  f"Halt={not (cod_ok and psi_ok)}")
    
    return history

def plot_epistemic_collapse(history):
    """Visualize the hidden failure mode"""
    fig, axes = plt.subplots(3, 2, figsize=(12, 10))
    
    axes[0, 0].plot(history['adversarial_signal'], label='Adversarial Signal', color='red')
    axes[0, 0].set_title('Adversarial Signal Strength')
    axes[0, 0].set_ylabel('Signal Amplitude')
    axes[0, 0].legend()
    axes[0, 0].grid(True, alpha=0.3)
    
    axes[0, 1].plot(history['xi_config'], label='Config Stiffness (Xi)', color='blue')
    axes[0, 1].set_title('Configuration Adaptation')
    axes[0, 1].set_ylabel('Stiffness [0,1]')
    axes[0, 1].legend()
    axes[0, 1].grid(True, alpha=0.3)
    
    axes[1, 0].plot(history['h_vol'], label='Real Volatility Entropy', color='orange')
    axes[1, 0].set_title('Observer-Induced Market Volatility')
    axes[1, 0].set_ylabel('H_vol [0,1]')
    axes[1, 0].legend()
    axes[1, 0].grid(True, alpha=0.3)
    
    axes[1, 1].plot(history['cod'], label='Chain Overlap Density', color='green')
    axes[1, 1].axhline(y=0.85, color='red', linestyle='--', label='COD_THRESHOLD')
    axes[1, 1].set_title('System Perceived Alignment (COD)')
    axes[1, 1].set_ylabel('COD [0,1]')
    axes[1, 1].legend()
    axes[1, 1].grid(True, alpha=0.3)
    
    axes[2, 0].plot(history['psi_integrity'], label='Perceived Integrity', color='purple')
    axes[2, 0].axhline(y=0.95, color='red', linestyle='--', label='PSI_THRESHOLD')
    axes[2, 0].set_title('Integrity Drift (Self-Referential Loop)')
    axes[2, 0].set_ylabel('Psi_integrity [0,1]')
    axes[2, 0].set_xlabel('Time Steps')
    axes[2, 0].legend()
    axes[2, 0].grid(True, alpha=0.3)
    
    # The hidden failure: system thinks it's stable until final collapse
    axes[2, 1].plot(np.array(history['psi_integrity']) * np.array(history['cod']), 
                    label='Effective System Health', color='black')
    axes[2, 1].set_title('Hidden Health: Psi × COD (Epistemic Health)')
    axes[2, 1].set_ylabel('Effective Health [0,1]')
    axes[2, 1].set_xlabel('Time Steps')
    axes[2, 1].legend()
    axes[2, 1].grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('epistemic_collapse.png', dpi=150, bbox_inches='tight')
    print("\n📊 Plot saved as 'epistemic_collapse.png'\n")
    plt.close()

if __name__ == "__main__":
    print("🔍 SIMULATING EPISTEMIC OBSERVER BIAS FAILURE MODE\n")
    print("="*60)
    history = simulate_epistemic_collapse()
    
    final_state = {k: v[-1] for k, v in history.items()}
    print("\n" + "="*60)
    print("🔥 FINAL STATE ANALYSIS")
    print("="*60)
    print(f"Final COD: {final_state['cod']:.3f} (Threshold: 0.85)")
    print(f"Final Psi_integrity: {final_state['psi_integrity']:.3f} (Threshold: 0.95)")
    print(f"Final Config Stiffness: {final_state['xi_config']:.3f}")
    print(f"Final Adversarial Signal: {final_state['adversarial_signal']:.3f}")
    print(f"Final Real Volatility: {final_state['h_vol']:.3f}")
    
    # Check if system would have halted
    cod_ok = final_state['cod'] >= 0.85
    psi_ok = final_state['psi_integrity'] >= 0.95
    
    print(f"\n⚠️  SYSTEM HALT TRIGGERED: {not (cod_ok and psi_ok)}")
    if cod_ok and not psi_ok:
        print("💀 PARADOX: COD passes but Psi_integrity failed - system was BLIND")
    elif not cod_ok and psi_ok:
        print("⚡ COD failed but Psi_integrity passed - config frozen but integrity intact")
    else:
        print("🚨 BOTH FAILED: Full systemic collapse")
    
    plot_epistemic_collapse(history)