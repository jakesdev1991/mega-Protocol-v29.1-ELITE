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

class NvidiaClient:
    def __init__(self):
        # Centralized Model Registry - Omega Protocol Elite Tier v29.1 (Updated)
        self.keys = {
            "minimax-m2.7": "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",
            "minimax-m2.5": "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",
            "kimi-k2": "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",
            "mistral-small": "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",
            "nemotron-super": "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",
            "qwen-122b": "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",
            "qwen-397b": "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",
            "glm5": "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",
            "step-flash": "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",
            "deepseek-v3.2": "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",
            "devstral": "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",
            "mistral-large": "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",
            "deepseek-terminus": "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",
            "stockmark-100b": "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",
            "qwen-thinking": "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",
            "qwen3-next-thinking": "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",
            "qwen3-next-instruct": "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",
            "qwen-coder": "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",
            "gpt-oss-120b": "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",
            "mistral-medium": "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",
            "llama-ultra": "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",
            "evo2-40b": "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",
            "llama-405b": "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",
            "sd-2.5": "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",
            "flux-dev": "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",
            "sd-3-medium": "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"
        }
        self.models = {
            "minimax-m2.7": "minimaxai/minimax-m2.7",
            "minimax-m2.5": "minimaxai/minimax-m2.5",
            "kimi-k2": "moonshotai/kimi-k2-thinking",
            "mistral-small": "mistralai/mistral-small-4-119b-2603",
            "nemotron-super": "nvidia/nemotron-3-super-120b-a12b",
            "qwen-122b": "qwen/qwen3.5-122b-a10b",
            "qwen-397b": "qwen/qwen3.5-397b-a17b",
            "glm5": "z-ai/glm5",
            "step-flash": "stepfun-ai/step-3.5-flash",
            "deepseek-v3.2": "deepseek-ai/deepseek-v3.2",
            "devstral": "mistralai/devstral-2-123b-instruct-2512",
            "mistral-large": "mistralai/mistral-large-3-675b-instruct-2512",
            "deepseek-terminus": "deepseek-ai/deepseek-v3.1-terminus",
            "stockmark-100b": "stockmark/stockmark-2-100b-instruct",
            "qwen-thinking": "qwen/qwen3-next-80b-a3b-thinking",
            "qwen3-next-thinking": "qwen/qwen3-next-80b-a3b-thinking",
            "qwen3-next-instruct": "qwen/qwen3-next-80b-a3b-instruct",
            "qwen-coder": "qwen/qwen3-coder-480b-a35b-instruct",
            "gpt-oss-120b": "openai/gpt-oss-120b",
            "mistral-medium": "mistralai/mistral-medium-3-instruct",
            "llama-ultra": "nvidia/llama-3.1-nemotron-ultra-253b-v1",
            "evo2-40b": "nvidia/evo2-40b",
            "llama-405b": "meta/llama-3.1-405b-instruct",
            "sd-2.5": "stabilityai/stable-diffusion-2-1",
            "flux-dev": "black-forest-labs/flux-1-dev",
            "sd-3-medium": "stabilityai/stable-diffusion-3-medium"
        }
        self.url = "https://integrate.api.nvidia.com/v1/chat/completions"
        
        # Rate limiting: 40 calls per minute per key
        self.rate_limit = 40
        self.time_window = 60 # seconds
        self.call_history = {key: deque() for key in self.keys.values()}

    def _wait_for_rate_limit(self, api_key):
        """Enforces a strict 40 calls/min limit using a sliding window."""
        history = self.call_history[api_key]
        now = time.time()
        
        while history and now - history[0] > self.time_window:
            history.popleft()
            
        if len(history) >= self.rate_limit:
            wait_time = self.time_window - (now - history[0])
            print(f"⏳ Rate Limit Reached for key ending in ...{api_key[-4:]}. Waiting {wait_time:.2f}s...")
            time.sleep(max(wait_time, 0.1))
            return self._wait_for_rate_limit(api_key)
            
        history.append(time.time())

    def rotate_chat(self, prompt, system_prompt=None):
        """
        Cycles through ALL available elite models to spread the 
        rate limit load across the entire registry.
        """
        # Filter for chat-capable models only (Excludes image models)
        chat_models = [k for k in self.keys.keys() if not any(x in k for x in ["flux", "sd-"])]
        
        # Pick a random model from the registry to ensure distribution
        import random
        target_model = random.choice(chat_models)
        print(f"🔄 [ModelCycler] Rotating to: {target_model}")
        return self.chat(target_model, prompt, system_prompt)

    def chat(self, model_key, prompt, system_prompt=None, max_retries=3):
        if not system_prompt:
            system_prompt = "You are an expert AI assistant for the Omega Protocol."
            
        if model_key not in self.keys:
            raise ValueError(f"Model {model_key} not configured.")
        
        api_key = self.keys[model_key]
        self._wait_for_rate_limit(api_key)
        
        # DYNAMIC ROLE SELECTION
        # Some models require 'developer', others require 'system'
        system_role = "developer" if any(x in model_key for x in ["nemotron", "llama", "gpt-oss"]) else "system"
        if "deepseek-v3.2" in model_key or "mistral-large" in model_key or "qwen" in model_key:
            system_role = "system"

        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        
        payload = {
            "model": self.models[model_key],
            "messages": [
                {"role": system_role, "content": system_prompt},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.1 if any(x in model_key for x in ["large", "small", "devstral", "405b", "ultra"]) else 0.7,
            "top_p": 0.95,
            "max_tokens": 16384 if any(x in model_key for x in ["qwen", "glm", "nemotron", "llama"]) else 8192,
            "stream": False
        }
        
        # Inject Thinking/Reasoning Parameters strategically
        if "qwen" in model_key:
            payload["chat_template_kwargs"] = {"enable_thinking": True}
            if "397b" in model_key:
                payload["top_k"] = 20
        elif "kimi" in model_key:
            payload["temperature"] = 1.0
            payload["top_p"] = 0.9
            payload["max_tokens"] = 16384
        elif "minimax-m2.5" in model_key:
            payload["temperature"] = 1.0
            payload["top_p"] = 0.95
        elif "glm" in model_key:
            payload["chat_template_kwargs"] = {"enable_thinking": True, "clear_thinking": False}
        elif "deepseek" in model_key:
            payload["chat_template_kwargs"] = {"thinking": True}
        elif "nemotron" in model_key:
            payload["chat_template_kwargs"] = {"enable_thinking": True}
            payload["reasoning_budget"] = 16384
        elif "mistral-small" in model_key:
            payload["reasoning_effort"] = "high"
        elif "gpt-oss" in model_key:
            payload["reasoning_effort"] = "medium"

        for attempt in range(max_retries):
            try:
                response = requests.post(self.url, headers=headers, json=payload, timeout=600)
                if response.status_code != 200:
                    print(f"❌ API Error {response.status_code} on {model_key}: {response.text}")
                response.raise_for_status()
                return response.json()['choices'][0]['message']['content']
            except Exception as e:
                print(f"⚠️ NVIDIA API Error on {model_key}: {e}. Retrying...")
                if attempt == max_retries - 1:
                    # Final attempt fallback: try 'system' if 'developer' failed or vice versa
                    new_role = "system" if system_role == "developer" else "developer"
                    print(f"🔄 FINAL ATTEMPT FALLBACK: Switching role to '{new_role}'...")
                    payload["messages"][0]["role"] = new_role
                    try:
                        response = requests.post(self.url, headers=headers, json=payload, timeout=600)
                        response.raise_for_status()
                        return response.json()['choices'][0]['message']['content']
                    except:
                        raise e
                time.sleep(2)

if __name__ == "__main__":
    # Test
    client = NvidiaClient()
    try:
        print("Testing NVIDIA Qwen Coder API...")
        res = client.chat("qwen-coder", "Say hello in one sentence.")
        print(f"Response: {res}")
    except Exception as e:
        print(f"Test Failed: {e}")
