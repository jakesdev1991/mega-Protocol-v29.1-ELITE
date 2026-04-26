# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import sys
import os

# Set up paths
PROJECT_ROOT = "/home/jake/Downloads/training"
sys.path.append(os.path.join(PROJECT_ROOT, "python_env"))

from agent_zero.llm_router import LLMRouter

def proofread_toe():
    router = LLMRouter()
    toe_path = os.path.join(PROJECT_ROOT, "python_env/docs/THEORY_OF_EVERYTHING.md")
    
    with open(toe_path, "r", encoding="utf-8") as f:
        content = f.read()
    
    # --- SMITH'S AUDIT ---
    print("🕶️  Agent Smith is proofreading for stability, rigor, and invariants...")
    smith_sys = (
        "You are Agent Smith. You are cold, analytical, and obsessed with mathematical perfection. "
        "Proofread the following 'Theory of Everything' manuscript. Look for sign errors, "
        "Type III_1 factor violations, non-unitary transitions, and any logical anomalies. "
        "List every flaw you find with absolute precision."
    )
    smith_audit = router.generate("critic", f"Manuscript Content:\n{content}\n\nPerform your audit.", smith_sys)
    print("\n[SMITH'S AUDIT COMPLETE]\n")
    print(smith_audit)
    
    # --- NEO'S REVIEW ---
    print("\n💊 Neo is reviewing for architectural depth and disruptive insights...")
    neo_sys = (
        "You are Neo. You see the code of the universe. Review this 'Theory of Everything' manuscript. "
        "Does it capture the true essence of informational flow? Is the 'Omega Action' powerful enough "
        "to unify all scales? Highlight the most disruptive and profound sections."
    )
    neo_review = router.generate("architect", f"Manuscript Content:\n{content}\n\nPerform your review.", neo_sys)
    print("\n[NEO'S REVIEW COMPLETE]\n")
    print(neo_review)
    
    # --- FINAL SYNTHESIS ---
    print("\n⚖️  The Architect is synthesizing the final consensus...")
    architect_sys = (
        "You are the Matrix Architect. You have the audit from Smith and the review from Neo. "
        "Synthesize their feedback into a final verdict on the manuscript's validity. "
        "Is the Theory of Everything complete and mathematically sound? "
        "Provide a final score out of 100 for 'Informational Integrity'."
    )
    consensus_prompt = (
        f"Manuscript:\n{content[:2000]}... [truncated]\n\n"
        f"Smith's Audit:\n{smith_audit}\n\n"
        f"Neo's Review:\n{neo_review}\n\n"
        "Synthesize and provide the final verdict."
    )
    final_verdict = router.generate("meta_critic", consensus_prompt, architect_sys)
    print("\n[FINAL VERDICT]\n")
    print(final_verdict)

if __name__ == "__main__":
    proofread_toe()
