# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import requests
import json
import time

class LLM7Client:
    def __init__(self, api_key):
        self.api_key = api_key
        self.url = "https://api.llm7.io/v1/chat/completions"
        self.models = ["default", "fast", "pro"]

    def chat(self, model, prompt, system_prompt=None):
        if not system_prompt:
            system_prompt = "You are an expert AI assistant for the Omega Protocol."
            
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": model if model in self.models else "default",
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.7
        }
        
        try:
            response = requests.post(self.url, headers=headers, json=payload, timeout=600)
            if response.status_code != 200:
                print(f"❌ LLM7 API Error {response.status_code}: {response.text}")
            response.raise_for_status()
            
            return response.json()['choices'][0]['message']['content']
        except Exception as e:
            print(f"⚠️ LLM7 API Error on {model}: {e}")
            raise e

if __name__ == "__main__":
    # Test
    token = "OBdnjOIQTb+McC2T/0EN5ldQPJOCiiBXM8L5pGC12oPx1Kw9IgynEVEWqeJH4XixSZTGWEU4iH+nlOER0JUPnyqSXisawUN6ntDBYn7PxYmjDxo0gsPujE233U69tNN0E80xK7m5lQ=="
    client = LLM7Client(token)
    try:
        print("Testing LLM7 API (Default Model)...")
        res = client.chat("default", "Tell me a one-sentence story about a brave squirrel.")
        print(f"Response: {res}")
    except Exception as e:
        print(f"Test Failed: {e}")
