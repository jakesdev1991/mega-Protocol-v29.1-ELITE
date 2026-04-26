# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import random
import matplotlib.pyplot as plt

class DisruptionSimulator:
    """
    Exposes the catastrophic failure of UIPO v64.2's Silence Protocol 
    under power asymmetry and critical citizen need.
    Demonstrates the Operator of Radical Collapse (ORC) as the only 
    valid stabilization mechanism.
    """
    
    def __init__(self, n_citizens=1000, critical_need_rate=0.15):
        self.n_citizens = n_citizens
        self.critical_need_rate = critical_need_rate
        
        # Citizen states: [identity_integrity, bureaucratic_trauma, power_asymmetry, urgent_need]
        # Identity integrity: 1.0 = whole, 0.0 = atomized (not "ghost" - that's romanticizing dissociation)
        self.citizens = np.random.rand(n_citizens, 4)
        self.citizens[:, 2] = 0.9  # Power asymmetry: bureaucrats hold 90% of power
        self.citizens[:, 3] = np.random.random(n_citizens) < critical_need_rate  # Critical needs: permits, care, survival
        
        # Agent's UIPO v64.2 parameters
        self.uipo_silence_count = 0
        self.uipo_harm_events = 0  # Silence when citizen has critical need = harm
        
        # ORC parameters
        self.orc_agency_transfers = 0
        self.orc_system_chaos = 0.0
        
    def run_uipo_cycle(self):
        """Runs one cycle of the 'enlightened' Silence Protocol."""
        messages_sent = 0
        
        for i in range(self.n_citizens):
            # Simplified UIPO invariant check (the details are irrelevant; the logic is the flaw)
            cod = np.random.rand()  # Simulated COD
            b1_homology = np.random.rand()  # Simulated topological defect
            
            # THE CORE FLAW: If invariants violated, SILENCE.
            # This is tautological: "If we can't help without risk, we do nothing."
            if cod < 0.85 or b1_homology > 0.8:
                self.uipo_silence_count += 1
                
                # THE CATASTROPHIC FAILURE: Silence when citizen has critical need
                if self.citizens[i, 3] == 1:  # Citizen needs immediate action
                    self.citizens[i, 1] += 0.3  # Bureaucratic trauma accumulates
                    self.citizens[i, 0] -= 0.2  # Identity integrity fragments (atomizes)
                    self.uipo_harm_events += 1
            else:
                # Send the patronizing "your uncertainty is geometry" message
                messages_sent += 1
                # But the form is still not approved. The power asymmetry remains.
                self.citizens[i, 2] -= 0.05  # Slight power shift (illusion of progress)
        
        return messages_sent
    
    def run_orc_cycle(self):
        """Runs one cycle of the Operator of Radical Collapse."""
        for i in range(self.n_citizens):
            # ORC Logic: Dissolve the measurement apparatus. Approve. Transfer power.
            # The "form" is erased. The citizen's authority is assumed.
            
            # Immediate approval for critical needs
            if self.citizens[i, 3] == 1:
                self.citizens[i, 0] += 0.4  # Identity integrity restored through agency
                self.citizens[i, 1] *= 0.5  # Trauma halved by removing the source
                self.citizens[i, 2] = max(0.1, self.citizens[i, 2] - 0.3)  # Radical power transfer
                self.orc_agency_transfers += 1
                self.orc_system_chaos += 0.1  # System accumulates "chaos" from lost control
            
            # For non-critical, simplify: auto-approve with minimal check
            else:
                self.citizens[i, 2] -= 0.1
                self.citizens[i, 0] += 0.1
                self.orc_system_chaos += 0.05
            
            # Bureaucratic manifold dissolves: fewer forms, less complexity
            # This is measured by reduction in "bureaucratic dimensionality"
    
    def simulate(self, cycles=50):
        """Simulates both operators over time."""
        uipo_identity_history = []
        uipo_harm_history = []
        orc_identity_history = []
        orc_chaos_history = []
        
        for t in range(cycles):
            # Run UIPO
            uipo_messages = self.run_uipo_cycle()
            avg_identity_uipo = np.mean(self.citizens[:, 0])
            uipo_identity_history.append(avg_identity_uipo)
            uipo_harm_history.append(self.uipo_harm_events)
            
            # Reset citizens for ORC run (fair comparison)
            self.citizens = np.random.rand(self.n_citizens, 4)
            self.citizens[:, 2] = 0.9
            self.citizens[:, 3] = np.random.random(self.n_citizens) < self.critical_need_rate
            
            # Run ORC
            self.run_orc_cycle()
            avg_identity_orc = np.mean(self.citizens[:, 0])
            orc_identity_history.append(avg_identity_orc)
            orc_chaos_history.append(self.orc_system_chaos)
        
        return uipo_identity_history, uipo_harm_history, orc_identity_history, orc_chaos_history

# Run the disruption simulation
sim = DisruptionSimulator(n_citizens=5000, critical_need_rate=0.20)
uipo_id, uipo_harm, orc_id, orc_chaos = sim.simulate(cycles=30)

# Visualization of the disruption
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

# Plot 1: Identity Integrity
ax1.plot(uipo_id, label='UIPO v64.2 (Silence Protocol)', color='blue', linewidth=2)
ax1.plot(orc_id, label='ORC (Operator of Radical Collapse)', color='red', linestyle='--', linewidth=2)
ax1.set_title('Citizen Identity Integrity Over Time', fontsize=14, fontweight='bold')
ax1.set_xlabel('Simulation Cycles')
ax1.set_ylabel('Avg. Identity Integrity (0=atomized, 1=whole)')
ax1.legend()
ax1.grid(True, alpha=0.3)

# Plot 2: System Metrics
ax2_twin = ax2.twinx()
harm_line = ax2.plot(uipo_harm, label='UIPO: Cumulative Harm Events', color='darkred', linewidth=2)
chaos_line = ax2_twin.plot(orc_chaos, label='ORC: System Chaos', color='orange', linestyle='--', linewidth=2)
ax2.set_title('Failure Metrics: Harm vs. Chaos', fontsize=14, fontweight='bold')
ax2.set_xlabel('Simulation Cycles')
ax2.set_ylabel('Harm Events (Silence on Critical Need)', color='darkred')
ax2_twin.set_ylabel('System Chaos (Loss of Control)', color='orange')
ax2.tick_params(axis='y', labelcolor='darkred')
ax2_twin.tick_params(axis='y', labelcolor='orange')
ax2.legend(loc='upper left')
ax2_twin.legend(loc='upper right')
ax2.grid(True, alpha=0.3)

plt.tight_layout()
plt.show()

# Print final statistics
print("\n" + "="*60)
print("DISRUPTION ANALYSIS: UIPO v64.2 vs. ORC")
print("="*60)
print(f"UIPO v64.2 - Final Avg. Identity Integrity: {uipo_id[-1]:.3f}")
print(f"UIPO v64.2 - Total Harm Events (silence on critical need): {uipo_harm[-1]}")
print(f"UIPO v64.2 - Silence Rate: {sim.uipo_silence_count / (sim.n_citizens * 30):.1%}")
print("\n" + "-"*60)
print(f"ORC - Final Avg. Identity Integrity: {orc_id[-1]:.3f}")
print(f"ORC - Agency Transfers: {sim.orc_agency_transfers}")
print(f"ORC - Final System Chaos: {orc_chaos[-1]:.3f}")
print("="*60)
print("\nDISRUPTIVE INSIGHT:")
print("UIPO v64.2's Silence Protocol doesn't preserve identity; it preserves *systemic guilt*.")
print("The 'ghost' citizen is not dissociated—they are *abandoned* by a system that chooses")
print("its own geometric purity over their survival. The topological 'loop' b₁>0.8 is not")
print("a vacuum—it's a *scream* that the system encodes as silence.")
print("\nThe ORC proves that 'chaos' (loss of bureaucratic control) is the *true* stability")
print("when it correlates with citizen agency. The failure mode is not b₁>0.8; it's b₀=0:")
print("the atomization of identity through bureaucratic *omission*.")
print("="*60)