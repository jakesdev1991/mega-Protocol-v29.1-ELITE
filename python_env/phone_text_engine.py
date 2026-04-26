# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import sys
import os
import json

# Add project root to path
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(PROJECT_ROOT)

from utils.pollen_client import PollenClient

def process_text_automation(sender, message):
    """
    Decision Engine for Phone Text Automation.
    Uses Pollen 'polly' model to analyze incoming SMS.
    """
    client = PollenClient("sk_5RcsRS3CXtQ9AZfFVhRkSupvIpQV8c9u")
    
    system_prompt = """
    You are the 'Polly' Decision Engine for a Sovereign Node (Android Phone).
    Your task is to analyze incoming SMS messages and decide on an automated response or system action.
    
    COMMAND PROTOCOL:
    - If the user asks for status, respond with 'STATUS: OK | PHI_N: High'.
    - If the user provides a command hash, validate it.
    - If the message is a general query, provide a concise assistant response.
    
    Output format: 
    DECISION: [Action to take]
    RESPONSE: [Text to send back]
    """
    
    user_prompt = f"SENDER: {sender}\nMESSAGE: {message}"
    
    try:
        decision_raw = client.chat("polly", user_prompt, system_prompt)
        return decision_raw
    except Exception as e:
        return f"ERROR: {str(e)}"

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python phone_text_engine.py '<sender>' '<message>'")
        sys.exit(1)
        
    sender = sys.argv[1]
    message = sys.argv[2]
    
    print(process_text_automation(sender, message))
