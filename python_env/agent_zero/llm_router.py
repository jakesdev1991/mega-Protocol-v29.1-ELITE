# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import os
import requests
import sys

# Ensure project root is in path
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(PROJECT_ROOT)

from utils.nvidia_client import NvidiaClient
from utils.gemini_client import GeminiClient
from utils.openrouter_client import OpenRouterClient
from utils.groq_client import GroqClient
from utils.llm7_client import LLM7Client
from utils.pollen_client import PollenClient

class LLMRouter:
    """
    Intelligent router for the Omega Protocol agentic framework.
    Distributes tasks across NVIDIA Elite Tier, Google Gemini, OpenRouter Nexus, Groq Speed Tier, LLM7, and Pollen Discovery.
    """
    def __init__(self):
        self.nvidia = NvidiaClient()
        self.gemini = GeminiClient("AIzaSyANofahjtPBhSIKUGLCi8qkzGsmYnFBpu0")
        self.openrouter = OpenRouterClient("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")
        self.groq = GroqClient("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")
        self.llm7 = LLM7Client("OBdnjOIQTb+McC2T/0EN5ldQPJOCiiBXM8L5pGC12oPx1Kw9IgynEVEWqeJH4XixSZTGWEU4iH+nlOER0JUPnyqSXisawUN6ntDBYn7PxYmjDxo0gsPujE233U69tNN0E80xK7m5lQ==")
        self.pollen = PollenClient("sk_5RcsRS3CXtQ9AZfFVhRkSupvIpQV8c9u")
        
        # --- STRATEGIC MODEL DISTRIBUTION (v29.1-ELITE) ---
        self.role_map = {
            "architect": {
                "primary": "deepseek-v3.2", 
                "secondary": "qwen-397b",
                "tertiary": "gemini-ultra-think" 
            },
            "coder": {
                "primary": "qwen-coder",
                "secondary": "qwen3-next-instruct",
                "tertiary": "devstral"
            },
            "critic": {
                "primary": "qwen-397b",
                "secondary": "deepseek-v3.2",
                "tertiary": "openrouter/minimax-reasoning" 
            },
            "meta_critic": {
                "primary": "deepseek-terminus",
                "secondary": "kimi-k2", 
                "tertiary": "gemini-ultra-think"
            },
            "writer": {
                "primary": "minimax-m2.5",
                "secondary": "minimax-m2.7",
                "tertiary": "mistral-medium"
            },
            "worker": {
                "primary": "qwen-122b",
                "secondary": "qwen3-next-instruct",
                "tertiary": "step-flash"
            },
            "finance_analyst": {
                "primary": "deepseek-v3.2",
                "secondary": "qwen-397b",
                "tertiary": "mistral-large"
            },
            "experimenter": { # NVIDIA prioritized for Sandbox Loop
                "primary": "deepseek-v3.2",
                "secondary": "qwen-397b",
                "tertiary": "openrouter/hermes-405b"
            }
        }

        self.role_aliases = {
            "planner": "architect",
            "executor": "coder",
            "scrutiny": "critic",
            "verifier": "meta_critic",
            "repairer": "coder",
            "engine": "architect"
        }

    def generate(self, role, prompt, system_prompt=None):
        """Generates a response using the primary model for a role, with fallback logic."""
        target_role = self.role_aliases.get(role, role)
        if target_role not in self.role_map:
            target_role = "worker"
            
        config = self.role_map[target_role]
        
        # Helper to execute chat on correct client
        def execute_chat(model_key, p, sp):
            if "gemini" in model_key:
                print(f"💎 [Gemini Nexus] Routing ultra-high reasoning task to Gemini Thinking...")
                return self.gemini.chat(p, sp)
            elif "groq" in model_key:
                print(f"⚡ [Groq Speed Tier] Routing to {model_key}...")
                return self.groq.chat(model_key.replace("groq/", ""), p, sp)
            elif "llm7" in model_key:
                print(f"🚀 [LLM7 High-Availability] Routing to {model_key}...")
                return self.llm7.chat(model_key.replace("llm7/", ""), p, sp)
            elif "pollen" in model_key:
                print(f"🐝 [Pollen Discovery] Routing to {model_key}...")
                return self.pollen.chat(model_key.replace("pollen/", ""), p, sp)
            elif "openrouter" in model_key:
                print(f"🌌 [OpenRouter Nexus] Routing to {model_key}...")
                if "hermes-405b" in model_key:
                    return self.openrouter.generate("nousresearch/hermes-3-llama-3.1-405b:free", p, sp)
                elif "minimax-reasoning" in model_key:
                    return self.openrouter.generate("minimax/minimax-m2.5:free", p, sp, reasoning=True)
                else:
                    return self.openrouter.generate(model_key.replace("openrouter/", ""), p, sp)
            else:
                return self.nvidia.chat(model_key, p, sp)

        # Try Primary
        try:
            print(f"[LLM Router] Routing '{role}' -> PRIMARY: {config['primary']}...")
            return execute_chat(config['primary'], prompt, system_prompt)
        except Exception as e:
            print(f"⚠️ Primary model {config['primary']} failed: {e}. Falling back to SECONDARY...")
            
            # Try Secondary
            try:
                print(f"[LLM Router] Routing '{role}' -> SECONDARY: {config['secondary']}...")
                return execute_chat(config['secondary'], prompt, system_prompt)
            except Exception as e2:
                print(f"⚠️ Secondary model {config['secondary']} failed: {e2}. Falling back to TERTIARY...")
                
                # Try Tertiary
                try:
                    print(f"[LLM Router] Routing '{role}' -> TERTIARY: {config['tertiary']}...")
                    return execute_chat(config['tertiary'], prompt, system_prompt)
                except Exception as e3:
                    print(f"❌ All models for role '{role}' failed. Last error: {e3}")
                    raise e3

if __name__ == "__main__":
    router = LLMRouter()
    print(router.generate("writer", "Say hello in one sentence."))
