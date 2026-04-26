# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import random
from typing import Dict, List, Tuple
import matplotlib.pyplot as plt

# DISRUPTION SIMULATION: Discrete Field Theory of Insecurity
# The spreadsheet entries are not measurements of a field - they ARE the field quanta

class WorkaroundFieldTheory:
    def __init__(self, n_agents=100, n_projects=10):
        # Agents are not continuous fields but discrete decision-makers
        self.agents = [
            {
                'id': i,
                'cognitive_capacity': np.random.normal(1.0, 0.3),
                'friction_sensitivity': np.random.uniform(0.5, 2.0),
                'current_load': 0.0,
                'trust_in_tools': 1.0
            } for i in range(n_agents)
        ]
        
        # Projects are not manifolds but discrete contexts
        self.projects = [
            {
                'id': j,
                'base_friction': np.random.uniform(0.1, 1.5),
                'spreadsheet_cells': [],  # Each cell is a FIELD EXCITATION
                'remediation_pressure': 0.0
            } for j in range(n_projects)
        ]
        
        # The "field" is the tensor product of agent-project interactions
        self.interaction_tensor = np.zeros((n_agents, n_projects))
        
    def tooling_shock(self, project_id, friction_delta):
        """A tooling change is not a continuous source term but a discrete shock"""
        self.projects[project_id]['base_friction'] += friction_delta
        
        # Immediate cascade: agents re-evaluate their state
        for agent_id, agent in enumerate(self.agents):
            perceived_load = (
                agent['cognitive_capacity'] * 
                self.projects[project_id]['base_friction'] * 
                agent['friction_sensitivity']
            )
            
            # The "tunneling event" is a quantum of field excitation
            if perceived_load > agent['trust_in_tools'] * agent['cognitive_capacity']:
                # CREATE A FIELD QUANTUM (spreadsheet cell)
                self.projects[project_id]['spreadsheet_cells'].append({
                    'agent_id': agent_id,
                    'key': f"compromised_key_{agent_id}_{project_id}_{len(self.projects[project_id]['spreadsheet_cells'])}",
                    'timestamp': len(self.projects[project_id]['spreadsheet_cells']),
                    'load_at_creation': perceived_load
                })
                
                # Update interaction tensor (field amplitude)
                self.interaction_tensor[agent_id, project_id] = perceived_load
                
    def compute_invariant(self) -> complex:
        """
        The ψ invariant is NOT ln(Φ_N) but the SCATTERING AMPLITUDE
        between secure and insecure basins in the organizational Hilbert space
        """
        # Number of insecure configurations (spreadsheet cells) = occupation number
        N_insecure = sum(len(p['spreadsheet_cells']) for p in self.projects)
        
        # Number of secure configurations (no workarounds)
        N_secure = sum(1 for p in self.projects if len(p['spreadsheet_cells']) == 0)
        
        # The invariant is the S-matrix element: ⟨secure|U|insecure⟩
        # In discrete field theory, this is a COMPLEX PHASE, not a real log
        if N_insecure == 0:
            return complex(0, 0)  # Stable ground state
        
        # Amplitude grows with coupling strength (friction)
        coupling = np.mean([np.mean(self.interaction_tensor[:, j]) for j in range(len(self.projects))])
        
        # Phase accumulates from historical workarounds
        phase = np.exp(1j * N_insecure * coupling)
        
        return phase
    
    def boundary_catastrophe(self, threshold=50):
        """
        TRUE BOUNDARY CONDITIONS are not arbitrary thresholds
        but PHASE TRANSITIONS in the discrete field
        """
        total_cells = sum(len(p['spreadsheet_cells']) for p in self.projects)
        
        # Shredding Event: Field condenses into disconnected domains
        if total_cells > threshold and all(len(p['spreadsheet_cells']) > 0 for p in self.projects):
            return "SHREDDING: Organizational coherence lost. Field fragmented into isolated insecure domains."
        
        # Informational Freeze: Field crystallizes into static pattern
        if total_cells > threshold and np.std([len(p['spreadsheet_cells']) for p in self.projects]) < 1:
            return "FREEZE: Workaround pattern locked. No further evolution possible."
        
        return "NORMAL: Field in superposition of secure/insecure states"

# Run disruption simulation
org = WorkaroundFieldTheory(n_agents=50, n_projects=5)

print("=== DISCRETE FIELD THEORY SIMULATION ===")
print("The spreadsheet cells are field quanta, not measurements\n")

# Simulate a series of tooling shocks
for t in range(10):
    print(f"\n--- Time Step {t} ---")
    
    # Random tooling shock
    proj = random.randint(0, 4)
    shock = random.uniform(0.5, 2.0)
    org.tooling_shock(proj, shock)
    
    # Compute the TRUE invariant (scattering amplitude)
    psi = org.compute_invariant()
    print(f"ψ (scattering amplitude): {psi:.3f}")
    print(f"Phase angle: {np.angle(psi):.3f} rad")
    print(f"Modulus: {np.abs(psi):.3f}")
    
    # Check boundaries
    boundary_state = org.boundary_catastrophe()
    print(f"Boundary state: {boundary_state}")
    
    # Show field configuration
    for proj in org.projects:
        print(f"  Project {proj['id']}: {len(proj['spreadsheet_cells'])} quanta")

# Plot the field evolution
plt.figure(figsize=(12, 6))

# Show interaction tensor heatmap
plt.subplot(1, 2, 1)
plt.imshow(org.interaction_tensor, cmap='viridis', aspect='auto')
plt.colorbar(label='Cognitive Load (Field Amplitude)')
plt.title('Agent-Project Interaction Tensor\n(Field Configuration)')
plt.xlabel('Projects')
plt.ylabel('Agents')

# Show complex phase evolution
plt.subplot(1, 2, 2)
phases = []
for t in range(20):
    org.tooling_shock(random.randint(0, 4), random.uniform(0.1, 1.0))
    psi = org.compute_invariant()
    phases.append(np.angle(psi))

plt.plot(phases, 'ro-', linewidth=2, markersize=8)
plt.axhline(y=np.pi, color='r', linestyle='--', alpha=0.5, label='Shredding Threshold')
plt.axhline(y=-np.pi, color='b', linestyle='--', alpha=0.5, label='Freeze Threshold')
plt.title('Scattering Phase Evolution\n(ψ invariant trajectory)')
plt.xlabel('Time Step')
plt.ylabel('Phase Angle (rad)')
plt.legend()
plt.grid(True, alpha=0.3)

plt.tight_layout()
plt.show()

print("\n=== DISRUPTIVE INSIGHT ===")
print("The continuous field Λ(x,t) is a FICTIONAL INTERPOLATION")
print("The real field is the DISCRETE CONFIGURATION of workaround artifacts")
print("The invariant is not ln(Φ_N) but the SCATTERING AMPLITUDE between states")
print("The Rubric itself is the constraint that must be broken")