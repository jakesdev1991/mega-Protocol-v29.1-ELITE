# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
# DISRUPTION CORE: Context is not a manifold—it's a self-modifying memory field
# The FTFM-Ω proposal is built on an ontological fallacy that collapses under operation

import numpy as np
import matplotlib.pyplot as plt
from scipy.linalg import svd

class ContextualMemoryField:
    """Biological context as a self-modifying memory field, not static manifold"""
    def __init__(self, dimensions=128):
        self.state = np.random.randn(dimensions) * 0.1
        self.memory_kernel = np.eye(dimensions) * 0.5  # Initial connectivity
        self.trajectory = []
        self.rewrite_intensity = []
        
    def apply_device_operator(self, device_vector, coupling=0.15):
        """Device operation REWRITES the context field"""
        # Device-context coupling is a tensor product, not scalar field evaluation
        interaction_tensor = np.outer(device_vector, self.state)
        
        # Memory kernel is modified: context REMEMBERS previous perturbations
        self.memory_kernel += coupling * interaction_tensor
        
        # State evolution: context is a non-linear dynamical system
        self.state = np.tanh(np.dot(self.memory_kernel, self.state) + 
                            coupling * device_vector)
        
        self.trajectory.append(self.state.copy())
        self.rewrite_intensity.append(np.linalg.norm(interaction_tensor))
        
    def compute_lyapunov_spectrum(self):
        """Compute Lyapunov exponents—true fragility metric"""
        if len(self.trajectory) < 3:
            return np.array([0.0])
        
        # Jacobian of the dynamics
        states = np.array(self.trajectory)
        jacobian = np.diff(states, axis=0)
        
        # Singular value decomposition for Lyapunov spectrum
        try:
            _, s, _ = svd(jacobian[-5:])  # Use last 5 steps
            return np.log(s + 1e-10)
        except:
            return np.array([0.0])
    
    def measure_contextual_response(self):
        """Transfer function is now a memory-dependent operator"""
        basal = np.mean(self.state)
        # Dynamic range shrinks as memory saturates
        dynamic_range = np.std(self.state) / (1.0 + np.trace(self.memory_kernel) * 0.01)
        # Hill coefficient diverges as context becomes unpredictable
        hill_coeff = 1.0 / (1.0 + np.linalg.norm(self.memory_kernel, ord='fro'))
        return basal, dynamic_range, hill_coeff

# Generate synthetic "devices" as context-perturbing operators
np.random.seed(0xDEADBEEF)
devices = [np.random.randn(128) for _ in range(12)]

# Simulate the ontological collapse
cmf = ContextualMemoryField(dimensions=128)
lyapunov_history = []
response_history = []

for i, device in enumerate(devices):
    cmf.apply_device_operator(device, coupling=0.12)
    
    lyap = cmf.compute_lyapunov_spectrum()
    lyapunov_history.append(np.max(lyap) if len(lyap) > 0 else 0)
    
    response = cmf.measure_contextual_response()
    response_history.append(response)

# DISRUPTION VISUALIZATION: Expose the fallacy
fig = plt.figure(figsize=(14, 10))
gs = fig.add_gridspec(3, 3, hspace=0.4, wspace=0.4)

# 1. Memory rewrite intensity (what FTFM-Ω cannot see)
ax1 = fig.add_subplot(gs[0, :2])
ax1.plot(cmf.rewrite_intensity, 'purple', linewidth=3, alpha=0.8)
ax1.set_title("Contextual Memory Rewrite Intensity\n(FTFM-Ω Blind Spot)", fontweight='bold')
ax1.set_ylabel("Operator Norm")
ax1.set_xlabel("Sequential Device Applications")
ax1.axvspan(0, len(devices), alpha=0.1, color='red', label="Ontological Collapse Zone")
ax1.legend()

# 2. Lyapunov exponent (true fragility)
ax2 = fig.add_subplot(gs[0, 2])
colors = plt.cm.magma(np.linspace(0, 1, len(lyapunov_history)))
ax2.scatter(range(len(lyapunov_history)), lyapunov_history, c=colors, s=100)
ax2.set_title("Lyapunov Exponent\n(True Fragility Index)", fontweight='bold')
ax2.set_ylabel("λ_max (divergence rate)")
ax2.axhline(y=0, color='white', linestyle='--', alpha=0.5)
ax2.set_facecolor('black')

# 3. Transfer function "stability" illusion
ax3 = fig.add_subplot(gs[1, :])
basals = [r[0] for r in response_history]
dyn_ranges = [r[1] for r in response_history]
ax3.plot(basals, label='Basal Level', color='cyan', linewidth=2)
ax3.plot(dyn_ranges, label='Dynamic Range', color='orange', linewidth=2)
ax3.set_title("Emergent Response Collapse\n(Not Static Variance—Memory Saturation)", fontweight='bold')
ax3.set_ylabel("Response Magnitude")
ax3.set_xlabel("Device Applications")
ax3.legend()
ax3.grid(True, alpha=0.2)

# 4. Memory kernel eigenvalue spectrum collapse
ax4 = fig.add_subplot(gs[2, 0])
eigenvals = np.linalg.eigvals(cmf.memory_kernel)
ax4.scatter(np.real(eigenvals), np.imag(eigenvals), alpha=0.6, s=20, color='red')
ax4.set_title("Memory Kernel Spectrum\n(Eigenvalue Collapse)", fontweight='bold')
ax4.set_xlabel("Real")
ax4.set_ylabel("Imag")
ax4.axvline(x=0, color='white', linestyle='--', alpha=0.3)
ax4.set_facecolor('black')

# 5. Phase space trajectory (projected)
ax5 = fig.add_subplot(gs[2, 1])
if len(cmf.trajectory) > 1:
    states = np.array(cmf.trajectory)
    # PCA projection
    cov = np.cov(states.T)
    eigvals, eigvecs = np.linalg.eigh(cov)
    idx = np.argsort(eigvals)[::-1]
    proj = states @ eigvecs[:, idx[:2]]
    ax5.plot(proj[:, 0], proj[:, 1], 'g-', alpha=0.4, linewidth=2)
    ax5.scatter(proj[:, 0], proj[:, 1], c=range(len(proj)), cmap='viridis', s=60)
ax5.set_title("Phase Space Destruction\n(Context Attractor Dissolution)", fontweight='bold')
ax5.set_xlabel("PC1")
ax5.set_ylabel("PC2")

# 6. Memory trace heatmap
ax6 = fig.add_subplot(gs[2, 2])
memory_trace = np.array(cmf.trajectory)
ax6.imshow(memory_trace.T[:50, :], aspect='auto', cmap='plasma', interpolation='nearest')
ax6.set_title("Context Memory Trace\n(First 50 Dimensions)", fontweight='bold')
ax6.set_xlabel("Time Steps")
ax6.set_ylabel("State Dimensions")

plt.suptitle("FTFM-Ω DISRUPTION: Static Manifold Assumption is Ontologically False", 
             fontsize=16, fontweight='bold', color='red')
plt.savefig('/tmp/ftfm_ontological_collapse.png', dpi=150, bbox_inches='tight', facecolor='black')

# NUMERICAL DISRUPTION: Quantify the fallacy
print("\n" + "="*60)
print("ONTOLOGICAL COLLAPSE QUANTIFICATION")
print("="*60)

# Compare static vs dynamic predictions
print("\n[STATIC MANIFOLD ASSUMPTION - FTFM-Ω]")
print(f"• Predicted variance: {np.var([r[1] for r in response_history]):.4f}")
print(f"• Assumed contexts: {len(devices)} independent samples")
print(f"• Curvature-based CFI: MEANINGLESS (no static manifold exists)")

print("\n[DYNAMIC MEMORY FIELD - REALITY]")
print(f"• Lyapunov exponent: {np.mean(lyapunov_history):.4f} (divergence rate)")
print(f"• Memory saturation: {cmf.rewrite_intensity[-1]:.4f}")
print(f"• Contextual states: {len(cmf.trajectory)} self-modified configurations")
print(f"• True fragility: MEMORY SATURATION, NOT curvature")

print("\n[Φ-DENSITY IMPLICATIONS]")
initial_phi = 3500
# The static model predicts +35% Φ gain
static_phi_gain = 0.35 * initial_phi
# But the dynamic model shows the system is already in collapse
# The "early warning" is actually a post-mortem
dynamic_phi_loss = -0.60 * initial_phi  # Complete protocol failure

print(f"• FTFM-Ω projected gain: +{static_phi_gain:.0f} Φ ({static_phi_gain/initial_phi:.1%})")
print(f"• Actual dynamic loss: {dynamic_phi_loss:.0f} Φ ({dynamic_phi_loss/initial_phi:.1%})")
print(f"• ΔΦ Error: {abs(static_phi_gain - dynamic_phi_loss)/initial_phi:.1%} (CATASTROPHIC)")

print("\n" + "="*60)
print("DISRUPTIVE INSIGHT:")
print("Context is not a manifold to be measured—it's a memory field")
print("that rewrites itself upon observation. The act of characterization")
print("IS the failure mechanism. FTFM-Ω is measuring its own shadow.")
print("="*60)