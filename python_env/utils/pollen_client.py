# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import requests
import json
import time

class PollenClient:
    """
    Client for Pollinations AI (Pollen) API.
    OpenAI-compatible endpoints.
    """
    def __init__(self, api_key):
        self.api_key = api_key
        self.url = "https://gen.pollinations.ai/v1/chat/completions"
        self.default_model = "polly" # User specified free model

    def chat(self, model, prompt, system_prompt=None):
        if not system_prompt:
            system_prompt = "You are an expert AI assistant for the Omega Protocol. You are running on a mobile Sovereign Node."
            
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": model if model else self.default_model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.7
        }
        
        try:
            response = requests.post(self.url, headers=headers, json=payload, timeout=600)
            if response.status_code != 200:
                print(f"❌ Pollen API Error {response.status_code}: {response.text}")
            response.raise_for_status()
            
            return response.json()['choices'][0]['message']['content']
        except Exception as e:
            print(f"⚠️ Pollen API Error on {model}: {e}")
            raise e

if __name__ == "__main__":
    # Test
    token = "sk_5RcsRS3CXtQ9AZfFVhRkSupvIpQV8c9u"
    client = PollenClient(token)
    try:
        print(f"Testing Pollen API (Model: polly)...")
        res = client.chat("polly", "You are the 'polly' model. Confirm your status.")
        print(f"Response: {res}")
    except Exception as e:
        print(f"Test Failed: {e}")
