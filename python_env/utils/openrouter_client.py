# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import requests
import json
import time

class OpenRouterClient:
    def __init__(self, api_key):
        self.api_key = api_key
        self.url = "https://openrouter.ai/api/v1/chat/completions"

    def chat(self, model, messages, reasoning=False):
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://omega-protocol.ai", # Optional
            "X-Title": "Omega Protocol v29.1"
        }
        
        payload = {
            "model": model,
            "messages": messages
        }
        
        if reasoning:
            payload["reasoning"] = {"enabled": True}
            
        try:
            response = requests.post(self.url, headers=headers, json=payload, timeout=600)
            if response.status_code != 200:
                print(f"❌ OpenRouter API Error {response.status_code}: {response.text}")
            response.raise_for_status()
            
            return response.json()
        except Exception as e:
            print(f"⚠️ OpenRouter API Error: {e}")
            raise e

    def generate(self, model, prompt, system_prompt=None, reasoning=False):
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        
        resp = self.chat(model, messages, reasoning=reasoning)
        return resp['choices'][0]['message']['content']

if __name__ == "__main__":
    # Test
    client = OpenRouterClient("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")
    try:
        print("Testing OpenRouter Llama 3.1 405B...")
        res = client.generate("nousresearch/hermes-3-llama-3.1-405b:free", "What is the meaning of life?")
        print(f"Response: {res}")
    except Exception as e:
        print(f"Test Failed: {e}")
