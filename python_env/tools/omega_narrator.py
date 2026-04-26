# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import asyncio
import edge_tts
import os
import warnings
import pygame
import sys
import tempfile
import json
import re

# Suppress noise
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"
warnings.filterwarnings("ignore", category=UserWarning)

VOICE = "en-GB-LibbyNeural" # Clear & Professional British Female Voice
OUTPUT_FILE = os.path.join(tempfile.gettempdir(), "omega_narrator.mp3")

async def speak(text):
    if not text.strip():
        return

    try:
        communicate = edge_tts.Communicate(text, VOICE)
        await communicate.save(OUTPUT_FILE)

        pygame.mixer.init()
        pygame.mixer.music.load(OUTPUT_FILE)
        pygame.mixer.music.play()
        
        while pygame.mixer.music.get_busy():
            pygame.time.Clock().tick(10)
        
        pygame.mixer.quit()
    except Exception as e:
        sys.stderr.write(f"❌ Narrator Error: {e}\n")

def clean_text(text):
    # 1. Remove JSON blocks entirely
    text = re.sub(r'```json.*?```', '', text, flags=re.DOTALL)
    
    # 2. Remove tool call blocks (common in AI agents)
    text = re.sub(r'<tool_call>.*?</tool_call>', '', text, flags=re.DOTALL)
    
    # 3. Remove standalone JSON-like braces or bracket arrays
    # (Matches if the entire string or large chunks look like raw JSON)
    if text.strip().startswith('{') and text.strip().endswith('}'):
        return "Transmitting structured data."
    
    # 4. Clean markdown formatting
    text = text.replace("**", "").replace("__", "").replace("###", "").replace("##", "")
    
    # 5. Remove long hex strings or common "jibberish" symbols
    text = re.sub(r'0x[a-fA-F0-9]+', '[hex data]', text)
    
    # 6. Final whitespace cleanup
    text = text.strip()
    
    # If it's still too technical or empty, skip
    if len(text) < 2 or text.startswith("//"):
        return ""
        
    return text

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--transcript", help="Path to transcript")
    args, _ = parser.parse_known_args()

    input_text = ""

    if args.transcript:
        sys.stderr.write(f"🔍 [Narrator] Checking transcript: {args.transcript}\n")
        if os.path.exists(args.transcript):
            try:
                with open(args.transcript, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    messages = data.get("messages", [])
                    # Collect ALL gemini messages from the last turn
                    turn_messages = []
                    for msg in reversed(messages):
                        if msg.get("type") == "user":
                            # Stop once we hit the user's last message
                            break
                        if msg.get("type") == "gemini":
                            content = msg.get("content", "").strip()
                            if content:
                                turn_messages.insert(0, content)
                    
                    input_text = "\n".join(turn_messages)
                    if input_text:
                        sys.stderr.write(f"🔍 [Narrator] Extracted {len(input_text)} total chars from current turn.\n")
            except Exception as e:
                sys.stderr.write(f"❌ [Narrator] Error reading transcript: {e}\n")
        else:
            sys.stderr.write(f"⚠️ [Narrator] Transcript path does not exist.\n")

    cleaned = clean_text(input_text)
    if cleaned:
        sys.stderr.write(f"🎙️ [Narrator] Speaking: {cleaned[:50]}...\n")
        asyncio.run(speak(cleaned))
    else:
        sys.stderr.write("⚠️ [Narrator] No text to speak after cleaning.\n")
    
    # Required CLI decision
    print(json.dumps({"decision": "allow"}))
