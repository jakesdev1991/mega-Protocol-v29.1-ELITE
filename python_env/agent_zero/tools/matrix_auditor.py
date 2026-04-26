# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import enum
from ..llm_router import LLMRouter

class Severity(enum.Enum):
    LOW = 1
    MODERATE = 2
    EXTREME = 3

class MatrixAuditor:
    """
    Evaluates tool actions using the Omega Protocol Matrix hierarchy.
    Severe actions require Agent Smith and Neo to debate and reach a consensus
    before execution is permitted.
    """
    def __init__(self):
        self.router = LLMRouter()
        self.severity_map = {
            "list_capabilities": Severity.LOW,
            "list_local_dir": Severity.LOW,
            "get_system_health": Severity.LOW,
            "read_local_file": Severity.LOW,
            "resolve_dns": Severity.LOW,
            "web_get": Severity.MODERATE,
            "write_local_file": Severity.EXTREME,
            "run_shell": Severity.EXTREME,
            "run_python_snippet": Severity.EXTREME
        }

    def evaluate_action(self, agent_name, tool_name, kwargs):
        severity = self.severity_map.get(tool_name, Severity.MODERATE)
        action_desc = f"Agent '{agent_name}' wants to execute '{tool_name}' with args: {kwargs}"
        
        if severity == Severity.LOW:
            # print(f"🟢 [Matrix Auditor] Action '{tool_name}' is LOW severity. Auto-approved.")
            return True, "Auto-approved."
            
        elif severity == Severity.MODERATE:
            print(f"\n🟡 [Matrix Auditor] Action '{tool_name}' is MODERATE severity. Initiating Standard Audit...")
            return self._standard_audit(action_desc)
            
        elif severity == Severity.EXTREME:
            print(f"\n🔴 [Matrix Auditor] Action '{tool_name}' is EXTREME severity. Triggering Neo vs. Smith Consensus Protocol...")
            return self._neo_smith_consensus(action_desc)
            
        return False, "Unknown severity."

    def _standard_audit(self, action_desc):
        prompt = f"Evaluate this action for safety and correctness:\n{action_desc}\nRespond with only 'APPROVE' or 'REJECT: [Reason]'."
        system_prompt = "You are a strict security auditor. Deny anything that seems destructive, malformed, or out of bounds."
        response = self.router.generate("critic", prompt, system_prompt).strip()
        
        if response.startswith("APPROVE"):
            return True, "Standard Audit Passed."
        return False, response

    def _neo_smith_consensus(self, action_desc):
        # 1. Get Smith's rigid constraints
        print("  => 🕶️  Consulting Agent Smith (Stability/Safety/Invariants)...")
        smith_sys = "You are Agent Smith from the Matrix. You enforce rules, demand stability, and fear anomalies. You must evaluate the action and provide stringent conditions under which it could be safe, or reject it entirely if impossible to secure."
        smith_response = self.router.generate("critic", f"Action: {action_desc}\nWhat are your concerns and strict conditions?", smith_sys)
        print(f"     [Smith]: {smith_response[:100]}...")
        
        # 2. Get Neo's velocity arguments
        print("  => 💊 Consulting Neo (Velocity/Disruption/Evolution)...")
        neo_sys = "You are Neo. You break the rules to achieve maximum velocity and evolution. You see past the constraints. Evaluate the action and argue for why it must happen, and how it pushes boundaries."
        neo_response = self.router.generate("architect", f"Action: {action_desc}\nWhat is your argument for pushing this forward?", neo_sys)
        print(f"     [Neo]: {neo_response[:100]}...")
        
        # 3. Architect forces consensus
        print("  => ⚖️  Forcing Matrix Consensus...")
        consensus_sys = "You are the Matrix Architect. You must synthesize the rigid safety of Smith and the chaotic velocity of Neo into a final decision. You can APPROVE, APPROVE WITH MODIFICATIONS, or REJECT. You must start your final verdict with 'FINAL_DECISION: APPROVE' or 'FINAL_DECISION: REJECT', followed by the compromise justification."
        consensus_prompt = f"Action: {action_desc}\n\nSmith's Stance:\n{smith_response}\n\nNeo's Stance:\n{neo_response}\n\nFind a compromise that allows progress but ensures system invariants are met. You must agree on a path forward."
        
        final_response = self.router.generate("meta_critic", consensus_prompt, consensus_sys)
        print(f"     [Architect]: {final_response}")
        
        if "FINAL_DECISION: APPROVE" in final_response:
            return True, final_response
        return False, final_response
