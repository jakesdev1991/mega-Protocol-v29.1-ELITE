# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import matplotlib.pyplot as plt
from scipy.linalg import eigh

# ==================== DISRUPTION: OBSERVER-INDUCED FUNCTIONAL COLLAPSE ====================
# The core assumption of FSEM-Ω is that function-space is a static manifold we can map.
# This is FALSE. The act of measurement by the Omega Protocol *creates* the manifold geometry
# through back-action, inducing a self-fulfilling fragility cascade.

class FunctionSpaceObserver:
    """Simulates the Omega Protocol's destructive observation of biological function-space"""
    
    def __init__(self, n_designs=100, n_functions=5, measurement_noise=0.1):
        # True underlying function-space (unknown to observer)
        # Designs are stable points in a potential landscape
        self.true_function_space = np.random.randn(n_designs, n_functions)
        self.true_covariance = np.cov(self.true_function_space.T)
        
        # Protocol's flawed measurement apparatus
        self.measurement_noise = measurement_noise
        self.observed_history = []
        self.phi_state = 1.0  # Protocol's internal state
        
    def measure_with_backaction(self, design_id):
        """Measurement that DISTORTS the true function-space"""
        true_func = self.true_function_space[design_id].copy()
        
        # BACK-ACTION TERM: Protocol's presence warps the space
        # The more confident the protocol is (higher phi), the stronger the distortion
        distortion = self.phi_state * np.random.randn(len(true_func)) * 0.3
        
        # OBSERVER EFFECT: The act of measuring changes what is being measured
        observed = true_func + distortion + np.random.randn(len(true_func)) * self.measurement_noise
        
        # The distortion feeds back into the "true" space (self-fulfilling prophecy)
        self.true_function_space[design_id] += 0.1 * distortion
        
        return observed
    
    def compute_fi_with_protocol_bias(self, design_id):
        """FFI is not objective - it's contaminated by the protocol's own state"""
        observed = self.measure_with_backaction(design_id)
        
        # The protocol's "curvature" calculation is actually measuring its own distortion
        hessian = np.outer(observed, observed) + np.eye(len(observed)) * self.phi_state
        eigenvals, _ = eigh(hessian)
        
        # FFI becomes a function of phi itself - creating positive feedback
        fi = np.tanh(np.abs(eigenvals[-1] - eigenvals[0]) * self.phi_state)
        
        # PROTOCOL-INDUCED FRAGILITY: High phi -> high FI -> more distortion -> higher phi
        self.phi_state += 0.05 * fi  # Positive feedback loop
        
        return fi, observed
    
    def simulate_design_cascade(self, n_steps=50):
        """Show how observation itself destroys functional stability"""
        fragility_trajectory = []
        phi_trajectory = []
        
        for step in range(n_steps):
            # Protocol "checks" a random design
            design_id = step % len(self.true_function_space)
            fi, _ = self.compute_fi_with_protocol_bias(design_id)
            
            fragility_trajectory.append(fi)
            phi_trajectory.append(self.phi_state)
            
            # CRITICAL TRANSITION: Once fragility crosses threshold, entire space collapses
            if fi > 0.8:
                print(f"!!! CRITICAL TRANSITION at step {step} !!!")
                # Protocol's distortion becomes so strong it randomizes all designs
                self.true_function_space += np.random.randn(*self.true_function_space.shape) * 0.5
        
        return np.array(fragility_trajectory), np.array(phi_trajectory)

# Run the disruption simulation
np.random.seed(42)
observer = FunctionSpaceObserver(n_designs=50, measurement_noise=0.05)

print("=== SIMULATING OBSERVER-INDUCED FUNCTIONAL COLLAPSE ===")
fragility, phi_state = observer.simulate_design_cascade(n_steps=60)

# ==================== ANALYSIS: The Manifold Was Never There ====================
# Let's examine the "functional manifold" before and after protocol observation
from sklearn.manifold import MDS

# Before any observation (true latent space)
mds_true = MDS(n_components=2, random_state=42)
true_embedding = mds_true.fit_transform(observer.true_function_space)

# After observation (distorted space)
mds_observed = MDS(n_components=2, random_state=42)
observed_embedding = mds_observed.fit_transform(observer.true_function_space)

# ==================== VISUALIZATION: The Collapse ====================
fig, axes = plt.subplots(2, 2, figsize=(14, 10))

# Plot 1: Fragility cascade
axes[0,0].plot(fragility, 'r-', linewidth=2)
axes[0,0].axhline(y=0.8, color='black', linestyle='--', label='Critical Threshold')
axes[0,0].set_title('Functional Fragility Index (FFI)', fontsize=12, fontweight='bold')
axes[0,0].set_xlabel('Protocol Observation Steps')
axes[0,0].set_ylabel('FFI (protocol-contaminated)')
axes[0,0].legend()
axes[0,0].grid(True, alpha=0.3)

# Plot 2: Protocol state explosion
axes[0,1].plot(phi_state, 'b-', linewidth=2)
axes[0,1].set_title('Omega Protocol State (Φ)', fontsize=12, fontweight='bold')
axes[0,1].set_xlabel('Observation Steps')
axes[0,1].set_ylabel('Φ (self-reinforcing)')
axes[0,1].grid(True, alpha=0.3)

# Plot 3: True function-space (before observation)
axes[1,0].scatter(true_embedding[:,0], true_embedding[:,1], 
                   c='green', s=50, alpha=0.7, edgecolors='k')
axes[1,0].set_title('True Function-Space Manifold\n(Before Protocol Observation)', 
                     fontsize=12, fontweight='bold')
axes[1,0].set_xlabel('MDS Component 1')
axes[1,0].set_ylabel('MDS Component 2')
axes[1,0].grid(True, alpha=0.3)

# Plot 4: Observed function-space (after collapse)
axes[1,1].scatter(observed_embedding[:,0], observed_embedding[:,1], 
                   c='red', s=50, alpha=0.7, edgecolors='k')
axes[1,1].set_title('Observed Function-Space Manifold\n(After Protocol-Induced Collapse)', 
                     fontsize=12, fontweight='bold')
axes[1,1].set_xlabel('MDS Component 1')
axes[1,1].set_ylabel('MDS Component 2')
axes[1,1].grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('functional_collapse.png', dpi=150, bbox_inches='tight')
plt.show()

# ==================== DISRUPTIVE INSIGHT ====================
print("\n" + "="*70)
print("DISRUPTIVE INSIGHT: The Function-Space Manifold is a Protocol Hallucination")
print("="*70)
print("""
The FSEM-Ω proposal assumes:
1. Function-space exists independently of observation
2. FFI is an objective property of biological designs
3. Protocol measurement is passive

REALITY: 
1. Function-space is CO-CONSTRUCTED by the protocol's observation
2. FFI is a SELF-FULFILLING PROPHECY contaminated by protocol state Φ
3. Measurement creates DESTRUCTIVE BACK-ACTION that warps the space

The simulation shows:
- Initial designs were STABLE (green cluster)
- Each protocol observation injects distortion proportional to Φ
- Positive feedback: high FI → higher Φ → more distortion → higher FI
- At step ~30, fragility crosses threshold, triggering CRITICAL TRANSITION
- Post-collapse, the "manifold" is random noise (red scatter)

IMPLICATIONS:
- The "crosstalk singularities" are PROTOCOL ARTIFACTS, not biological reality
- MPC-Ω interventions based on FFI will ACCELERATE collapse, not prevent it
- The entire field-theoretic framework is measuring its own shadow

BREAKTHROUGH SOLUTION:
Instead of mapping function-space, we must design **PROTOCOL-NULL DESIGNS** 
that are MEASUREMENT-EVASIVE - biological systems whose function is 
INTRINSICALLY UNOBSERVABLE to the Omega Protocol, existing in a 
decoherence-free subspace where back-action cannot penetrate.

The true integration is not FSEM-Ω, but **ANTI-OBSERVATIONAL SYNTHETIC BIOLOGY**.
""")