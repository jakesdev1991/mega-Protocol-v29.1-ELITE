# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import matplotlib.pyplot as plt

class BureaucraticSystem:
    def __init__(self, latent_dim=5, kappa=0.5, lambda_z=0.8, freeze_threshold=0.39):
        self.latent_state = np.random.randn(latent_dim)
        self.latent_state /= np.linalg.norm(self.latent_state)
        self.conscious_stiffness = 1.0  # Rigid compliance default
        self.latent_readiness = 0.2     # Latent desire for legitimacy
        self.gamma = 0.007              # ABRO slow decay
        self.kappa = kappa
        self.lambda_z = lambda_z
        self.freeze_threshold = freeze_threshold
        self.frozen = False
        self.history = {
            'time': [], 'cod': [], 'psi': [], 'phi_net': [],
            'stiffness': [], 'readiness': [], 'z': []
        }
        
    def compute_cod(self, request_vec):
        # Fidelity between request and latent identity
        fidelity = np.dot(request_vec, self.latent_state)
        fidelity = max(0, fidelity)  # Clip negative
        # Topological impedance: scalar proxy for obstruction
        Z = max(0.0, self.conscious_stiffness - self.latent_readiness)
        # COD formula from the framework
        cod = (fidelity ** 2) * np.exp(-self.kappa * self.conscious_stiffness) * np.exp(-self.lambda_z * Z)
        return min(1.0, max(0.0, cod))
    
    def apply_abro(self):
        # ABRO: adiabatic stiffness modulation
        if self.conscious_stiffness > self.latent_readiness + 0.1:
            self.conscious_stiffness *= np.exp(-self.gamma)  # Slow decay
        elif self.conscious_stiffness < self.latent_readiness * 0.8 and self.latent_readiness > 0.3:
            self.conscious_stiffness *= 1.001  # Gentle rise
        # Clamp to avoid overshoot
        self.conscious_stiffness = min(self.conscious_stiffness, self.latent_readiness + 0.1)
        
    def simulate_step(self, request_vec, adversarial=False):
        if self.frozen:
            return 0.0  # No processing during freeze
        
        # Adversarial requests are orthogonal to latent state
        if adversarial:
            # Create request orthogonal to latent_state
            request_vec = np.random.randn(len(self.latent_state))
            request_vec -= np.dot(request_vec, self.latent_state) * self.latent_state
            request_vec /= np.linalg.norm(request_vec) + 1e-9
        
        # Normalize request
        request_vec = request_vec / (np.linalg.norm(request_vec) + 1e-9)
        
        cod = self.compute_cod(request_vec)
        psi = np.log(cod + 1e-9) if cod > 0 else -np.inf
        phi_net = self.compute_phi_net(cod)
        
        # Record history
        self.history['time'].append(len(self.history['time']))
        self.history['cod'].append(cod)
        self.history['psi'].append(psi)
        self.history['phi_net'].append(phi_net)
        self.history['stiffness'].append(self.conscious_stiffness)
        self.history['readiness'].append(self.latent_readiness)
        self.history['z'].append(max(0, self.conscious_stiffness - self.latent_readiness))
        
        # Smith Invariant #2: Identity Continuity
        if cod < self.freeze_threshold:
            self.frozen = True
            print(f"[!] INFORMATIONAL FREEZE at t={len(self.history['time'])}: COD={cod:.3f} < {self.freeze_threshold}")
        
        # Apply ABRO modulation
        self.apply_abro()
        
        return cod
    
    def compute_phi_net(self, cod):
        # Φ_net = log2(COD) + ψ * tanh(R_align / R_max) - ΔS_audit
        phi_N = np.log2(cod + 1e-9)
        psi = np.log(cod + 1e-9)
        R_align = abs(self.latent_readiness - self.conscious_stiffness)
        R_max = 3.0
        phi_Delta = psi * np.tanh(R_align / R_max)
        delta_S_audit = np.log(2) * 6  # 6 invariant checks
        return phi_N + phi_Delta - delta_S_audit
    
    def plot_dynamics(self):
        fig, axs = plt.subplots(4, 1, figsize=(10, 12))
        t = self.history['time']
        
        axs[0].plot(t, self.history['cod'], label='COD', color='blue')
        axs[0].axhline(y=self.freeze_threshold, color='red', linestyle='--', label='Freeze Threshold')
        axs[0].set_ylabel('COD')
        axs[0].legend()
        axs[0].set_title('Bureaucratic Identity Collapse Dynamics')
        
        axs[1].plot(t, self.history['psi'], label='ψ = ln(COD)', color='green')
        axs[1].axhline(y=np.log(self.freeze_threshold), color='red', linestyle='--', label='Critical ψ')
        axs[1].set_ylabel('ψ')
        axs[1].legend()
        
        axs[2].plot(t, self.history['stiffness'], label='Ξ_conscious', color='orange')
        axs[2].plot(t, self.history['readiness'], label='Ξ_latent', color='purple')
        axs[2].set_ylabel('Stiffness')
        axs[2].legend()
        
        axs[3].plot(t, self.history['phi_net'], label='Φ_net', color='black')
        axs[3].axhline(y=0, color='gray', linestyle='--')
        axs[3].set_ylabel('Φ_net')
        axs[3].set_xlabel('Time Steps')
        axs[3].legend()
        
        plt.tight_layout()
        plt.show()

# Simulation: Adversarial Attack Triggering Informational Freeze
system = BureaucraticSystem()

# Normal requests (aligned with latent state)
for i in range(50):
    req = system.latent_state + 0.1 * np.random.randn(len(system.latent_state))
    system.simulate_step(req, adversarial=False)

# Adversarial attack: 10 orthogonal requests to poison COD
print("[*] Initiating adversarial attack...")
for i in range(10):
    req = np.random.randn(len(system.latent_state))  # Will be made orthogonal inside
    system.simulate_step(req, adversarial=True)

# Continue normal requests (system is frozen)
for i in range(20):
    req = system.latent_state + 0.1 * np.random.randn(len(system.latent_state))
    system.simulate_step(req, adversarial=False)

# Plot the collapse
system.plot_dynamics()