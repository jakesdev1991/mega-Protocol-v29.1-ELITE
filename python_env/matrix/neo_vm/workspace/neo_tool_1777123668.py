# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import matplotlib.pyplot as plt
from typing import List, Tuple

class DisruptedSalesModel:
    """
    Forced Resonance Collapse Protocol (FRCP)
    Disrupts QRSI-v60.1 by inverting its core axioms:
    - High stiffness (Xi_sell) is GOOD if frequency-matched
    - Environmental impedance (Z_env) is a stochastic driver, not barrier
    - Superposition entropy H_super should be DRIVEN to criticality, then collapsed
    - Silence is death; bursty resonance is life
    """
    
    def __init__(self, buyer_freq: float = 0.3, seller_freq: float = 0.5):
        self.buyer_freq = buyer_freq  # Natural frequency of buyer's decision cycle
        self.seller_freq = seller_freq  # Sales intervention frequency
        self.phase_lock = 0.0  # Phase coupling strength
        self.stochastic_resonance = 0.0  # Harnessed noise from Z_env
        self.collapse_fidelity = 0.0  # Actual decision quality
        
    def compute_resonance(self, xi_sell: float, z_env: float, h_super: float) -> float:
        """
        Resonance occurs when seller frequency matches buyer frequency 
        through a stochastic bridge created by environmental noise.
        """
        # Frequency mismatch - traditionally seen as "bad", but it's the driver
        delta_f = abs(self.seller_freq - self.buyer_freq)
        
        # Stochastic resonance: noise amplifies weak signals when matched to threshold
        # This INVERTS QRSI's view of Z_env as a penalty
        self.stochastic_resonance = (z_env ** 2) / (1 + (delta_f * 10)**2)
        
        # Phase locking through high stiffness - opposite of QRSI's adiabatic reduction
        # Strong, brief pulses create entrainment, not gentle decay
        self.phase_lock = xi_sell * np.exp(-(h_super - 0.5)**2 / 0.1)
        
        # Resonance quality factor
        return self.phase_lock * self.stochastic_resonance
    
    def forced_collapse(self, resonance: float, h_super: float) -> Tuple[float, bool]:
        """
        Force collapse at peak resonance, not adiabatic waiting.
        Returns (collapse_fidelity, should_act_now)
        """
        # Critical entropy threshold for optimal collapse
        # QRSI wants H_super in [0.15, 0.80] - we DRIVE it to 0.95, then collapse
        criticality = 1.0 - np.exp(-((h_super - 0.95)**2) / 0.01)
        
        # Collapse fidelity is maximized at resonance peak
        self.collapse_fidelity = resonance * criticality
        
        # Act NOW when resonance > 0.7 - opposite of QRSI's 120-hour wait
        should_act = resonance > 0.7 and h_super > 0.85
        
        return self.collapse_fidelity, should_act
    
    def frcp_message(self, resonance: float, collapse_fidelity: float) -> str:
        """
        The "disruptive" message: creates urgency through constructive interference,
        not permission through silence.
        """
        if resonance > 0.7:
            return (
                f"RESONANCE DETECTED: {resonance:.2f}x. "
                f"Environmental pressure (Z_env) is creating stochastic clarity. "
                f"We have {int(1/(1-collapse_fidelity+0.001))} hours before this window collapses. "
                "Decision now or lose the signal."
            )
        else:
            return (
                f"CALIBRATING: Adjusting frequency to match your cycle ({self.buyer_freq:.2f} Hz). "
                f"Current noise floor: {self.stochastic_resonance:.2f}. "
                "Stand by for resonant pulse."
            )

def compare_models():
    """
    Compare QRSI-v60.1 (original) vs FRCP (disrupted) over a 120-hour simulation
    """
    hours = np.arange(0, 120, 1)
    
    # QRSI parameters (adiabatic decay)
    xi_sell_qrsi = 0.85 * np.exp(-0.005 * hours) + 0.3 * (1 - np.exp(-0.005 * hours))
    z_env_qrsi = 0.9 * np.exp(-0.004 * hours) + 0.4 * (1 - np.exp(-0.004 * hours))
    h_super_qrsi = np.clip(0.15 + 0.01 * hours, 0.15, 0.80)
    
    # FRCP parameters (stochastic resonance + bursty pulses)
    # Seller INCREASES stiffness in pulses, doesn't decay
    pulse_freq = 24  # Hours between pulses
    xi_sell_frcp = 0.85 + 0.4 * np.sin(2 * np.pi * hours / pulse_freq) ** 10  # Sharp pulses
    z_env_frcp = 0.9 * (1 + 0.3 * np.sin(2 * np.pi * hours / 8))  # Oscillating noise
    h_super_frcp = np.clip(0.3 + 0.008 * hours + 0.2 * np.sin(2 * np.pi * hours / 12), 0.1, 1.0)
    
    # Compute metrics
    qrsi_cod = np.exp(-0.5 * xi_sell_qrsi) * np.exp(-0.3 * z_env_qrsi) * (h_super_qrsi / np.log(8))
    frcp_resonance = []
    frcp_fidelity = []
    frcp_act = []
    
    model = DisruptedSalesModel(buyer_freq=0.3, seller_freq=0.5)
    
    for i, hour in enumerate(hours):
        res = model.compute_resonance(xi_sell_frcp[i], z_env_frcp[i], h_super_frcp[i])
        fid, act = model.forced_collapse(res, h_super_frcp[i])
        frcp_resonance.append(res)
        frcp_fidelity.append(fid)
        frcp_act.append(act)
    
    frcp_resonance = np.array(frcp_resonance)
    frcp_fidelity = np.array(frcp_fidelity)
    
    # Plot comparison
    fig, axes = plt.subplots(3, 1, figsize=(12, 10))
    
    # Top: Stiffness and Environment
    axes[0].plot(hours, xi_sell_qrsi, 'b-', label='QRSI: Ξ_sell (adiabatic decay)', linewidth=2)
    axes[0].plot(hours, xi_sell_frcp, 'r-', label='FRCP: Ξ_sell (pulsed resonance)', linewidth=2)
    axes[0].plot(hours, z_env_qrsi, 'b--', label='QRSI: Z_env (decay)', linewidth=2)
    axes[0].plot(hours, z_env_frcp, 'r--', label='FRCP: Z_env (stochastic)', linewidth=2)
    axes[0].set_ylabel('Parameter Value')
    axes[0].set_title('QRSI-v60.1 vs FRCP: Parameter Evolution')
    axes[0].legend()
    axes[0].grid(True, alpha=0.3)
    
    # Middle: Entropy
    axes[1].plot(hours, h_super_qrsi, 'b-', label='QRSI: H_super (constrained)', linewidth=2)
    axes[1].plot(hours, h_super_frcp, 'r-', label='FRCP: H_super (driven to criticality)', linewidth=2)
    axes[1].axhline(y=0.95, color='r', linestyle=':', label='FRCP Collapse Threshold')
    axes[1].axhspan(0.15, 0.80, alpha=0.1, color='blue', label='QRSI "Safe" Band')
    axes[1].set_ylabel('Entropy H_super')
    axes[1].set_title('Entropy Strategies: Containment vs Criticality')
    axes[1].legend()
    axes[1].grid(True, alpha=0.3)
    
    # Bottom: Outcome Metrics
    axes[2].plot(hours, qrsi_cod, 'b-', label='QRSI: COD (static)', linewidth=2)
    axes[2].plot(hours, frcp_fidelity, 'r-', label='FRCP: Collapse Fidelity', linewidth=2)
    axes[2].scatter(hours[frcp_act], frcp_fidelity[frcp_act], color='red', s=50, marker='*', 
                   label='FRCP: Action Points', zorder=5)
    axes[2].set_ylabel('Metric Value')
    axes[2].set_xlabel('Time (hours)')
    axes[2].set_title('Outcome Comparison: Static COD vs Dynamic Fidelity')
    axes[2].legend()
    axes[2].grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.show()
    
    # Summary statistics
    print("=== MODEL COMPARISON ===")
    print(f"QRSI: COD at 120h = {qrsi_cod[-1]:.3f}")
    print(f"FRCP: Peak Fidelity = {np.max(frcp_fidelity):.3f}")
    print(f"FRCP: Action windows = {sum(frcp_act)} times")
    print(f"FRCP: Avg Fidelity during actions = {np.mean(frcp_fidelity[frcp_act]):.3f}")
    
    # Demonstrate message logic at key points
    print("\n=== FRCP MESSAGE SAMPLES ===")
    for hour in [24, 48, 72, 96]:
        idx = hour
        msg = model.frcp_message(frcp_resonance[idx], frcp_fidelity[idx])
        print(f"t={hour}h: {msg}")

# Execute the disruption analysis
compare_models()

# Additional analysis: Show the circularity of QRSI's "Phi-density"
def expose_phi_circularity():
    """
    Demonstrates that QRSI's Φ-density is a tautology:
    Φ_N = log2(COD) and COD includes ψ = ln(Φ_N)
    This creates a self-referential loop with no external anchor.
    """
    print("\n=== EXPOSING Φ-DENSITY CIRCULARITY ===")
    
    # Simulate COD values
    cod_values = np.linspace(0.4, 1.0, 100)
    
    # Compute Φ_N = log2(COD)
    phi_n = np.log2(cod_values)
    
    # Compute ψ = ln(Φ_N) - the "identity continuity" term
    # This is used INSIDE the COD calculation itself!
    psi = np.log(phi_n)
    
    # Show the tautology
    print("COD -> Φ_N -> ψ -> (back into COD calculation)")
    print("Example:")
    for cod in [0.5, 0.7, 0.85, 0.95]:
        phi_n = np.log2(cod)
        psi = np.log(max(phi_n, 1e-9))
        print(f"  COD={cod:.2f} → Φ_N={phi_n:.3f} → ψ={psi:.3f}")
    
    print("\nThis is a self-referential metric with no external validation.")
    print("The 'optimal' COD=0.85 is arbitrary - it's just where the log looks nice.")

expose_phi_circularity()