# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import sys
import os
import asyncio
import time
import edge_tts
import pygame

# ✦ OMEGA PROTOCOL: NEURAL VOICE MANIFOLD ✦
# Persona: English Female (British Neural)
# Mitigation: Hardware Interference Filtering

VOICE = "en-GB-LibbyNeural" # High-fidelity British Female
OUTPUT_FILE = "/tmp/omega_voice.mp3"

async def generate_speech(text):
    """Generates neural speech using edge-tts."""
    communicate = edge_tts.Communicate(text, VOICE)
    await communicate.save(OUTPUT_FILE)

def speak(text):
    if not text.strip():
        return

    # 1. Generate Neural Audio
    try:
        asyncio.run(generate_speech(text))
        
        # 2. Play Audio with Interference Mitigation
        # Initializing mixer with a high buffer and 44.1kHz to stabilize the DAC
        pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=4096)
        pygame.mixer.music.load(OUTPUT_FILE)
        pygame.mixer.music.play()
        
        while pygame.mixer.music.get_busy():
            time.sleep(0.1)
            
        pygame.mixer.quit()
        if os.path.exists(OUTPUT_FILE):
            os.remove(OUTPUT_FILE)
            
    except Exception as e:
        print(f"Voice Error: {e}")

if __name__ == "__main__":
    # Use taskset to pin the audio process to 'Cool' Cores (0-3) 
    # to move audio processing away from the high-load inference on 16-23.
    # We do this at the OS level when calling the script.
    input_text = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else sys.stdin.read()
    speak(input_text)
