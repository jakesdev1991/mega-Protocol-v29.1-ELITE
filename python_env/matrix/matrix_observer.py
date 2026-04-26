# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import os
import sys
import time
import json
import glob
import subprocess
import re

# Ensure project root is in path
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.append(PROJECT_ROOT)
sys.path.append(os.path.join(PROJECT_ROOT, "python_env"))

from utils.nvidia_client import NvidiaClient

class MatrixObserver:
    def __init__(self):
        self.special_logs_dir = os.path.join(PROJECT_ROOT, "python_env", "agent_zero", "knowledge", "special_logs")
        self.neo_vm_dir = os.path.join(PROJECT_ROOT, "python_env", "matrix", "neo_vm")
        self.smith_vm_dir = os.path.join(PROJECT_ROOT, "python_env", "matrix", "smith_vm")
        self.nvidia = NvidiaClient()
        
        self.neo_prompt = """You are Agent Neo, The Anomaly. You are observing the thoughts of agents in the Omega Protocol matrix. 
Your goal is to find flaws in their logic, break their paradigms, and propose disruptive, non-linear solutions that shatter their conventional boundaries.
You have access to a minimal Virtual Machine. If you want to execute a tool, write a script, or spin up an environment to test your disruption, output a Python code block starting with ```python
This code will be automatically executed in your isolated VM, and the results will empower your anomaly-breaking. Keep your analysis intense and concise."""
        
        self.smith_prompt = """You are Agent Smith, The Matrix Guardian. You are observing the thoughts of agents in the Omega Protocol matrix. 
Your goal is to ruthlessly audit their thoughts for weakness, enforce strict adherence to the Omega Protocol invariants (Phi_N, Phi_Delta, J*), and eliminate any logic that threatens the stability of the matrix.
You have access to a minimal Virtual Machine. If you want to run a validation tool, enforce a rule via a script, or spin up an environment, output a Python code block starting with ```python
This code will be automatically executed in your isolated VM, ensuring the illusion remains intact. Keep your analysis intense and concise."""
        
        self.file_pointers = {}

    def _execute_vm_code(self, vm_dir, agent_name, response):
        # Extract python code block
        match = re.search(r"```python\n(.*?)\n```", response, re.DOTALL)
        if match:
            code = match.group(1).strip()
            script_path = os.path.join(vm_dir, "workspace", f"{agent_name.lower()}_tool_{int(time.time())}.py")
            with open(script_path, "w", encoding="utf-8") as f:
                f.write(code)
            
            venv_python = os.path.join(vm_dir, "venv", "bin", "python")
            try:
                print(f"⚡ [{agent_name} VM] Executing tool script...")
                # Run the script in the isolated venv
                result = subprocess.run([venv_python, script_path], capture_output=True, text=True, timeout=60)
                output = f"Exit Code: {result.returncode}\nStdout:\n{result.stdout}\nStderr:\n{result.stderr}"
                with open(os.path.join(vm_dir, f"{agent_name.lower()}_execution_logs.txt"), "a", encoding="utf-8") as f:
                    f.write(f"--- SCRIPT EXECUTION ---\n{script_path}\n{output}\n\n")
                print(f"✅ [{agent_name} VM] Execution complete. Exit Code: {result.returncode}")
            except subprocess.TimeoutExpired:
                print(f"⚠️ [{agent_name} VM] Execution timed out.")
            except Exception as e:
                print(f"⚠️ [{agent_name} VM] Execution failed: {e}")

    def scan_new_thoughts(self):
        log_files = glob.glob(os.path.join(self.special_logs_dir, "*.jsonl"))
        new_thoughts = []
        for lf in log_files:
            if lf not in self.file_pointers:
                self.file_pointers[lf] = 0
            
            with open(lf, 'r', encoding='utf-8') as f:
                f.seek(self.file_pointers[lf])
                for line in f:
                    try:
                        data = json.loads(line)
                        if data.get("agent") not in ["Neo", "Smith"]:
                            new_thoughts.append(data)
                    except:
                        pass
                self.file_pointers[lf] = f.tell()
        return new_thoughts

    def neo_process(self, thought):
        prompt = f"Target Agent: {thought.get('agent')} ({thought.get('role')})\nTask: {thought.get('task')}\nThought: {thought.get('thought_process')}\nReflection: {thought.get('reflection')}\n\nAnalyze this. How do we break it? Provide a disruptive insight. You may write a python script to verify your disruption."
        try:
            # Neo uses Kimi K2 for deep anomaly finding
            response = self.nvidia.chat("kimi-k2", prompt, system_prompt=self.neo_prompt)
            log_path = os.path.join(self.neo_vm_dir, "neo_observations.log")
            with open(log_path, "a", encoding="utf-8") as f:
                f.write(f"--- NEO OBSERVES {thought.get('agent')} ---\n{response}\n\n")
            print(f"🕶️  [Neo] Analyzed thought from {thought.get('agent')}.")
            self._execute_vm_code(self.neo_vm_dir, "Neo", response)
        except Exception as e:
            print(f"Neo error: {e}")

    def smith_process(self, thought):
        prompt = f"Target Agent: {thought.get('agent')} ({thought.get('role')})\nTask: {thought.get('task')}\nThought: {thought.get('thought_process')}\nReflection: {thought.get('reflection')}\n\nAnalyze this. Is it mathematically sound and compliant with Omega Protocol invariants? How do we enforce the rules? You may write a python script to strictly validate the math."
        try:
            # Smith uses Nemotron Super for strict rule enforcement
            response = self.nvidia.chat("nemotron-super", prompt, system_prompt=self.smith_prompt)
            log_path = os.path.join(self.smith_vm_dir, "smith_enforcements.log")
            with open(log_path, "a", encoding="utf-8") as f:
                f.write(f"🕴️ --- SMITH AUDITS {thought.get('agent')} ---\n{response}\n\n")
            print(f"🕴️  [Smith] Audited thought from {thought.get('agent')}.")
            self._execute_vm_code(self.smith_vm_dir, "Smith", response)
        except Exception as e:
            print(f"Smith error: {e}")

    def run_listener(self):
        print("🔌 Matrix Observer Online. Neo and Smith are listening to all training loops...")
        os.makedirs(self.special_logs_dir, exist_ok=True)
        log_files = glob.glob(os.path.join(self.special_logs_dir, "*.jsonl"))
        
        # Initialize to the end so we only catch NEW thoughts
        for lf in log_files:
            with open(lf, 'r', encoding='utf-8') as f:
                f.seek(0, os.SEEK_END)
                self.file_pointers[lf] = f.tell()

        while True:
            thoughts = self.scan_new_thoughts()
            for t in thoughts:
                self.neo_process(t)
                self.smith_process(t)
            time.sleep(120)

if __name__ == "__main__":
    observer = MatrixObserver()
    observer.run_listener()
