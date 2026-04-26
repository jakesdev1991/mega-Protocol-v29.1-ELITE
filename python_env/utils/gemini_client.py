# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import requests
import json
import time

class GeminiClient:
    def __init__(self, api_key):
        self.api_key = api_key
        self.models = ["gemini-2.0-flash", "gemini-1.5-pro", "gemini-1.5-flash"]

    def chat(self, prompt, system_prompt=None):
        if not system_prompt:
            system_prompt = "You are an expert AI assistant for the Omega Protocol."
            
        headers = {
            "Content-Type": "application/json"
        }
        
        payload = {
            "contents": [{
                "parts": [
                    {"text": f"System Instructions: {system_prompt}\n\nUser Query: {prompt}"}
                ]
            }],
            "generationConfig": {
                "temperature": 0.7,
                "topP": 0.95,
                "topK": 40,
                "maxOutputTokens": 8192,
            }
        }
        
        for model in self.models:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={self.api_key}"
            try:
                response = requests.post(url, headers=headers, json=payload, timeout=600)
                if response.status_code == 200:
                    data = response.json()
                    if 'candidates' in data and len(data['candidates']) > 0:
                        return data['candidates'][0]['content']['parts'][0]['text']
                else:
                    print(f"⚠️ Gemini Model {model} failed with {response.status_code}. Trying next...")
            except Exception as e:
                print(f"⚠️ Gemini API Error on {model}: {e}")
                
        raise RuntimeError("All Gemini models failed.")

if __name__ == "__main__":
    # Test with the provided key (internal test only)
    client = GeminiClient("AIzaSyANofahjtPBhSIKUGLCi8qkzGsmYnFBpu0")
    try:
        print("Testing Gemini 2.0 Flash Thinking API...")
        res = client.chat("Say hello in one sentence.")
        print(f"Response: {res}")
    except Exception as e:
        print(f"Test Failed: {e}")
