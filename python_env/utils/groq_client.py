# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import requests
import json
import time
from collections import deque

class GroqClient:
    def __init__(self, api_key):
        self.api_key = api_key
        self.url = "https://api.groq.com/openai/v1/chat/completions"
        
        # Free Model Tier Registry with provided RPM/RPD limits
        self.model_metadata = {
            "allam-2-7b": {"rpm": 30, "rpd": 7000},
            "canopylabs/orpheus-arabic-saudi": {"rpm": 10, "rpd": 100},
            "canopylabs/orpheus-v1-english": {"rpm": 10, "rpd": 100},
            "groq/compound": {"rpm": 30, "rpd": 250},
            "groq/compound-mini": {"rpm": 30, "rpd": 250},
            "llama-3.1-8b-instant": {"rpm": 30, "rpd": 14400},
            "llama-3.3-70b-versatile": {"rpm": 30, "rpd": 1000},
            "meta-llama/llama-4-scout-17b-16e-instruct": {"rpm": 30, "rpd": 1000},
            "meta-llama/llama-prompt-guard-2-22m": {"rpm": 30, "rpd": 14400},
            "meta-llama/llama-prompt-guard-2-86m": {"rpm": 30, "rpd": 14400},
            "openai/gpt-oss-120b": {"rpm": 30, "rpd": 1000},
            "openai/gpt-oss-20b": {"rpm": 30, "rpd": 1000},
            "openai/gpt-oss-safeguard-20b": {"rpm": 30, "rpd": 1000},
            "qwen/qwen3-32b": {"rpm": 60, "rpd": 1000},
            "whisper-large-v3": {"rpm": 20, "rpd": 2000},
            "whisper-large-v3-turbo": {"rpm": 20, "rpd": 2000}
        }
        
        # History trackers for rate limiting
        self.rpm_history = {model: deque() for model in self.model_metadata}
        self.rpd_count = {model: 0 for model in self.model_metadata}
        self.last_day_reset = time.time()

    def _enforce_rate_limit(self, model):
        """Enforces RPM and RPD limits for the specified model."""
        if model not in self.model_metadata:
            return

        now = time.time()
        
        # Handle Day Reset (Simple runtime reset)
        if now - self.last_day_reset > 86400:
            self.rpd_count = {m: 0 for m in self.model_metadata}
            self.last_day_reset = now

        limits = self.model_metadata[model]
        
        # Check RPD
        if self.rpd_count[model] >= limits["rpd"]:
            print(f"🛑 [Groq] RPD Limit Exhausted for {model}. ({limits['rpd']} requests reached)")
            raise RuntimeError(f"Daily limit reached for {model}")

        # Check RPM (Sliding Window)
        history = self.rpm_history[model]
        while history and now - history[0] > 60:
            history.popleft()

        if len(history) >= limits["rpm"]:
            wait_time = 60 - (now - history[0])
            print(f"⏳ [Groq] RPM Limit reached for {model}. Waiting {wait_time:.2f}s...")
            time.sleep(max(wait_time, 0.1))
            return self._enforce_rate_limit(model)

        history.append(now)
        self.rpd_count[model] += 1

    def chat(self, model, prompt, system_prompt=None):
        if not system_prompt:
            system_prompt = "You are an expert AI assistant for the Omega Protocol."
            
        self._enforce_rate_limit(model)
            
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.7
        }
        
        try:
            response = requests.post(self.url, headers=headers, json=payload, timeout=600)
            if response.status_code == 429:
                print(f"⚠️ [Groq] Rate limit trigger (429) on {model}. Adjusting local counter...")
                # Add dummy entries to force local wait if server is more restrictive
                for _ in range(5): self.rpm_history[model].append(time.time())
                
            if response.status_code != 200:
                print(f"❌ Groq API Error {response.status_code}: {response.text}")
            response.raise_for_status()
            
            return response.json()['choices'][0]['message']['content']
        except Exception as e:
            print(f"⚠️ Groq API Error on {model}: {e}")
            raise e

if __name__ == "__main__":
    # Test
    client = GroqClient("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")
    try:
        model = "llama-3.3-70b-versatile"
        print(f"Testing Groq {model}...")
        res = client.chat(model, "Say hello in one sentence.")
        print(f"Response: {res}")
    except Exception as e:
        print(f"Test Failed: {e}")
