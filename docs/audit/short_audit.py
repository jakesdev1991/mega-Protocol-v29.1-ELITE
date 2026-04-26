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

def short_audit():
    router = LLMRouter()
    toe_path = os.path.join(PROJECT_ROOT, "python_env/docs/THEORY_OF_EVERYTHING.md")
    
    with open(toe_path, "r", encoding="utf-8") as f:
        content = f.read()
    
    # Just the Abstract and Conclusion
    summary = content[:1000] + "\n...\n" + content[-2000:]
    
    print("🕶️  Smith Audit (Summary)...")
    smith = router.generate("critic", f"Summary:\n{summary}\nAudit for rigor.", "You are Agent Smith. Be brief.")
    print(f"\n[Smith]: {smith}")
    
    print("\n💊 Neo Review (Summary)...")
    neo = router.generate("architect", f"Summary:\n{summary}\nReview for insight.", "You are Neo. Be brief.")
    print(f"\n[Neo]: {neo}")

if __name__ == "__main__":
    short_audit()
