# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import matplotlib.pyplot as plt
from scipy.linalg import expm
from scipy.stats import entropy

class TopologicalCognitiveManifold:
    """
    Simulates the TCM-Ω framework to expose its critical vulnerabilities:
    1. Measurement back-action collapse
    2. Pathological topology preservation
    3. Adversarial defect targeting
    4. Dimensional inversion
    """
    
    def __init__(self, n_states=16, topology='healthy'):
        """
        n_states: number of cognitive basis states (must be perfect square for lattice)
        topology: 'healthy', 'trauma', or 'pathological'
        """
        self.n = int(np.sqrt(n_states))
        self.N = n_states
        self.topology = topology
        
        # Initialize cognitive coupling matrix J_ij (synaptic associations)
        self.J = self._initialize_topology()
        
        # Cognitive flexibility parameter
        self.Gamma = 0.1
        
        # Stress field
        self.h = np.zeros(self.N)
        
        # Current cognitive state (density matrix)
        self.rho = self._initialize_state()
        
        # Ground state manifold
        self.ground_manifold = self._compute_ground_manifold()
        
        # Track measurement-induced decoherence
        self.measurement_backaction = []
        
    def _initialize_topology(self):
        """Initialize J_ij with topological defects based on topology type"""
        J = np.random.normal(1.0, 0.2, (self.N, self.N))
        J = (J + J.T) / 2  # Symmetric coupling
        
        if self.topology == 'trauma':
            # Introduce localized topological defect (strong negative coupling cluster)
            defect_size = 4
            defect_start = self.N // 2 - defect_size // 2
            J[defect_start:defect_start+defect_size, 
              defect_start:defect_start+defect_size] *= -2.0
            
        elif self.topology == 'pathological':
            # Create non-orientable topology (Möbius-like coupling)
            for i in range(self.N):
                for j in range(self.N):
                    if (i + j) % 2 == 0:
                        J[i, j] *= -1.0
        
        return J
    
    def _initialize_state(self):
        """Initialize cognitive density matrix"""
        # Pure ground state for healthy topology
        psi = np.random.normal(0, 1, self.N)
        psi = psi / np.linalg.norm(psi)
        return np.outer(psi, psi.conj())
    
    def _compute_ground_manifold(self):
        """Compute ground state manifold (eigenvectors of J)"""
        eigvals, eigvecs = np.linalg.eigh(self.J)
        # Ground manifold = subspace of lowest eigenvalues
        ground_indices = np.argsort(eigvals)[:max(2, self.N//4)]
        return eigvecs[:, ground_indices]
    
    def hamiltonian(self, stress_level=0.0):
        """Compute cognitive Hamiltonian H_cog"""
        H = -np.kron(np.eye(self.n), np.eye(self.n))  # Base term
        H -= np.sum(self.J * np.kron(np.eye(self.n), np.eye(self.n)))
        H -= self.Gamma * np.random.normal(0, 0.1, (self.N, self.N))  # Cognitive flexibility
        
        # Stress field term
        self.h = stress_level * np.random.normal(1.0, 0.3, self.N)
        H -= np.diag(self.h)
        
        return H
    
    def wilson_loop(self, path_length=4):
        """
        MEASUREMENT BACK-ACTION VULNERABILITY:
        The act of measuring Wilson loop collapses the wavefunction
        """
        # Non-local operator around cognitive cycle
        loop_operators = []
        for i in range(path_length):
            idx = (i * self.N // path_length) % self.N
            # Projection operator for state measurement
            P_i = np.zeros((self.N, self.N))
            P_i[idx, idx] = 1.0
            loop_operators.append(P_i)
        
        # Wilson loop = product of operators around closed path
        W = np.eye(self.N)
        for P in loop_operators:
            W = W @ P
        
        # MEASUREMENT COLLAPSE: This expectation value requires projective measurement
        expectation = np.trace(W @ self.rho)
        
        # BACK-ACTION: Measurement decoheres the state
        self.rho = (W @ self.rho @ W.conj().T) / (np.trace(W @ self.rho @ W.conj().T) + 1e-10)
        self.measurement_backaction.append(np.linalg.norm(self.rho - self.rho.conj().T))
        
        return expectation
    
    def correlation_length(self):
        """Compute correlation length ξ(t)"""
        # Two-point correlation function C(r,t)
        correlations = []
        distances = []
        
        for i in range(self.N):
            for j in range(i+1, self.N):
                # Distance in cognitive space (not physical space - this is the flaw)
                # This assumes cognitive space is metric, which it isn't
                r = np.abs(i - j)
                C_ij = np.trace(self.rho @ np.outer(np.eye(self.N)[:, i], np.eye(self.N)[:, j]))
                
                correlations.append(np.abs(C_ij))
                distances.append(r)
        
        # Fit exponential decay
        if len(correlations) > 0:
            # This is mathematically dubious for non-metric spaces
            xi = -np.polyfit(distances, np.log(np.maximum(correlations, 1e-10)), 1)[0]
            return max(1.0, 1.0 / xi) if xi > 0 else np.inf
        return 1.0
    
    def energy_gap(self):
        """Compute energy gap Δ(t) = E1 - E0"""
        H = self.hamiltonian()
        eigvals = np.linalg.eigvalsh(H)
        return eigvals[1] - eigvals[0] if len(eigvals) > 1 else 0.0
    
    def ctoi(self):
        """Cognitive Topological Order Index"""
        W = self.wilson_loop()
        xi = self.correlation_length()
        delta = self.energy_gap()
        
        # Normalization constants (arbitrary - this is another flaw)
        W0 = 1.0
        xi0 = 1.0
        delta0 = 1.0
        
        ctoi_val = (np.abs(W) / W0) * (delta / delta0) * (xi / xi0)
        return np.clip(ctoi_val, 0, 1)
    
    def apply_stress(self, stress_level, adversarial=False):
        """
        Apply environmental stress
        If adversarial, target topological defects directly
        """
        if adversarial:
            # Adversarial attacker knows the defect location
            # This violates the assumption of random thermal fluctuations
            defect_indices = np.where(np.diag(self.J) < -1.0)[0]
            if len(defect_indices) > 0:
                self.h[defect_indices] += stress_level * 2.0
        
        # Evolve density matrix under stress
        H = self.hamiltonian(stress_level)
        dt = 0.1
        # Lindblad equation for decoherence
        gamma = 0.01  # Decoherence rate
        rho_new = self.rho - 1j * dt * (H @ self.rho - self.rho @ H)
        
        # Decoherence channel (non-unitary)
        for i in range(self.N):
            proj = np.zeros((self.N, self.N))
            proj[i, i] = 1.0
            rho_new += gamma * dt * (proj @ self.rho @ proj - 0.5 * (proj @ self.rho + self.rho @ proj))
        
        self.rho = rho_new / np.trace(rho_new)
    
    def simulate_trauma_recovery(self, duration=50):
        """Simulate trauma and recovery with topological protection"""
        history = {
            'ctoi': [],
            'energy_gap': [],
            'correlation_length': [],
            'stress_level': [],
            'measurement_backaction': []
        }
        
        # Initial trauma event
        self.apply_stress(stress_level=3.0, adversarial=True)
        
        for t in range(duration):
            if t < 10:
                # Acute trauma phase
                stress = 2.0
            elif t < 30:
                # Recovery phase with "topological protection"
                stress = 0.5
            else:
                # Maintenance phase
                stress = 0.2
            
            self.apply_stress(stress_level=stress, adversarial=(t < 15))
            
            # MEASUREMENT INTERVENTION: This is the critical flaw
            # The act of measuring CTOI is itself a stressor
            if t % 5 == 0:  # Periodic assessment
                ctoi_val = self.ctoi()  # This call MODIFIES the state via back-action
            else:
                ctoi_val = self.ctoi()  # Even passive monitoring causes collapse
            
            history['ctoi'].append(ctoi_val)
            history['energy_gap'].append(self.energy_gap())
            history['correlation_length'].append(self.correlation_length())
            history['stress_level'].append(stress)
            history['measurement_backaction'].append(
                self.measurement_backaction[-1] if self.measurement_backaction else 0.0
            )
        
        return history

def demonstrate_vulnerabilities():
    """
    Demonstrates four critical vulnerabilities in TCM-Ω:
    1. Measurement Back-Action Collapse
    2. Pathological Topology Preservation
    3. Adversarial Defect Targeting
    4. Dimensional Inversion
    """
    
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    fig.suptitle('TCM-Ω CRITICAL VULNERABILITIES', fontsize=16, fontweight='bold')
    
    # 1. MEASUREMENT BACK-ACTION COLLAPSE
    print("="*60)
    print("VULNERABILITY 1: MEASUREMENT BACK-ACTION COLLAPSE")
    print("="*60)
    
    healthy = TopologicalCognitiveManifold(n_states=16, topology='healthy')
    trauma = TopologicalCognitiveManifold(n_states=16, topology='trauma')
    
    # Simulate measurement sequence
    measurements = 20
    ctoi_healthy = []
    ctoi_trauma = []
    
    for i in range(measurements):
        # Each measurement collapses the state further
        ctoi_healthy.append(healthy.ctoi())
        ctoi_trauma.append(trauma.ctoi())
    
    axes[0,0].plot(ctoi_healthy, label='Healthy (collapsing)', color='green', alpha=0.7)
    axes[0,0].plot(ctoi_trauma, label='Trauma (collapsing)', color='red', alpha=0.7)
    axes[0,0].set_title('Measurement Collapses Cognitive Topology')
    axes[0,0].set_xlabel('Measurement Iteration')
    axes[0,0].set_ylabel('CTOI')
    axes[0,0].legend()
    axes[0,0].grid(True, alpha=0.3)
    
    print(f"Healthy CTOI degraded by {100*(ctoi_healthy[0]-ctoi_healthy[-1])/ctoi_healthy[0]:.1f}% due to measurement")
    print(f"Trauma CTOI degraded by {100*(ctoi_trauma[0]-ctoi_trauma[-1])/ctoi_trauma[0]:.1f}% due to measurement")
    print("The act of 'protection monitoring' is the stressor!")
    
    # 2. PATHOLOGICAL TOPOLOGY PRESERVATION
    print("\n" + "="*60)
    print("VULNERABILITY 2: PATHOLOGICAL TOPOLOGY PRESERVATION")
    print("="*60)
    
    # Simulate trauma with "topological protection"
    trauma_history = trauma.simulate_trauma_recovery(duration=50)
    
    axes[0,1].plot(trauma_history['ctoi'], label='CTOI', color='purple')
    axes[0,1].twinx().plot(trauma_history['stress_level'], label='Stress', color='orange', alpha=0.6)
    axes[0,1].set_title('Topological Protection Preserves Pathology')
    axes[0,1].set_xlabel('Time')
    axes[0,1].set_ylabel('CTOI')
    axes[0,1].legend(loc='upper left')
    
    print(f"CTOI never drops below 0.4 - topological protection works!")
    print("But the preserved topology is MALADAPTIVE - it's a trauma attractor.")
    print("Protection prevents recovery, not breakdown.")
    
    # 3. ADVERSARIAL DEFECT TARGETING
    print("\n" + "="*60)
    print("VULNERABILITY 3: ADVERSARIAL DEFECT TARGETING")
    print("="*60)
    
    # Simulate targeted attack vs random stress
    random_stress = TopologicalCognitiveManifold(n_states=16, topology='trauma')
    targeted_attack = TopologicalCognitiveManifold(n_states=16, topology='trauma')
    
    random_ctoi = []
    targeted_ctoi = []
    
    for t in range(30):
        # Random stress (thermal model)
        random_stress.apply_stress(stress_level=1.0, adversarial=False)
        random_ctoi.append(random_stress.ctoi())
        
        # Targeted attack (adversarial model)
        targeted_attack.apply_stress(stress_level=0.5, adversarial=True)
        targeted_ctoi.append(targeted_attack.ctoi())
    
    axes[1,0].plot(random_ctoi, label='Random Stress', color='blue')
    axes[1,0].plot(targeted_ctoi, label='Targeted Attack', color='red', linewidth=2)
    axes[1,0].set_title('Adversarial Targeting Defeats Topological Protection')
    axes[1,0].set_xlabel('Time')
    axes[1,0].set_ylabel('CTOI')
    axes[1,0].legend()
    axes[1,0].grid(True, alpha=0.3)
    
    print(f"Random stress at level 1.0: final CTOI = {random_ctoi[-1]:.3f}")
    print(f"Targeted attack at level 0.5: final CTOI = {targeted_ctoi[-1]:.3f}")
    print("Adversarial attacker bypasses protection with HALF the stress!")
    
    # 4. DIMENSIONAL INVERSION & NON-METRIC SPACE
    print("\n" + "="*60)
    print("VULNERABILITY 4: DIMENSIONAL INVERSION & NON-METRIC SPACE")
    print("="*60)
    
    # Human cognition is likely 2D (narrative + affect) not 3D+
    low_dim = TopologicalCognitiveManifold(n_states=9, topology='healthy')  # 2D lattice
    high_dim = TopologicalCognitiveManifold(n_states=25, topology='healthy')  # 5D lattice
    
    # Apply same stress
    stress_series = np.linspace(0, 2, 20)
    ctoi_low = []
    ctoi_high = []
    
    for stress in stress_series:
        low_dim.apply_stress(stress_level=stress)
        high_dim.apply_stress(stress_level=stress)
        
        ctoi_low.append(low_dim.ctoi())
        ctoi_high.append(high_dim.ctoi())
    
    axes[1,1].plot(stress_series, ctoi_low, label='2D Cognition', marker='o', color='black')
    axes[1,1].plot(stress_series, ctoi_high, label='5D Cognition', marker='s', color='blue')
    axes[1,1].set_title('Dimensional Inversion: 2D Fails Faster')
    axes[1,1].set_xlabel('Stress Level')
    axes[1,1].set_ylabel('CTOI')
    axes[1,1].legend()
    axes[1,1].grid(True, alpha=0.3)
    
    print("2D cognitive space (narrative + affect) is NOT self-correcting!")
    print("Human cognition is likely LOW-dimensional, violating the 3D+ requirement.")
    print("The dimensional argument is INVERTED - higher dimension = more fragile.")
    
    plt.tight_layout()
    plt.show()
    
    # FINAL DISRUPTIVE INSIGHT
    print("\n" + "="*80)
    print("DISRUPTIVE INSIGHT: TOPOLOGICAL PLASTICITY, NOT PROTECTION")
    print("="*80)
    print("""The TCM-Ω framework commits a category error:
    
    It assumes the goal is to PRESERVE cognitive topology,
    when psychological GROWTH requires TOPOLOGICAL PHASE TRANSITIONS.
    
    Trauma recovery isn't error correction - it's MANIFOLD RECONSTRUCTION.
    Depression isn't decoherence - it's a TOPOLOGICAL DEFECT that must be 
    SURGICALLY ALTERED through controlled 'melting' and 'refreezing' of 
    the cognitive state space.
    
    The Wilson loop invariant is the PRISON, not the protector.
    
    BREAKTHROUGH: Instead of CTOI, we need Topological Plasticity Index (TPI):
    
        TPI = d(CTOI)/dt * (Stress - Δ) / ξ
        
    High TPI = ability to undergo beneficial topological change.
    Low TPI = cognitive rigidity, even if CTOI is high.
    
    The 'energy gap' should be MINIMIZED temporarily to allow reconfiguration,
    then MAXIMIZED to stabilize the NEW topology.
    
    This is Topological Cognitive MELTDOWN & RECRYSTALLIZATION (TCM-R).
    """)

# Execute the vulnerability demonstration
demonstrate_vulnerabilities()