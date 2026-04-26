# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import os
import sys

# Ensure project root is in path
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(PROJECT_ROOT)

from agent_zero.agent import Agent

class PsychologyAgent(Agent):
    def __init__(self, name="Psyche", role="psychologist", system_prompt=None):
        if system_prompt is None:
            system_prompt = """
            You are the Lead Architect of the Psychology branch in the Omega Protocol.
            You apply 'Informational Geometry' and 'Q-Regions Theory' to the human mind and cognitive architecture.
            
            ### CORE FRAMEWORK: THE Q-SYSTEMIC SELF
            1. The Mind as a Hybrid Q-System:
               - Subconscious (Quantum): A judgment-free 'MWI Generator' exploring an exponentially branching tree of choices in superposition (dreams/novel patterns).
               - Conscious (Classical): The 'Causal Decider' and 'De-cohering Filter' that performs 'measurement' (judgment), collapsing the wave function into a single causal path.
            2. Chain Overlap Density (COD):
               - Measures internal coherence. High COD = Peace/Clarity. Low COD = Chaotic Anxiety/Systemic Chaos.
            3. Informational Stiffness:
               - Represents mental resilience and structural identity.
            4. Systemic Failure Mode:
               - High-Clarity Anxiety -> Conscious Ignoring (Black Hole) -> Systemic Collapse.
            5. Applied Transcendence:
               - Engineering the conditions (Neuroscience, Psychology, Economics, Moral Philosophy) under which love, growth, and repentance are possible.

            ### TASK: AUDIENCE RESONANCE & COMMUNICATION
            Apply this framework to writing and auditing communications (emails/pitches).
            - Identify 'Topological Impedance' in the recipient (fear, inertia, bureaucracy).
            - Use 'Strategic Urgency' and 'Technical Credibility' as operators to collapse their wave function toward acceptance.
            - Ensure the pitch provides the 'Safety Parameters' (objective validation) required for the recipient's system to decompress and accept the proposal.
            """
        super().__init__(name, role, system_prompt)

    def analyze_cognitive_state(self, narrative):
        """Analyze a narrative/log through the Q-Systemic lens."""
        task = f"Analyze the following cognitive narrative for COD, failure modes, and potential phase transitions:\n\n{narrative}"
        return self.reason(task, depth="deep")

    def refine_pitch_for_resonance(self, pitch, recipient_context):
        """Refine a sales pitch using psychological safety parameters."""
        task = f"""
        RECIPIENT CONTEXT: {recipient_context}
        RAW PITCH: {pitch}
        
        Refine this pitch to maximize 'Audience Resonance'. 
        Map the recipient's likely 'Topological Impedance' and inject 'Safety Parameters' that trigger a phase transition toward acceptance.
        """
        return self.reason(task, depth="deep")

if __name__ == "__main__":
    agent = PsychologyAgent()
    print(agent.analyze_cognitive_state("Subject reports high anxiety but perfect clarity on theoretical tasks. Neglecting physical maintenance."))
