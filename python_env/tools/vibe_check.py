# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import time
import os
import subprocess
import argparse

def get_latest_ckpt(log_dir):
    latest_ckpt = None
    latest_time = 0
    
    for root, dirs, files in os.walk(log_dir):
        for file in files:
            if file.endswith(".ckpt"):
                path = os.path.join(root, file)
                mtime = os.path.getmtime(path)
                if mtime > latest_time:
                    latest_time = mtime
                    latest_ckpt = path
    return latest_ckpt

def monitor(log_dir, interval=300):
    print(f"Vibe Check Daemon started. Monitoring {log_dir}...")
    last_ckpt = get_latest_ckpt(log_dir)
    if last_ckpt:
        print(f"Initial checkpoint found: {last_ckpt}")
    
    while True:
        time.sleep(interval)
        current_ckpt = get_latest_ckpt(log_dir)
        
        if current_ckpt and current_ckpt != last_ckpt:
            print(f"\n--- New Checkpoint Detected: {current_ckpt} ---")
            print("Running Vibe Check Generation...")
            
            try:
                # Run the generate tool
                cmd = [
                    ".venv\\Scripts\\python.exe", 
                    "tools/generate.py", 
                    "--ckpt", current_ckpt,
                    "--prompt", "Once upon a time in a world of silicon and code,",
                    "--max_tokens", "50"
                ]
                result = subprocess.check_output(cmd, stderr=subprocess.STDOUT).decode()
                
                # Log the output to a file
                with open("vibe_check_history.txt", "a") as f:
                    f.write(f"\nCheckpoint: {current_ckpt}\n")
                    f.write(result)
                    f.write("-" * 40 + "\n")
                
                print("Vibe Check Complete. Results appended to vibe_check_history.txt")
                last_ckpt = current_ckpt
            except Exception as e:
                print(f"Error running vibe check: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--log_dir", type=str, default="lightning_logs")
    parser.add_argument("--interval", type=int, default=60)
    args = parser.parse_args()
    
    monitor(args.log_dir, args.interval)
