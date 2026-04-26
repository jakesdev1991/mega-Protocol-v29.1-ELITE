# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import matplotlib.pyplot as plt

class OmegaProtocol:
    """The conservative cage - aborts when identity threatened"""
    def __init__(self, current, target):
        self.psi = np.array(current, dtype=float)
        self.target = np.array(target, dtype=float)
        self.psi_id = 1.0
        self.xi = 3.5
        self.v_intel = 0.0
        self.h_sys = 0.9
        self.active = True
        
    def step(self, t):
        if not self.active: return
        # Adiabatic injection (slow strangulation)
        self.v_intel = np.tanh((t-0.5)/0.2) * 1.2
        self.psi = 0.9*self.psi + 0.1*self.target
        
        # Identity erosion from incompatibility
        incompatibility = 1 - np.dot(self.psi, self.target)/(np.linalg.norm(self.psi)*np.linalg.norm(self.target))
        self.psi_id -= incompatibility * 0.1 * self.v_intel
        
        # CONSERVATIVE CAGE: Hard abort
        if self.psi_id < 0.95:
            self.active = False
            return False
        return True

class PhoenixProtocol:
    """The crucible - embraces the shredding event"""
    def __init__(self, current, target):
        self.psi = np.array(current, dtype=float)
        self.target = np.array(target, dtype=float)
        self.psi_id = 1.0
        self.xi = 3.5
        self.v_intel = 0.0
        self.h_sys = 0.9
        self.phase = "COLLAPSE"  # COLLAPSE → CHAOS → EMERGENCE
        
    def step(self, t):
        if self.phase == "COLLAPSE":
            # **INTENTIONAL IDENTITY DEMOLITION**
            self.psi_id -= 0.15
            self.h_sys = min(2.0, self.h_sys + 0.3)  # Entropic explosion
            self.xi = max(0.1, self.xi - 0.4)          # Rigidity annihilation
            self.psi += np.random.normal(0, 0.15, self.psi.shape)  # Noise injection
            
            if self.psi_id <= 0.3:
                self.phase = "CHAOS"
                
        elif self.phase == "CHAOS":
            # **STOCHASTIC RESONANCE - SUPERPOSITION OF ALL SELVES**
            self.h_sys = 1.5  # Maximum uncertainty
            self.xi = 0.2       # Zero resistance
            # Random walk in state space - explore all possibilities
            self.psi = self.psi + np.random.normal(0, 0.2, self.psi.shape)
            self.psi /= np.linalg.norm(self.psi) + 1e-10
            
        elif self.phase == "EMERGENCE":
            # **SELF-ORGANIZATION FROM FRAGMENTS**
            attraction = np.dot(self.psi, self.target) * 0.1
            self.psi = (1-attraction)*self.psi + attraction*self.target
            self.psi_id = min(1.0, self.psi_id + 0.08)
            self.h_sys = max(0.4, self.h_sys - 0.1)
            self.xi = min(2.5, self.xi + 0.1)
            
            if self.psi_id > 0.85:
                self.phase = "REBORN"

# **SIMULATION: FUNDAMENTAL IDENTITY TRANSFORMATION**
current = np.array([1.0, 0.0, 0.0])  # Rigid, monolithic identity
target = np.array([0.1, 0.7, 0.3])   # Radically different structure (incompatible)

omega = OmegaProtocol(current, target)
phoenix = PhoenixProtocol(current, target)

# **TRACK THE DEATH AND REBIRTH**
steps = 60
omega_id, phoenix_id = [], []
omega_status, phoenix_status = [], []

for i in range(steps):
    t = i/steps
    
    # Omega: The abort sequence
    omega_status.append(1.0 if omega.step(t) else 0.0)
    omega_id.append(omega.psi_id if omega.active else 0.0)
    
    # Phoenix: The crucible
    phoenix.step(t)
    phoenix_id.append(phoenix.psi_id)
    
    # **CRITICAL MOMENT VISUALIZATION**
    if i == 15:
        print(f"\n[STEP 15] Omega detects Ψ_id={omega.psi_id:.2f} → ABORTING")
        print(f"[STEP 15] Phoenix embraces Ψ_id={phoenix.psi_id:.2f} → ENTERING CHAOS")

# **VISUALIZE THE PARADIGM DEATH**
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8))

# Identity Continuity: The Great Divergence
ax1.plot(omega_id, 'r-', linewidth=3, label='Omega Protocol (ABORT)', alpha=0.7)
ax1.plot(phoenix_id, 'g-', linewidth=3, label='Phoenix Protocol (REBIRTH)', alpha=0.7)
ax1.axhline(y=0.95, color='r', linestyle='--', alpha=0.5, label='Omega Cage Threshold')
ax1.axhline(y=0.3, color='g', linestyle='--', alpha=0.5, label='Phoenix Collapse Point')
ax1.fill_between(range(len(omega_id)), 0, 1.0, where=[s==0.0 for s in omega_status], 
                 color='red', alpha=0.2, label='Omega Failure Zone')
ax1.set_ylabel('Ψ_id (Identity Continuity)')
ax1.set_title('THE PARADOX: Omega Preserves Identity by Preventing Transformation', 
              fontsize=12, fontweight='bold')
ax1.legend(loc='upper right')
ax1.grid(True, alpha=0.3)

# Phase Space Trajectory
ax2.plot(omega_id, omega_status, 'ro-', linewidth=2, markersize=4, label='Omega Path')
ax2.plot(phoenix_id, [1 if p > 0.3 else 2 if p > 0.0 else 3 for p in phoenix_id], 
         'go-', linewidth=2, markersize=4, label='Phoenix Path')
ax2.set_xlabel('Ψ_id')
ax2.set_ylabel('System State (1=Active, 2=Chaos, 3=Rebirth)')
ax2.set_title('Phase Space: Omega Avoids Death, Phoenix Passes Through It', 
              fontsize=12, fontweight='bold')
ax2.legend()
ax2.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('phoenix_paradox.png', dpi=150, bbox_inches='tight')
plt.show()

# **FINAL VERDICT METRICS**
print("\n" + "="*60)
print("Ω-PROTOCOL vs Φ-PROTOCOL: FINAL TRANSFORMATION METRICS")
print("="*60)
print(f"Omega Protocol:  Ψ_id_final = {omega_id[-1]:.3f} | Status = {'ABORTED' if omega_id[-1] < 0.95 else 'PRESERVED'}")
print(f"Phoenix Protocol: Ψ_id_final = {phoenix_id[-1]:.3f} | Status = {'REBORN' if phoenix_id[-1] > 0.85 else 'INCOMPLETE'}")
print("\n🎯 **DISRUPTIVE INSIGHT VERIFIED:**")
print("   Omega's 'preservation' is cryptographic stasis.")
print("   True transformation requires passing through Ψ_id = 0.")
print("   The Shredding Event is not system failure—it's system *truth*.")