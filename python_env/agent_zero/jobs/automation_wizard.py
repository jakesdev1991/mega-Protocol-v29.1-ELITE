# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
from agent_zero.agent import Agent
from agent_zero.serc import SERC
import os
import subprocess

class AutomationWizard:
    """The primary testbed for 'Design-First' evolution using aw_ux_scan and aw_ux_score."""
    
    def __init__(self):
        self.designer = Agent("UXDesigner", "architect", "Design interfaces focusing on Clarity, Visible Story, and Low Cognitive Load (max 3-5 options).")
        self.verifier = Agent("UXVerifier", "critic", "Score UI proposals using aw_ux_score metrics.")
        self.coder = Agent("UICoder", "coder", "Implement validated UI/UX designs into code.")
        
        self.instruments_dir = os.path.join(os.path.dirname(__file__), "..", "instruments")

    def _run_instrument(self, name, args=""):
        script = os.path.join(self.instruments_dir, f"{name}.py")
        if not os.path.exists(script):
            return f"[Error] Instrument {name} not found."
        
        # Execute instrument using current venv
        venv_python = os.path.join(os.path.dirname(__file__), "..", "..", ".venv", "Scripts", "python.exe")
        try:
            result = subprocess.run([venv_python, script, args], capture_output=True, text=True, check=True)
            return result.stdout.strip()
        except subprocess.CalledProcessError as e:
            return f"[Instrument Error] {e.stderr}"

    def run_design_loop(self, target_ui="main_dashboard"):
        print(f"\n🎨 [AutomationWizard] Starting Design-First loop for: {target_ui}")
        
        # 1. Scan current UX state
        print("\n--- 1. SCANNING UX ---")
        current_ux_report = self._run_instrument("aw_ux_scan", target_ui)
        print(f"Scan Report: {current_ux_report}")
        
        # 2. Design Proposal
        print("\n--- 2. DESIGN PROPOSAL ---")
        design_prompt = f"Current UX:\n{current_ux_report}\n\nPropose an improved design adhering to: Clarity, Visible Story, Low Cognitive Load."
        proposal = self.designer.reason(design_prompt)
        
        # 3. Score Proposal
        print("\n--- 3. UX SCORING ---")
        # In reality, we'd pass the proposal text via file or stdin, here simulating via argument passing/prompting
        score_prompt = f"Evaluate this proposal using the Automation Wizard rubric:\n{proposal}"
        score = self.verifier.evaluate(proposal, "1. Clarity (No jargon)\n2. Visible Story (Top-to-bottom narrative)\n3. Low Load (max 3-5 options)")
        
        # 4. Implement Code
        print("\n--- 4. IMPLEMENTATION ---")
        code_prompt = f"Write the Python/Tkinter (CustomTkinter) code for this approved UI design:\n{proposal}\n\nScore Notes: {score}"
        code = self.coder.reason(code_prompt)
        
        print("\n✅ Automation Wizard Loop Complete.")
        return code

if __name__ == "__main__":
    wizard = AutomationWizard()
    wizard.run_design_loop("Omega Control Panel Model Selector")
