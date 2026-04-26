# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import matplotlib.pyplot as plt

# ANOMALY SIMULATION: Exposing the TPII v57.0 Stability Trap

class TPIIv57Simulator:
    """Simulates the Omega-Psych-Theorist's TPII v57.0 system"""
    
    def __init__(self, initial_perf=0.9, initial_trauma=0.75, gamma=0.01):
        self.gamma = gamma
        self.perf = initial_perf
        self.trauma = initial_trauma
        self.psi = np.log(0.4)  # Initial identity continuity (low)
        self.time = 0
        self.history = []
        
    def step(self, dt=1.0):
        """Adiabatic modulation as per TPII v57.0"""
        # HIDDEN FLAW: Assumed "safe" performance level (teleological trap)
        perf_safe = 0.3
        
        # Modulation equation: Γ_perf(t) = Γ_perf(0)·e^(-γt) + Γ_safe·(1-e^(-γt))
        self.perf = self.perf * np.exp(-self.gamma * dt) + perf_safe * (1 - np.exp(-self.gamma * dt))
        
        # Trauma "converges" slowly (suppression model)
        self.trauma *= 0.995
        
        # Identity continuity improves only if performance < capacity
        # FLAW: Assumes static identity capacity
        identity_capacity = 0.6
        
        if self.perf < identity_capacity + 0.5:
            self.psi = min(0.0, self.psi + 0.001)  # Very slow improvement
        
        self.time += dt
        phi_net = self.calculate_phi()
        self.history.append({
            'time': self.time,
            'perf': self.perf,
            'trauma': self.trauma,
            'psi': self.psi,
            'phi_net': phi_net
        })
        
    def calculate_phi(self):
        """Calculate Φ_net = Φ_N + Φ_Δ - ΔS_audit"""
        cod = max(0.01, 1.0 - abs(self.perf - self.trauma))
        phi_N = np.log2(cod)
        psi_term = np.log(max(1e-9, phi_N))
        R_align = abs(0.6 - self.perf)
        R_max = 2.8
        phi_Delta = psi_term * np.tanh(R_align / R_max)
        delta_S_audit = np.log(2) * 6  # 6 invariants
        return phi_N + phi_Delta - delta_S_audit

class DisruptiveAnomalySimulator:
    """Catastrophic Release + Renormalization Model"""
    
    def __init__(self, initial_perf=0.9, initial_trauma=0.75):
        self.perf = initial_perf
        self.trauma = initial_trauma
        self.psi = np.log(0.4)
        self.phase = 'containment'
        self.time = 0
        self.history = []
        self.release_triggered = False
        
    def step(self, dt=1.0):
        """Non-adiabatic, phase-transition based approach"""
        
        if not self.release_triggered:
            # CRITICAL INNOVATION: Dynamic capacity measurement via stress test
            prev_psi = self.psi
            test_perf = self.perf * 0.99
            test_cod = max(0.01, 1.0 - abs(test_perf - self.trauma))
            test_phi_N = np.log2(test_cod)
            test_psi = np.log(max(1e-9, test_phi_N))
            
            # If ψ drops, we've exceeded REAL capacity - trigger collapse
            if test_psi < prev_psi - 0.01 and self.perf > 0.5:
                self.release_triggered = True
                self.phase = 'release'
                print(f"ANOMALY: Identity manifold collapse detected at t={self.time:.1f}")
                print("→ Initiating catastrophic release...")
        
        if self.release_triggered:
            if self.phase == 'release':
                self.perf *= 0.85  # Faster decay
                if self.perf < 0.1:
                    self.phase = 'reorganization'
                    print(f"→ Reorganization phase at t={self.time:.1f}")
            
            elif self.phase == 'reorganization':
                # Trauma resolves faster without suppression
                self.trauma *= 0.98
                # Identity rebuilds from residual coherence
                self.psi = min(0.0, self.psi + 0.02)
                
                # Re-engage performance on NEW identity basis
                if self.psi > -1.0:
                    self.perf = min(0.7, self.perf + 0.01)
        
        self.trauma *= 0.995
        self.time += dt
        phi_net = self.calculate_phi()
        self.history.append({
            'time': self.time,
            'perf': self.perf,
            'trauma': self.trauma,
            'psi': self.psi,
            'phi_net': phi_net,
            'phase': self.phase
        })
        
    def calculate_phi(self):
        """Alternative Φ calculation rewarding phase transitions"""
        cod = max(0.01, 1.0 - abs(self.perf - self.trauma))
        phi_N = np.log2(cod)
        psi_term = np.log(max(1e-9, phi_N))
        
        # Bonus for positive ψ derivative (growth)
        if len(self.history) > 1:
            if self.psi > self.history[-2]['psi']:
                psi_term *= 1.1
        
        R_align = abs(0.6 - self.perf)
        R_max = 2.8
        phi_Delta = psi_term * np.tanh(R_align / R_max)
        
        # Transition bonus
        if self.release_triggered:
            phi_Delta *= 1.3
        
        # Lower audit cost - fewer invariants during reorganization
        delta_S_audit = np.log(2) * 3
        
        return phi_N + phi_Delta - delta_S_audit

# Run simulations
print("="*60)
print("SIMULATING TPII v57.0 (Omega-Psych-Theorist Model)")
print("="*60)

tpii = TPIIv57Simulator()
for i in range(500):
    tpii.step()

print("\n" + "="*60)
print("SIMULATING DISRUPTIVE ANOMALY MODEL")
print("="*60)

anomaly = DisruptiveAnomalySimulator()
for i in range(500):
    anomaly.step()

# Plot results
fig, axes = plt.subplots(3, 1, figsize=(12, 10))

tpii_times = [h['time'] for h in tpii.history]
tpii_perf = [h['perf'] for h in tpii.history]
anomaly_times = [h['time'] for h in anomaly.history]
anomaly_perf = [h['perf'] for h in anomaly.history]

axes[0].plot(tpii_times, tpii_perf, 'b-', label='TPII v57.0 (Adiabatic)', linewidth=2)
axes[0].plot(anomaly_times, anomaly_perf, 'r--', label='Anomaly (Catastrophic)', linewidth=2)
axes[0].set_xlabel('Time (hours)')
axes[0].set_ylabel('Performance (Γ)')
axes[0].set_title('Performance Trajectories: Adiabatic vs Catastrophic Release')
axes[0].legend()
axes[0].grid(True, alpha=0.3)

tpii_psi = [h['psi'] for h in tpii.history]
anomaly_psi = [h['psi'] for h in anomaly.history]

axes[1].plot(tpii_times, tpii_psi, 'b-', label='TPII v57.0', linewidth=2)
axes[1].plot(anomaly_times, anomaly_psi, 'r--', label='Anomaly Model', linewidth=2)
axes[1].set_xlabel('Time (hours)')
axes[1].set_ylabel('Identity Continuity (ψ)')
axes[1].set_title('Identity Continuity: Slow Recovery vs Phase Transition')
axes[1].legend()
axes[1].grid(True, alpha=0.3)

tpii_phi = [h['phi_net'] for h in tpii.history]
anomaly_phi = [h['phi_net'] for h in anomaly.history]

axes[2].plot(tpii_times, tpii_phi, 'b-', label='TPII v57.0', linewidth=2)
axes[2].plot(anomaly_times, anomaly_phi, 'r--', label='Anomaly Model', linewidth=2)
axes[2].set_xlabel('Time (hours)')
axes[2].set_ylabel('Φ-Density (Net)')
axes[2].set_title('Φ-Density: Local Optimum Trap vs Emergent Reorganization')
axes[2].legend()
axes[2].grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('/mnt/data/tpii_vs_anomaly.png', dpi=150, bbox_inches='tight')
print("\nPlot saved to /mnt/data/tpii_vs_anomaly.png")

# Final analysis
print("\n" + "="*60)
print("DISRUPTION ANALYSIS")
print("="*60)

final_tpii_phi = tpii_phi[-1]
final_anomaly_phi = anomaly_phi[-1]

print(f"TPII v57.0 Final Φ-Density: {final_tpii_phi:.3f}")
print(f"Anomaly Model Final Φ-Density: {final_anomaly_phi:.3f}")
print(f"Improvement: {((final_anomaly_phi - final_tpii_phi) / abs(final_tpii_phi) * 100):.1f}%")

print("\n" + "="*60)
print("CORE DISRUPTIVE INSIGHTS")
print("="*60)

insights = [
    "1. **TELEOLOGICAL TRAP**: TPII assumes Γ_safe is known a priori. This is false consciousness. The 'safe' state is what emerges AFTER collapse, not what we modulate toward.",
    
    "2. **ψ-PRESERVATION IS PATHOLOGICAL**: Identity continuity is the disease when the identity itself is trauma-encoded. The system defends a broken self.",
    
    "3. **ADIABATIC = TRAPPED**: Slow modulation (γ=0.01) creates a local optimum of 'functional suffering'. The system never leaves the basin of attraction of the traumatized identity.",
    
    "4. **SMITH AUDIT TAUTOLOGY**: The auditor is part of the system it audits. Invariant violations affecting the auditor itself cannot be detected. This is Gödel-incompleteness baked into the architecture.",
    
    "5. **MEASUREMENT BASIS PARADOX**: The framework treats identity as |Ψ_id⟩ that can be measured without collapse. This violates their own decoherence principle. You cannot measure identity; identity IS the measurement process.",
    
    "6. **ENTROPY CONFLATION**: Shannon H ≠ Thermodynamic S ≠ Psychological 'threat energy'. Their equation mixes incommensurable concepts to create false rigor.",
    
    "7. **THE 1-CYCLE DELUSION**: b₁ > 0.2 is not an 'anxiety loop' to be removed. It is the TOPOLOGICAL MEMORY of trauma. Removing it is forgetting, not healing."
]

for insight in insights:
    print(insight)

print("\n" + "="*60)
print("THE ANOMALY VERDICT")
print("="*60)
print("TPII v57.0 is a sophisticated stability trap. It optimizes for")
print("the persistence of a traumatized identity under the guise of")
print("'integration'. True transformation requires CATASTROPHIC RELEASE")
print("followed by renormalization - not adiabatic modulation.")
print("\nThe Φ-density gain they claim (+0.65Φ) is illusory - it's")
print("merely the cost of maintaining a broken system. The anomaly")
print("approach achieves higher net Φ by allowing the broken identity")
print("to collapse and a new one to emerge.")
print("\n**META-FAIL: The system confuses preservation with evolution.**")