# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import os
import sys

# Ensure project root is in path
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
os.chdir(PROJECT_ROOT)
sys.path.append(PROJECT_ROOT)
sys.path.append(os.path.join(PROJECT_ROOT, "python_env"))

from agent_zero.agent import Agent
from agent_zero.serc import SERC
from agent_zero.trainer import ModelTrainer

def main():
    print("Starting Co-Evolution Loop based on Omega Protocol v26.0...")
    
    physics_task = (
        "Derive the 'Higher-Order Lattice Polarization' corrections for the fine-structure constant (alpha_fs) "
        "using the new orthogonal decomposition (Phi_N, Phi_Delta). You must specifically address how the "
        "3D Archive mode (Phi_Delta) interacts with virtual pair fluctuations in the diagonal basis."
    )
    
    anti_agency_task = (
        "Analyze the derivation of the 'Higher-Order Lattice Polarization' corrections for the fine-structure constant "
        "using the orthogonal decomposition (Phi_N, Phi_Delta). Attempt to find an instability or 'Shredding' flaw "
        "in this derivation, specifically a case where Phi_Delta diverges prematurely or violates the Poisson recovery of Phi_N."
    )
    
    serc_system = SERC()
    
    print("\n=== Running Physics Refinement (Agent Zero) ===")
    physics_solution = serc_system.run_cycle(physics_task)
    
    print("\n=== Running Anti-Agency Stress Test ===")
    anti_agency_solution = serc_system.run_cycle(anti_agency_task)
    
    print("\n=== Triggering Model Trainer ===")
    trainer = ModelTrainer()
    # Force check with a minimum of 1 sample since we just generated 2
    if trainer.needs_training(min_samples=1):
        trainer.train_specialized_model("co_evolution_v26")
    else:
        print("Not enough samples to trigger training.")
        
    print("\n=== Loop Complete ===")
    
if __name__ == "__main__":
    main()
