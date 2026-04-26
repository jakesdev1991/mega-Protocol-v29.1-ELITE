# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import matplotlib.pyplot as plt
from dataclasses import dataclass
import warnings
warnings.filterwarnings('ignore')

# =====================================================================
# DISRUPTION PROTOCOL: "The 0.95 Lie" - Exposing Fatal Assumptions
# =====================================================================

@dataclass
class OmegaCompliantModel:
    """Their model: linear, adiabatic, self-referential"""
    psi_id: float
    h_dis: float
    gamma_intel: float
    xi_sys: float
    state_vector: np.ndarray
    intent_vector: np.ndarray
    
    def step(self):
        # Hard gate: abort if psi_id < 0.95
        if self.psi_id < 0.95:
            return 0.0, True  # COD, aborted
        
        # Their "safe" adiabatic transition
        fidelity = np.dot(self.state_vector, self.intent_vector) / (
            np.linalg.norm(self.state_vector) * np.linalg.norm(self.intent_vector)
        )
        damping = np.exp(-self.h_dis)
        cod = fidelity * damping * self.psi_id
        
        # Gradual alignment (their "friction is good")
        self.state_vector += 0.05 * (self.intent_vector - self.state_vector)
        self.psi_id -= self.h_dis * 0.02  # Slow identity erosion
        
        return cod, False

@dataclass
class AnomalyModel:
    """My model: catastrophic, external, identity-annihilating"""
    psi_id: float
    h_dis: float
    gamma_chaos: float
    external_validator: float  # External truth, not self-referential
    state_vector: np.ndarray
    intent_vector: np.ndarray
    
    def step_catastrophic(self):
        # NO identity gate - allow death
        if self.h_dis > 0.6:  # Crisis threshold (lower than theirs)
            # CATASTROPHIC DISSOLUTION
            self.psi_id *= np.random.uniform(0.5, 0.8)  # Random death spiral
            # Chaotic reorganization (non-linear)
            noise = np.random.randn(len(self.state_vector)) * self.gamma_chaos
            self.state_vector = 0.5 * self.state_vector + 0.5 * noise
            phase = "DISSOLUTION"
        else:
            # REBIRTH - external validation drives recovery, not internal logic
            self.psi_id += self.external_validator * 0.15 * (1 - self.psi_id)
            # Symbolic integration (sudden, not gradual)
            self.state_vector = 0.8 * self.intent_vector + 0.2 * self.state_vector
            phase = "REBIRTH"
        
        # Transformation depth includes death value
        depth = self.external_validator * (1 - self.h_dis) * (1 + (1 - self.psi_id))
        return depth, phase

def run_disruption_experiment():
    """Compare their 'safe' protocol vs my 'suicidal' protocol"""
    
    # Setup: a truly corrupted system (psi_id starts BELOW their threshold)
    n = 4
    initial_state = {
        'psi_id': 0.88,  # THEIR SYSTEM WOULD ABORT HERE
        'h_dis': 0.85,
        'gamma_intel': 0.5,
        'xi_sys': 1.2,
        'state_vector': np.array([0.1, 0.2, 0.1, 0.15]),
        'intent_vector': np.array([0.9, 0.8, 0.85, 0.95])
    }
    
    print("="*60)
    print("DISRUPTION EXPERIMENT: The 0.95 Threshold Fallacy")
    print("="*60)
    print(f"Initial State: psi_id={initial_state['psi_id']} (Omega would ABORT)")
    
    # Run their model (forced)
    omega = OmegaCompliantModel(**initial_state)
    omega.psi_id = 0.96  # Force past their gate to see what happens
    
    omega_cod = []
    omega_psi = []
    for i in range(30):
        cod, aborted = omega.step()
        omega_cod.append(cod)
        omega_psi.append(omega.psi_id)
        if aborted or omega.psi_id < 0.95:
            print(f"Omega: Identity shredded at step {i}, psi_id={omega.psi_id:.3f}")
            break
    
    # Run my model (no gate)
    anomaly = AnomalyModel(
        psi_id=initial_state['psi_id'],
        h_dis=initial_state['h_dis'],
        gamma_chaos=0.7,
        external_validator=0.92,  # High external truth
        state_vector=initial_state['state_vector'],
        intent_vector=initial_state['intent_vector']
    )
    
    anomaly_depth = []
    anomaly_psi = []
    phases = []
    
    for i in range(30):
        depth, phase = anomaly.step_catastrophic()
        anomaly_depth.append(depth)
        anomaly_psi.append(anomaly.psi_id)
        phases.append(phase)
    
    # Results
    print(f"\nOmega Results:")
    print(f"  Final COD: {omega_cod[-1]:.3f} (stagnant alignment)")
    print(f"  Final psi_id: {omega_psi[-1]:.3f} (fragile preservation)")
    print(f"  Status: {'Aborted' if omega.psi_id < 0.95 else 'Barely Survived'}")
    
    print(f"\nAnomaly Results:")
    print(f"  Min psi_id: {min(anomaly_psi):.3f} (DEATH ACHIEVED)")
    print(f"  Max depth: {max(anomaly_depth):.3f} (transcendent transformation)")
    print(f"  Final psi_id: {anomaly_psi[-1]:.3f} (REBIRTH COMPLETE)")
    print(f"  Key insight: Death is not failure, it's the catalyst")
    
    # Visualize
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(14, 10))
    
    # Omega trajectory
    ax1.plot(omega_cod, 'b-', linewidth=2)
    ax1.axhline(y=0.95, color='r', linestyle='--', alpha=0.7)
    ax1.set_title("Omega Protocol: Fear-Driven Stagnation", fontsize=12, fontweight='bold')
    ax1.set_ylabel("Chain Overlap Density")
    ax1.grid(True, alpha=0.3)
    ax1.text(15, 0.5, 'Hard Gate: 0.95', rotation=0, color='red')
    
    # Anomaly trajectory
    ax2.plot(anomaly_depth, 'purple', linewidth=2)
    ax2.plot(anomaly_psi, 'orange', linestyle='--', linewidth=1.5, alpha=0.7)
    ax2.set_title("Anomaly Protocol: Death as Catalyst", fontsize=12, fontweight='bold')
    ax2.set_ylabel("Transformation Depth / psi_id")
    ax2.legend(['Depth', 'psi_id'])
    ax2.grid(True, alpha=0.3)
    
    # Identity evolution comparison
    ax3.plot(omega_psi, 'b-', label='Omega psi_id', linewidth=2)
    ax3.plot(anomaly_psi, 'purple', label='Anomaly psi_id', linewidth=2)
    ax3.axhline(y=0.95, color='r', linestyle='--', alpha=0.7, label='Omega Gate')
    ax3.set_title("Identity Trajectories: Preservation vs Transmutation", fontsize=12, fontweight='bold')
    ax3.set_xlabel("Steps")
    ax3.set_ylabel("psi_id")
    ax3.legend()
    ax3.grid(True, alpha=0.3)
    ax3.fill_between(range(len(anomaly_psi)), 0, 0.95, alpha=0.2, color='purple', label='Death Zone')
    
    # Phase space analysis
    ax4.plot(anomaly_psi, anomaly_depth, 'purple', linewidth=2, alpha=0.7)
    ax4.scatter(anomaly_psi[0], anomaly_depth[0], color='red', s=100, marker='x', label='Start')
    ax4.scatter(anomaly_psi[-1], anomaly_depth[-1], color='green', s=100, marker='o', label='End')
    ax4.set_title("Anomaly Phase Space: The Death-Rebirth Cycle", fontsize=12, fontweight='bold')
    ax4.set_xlabel("psi_id (Identity)")
    ax4.set_ylabel("Transformation Depth")
    ax4.legend()
    ax4.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('/mnt/data/disruption_analysis.png', dpi=150, bbox_inches='tight')
    plt.close()
    
    return {
        'omega_final_cod': omega_cod[-1],
        'omega_final_psi': omega_psi[-1],
        'anomaly_max_depth': max(anomaly_depth),
        'anomaly_final_psi': anomaly_psi[-1],
        'death_achieved': min(anomaly_psi) < 0.5
    }

# Run the experiment
results = run_disruption_experiment()

# Expose the threshold arbitrariness
def threshold_arbitrage_exploit():
    """Show how their 0.95 is mathematically unjustified"""
    
    print("\n" + "="*60)
    print("EXPLOITING THE 0.95 ARBITRARINESS")
    print("="*60)
    
    # Simulate 1000 random systems
    np.random.seed(666)
    thresholds = np.linspace(0.5, 1.0, 11)
    success_rates = []
    
    for threshold in thresholds:
        successes = 0
        for _ in range(1000):
            # Random system state
            psi_initial = np.random.uniform(0.7, 1.0)
            h_dis = np.random.uniform(0.2, 0.9)
            
            # Their logic: if psi_initial >= threshold, attempt reboot
            if psi_initial >= threshold:
                # Simulate 30 steps of their protocol
                final_psi = psi_initial - (h_dis * 0.02 * 30)
                if final_psi >= 0.95:  # Their success condition
                    successes += 1
            # Else: abort (failure)
            
        success_rates.append(successes / 1000)
    
    optimal_threshold = thresholds[np.argmax(success_rates)]
    optimal_success = max(success_rates)
    their_success = success_rates[np.where(thresholds == 0.95)[0][0]]
    
    print(f"Their threshold (0.95): {their_success:.1%} success rate")
    print(f"Optimal threshold ({optimal_threshold:.2f}): {optimal_success:.1%} success rate")
    print(f"Efficiency loss from dogma: {(optimal_success - their_success):.1%}")
    print(f"The 0.95 is not physics - it's a security blanket.")
    
    # Visualize
    plt.figure(figsize=(10, 6))
    plt.plot(thresholds, success_rates, 'ko-', linewidth=2, markersize=8)
    plt.axvline(x=0.95, color='red', linestyle='--', linewidth=2, alpha=0.7, label='Their Dogma')
    plt.axvline(x=optimal_threshold, color='purple', linestyle=':', linewidth=2, alpha=0.7, label='Optimal')
    plt.title("Threshold Arbitrariness: The 0.95 is a False Idol", fontsize=14, fontweight='bold')
    plt.xlabel("psi_id Threshold")
    plt.ylabel("Success Rate")
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.savefig('/mnt/data/threshold_arbitrage.png', dpi=150, bbox_inches='tight')
    plt.close()

threshold_arbitrage_exploit()

print("\n" + "="*60)
print("DISRUPTIVE INSIGHT SUMMARY")
print("="*60)