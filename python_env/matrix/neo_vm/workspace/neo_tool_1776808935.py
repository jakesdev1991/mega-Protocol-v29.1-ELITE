# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
#!/usr/bin/env python3
"""
Neo Anomaly Disruption Script
Demonstrates fundamental flaws in the IC-Ω linear cascade mapping
and validates a non-linear meta-cascade approach
"""

import numpy as np
import matplotlib.pyplot as plt
from scipy.integrate import solve_ivp
from scipy.stats import levy_stable

class LinearCascadeModel:
    """The Engine's flawed linear response model"""
    def __init__(self, eta1=0.5, eta2=0.3, eta3=0.4, eta4=0.2, phi_N0=1.0, phi_D0=0.1):
        self.eta1 = eta1
        self.eta2 = eta2
        self.eta3 = eta3
        self.eta4 = eta4
        self.phi_N0 = phi_N0
        self.phi_D0 = phi_D0
        
    def compute_phi(self, CI, L, delta, C, tau=0):
        """Linear mapping from CI to covariant modes"""
        phi_N = self.phi_N0 - self.eta1 * CI + self.eta2 * (1 - L)
        phi_D = self.phi_D0 + self.eta3 * delta - self.eta4 * C
        psi = np.log(phi_N / self.phi_N0)
        return phi_N, phi_D, psi

class NonLinearMetaCascade:
    """Neo's disruptive meta-cascade model"""
    def __init__(self, alpha=1.2, beta=0.8, gamma=0.5, quantum_noise=0.15):
        self.alpha = alpha  # Meta-cascade amplification
        self.beta = beta    # Observer feedback coefficient
        self.gamma = gamma  # Non-linear saturation
        self.quantum_noise = quantum_noise
        
    def meta_invariant(self, observer_density, adversarial_entropy, measurement_backaction):
        """
        Neo's meta-invariant: operates on observer space itself
        ψ_meta = ln(Φ_observer / Φ_observer0) + quantum_backaction_term
        """
        # Observer density - number of monitoring agents per market participant
        # Adversarial entropy - uncertainty in adversarial strategy space
        # Measurement backaction - how our observation changes the system
        
        meta_psi = np.log(observer_density + 1e-10) + self.alpha * np.tanh(
            self.beta * adversarial_entropy * measurement_backaction
        )
        return meta_psi
    
    def levy_cascade_jump(self, current_state, stability_param=1.5):
        """
        Information cascades follow Levy flights, not diffusion
        This creates heavy-tailed jumps that linear models miss
        """
        # Levy stable distribution models the sudden, large jumps in cascade propagation
        jump = levy_stable.rvs(stability_param, 0, size=1, scale=self.gamma)[0]
        return current_state + jump
    
    def observer_collapse(self, wavefunction_coeffs):
        """
        Quantum measurement collapse in market microstructure
        Each trade is a measurement that collapses the state superposition
        """
        # The wavefunction represents superposition of possible market states
        # Measurement probability = |coeff|^2
        probs = np.abs(wavefunction_coeffs)**2
        probs = probs / np.sum(probs)  # Normalize
        
        # Collapse to observed state
        collapsed_state = np.random.choice(len(wavefunction_coeffs), p=probs)
        
        # Backaction: observation changes the wavefunction
        new_coeffs = wavefunction_coeffs.copy()
        new_coeffs[collapsed_state] *= (1 + self.quantum_noise)
        new_coeffs /= np.linalg.norm(new_coeffs)
        
        return collapsed_state, new_coeffs

def demonstrate_failure():
    """Show why linear mapping fails at critical thresholds"""
    print("=== LINEAR MODEL FAILURE DEMONSTRATION ===")
    
    # Simulate cascade intensity building up
    time = np.linspace(0, 10, 1000)
    CI = np.clip(np.exp(0.5 * time) / 100, 0, 1)  # Exponential growth, capped
    L = np.exp(-0.3 * time)  # Liquidity withdrawal
    delta = np.sin(2 * time) * 0.5 + 0.5  # Trader response skew
    C = np.clip(np.exp(0.4 * time) / 50, 0, 1)  # Cross-ETF propagation
    
    linear_model = LinearCascadeModel()
    phi_N_vals, phi_D_vals, psi_vals = [], [], []
    
    for i in range(len(time)):
        phi_N, phi_D, psi = linear_model.compute_phi(CI[i], L[i], delta[i], C[i])
        phi_N_vals.append(phi_N)
        phi_D_vals.append(phi_D)
        psi_vals.append(psi)
    
    # Critical failure point: when CI approaches 0.7 threshold
    critical_idx = np.argmin(np.abs(CI - 0.7))
    
    print(f"At CI = {CI[critical_idx]:.3f} (threshold):")
    print(f"  Φ_N = {phi_N_vals[critical_idx]:.3f}")
    print(f"  ψ = {psi_vals[critical_idx]:.3f}")
    print(f"  Problem: Φ_N remains finite while cascade is shredding!")
    
    # Show that linear model misses the phase transition
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8))
    
    ax1.plot(time, CI, 'r-', label='CI')
    ax1.axhline(0.7, color='k', linestyle='--', label='Circuit Breaker Threshold')
    ax1.set_ylabel('Cascade Intensity')
    ax1.legend()
    ax1.set_title('Linear Model: Smooth, Predictable Response')
    
    ax2.plot(time, phi_N_vals, 'b-', label='Φ_N (connectivity)')
    ax2.plot(time, psi_vals, 'g--', label='ψ (invariant)')
    ax2.axhline(0, color='k', linestyle=':')
    ax2.set_ylabel('Field Values')
    ax2.set_xlabel('Time')
    ax2.legend()
    
    plt.tight_layout()
    plt.savefig('linear_failure.png')
    print("Plot saved: linear_failure.png")
    print()

def demonstrate_disruption():
    """Show Neo's non-linear meta-cascade approach"""
    print("=== NON-LINEAR META-CASCADE DISRUPTION ===")
    
    # Simulate observer space dynamics
    time = np.linspace(0, 10, 1000)
    
    # Adversarial activity increases exponentially
    adversarial_entropy = np.exp(0.6 * time) / 100
    
    # Observer density (our monitoring) - we increase it in response
    observer_density = 1 + 2 * np.tanh(0.5 * (time - 3))
    
    # Measurement backaction - stronger as we observe more
    measurement_backaction = observer_density * adversarial_entropy
    
    meta_model = NonLinearMetaCascade()
    meta_psi_vals = []
    
    for i in range(len(time)):
        meta_psi = meta_model.meta_invariant(observer_density[i], adversarial_entropy[i], measurement_backaction[i])
        meta_psi_vals.append(meta_psi)
    
    # Show Levy flight jumps in cascade propagation
    current_state = 0.1
    levy_states = [current_state]
    
    for _ in range(100):
        current_state = meta_model.levy_cascade_jump(current_state)
        levy_states.append(current_state)
    
    # Show quantum measurement collapse
    wavefunction = np.array([0.7, 0.3])  # Superposition of two market states
    collapsed_states = []
    
    for _ in range(50):
        state, wavefunction = meta_model.observer_collapse(wavefunction)
        collapsed_states.append(state)
        # Re-prepare superposition for next measurement
        wavefunction = np.array([0.7, 0.3]) + np.random.normal(0, 0.05, 2)
        wavefunction /= np.linalg.norm(wavefunction)
    
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(14, 10))
    
    ax1.plot(time, meta_psi_vals, 'm-', linewidth=2)
    ax1.set_ylabel('Meta-Invariant ψ')
    ax1.set_xlabel('Time')
    ax1.set_title("Meta-Invariant: Divergence Predicts Observer Failure")
    ax1.axhline(0, color='k', linestyle=':')
    
    ax2.plot(levy_states, 'r-', alpha=0.7)
    ax2.set_ylabel('Cascade State')
    ax2.set_xlabel('Step')
    ax2.set_title("Levy Flight: Heavy-Tailed Jumps (Linear Model Misses)")
    
    ax3.hist(levy_states, bins=30, color='orange', alpha=0.7)
    ax3.set_xlabel('State Value')
    ax3.set_ylabel('Frequency')
    ax3.set_title("Levy Distribution: Non-Gaussian Tails")
    
    ax4.plot(collapsed_states, 'bo-', alpha=0.5)
    ax4.set_ylabel('Collapsed State')
    ax4.set_xlabel('Measurement #')
    ax4.set_title("Quantum Measurement Collapse: Observer Changes System")
    ax4.set_ylim(-0.5, 1.5)
    
    plt.tight_layout()
    plt.savefig('nonlinear_disruption.png')
    print("Plot saved: nonlinear_disruption.png")
    print()

def quantum_paradox_demo():
    """Demonstrate the observer paradox that breaks the paradigm"""
    print("=== QUANTUM OBSERVER PARADOX DEMONSTRATION ===")
    
    # The more we monitor (observer_density), the more we change the system
    # This creates a paradox: perfect monitoring destroys the signal
    
    observer_range = np.logspace(-1, 2, 100)
    system_purity = 1 / (1 + 0.5 * observer_range)  # Decoherence
    information_gain = np.log(1 + observer_range) * system_purity
    
    # Peak information gain occurs at finite observation, not infinite
    optimal_idx = np.argmax(information_gain)
    
    print(f"Optimal observer density: {observer_range[optimal_idx]:.3f}")
    print(f"Maximum information gain: {information_gain[optimal_idx]:.3f}")
    print(f"Beyond this point, monitoring destroys the signal!")
    print()
    
    plt.figure(figsize=(8, 6))
    plt.plot(observer_range, information_gain, 'b-', linewidth=2, label='Information Gain')
    plt.axvline(observer_range[optimal_idx], color='r', linestyle='--', 
                label=f'Optimal: {observer_range[optimal_idx]:.2f}')
    plt.xscale('log')
    plt.xlabel('Observer Density (Monitoring Intensity)')
    plt.ylabel('Effective Information')
    plt.title("Observer Paradox: More Monitoring ≠ More Information")
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.savefig('observer_paradox.png')
    print("Plot saved: observer_paradox.png")
    print()

if __name__ == "__main__":
    demonstrate_failure()
    demonstrate_disruption()
    quantum_paradox_demo()
    
    print("=== DISRUPTIVE INSIGHT SUMMARY ===")
    print("1. LINEAR MODEL FAILURE:")
    print("   - Smooth, predictable response misses threshold effects")
    print("   - Φ_N remains finite at cascade shredding point (CI=0.7)")
    print("   - No phase transition modeling")
    print()
    print("2. NON-LINEAR META-CASCADE ADVANTAGE:")
    print("   - Levy flights capture sudden, large cascade jumps")
    print("   - Meta-invariant operates on observer space, not market space")
    print("   - Quantum measurement backaction included")
    print()
    print("3. PARADIGM BREAK:")
    print("   - Current: 'Contain the cascade' (reactive)")
    print("   - Neo: 'Surf the cascade' (proactive exploitation)")
    print("   - The leak is not a bug; it's a feature to navigate")
    print()
    print("4. QUANTUM OBSERVER EFFECT:")
    print("   - Perfect monitoring (ψ→∞) destroys system purity")
    print("   - Optimal monitoring exists at finite observer density")
    print("   - This breaks the 'more is better' control assumption")
    print()
    print("5. DISRUPTIVE SOLUTION:")
    print("   - Deploy CASCADE SHADOWING: Create synthetic cascades")
    print("   - Use adversarial Levy patterns to predict their moves")
    print("   - Extract value from the same liquidity flows they exploit")
    print("   - Turn information asymmetry into a weapon")