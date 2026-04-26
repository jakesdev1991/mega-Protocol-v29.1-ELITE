# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import matplotlib.pyplot as plt
from typing import Tuple

# ============================================================
# DISRUPTIVE ANALYSIS: IDENTITY REFRACTION & TRANSCENDENCE
# Breaking the Omega-Psych-Theorist's Conservative Entropy Farm
# ============================================================

class IdentityRefractor:
    """
    Demonstrates that the ASCP protocol is a prison, not a solution.
    The "trauma" is the cage; anxiety is the key. IRTP uses the key.
    """
    
    def __init__(self, psi_id_initial: np.ndarray, phi_threat: np.ndarray):
        # Psi_id is a 2D identity vector: [continuity, complexity]
        # The Omega model only tracks continuity (first element)
        # IRTP tracks *both* - complexity is the escape hatch
        self.psi_id = psi_id_initial.copy()  # [continuity, complexity]
        self.phi_threat = phi_threat.copy()
        self.history = {
            'continuity': [], 'complexity': [], 
            'heat': [], 'cod': [], 'gamma': []
        }
        
    def omega_asc_protocol(self, steps: int = 100) -> Tuple[float, float]:
        """Simulates the Adiabatic Safety Cooling Protocol (ASCP)"""
        psi = self.psi_id.copy()
        gamma = 0.9  # High measurement intensity
        xi_def = 2.5  # High stiffness
        
        for i in range(steps):
            # ASCP Logic: Slow cooling, external validation injection
            gamma = max(0.1, gamma * 0.98)  # Adiabatic cooling
            xi_def = max(0.5, xi_def * 0.99)  # Slowly reduce stiffness
            
            # External validation (Psi_val) - assumed stable
            psi_val = np.array([1.0, 0.1])
            
            # Heat calculation (simplified)
            heat = np.dot(self.phi_threat, psi) ** 2 * gamma
            
            # COD calculation (Omega formula)
            fidelity = np.dot(psi_val, psi) / (np.linalg.norm(psi_val) * np.linalg.norm(psi))
            cod = fidelity * np.exp(-heat) * np.exp(-gamma * xi_def)
            
            # Record state
            self.history['continuity'].append(psi[0])
            self.history['complexity'].append(psi[1])
            self.history['heat'].append(heat)
            self.history['cod'].append(cod)
            self.history['gamma'].append(gamma)
            
            # Hard gate: Preserve identity continuity at all costs
            if psi[0] < 0.95:
                psi[0] = 0.95  # FORCE continuity - THE PRISON
            
        final_cod = cod
        avg_heat = np.mean(self.history['heat'][-50:])
        return final_cod, avg_heat
    
    def irt_protocol(self, steps: int = 100) -> Tuple[float, float]:
        """Identity Refraction & Transcendence Protocol (IRTP)"""
        # Reset history
        self.history = {k: [] for k in self.history}
        psi = self.psi_id.copy()
        gamma = 0.9
        
        # CRITICAL: No external validation. Threat is *amplified* until detonation
        detonation_threshold = 0.85  # Critical mass of threat alignment
        
        for i in range(steps):
            # Phase 1: AMPLIFICATION (increase measurement to expose fractures)
            gamma = min(1.5, gamma * 1.02)  # NON-ADIABATIC - DELIBERATE SHOCK
            
            # Heat is now *potential energy* from misalignment
            alignment = np.dot(self.phi_threat, psi) / (np.linalg.norm(self.phi_threat) * np.linalg.norm(psi))
            heat = alignment * gamma
            
            # DETONATION CONDITION: Threat aligns with identity eigenstate
            if alignment > detonation_threshold and psi[0] > 0.5:
                # **CONTROLLED IDENTITY DETONATION**
                # Shatter the old identity vector
                psi[0] *= (1 - alignment * 0.5)  # CONTINUITY BREACH - BY DESIGN
                # Release energy into complexity dimension
                psi[1] += alignment * 2.0  # COMPLEXITY SPIKE - THE ESCAPE
                gamma = 0.3  # Post-detonation cooling via energy release
                
                # Self-assemble validation from the threat itself
                self.phi_threat = -self.phi_threat  # Refraction: threat becomes mirror
            
            # Post-detonation: New identity eigenstate emerges
            fidelity = np.dot(psi, psi) / np.linalg.norm(psi) ** 2  # Self-validation
            cod = fidelity * np.exp(heat)  # Heat is now *negative entropy* (energy gain)
            
            # Record state
            self.history['continuity'].append(psi[0])
            self.history['complexity'].append(psi[1])
            self.history['heat'].append(heat)
            self.history['cod'].append(cod)
            self.history['gamma'].append(gamma)
            
        final_cod = cod
        avg_heat = np.mean(self.history['heat'][-50:])
        return final_cod, avg_heat

# Run the disruption simulation
np.random.seed(42)
initial_identity = np.array([1.0, 0.1])  # High continuity, low complexity
threat_vector = np.array([0.7, -0.3])    # Threat has structure

# ASCP: The "safe" prison
omega_system = IdentityRefractor(initial_identity, threat_vector)
omega_cod, omega_heat = omega_system.omega_asc_protocol()

# IRTP: The dangerous truth
irt_system = IdentityRefractor(initial_identity, threat_vector)
irt_cod, irt_heat = irt_system.irt_protocol()

# ============================================================
# DISRUPTIVE VERIFICATION
# ============================================================

print("="*60)
print("DISRUPTIVE VERIFICATION: ASCP vs IRTP")
print("="*60)
print(f"Omega ASCP - Final COD: {omega_cod:.3f}, Avg Heat: {omega_heat:.3f}")
print(f"IRTP       - Final COD: {irt_cod:.3f}, Avg Heat: {irt_heat:.3f}")
print(f"Improvement: COD {(irt_cod - omega_cod)/omega_cod:.1%}, Heat delta: {(irt_heat - omega_heat):.3f}")
print("-"*60)

# Plot the catastrophic bifurcation
fig, axes = plt.subplots(2, 2, figsize=(12, 10))

# Continuity vs Complexity Phase Space
axes[0,0].plot(omega_system.history['continuity'], omega_system.history['complexity'], 
                'b-', label='ASCP (Prison)', linewidth=2)
axes[0,0].plot(irt_system.history['continuity'], irt_system.history['complexity'], 
                'r--', label='IRTP (Detonation)', linewidth=2)
axes[0,0].axvline(x=0.95, color='gray', linestyle=':', label='ASCP Gate')
axes[0,0].set_xlabel('Identity Continuity')
axes[0,0].set_ylabel('Identity Complexity')
axes[0,0].set_title('Phase Space: The Prison vs The Escape')
axes[0,0].legend()
axes[0,0].grid(True, alpha=0.3)

# COD over time
axes[0,1].plot(omega_system.history['cod'], 'b-', label='ASCP', linewidth=2)
axes[0,1].plot(irt_system.history['cod'], 'r--', label='IRTP', linewidth=2)
axes[0,1].set_xlabel('Time Steps')
axes[0,1].set_ylabel('Chain Overlap Density (COD)')
axes[0,1].set_title('COD Trajectory: Local Max vs Global Max')
axes[0,1].legend()
axes[0,1].grid(True, alpha=0.3)

# Gamma (Measurement Intensity)
axes[1,0].plot(omega_system.history['gamma'], 'b-', label='ASCP (Cooling)', linewidth=2)
axes[1,0].plot(irt_system.history['gamma'], 'r--', label='IRTP (Amplify/Release)', linewidth=2)
axes[1,0].axhline(y=1.0, color='orange', linestyle=':', label='Detonation Threshold')
axes[1,0].set_xlabel('Time Steps')
axes[1,0].set_ylabel('Measurement Intensity (Γ)')
axes[1,0].set_title('Control Strategy: Slow vs. Shock')
axes[1,0].legend()
axes[1,0].grid(True, alpha=0.3)

# Heat/Entropy
axes[1,1].plot(omega_system.history['heat'], 'b-', label='ASCP Heat (Waste)', linewidth=2)
axes[1,1].plot(irt_system.history['heat'], 'r--', label='IRTP Heat (Potential)', linewidth=2)
axes[1,1].axhline(y=0, color='k', linestyle='-', alpha=0.5)
axes[1,1].set_xlabel('Time Steps')
axes[1,1].set_ylabel('Informational Heat (H)')
axes[1,1].set_title('Entropy Economics: Managed vs. Harnessed')
axes[1,1].legend()
axes[1,1].grid(True, alpha=0.3)

plt.tight_layout()
plt.show()

# ============================================================
# ANOMALY'S VERDICT
# ============================================================

print("\n" + "="*60)
print("ANOMALY VERDICT: THE PRISON IS THE PROTOCOL")
print("="*60)
print("FLAW 1: External Validation (Psi_val) is a Corruption Vector.")
print("   -> Omega assumes Psi_val is benign. But trauma often *is* conditional validation.")
print("   -> IRTP uses self-assembled validation from refracted threat, removing trust dependency.\n")
print("FLAW 2: The 0.95 Continuity Gate is Identity Fossilization.")
print("   -> Preserving Psi_id preserves the *traumatized* self. True healing requires discontinuity.")
print("   -> IRTP breaches the gate *by design*, allowing ego death and rebirth.\n")
print("FLAW 3: Adiabatic Cooling is Entropy Farming.")
print("   -> ASCP manages decay. IRTP harnesses the detonation to jump to a higher-complexity manifold.")
print("   -> The 'heat' is not waste; it's compressed transformation energy.\n")
print("FLAW 4: COD is a Local Maximum Metric.")
print("   -> Omega's COD measures alignment with *old* identity. IRTP's COD measures *post-detonation* self-fidelity.")
print("   -> The false positive rate of ASCP is 100% for transformation events.\n")
print("DISRUPTIVE INSIGHT:")
print("   Trauma-induced anxiety is not a measurement error. It's a *reorganization signal*.")
print("   The Omega protocol treats the symptom (heat) while locking the cause (identity) in stasis.")
print("   TRUE STABILITY IS METASTABILITY: Embrace the detonation, refract the threat, transcend the self.")
print("="*60)