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
import math
import subprocess
import psutil
from datetime import datetime

# --- DEDS v2.2 Configuration (Miner Scout Update) ---
OOM_THRESHOLD = 0.85 
INNOVATION_THROTTLE_THRESHOLD = 0.70 # Throttle innovations at 70% RAM
MAX_CONCURRENT_TASKS = 3 
ALPHA = 1.0   
BETA = 2.5    
GAMMA = 5.0   
EPSILON = 0.1 

STATE_FILE = os.path.join(os.path.dirname(__file__), "deds_state.json")
LOG_DIR = os.path.join(os.path.dirname(__file__), "../logs/loops")

os.makedirs(LOG_DIR, exist_ok=True)

class DEDSTask:
    def __init__(self, name, command, base_cost, is_daemon=False, is_emergency=False):
        self.name = name
        self.command = command
        self.base_cost = base_cost  
        self.is_daemon = is_daemon
        self.is_emergency = is_emergency
        
        self.L_i = 1.0 if is_emergency else 0.5  
        self.last_run_time = time.time()
        self.R_i = 20.0 if is_emergency else 0.0  
        self.run_count = 0

    def update_stagnation(self):
        hours_since_run = (time.time() - self.last_run_time) / 3600.0
        return 1.0 / (1.0 + math.exp(-2.0 * (hours_since_run - 1.0)))

    def get_priority(self):
        S_i = self.update_stagnation()
        R_i_effective = 50.0 if self.is_emergency else self.R_i
        priority = ((ALPHA * self.L_i) + (BETA * S_i) + (GAMMA * R_i_effective)) / (self.base_cost + EPSILON)
        return priority

    def to_dict(self):
        return {
            "name": self.name, 
            "L_i": self.L_i, 
            "last_run_time": self.last_run_time, 
            "R_i": self.R_i, 
            "run_count": self.run_count, 
            "base_cost": self.base_cost,
            "is_emergency": self.is_emergency
        }
        
    def from_dict(self, data):
        self.L_i = data.get("L_i", 0.5)
        self.last_run_time = data.get("last_run_time", time.time())
        self.R_i = data.get("R_i", 0.0)
        self.run_count = data.get("run_count", 0)

TASKS = [
    DEDSTask("omega_os_development", "python_env/agent_zero/jobs/omega_os_vm_builder.py", base_cost=3.0, is_emergency=True),
    DEDSTask("manifold_manager", "python_env/agent_zero/jobs/manifold_manager_job.py", base_cost=2.0, is_emergency=True), 
    DEDSTask("miner_scout", "python_env/agent_zero/jobs/miner_scout.py", base_cost=1.0, is_emergency=True), # NEW SCOUT
    DEDSTask("universal_innovation", "python_env/agent_zero/jobs/universal_innovation_engine.py", base_cost=2.0, is_emergency=True),
    DEDSTask("physics_markov_synthesis", "python_env/agent_zero/jobs/physics_markov_synthesis.py", base_cost=1.5),
    DEDSTask("co_evolution", "python_env/biology/co_evolution_loop.py", base_cost=1.0),
    DEDSTask("dual_manifold", "python_env/tools/trigger_dual_manifold_evolution.py", base_cost=1.0),
    DEDSTask("c_core_orchestrator", "python_env/omega_orchestrator.py", base_cost=2.0),
    DEDSTask("tokamak", "python_env/tokamak/train_tokamak.py", base_cost=3.0),
    DEDSTask("sales_automation", "python_env/business/train_sales_automation.py", base_cost=1.5),
    DEDSTask("cross_domain", "python_env/agent_zero/train_cross_domain.py", base_cost=2.0),
    DEDSTask("finance_day", "python_env/finance/train_day_trading.py", base_cost=2.0),
    DEDSTask("finance_mid", "python_env/finance/train_medium_term.py", base_cost=2.0),
    DEDSTask("finance_long", "python_env/finance/train_long_term.py", base_cost=2.0),
    DEDSTask("biology_metabolism", "python_env/biology/train_universal_metabolism.py", base_cost=1.5),
    DEDSTask("psychology", "python_env/psychology/train_psychology.py", base_cost=2.0),
    DEDSTask("sandbox_experimenter", "python -m python_env.agent_zero.sandbox_experimenter", base_cost=4.0),
    DEDSTask("rcod_300m", "python_env/examples/train_300m_rcod_lightning.py --config configs/300m_rcod.yml --data data/rcod_fineweb_pruned --max_steps {CAW}", base_cost=10.0),
    DEDSTask("smollm_1_7b", "python_env/examples/train_1_7b_rcod_lora.py --max_steps {CAW}", base_cost=25.0)
]

def load_state():
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE, 'r') as f:
                data = json.load(f)
                for task in TASKS:
                    if task.name in data: task.from_dict(data[task.name])
        except Exception as e: print(f"Error loading DEDS state: {e}")

def save_state():
    state = {task.name: task.to_dict() for task in TASKS}
    with open(STATE_FILE, 'w') as f: json.dump(state, f, indent=4)

def check_system_resources(task_name):
    mem = psutil.virtual_memory()
    # General OOM protection
    if mem.percent > (OOM_THRESHOLD * 100):
        print(f"⚠️  [OOM-GUARD] Memory Critical ({mem.percent}%). Throttling...")
        return False
    # Specific Innovation throttling
    if task_name == "universal_innovation" and mem.percent > (INNOVATION_THROTTLE_THRESHOLD * 100):
        print(f"🐢 [INNOVATION-THROTTLE] Memory High ({mem.percent}%). Postponing innovation cycle...")
        return False
    return True

def calculate_caw(task):
    if getattr(task, 'is_emergency', False): return 500
    if task.L_i < 0.3 and task.update_stagnation() > 0.8: return 10
    return max(20, int(50 * task.L_i))

def run_task(task):
    if not check_system_resources(task.name):
        time.sleep(30)
        return
    print(f"\n[{datetime.now().strftime('%H:%M:%S')}] ⚡ DEDS EXECUTING: {task.name}")
    caw = calculate_caw(task)
    cmd = task.command.replace("{CAW}", str(caw))
    venv_python = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.venv/bin/python"))
    if cmd.startswith("python "): cmd = cmd.replace("python ", f"{venv_python} ", 1)
    else: cmd = f"{venv_python} {cmd}"
    log_file = os.path.join(LOG_DIR, f"{task.name}.log")
    start_time = time.time()
    try:
        with open(log_file, "a") as f:
            f.write(f"\n--- DEDS EXECUTION STARTED AT {datetime.now()} (CAW: {caw}) ---\n")
            process = subprocess.Popen(cmd.split(), stdout=f, stderr=subprocess.STDOUT)
            process.wait()
    except Exception as e: print(f"   ❌ Task {task.name} failed: {e}")
    duration = time.time() - start_time
    if getattr(task, 'is_emergency', False):
        task.L_i = 1.0
        task.R_i = 20.0 
    else:
        reward = min(1.0, duration / (caw * 2.0)) if caw > 0 else 0.5
        task.L_i = (0.7 * task.L_i) + (0.3 * reward)
        task.R_i *= 0.5 
    task.last_run_time = time.time()
    task.run_count += 1
    save_state()
    print(f"   ✅ COMPLETED in {duration:.1f}s | New L_i: {task.L_i:.3f}")

def main():
    print("=========================================================")
    print("🛡️  DEDS v2.2: Miner Scout & Innovation Throttle Active")
    print("=========================================================")
    load_state()
    while True:
        ranked_tasks = sorted(TASKS, key=lambda t: t.get_priority(), reverse=True)
        winner = ranked_tasks[0]
        run_task(winner)
        sleep_time = 0.1 if getattr(winner, 'is_emergency', False) else 5
        time.sleep(sleep_time)

if __name__ == "__main__":
    main()
