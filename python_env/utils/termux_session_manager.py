# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import json
import os
from collections import deque

class TermuxSessionManager:
    """
    Manages working memory (last 6 messages) per phone number for the Termux Service Agent.
    Interfaces with the fine-tuned 135M model to generate customer-friendly replies.
    """
    def __init__(self, history_limit=6):
        self.history_limit = history_limit
        self.sessions = {} # number -> deque of messages
        self.state_file = "/home/jake/Downloads/training/agent_zero/knowledge/termux_sessions.json"
        self.load_sessions()

    def load_sessions(self):
        if os.path.exists(self.state_file):
            with open(self.state_file, "r") as f:
                data = json.load(f)
                for number, history in data.items():
                    self.sessions[number] = deque(history, maxlen=self.history_limit)

    def save_sessions(self):
        data = {number: list(history) for number, history in self.sessions.items()}
        with open(self.state_file, "w") as f:
            json.dump(data, f, indent=4)

    def add_message(self, number, message, role="User"):
        if number not in self.sessions:
            self.sessions[number] = deque(maxlen=self.history_limit)
        
        self.sessions[number].append(f"{role}: {message}")
        self.save_sessions()

    def get_context(self, number):
        if number not in self.sessions:
            return "[None]"
        return " | ".join(list(self.sessions[number])[:-1]) # Context excluding the latest message

    def generate_prompt(self, number, latest_message):
        context = self.get_context(number)
        prompt = f"History: [{context}] User: {number}: {latest_message} Agent:"
        return prompt

if __name__ == "__main__":
    manager = TermuxSessionManager()
    # Test session for a specific number
    test_number = "555-0199"
    manager.add_message(test_number, "Can I get 2 hours tomorrow?")
    manager.add_message(test_number, "I have 2 hours at 3pm tomorrow. Want it?", role="Agent")
    
    latest = "Yes please."
    print(f"Generated Prompt for {test_number}:")
    print(manager.generate_prompt(test_number, latest))
