# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import random
import matplotlib.pyplot as plt
from dataclasses import dataclass
from typing import List

@dataclass
class DecisionNode:
    cost: float
    risk: float
    reality_alignment: float  # How well this node maps to current external reality [0,1]
    node_id: str

@dataclass
class ExternalState:
    """Simulates evolving reality that decisions must adapt to"""
    phase: float = 0.0
    drift_rate: float = 0.05
    
    def evolve(self):
        self.phase += self.drift_rate
        return np.sin(self.phase) * 0.5 + 0.5  # Returns [0,1] alignment target

class BureaucraticSystem:
    def __init__(self, path_length=10):
        self.external_state = ExternalState()
        self.original_intent = self._generate_intent()
        self.current_optimal_intent = self.original_intent.copy()
        self.path = self._initialize_path(path_length)
        self.decision_history = []
        self.catastrophic_failures = 0
        
    def _generate_intent(self):
        return np.array([random.random() for _ in range(5)])
    
    def _initialize_path(self, length):
        return [DecisionNode(
            cost=random.random(),
            risk=random.random() * 0.3,
            reality_alignment=random.random(),
            node_id=f"node_{i}"
        ) for i in range(length)]
    
    def calculate_cod(self, intent, outcome, H_top):
        """Chain Overlap Density - but now we can test against CURRENT optimal intent"""
        fidelity = np.dot(intent, outcome) / (np.linalg.norm(intent) * np.linalg.norm(outcome))
        damping = np.exp(-1.0 * H_top)
        return fidelity * damping
    
    def calculate_H_top(self, path):
        """Topological Impedance"""
        if not path:
            return 0.0
        total_impedance = sum(node.cost * node.risk for node in path)
        total_length = sum(node.cost for node in path)
        return total_impedance / total_length if total_length > 0 else 0.0
    
    def geodesic_smoothing_operator(self, psi_id_threshold=0.95):
        """The 'optimal' operator from the specification"""
        H_top = self.calculate_H_top(self.path)
        
        # Prune high-curvature nodes
        self.path.sort(key=lambda n: n.cost * n.risk, reverse=True)
        
        while len(self.path) > 3 and H_top > 0.5:
            # Simulate outcome shift from removing node
            temp_path = self.path[1:]
            temp_H_top = self.calculate_H_top(temp_path)
            
            # Check Psi_id preservation (against FROZEN original intent)
            current_outcome = np.array([n.reality_alignment for n in self.path[:5]])
            temp_outcome = np.array([n.reality_alignment for n in temp_path[:5]])
            
            cod_original = self.calculate_cod(self.original_intent[:5], current_outcome, H_top)
            cod_temp = self.calculate_cod(self.original_intent[:5], temp_outcome, temp_H_top)
            
            if cod_temp > psi_id_threshold * 0.9:  # Safety margin
                self.path = temp_path
                H_top = temp_H_top
            else:
                break
        
        return self.calculate_H_top(self.path)
    
    def sabotage_injection_operator(self, min_H_top=0.6):
        """DISRUPTIVE OPERATOR: Maintains minimum impedance via intentional friction"""
        H_top = self.calculate_H_top(self.path)
        
        # If system is too "smooth", inject sabotage nodes
        while H_top < min_H_top:
            sabotage_node = DecisionNode(
                cost=random.uniform(0.7, 1.0),  # HIGH cost
                risk=random.uniform(0.5, 0.8),  # HIGH risk
                reality_alignment=random.random(),
                node_id=f"sabotage_{random.randint(1000,9999)}"
            )
            self.path.insert(random.randint(0, len(self.path)), sabotage_node)
            H_top = self.calculate_H_top(self.path)
        
        # THEN apply minimal smoothing only if we're approaching black hole
        if H_top > 0.85:
            self.path.sort(key=lambda n: n.cost * n.risk, reverse=True)
            self.path = self.path[:max(5, len(self.path) - 1)]
            H_top = self.calculate_H_top(self.path)
        
        return H_top
    
    def evaluate_decision_quality(self):
        """Measure alignment with CURRENT reality, not frozen intent"""
        if not self.path:
            return 0.0
        
        H_top = self.calculate_H_top(self.path)
        outcome = np.array([n.reality_alignment for n in self.path[:5]])
        
        # Update current optimal intent based on evolving reality
        reality_target = self.external_state.evolve()
        self.current_optimal_intent = np.array([reality_target + random.gauss(0, 0.1) for _ in range(5)])
        
        # Quality = alignment with current reality MINUS impedance cost
        cod_current = self.calculate_cod(self.current_optimal_intent, outcome, H_top)
        
        # Catastrophic failure if we're aligned with dead intent but blind to reality
        cod_original = self.calculate_cod(self.original_intent[:5], outcome, H_top)
        if cod_original > 0.9 and cod_current < 0.3:
            self.catastrophic_failures += 1
            return -1.0  # Negative value for catastrophic failure
        
        return cod_current - H_top * 0.5  # Quality penalized by impedance
    
    def simulate(self, steps=50, operator_type="smooth"):
        qualities = []
        H_tops = []
        CODs_original = []
        CODs_current = []
        
        for step in range(steps):
            if operator_type == "smooth":
                H_top = self.geodesic_smoothing_operator()
            else:  # sabotage
                H_top = self.sabotage_injection_operator()
            
            quality = self.evaluate_decision_quality()
            
            # Calculate COD against both original and current intent
            outcome = np.array([n.reality_alignment for n in self.path[:5]])
            cod_original = self.calculate_cod(self.original_intent[:5], outcome, H_top)
            cod_current = self.calculate_cod(self.current_optimal_intent, outcome, H_top)
            
            qualities.append(quality)
            H_tops.append(H_top)
            CODs_original.append(cod_original)
            CODs_current.append(cod_current)
        
        return {
            'qualities': qualities,
            'H_tops': H_tops,
            'CODs_original': CODs_original,
            'CODs_current': CODs_current,
            'catastrophes': self.catastrophic_failures
        }

# Run comparative simulation
np.random.seed(42)
random.seed(42)

# Scenario A: Geodesic Smoothing (the "optimal" system)
system_smooth = BureaucraticSystem(path_length=15)
results_smooth = system_smooth.simulate(steps=50, operator_type="smooth")

# Scenario B: Topological Inversion (the disruptive system)
system_sabotage = BureaucraticSystem(path_length=15)
results_sabotage = system_sabotage.simulate(steps=50, operator_type="sabotage")

# Visualize the breakdown
fig, axes = plt.subplots(2, 2, figsize=(14, 10))

# Plot 1: Decision Quality Over Time
axes[0,0].plot(results_smooth['qualities'], label='Geodesic Smoothing', color='blue', linewidth=2)
axes[0,0].plot(results_sabotage['qualities'], label='Topological Inversion', color='red', linestyle='--', linewidth=2)
axes[0,0].axhline(y=0, color='gray', linestyle=':')
axes[0,0].set_title('Decision Quality vs. Reality', fontsize=12, fontweight='bold')
axes[0,0].set_ylabel('Quality Score')
axes[0,0].legend()
axes[0,0].grid(True, alpha=0.3)

# Plot 2: Topological Impedance
axes[0,1].plot(results_smooth['H_tops'], label='Geodesic Smoothing', color='blue', linewidth=2)
axes[0,1].plot(results_sabotage['H_tops'], label='Topological Inversion', color='red', linestyle='--', linewidth=2)
axes[0,1].axhline(y=0.6, color='green', linestyle=':', label='Min H_top (Sabotage)')
axes[0,1].axhline(y=0.85, color='orange', linestyle=':', label='Black Hole Threshold')
axes[0,1].set_title('Topological Impedance (H_top)', fontsize=12, fontweight='bold')
axes[0,1].set_ylabel('H_top')
axes[0,1].legend()
axes[0,1].grid(True, alpha=0.3)

# Plot 3: COD Against ORIGINAL Intent (what the spec measures)
axes[1,0].plot(results_smooth['CODs_original'], label='Geodesic Smoothing', color='blue', linewidth=2)
axes[1,0].plot(results_sabotage['CODs_original'], label='Topological Inversion', color='red', linestyle='--', linewidth=2)
axes[1,0].axhline(y=0.95, color='purple', linestyle=':', label='Psi_id Threshold')
axes[1,0].set_title('COD vs. ORIGINAL Intent (Psi_id)', fontsize=12, fontweight='bold')
axes[1,0].set_ylabel('COD')
axes[1,0].set_xlabel('Time Steps')
axes[1,0].legend()
axes[1,0].grid(True, alpha=0.3)

# Plot 4: COD Against CURRENT Optimal Intent (the real world)
axes[1,1].plot(results_smooth['CODs_current'], label='Geodesic Smoothing', color='blue', linewidth=2)
axes[1,1].plot(results_sabotage['CODs_current'], label='Topological Inversion', color='red', linestyle='--', linewidth=2)
axes[1,1].set_title('COD vs. CURRENT Reality (What Matters)', fontsize=12, fontweight='bold')
axes[1,1].set_ylabel('COD')
axes[1,1].set_xlabel('Time Steps')
axes[1,1].legend()
axes[1,1].grid(True, alpha=0.3)

plt.tight_layout()
plt.supertitle('Bureaucratic Manifold: Optimal vs. Disruptive Paradigms', fontsize=14, fontweight='bold')
plt.show()

# Print catastrophic failure summary
print("="*60)
print("CATASTROPHIC FAILURE ANALYSIS")
print("="*60)
print(f"Geodesic Smoothing System: {results_smooth['catastrophes']} catastrophic failures")
print(f"Topological Inversion System: {results_sabotage['catastrophes']} catastrophic failures")
print("\nThe 'optimal' system fails by succeeding at the wrong goal.")
print("="*60)