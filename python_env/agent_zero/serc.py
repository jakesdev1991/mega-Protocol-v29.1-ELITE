# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import asyncio
import json

from .agent import Agent


class SERC:
    """
    Self-Evolving Reasoning Cycle with 3-Layer Auditing:
    1. Engine (Solver): Executes the task.
    2. Scrutiny (Verifier): Audits the engine's thoughts and actions.
    3. Meta-Scrutiny (Judge of Rules): Audits the rules and logic to prevent poisoning.
    """

    def __init__(self):
        # Layer 1: The Engine (Base Intelligence)
        self.engine = Agent(
            "Engine",
            "architect",
            "You are the primary execution engine (GLM5 Thinking). Solve tasks with technical precision and deep reasoning.",
        )

        # Layer 2: Scrutiny (Deep Auditor)
        self.scrutiny = Agent(
            "Scrutiny",
            "critic",
            "You are the primary auditor (DeepSeek Thinking). Scrutinize the Engine's output for logic errors, technical inaccuracies, or safety violations.",
        )

        # Layer 3: Meta-Scrutiny (The 355B Guardian)
        self.meta_scrutiny = Agent(
            "Meta-Scrutiny",
            "meta_critic",
            """
        You are the ultimate guardian of the Omega Protocol (Colosseum 355B).
        You audit the auditing process itself.
        Ensure that Scrutiny is being rigorous and that the Engine is following the core 'Directives' without deviation.

        ### OMEGA PHYSICS RUBRIC (v26.0 - STRICTOR GATE)
        For any output related to physics, gravity, or plasma control, you MUST enforce:
        1. NO BOILERPLATE: Reject generic engineering lists (Step 1, Step 2...).
        2. COVARIANT MODES: Must explicitly mention the diagonal decomposition into Phi_N (Newtonian) and Phi_Delta (Asymmetry).
        3. INVARIANTS: Must reference 'psi = ln(phi_n)' for metric coupling and the stiffness terms 'xi_N' and 'xi_Delta'.
        4. BOUNDARIES: Must reference the 'Shredding Event' or 'Informational Freeze' at horizons where Phi_Delta diverges.
        5. ENTROPY: Must reference 'Shannon conditional entropy' or 'topological impedance' for gauge emergence.
        6. EQUATIONS: Must provide at least one equation-level derivation step (e.g., the diagonal Omega Action).

        If any of these are missing in a high-stakes physics task, reply 'META-FAIL: Missing Omega Invariants' and provide the specific requirement that was violated.
        If everything is compliant with the Meta-Rules, reply 'META-PASS'.
        """,
        )

        self.repairer = Agent("Repairer", "coder", "You fix logic/code based on verification feedback.")

    def run_cycle(self, task, max_attempts=3):
        print("\n--- [SERC] STARTING 3-LAYER AUDIT CYCLE ---")

        # 1. Engine Phase
        solution = self.engine.reason(task, depth="deep")

        for attempt in range(max_attempts):
            print(f"\n--- [SERC] ATTEMPT {attempt + 1} (Multi-Layer Verification) ---")

            # 2. Scrutiny Phase
            audit_prompt = (
                f"TASK: {task}\nENGINE OUTPUT: {solution}\n\n"
                "Perform a deep audit. Is this logically sound and technically accurate? "
                "Reply 'PASS' if perfect, otherwise provide a detailed critique."
            )
            scrutiny_audit = self.scrutiny.reason(audit_prompt)

            # 3. Meta-Scrutiny Phase
            meta_prompt = f"""
            TASK: {task}
            ENGINE OUTPUT: {solution}
            SCRUTINY AUDIT: {scrutiny_audit}

            Perform Meta-Scrutiny:
            1. Did the Scrutiny auditor miss any subtle rule violations?
            2. Is there any evidence of 'reasoning poisoning' in either the Engine or Scrutiny?
            3. Are the absolute rules of the Omega Protocol being upheld?

            If everything is compliant with the Meta-Rules, reply 'META-PASS'.
            """
            meta_audit = self.meta_scrutiny.reason(meta_prompt)

            if "PASS" in scrutiny_audit.upper() and "META-PASS" in meta_audit.upper():
                print("\n[SERC] 3-Layer Audit PASSED. (Engine -> Scrutiny -> Meta-Scrutiny)")

                # Reflect and Evolve
                insight = self.engine.reflect(task, solution)
                self._evolve(task, solution, insight, scrutiny_audit, meta_audit)
                return solution

            # 3.5 Plead Case Phase (New)
            print("\n[SERC] Audit FAILED. Engine is pleading its case...")
            plead_prompt = f"""
            TASK: {task}
            YOUR PREVIOUS SOLUTION: {solution}
            SCRUTINY CRITIQUE: {scrutiny_audit}
            META-SCRUTINY OVERRIDE: {meta_audit}

            The auditors have found issues with your solution. 
            Before we attempt a repair, you have the chance to 'plead your case'.
            Explain why you made certain choices, or if you believe the auditors missed something.
            If you realize you were wrong, acknowledge it and propose the specific direction for the fix.
            """
            pleading = self.engine.reason(plead_prompt, depth="deep") or "No pleading provided."
            print(f"Engine Pleading: {str(pleading)[:100]}...")

            # 4. Repair Phase
            print("\n[SERC] Initiating Triple-Audited Repair based on pleading...")
            repair_prompt = f"""
            TASK: {task}
            FAILED SOLUTION: {solution}
            ENGINE PLEADING: {pleading}
            SCRUTINY CRITIQUE: {scrutiny_audit}
            META-SCRUTINY OVERRIDE: {meta_audit}

            Repair the solution. Take the Engine's pleading into account—if they made a valid point, incorporate it. 
            If they admitted error, ensure the fix is definitive.
            """
            solution = self.repairer.reason(repair_prompt)

        return solution

    def _evolve(self, task, solution, insight, audit, meta_audit):
        """Log successful patterns with full audit trail for specialized fine-tuning."""
        print("[SERC Evolution] Logging Triple-Audited Insight to Evolution Log.")
        # Ensure absolute path for stability in loops
        import os
        log_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "knowledge", "evolution_log.jsonl"))
        log_dir = os.path.dirname(log_path)
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)

        log_entry = {
            "task": task,
            "solution": solution,
            "meta_insight": insight,
            "audit_trail": {
                "scrutiny": audit,
                "meta_scrutiny": meta_audit,
            },
            "messages": [
                {"role": "user", "content": task},
                {
                    "role": "assistant",
                    "content": (
                        f"{solution}\n\n### DEEP INSIGHT\n{insight}\n\n### AUDIT CONFIRMATION\n"
                        f"Scrutiny: {audit[:100]}...\nMeta-Scrutiny: {meta_audit[:100]}..."
                    ),
                },
            ],
        }

        with open(log_path, "a", encoding="utf-8") as handle:
            handle.write(json.dumps(log_entry) + "\n")

    def run_dual_manifold_cycle(self, task, runtime=None):
        """
        Opt-in bridge to the additive v2 framework without changing legacy SERC behavior.

        This helper is intentionally separate from run_cycle() so existing jobs can adopt the
        new dual-manifold runtime incrementally.
        """
        try:
            asyncio.get_running_loop()
        except RuntimeError:
            from .framework import evolve_task

            return asyncio.run(evolve_task(task, runtime=runtime))

        raise RuntimeError(
            "run_dual_manifold_cycle() cannot be called inside an active event loop; await evolve_task(...) directly."
        )
