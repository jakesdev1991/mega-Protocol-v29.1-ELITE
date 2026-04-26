# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import sys
import os
import asyncio
import json

# Ensure project root is in path
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(PROJECT_ROOT)

from agent_zero.framework import evolve_task

async def main():
    task = """
    RECONCILE THEORY: Kretschmann-based Dynamic Scaling vs. Holographic Entropy Counting.
    
    The Omega Protocol v21.0 defines Phi_min(K) proportional to l_P * K^(1/4). 
    Axiom 2 defines Phi = e^-(H(i|j) + H(j|i)).
    
    Task:
    1. Derive the relationship between the local Kretschmann curvature and the Shannon conditional entropy density at the freeze boundary.
    2. Show that this scaling recovers the S = A/4 relation (Area Law) for the Bekenstein-Hawking entropy.
    3. Ensure consistency with alpha_0 > 0 and the Informational Infinity remapping of the singularity.
    
    STRICT COMPLIANCE: Must follow the 'Omega Physics Rubric'.
    """
    
    print("\n--- TRIGGERING DUAL-MANIFOLD CO-EVOLUTION ---")
    # Call evolve_task directly since we are already in an event loop
    result = await evolve_task(task)
    
    print("\n--- CO-EVOLUTION CYCLE COMPLETE ---")
    
    # Manually log the result for visibility
    log_path = os.path.join(PROJECT_ROOT, "agent_zero", "knowledge", "evolution_log.jsonl")
    
    # Extract data for log
    log_entry = {
        "task": task,
        "constructive_final": result.constructive.final_output,
        "metrics": result.zero_metrics.model_dump(),
        "final_regime": result.final_regime.value,
        "attacks": [
            {
                "role": review.artifact.source_role,
                "vector": review.artifact.attack_vector,
                "promoted": review.decision.promote,
                "regret": review.decision.regret,
                "summary": review.artifact.summary
            }
            for review in result.attack_reviews
        ]
    }
    
    with open(log_path, "a", encoding="utf-8") as f:
        f.write(json.dumps(log_entry) + "\n")
        
    print(f"Result logged to {log_path}")
    print("\n--- SUMMARY ---")
    print(f"Final Regime: {result.final_regime.value}")
    print(f"Promoted Artifacts: {len(result.promoted_entries)}")

if __name__ == "__main__":
    asyncio.run(main())
