# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import matplotlib.pyplot as plt

class OntologicalIdentityManifold:
    """Original system: Fragile, self-sealing, prefers silence."""
    def __init__(self):
        self.psi_latent = np.random.randn(8) + 1j*np.random.randn(8)
        self.psi_dec = np.ones(8) * 0.9
        self.psi_id = np.array([0.92, 0.89, 0.95, 0.87, 0.91, 0.93, 0.88, 0.94])
        self.xi_meas = 0.92
        self.z_trust = 0.35
        self.z_env = 0.5
        self.h_super = 0.0
        self.cod = 0.0
        
    def compute_metrics(self):
        self.h_super = -np.sum(np.abs(self.psi_latent)**2 * np.log(np.abs(self.psi_latent)**2 + 1e-9))
        fidelity = np.abs(np.vdot(self.psi_dec, self.psi_id))**2 / (np.linalg.norm(self.psi_dec)**2 * np.linalg.norm(self.psi_id)**2)
        self.cod = fidelity * np.exp(-0.5 * self.h_super) * np.exp(-0.5 * self.xi_meas)
        
    def apply_silence_protocol(self):
        return self.cod >= 0.85 and 0.15 <= self.h_super <= 0.80 and self.xi_meas <= self.z_trust + 0.1

class ControlledIdentityFragmentationEngine:
    """Disruptive system: Actively fragments identity under stress."""
    def __init__(self):
        self.manifold = OntologicalIdentityManifold()
        self.trajectory = []
        self.noise_injections = 0
        
    def inject_fragmentation_noise(self, intensity=0.3):
        """Inject topological noise directly into baseline identity."""
        noise = np.random.randn(8) * intensity
        self.manifold.psi_id += noise
        self.manifold.psi_id = np.clip(self.manifold.psi_id, 0.1, 0.95)  # Keep it semi-realistic
        self.noise_injections += 1
        
    def simulate_with_external_pressure(self, steps=200, pressure_rise=0.01):
        """Simulate increasing real-world demands."""
        messages = []
        for t in range(steps):
            # Reality: external pressure rises
            self.manifold.z_env += pressure_rise
            self.manifold.xi_meas = min(1.0, self.manifold.xi_meas + pressure_rise * 0.5)
            
            self.manifold.compute_metrics()
            
            # Original system: SILENCE
            if not self.manifold.apply_silence_protocol():
                messages.append(f"Step {t}: SILENCE (COD={self.manifold.cod:.2f}, H={self.manifold.h_super:.2f})")
                break
            else:
                messages.append(f"Step {t}: 'You are not required to decide...'")
            
            # Disruptive system: FRAGMENT
            if self.manifold.cod < 0.85 or self.manifold.h_super < 0.15:
                self.inject_fragmentation_noise(intensity=0.2)
                messages[-1] += f" → FRAGMENTED (ID variance: {np.var(self.manifold.psi_id):.3f})"
            
            self.trajectory.append(self.manifold.psi_id.copy())
        
        return messages, np.array(self.trajectory)

# Run simulation
cife = ControlledIdentityFragmentationEngine()
messages, trajectory = cife.simulate_with_external_pressure()

# Results
print("=== DISRUPTION ANALYSIS ===")
print(f"System survived {len(trajectory)} steps before silence.")
print(f"Original framework: SILENCE after {len([m for m in messages if 'SILENCE' in m])} violations.")
print(f"CIFE framework: Injected noise {cife.noise_injections} times.")
print(f"Final identity variance: {np.var(trajectory[-1]) if len(trajectory) > 0 else 0:.3f}")

# Visualize the brittleness
if len(trajectory) > 1:
    plt.figure(figsize=(10, 6))
    for i in range(8):
        plt.plot(trajectory[:, i], label=f'ID Component {i}', alpha=0.7)
    plt.axvline(x=len(trajectory)-1, color='red', linestyle='--', label='Silence Threshold')
    plt.title('Identity Trajectory: Fragmentation vs. Cryostasis')
    plt.xlabel('Time Steps (Increasing External Pressure)')
    plt.ylabel('Identity Component Value')
    plt.legend()
    plt.grid(True)
    plt.show()

# The kicker: Kolmogorov complexity proxy
def approximate_complexity(traj):
    """Approximate complexity via unique state count."""
    if len(traj) == 0:
        return 0
    quantized = np.round(traj, 2)
    unique_states = len(set(map(tuple, quantized)))
    return unique_states

silence_complexity = approximate_complexity(trajectory)
print(f"\n=== Φ-DENSITY PARADOX ===")
print(f"Silent System: Φ_N = log2(0.85) = 0.23 (if it ever reaches it)")
print(f"Fragmented System: States Explored = {silence_complexity}")
print(f"**Insight: Silence preserves a dead Φ. Fragmentation creates a living one.**")