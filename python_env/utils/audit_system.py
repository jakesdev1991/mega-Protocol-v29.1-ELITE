# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import os
import json
import sys

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(PROJECT_ROOT)

from finance.finance_agent import FinanceAgent

class AuditSystem:
    """
    Centralized verification for all training loop outputs.
    Ensures logical consistency, security, and accuracy before 'learning' happens.
    """
    def __init__(self):
        self.auditor = FinanceAgent("Omega-Auditor")

    def audit_learning(self, domain, proposed_insight, context=""):
        """
        Submits proposed learning to an LLM for rigorous validation.
        Returns: (is_approved: bool, rationale: str)
        """
        prompt = f"""
        ### OMEGA AUDIT PROTOCOL
        DOMAIN: {domain}
        CONTEXT: {context}
        
        PROPOSED INSIGHT:
        {proposed_insight}
        
        CRITERIA:
        1. Logical Validity: Does the insight follow from the data/context?
        2. Security: Does this propose any insecure practices or expose keys?
        3. Accuracy: Is the mathematical or physical derivation sound?
        4. Utility: Is this actually a 'learning' or just redundant noise?
        
        If the insight is fundamentally sound but lacks Formal Mapping to (Phi_N, Phi_Delta) or Omega Whitepaper axioms, flag it as 'needs_refinement'.
        
        Respond ONLY with a JSON object:
        {{
            "status": "approved" | "needs_refinement" | "hard_rejected",
            "rationale": "reasoning here",
            "critique_for_agent": "specific instructions for the agent to fix the mapping"
        }}
        """
        
        print(f"🕵️  [Auditing] {domain} proposal...")
        try:
            response = self.auditor.reason(prompt, depth="standard")
            if not response:
                return {"status": "error", "rationale": "Empty response"}
            
            import re
            match = re.search(r'\{.*\}', response, re.DOTALL)
            if match:
                result = json.loads(match.group())
                status = result.get("status", "hard_rejected").upper()
                print(f"🔍 [Audit Status]: {status} - {result.get('rationale')}")
                return result
        except Exception as e:
            print(f"⚠️  Audit system failure: {e}")
            return {"status": "error", "rationale": f"System error: {str(e)}"}
        
        return {"status": "error", "rationale": "Unknown audit failure (No JSON match)"}

if __name__ == "__main__":
    audit = AuditSystem()
    # Test
    audit.audit_learning("Test", "The sky is blue because of Rayleigh scattering.", "Basic physics check.")
