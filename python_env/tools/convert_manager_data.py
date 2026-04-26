# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import json
import os

INPUT_PATH = "agent_zero/knowledge/evolution_log.jsonl"
OUTPUT_PATH = "data/manager_train_data.jsonl"

def convert_dataset():
    if not os.path.exists(INPUT_PATH):
        print(f"❌ Input {INPUT_PATH} not found.")
        return

    print(f"🔄 Converting {INPUT_PATH} to training format...")
    converted_count = 0
    
    with open(INPUT_PATH, "r") as f_in, open(OUTPUT_PATH, "w") as f_out:
        for line in f_in:
            data = json.loads(line)
            messages = data.get("messages", [])
            if len(messages) < 2:
                continue
                
            user_content = messages[0]["content"]
            assistant_content = messages[1]["content"]
            
            # Skip entries that are just error messages
            if "HTTPConnectionPool" in assistant_content or "Error:" in assistant_content[:10]:
                print("⚠️ Skipping error entry.")
                continue
                
            # Map to Mistral Script Format: instruction, context, response
            new_entry = {
                "instruction": "Design a high-intellect technical training outline or solution based on the following Omega Protocol context.",
                "context": user_content,
                "response": assistant_content
            }
            f_out.write(json.dumps(new_entry) + "\n")
            converted_count += 1
            
    print(f"✅ Successfully converted {converted_count} valid samples to {OUTPUT_PATH}")

if __name__ == "__main__":
    convert_dataset()
