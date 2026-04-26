# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import psutil
import os

def recover_ram():
    print("🧹 [RAM Recovery] Identifying session-critical processes...")
    current = psutil.Process()
    protected_pids = {current.pid, os.getppid()}
    
    # Traverse up to find the root Node process
    parent = current.parent()
    while parent:
        if "node" in parent.name().lower():
            protected_pids.add(parent.pid)
            # Also protect grandparent of node just in case
            gparent = parent.parent()
            if gparent: protected_pids.add(gparent.pid)
            break
        parent = parent.parent()
        
    print(f"🔒 Protecting {len(protected_pids)} critical session IDs.")
    
    kill_count = 0
    freed_mb = 0
    
    for proc in psutil.process_iter(['pid', 'name', 'memory_info']):
        try:
            if "node" in proc.info['name'].lower() and proc.info['pid'] not in protected_pids:
                mem = proc.info['memory_info'].rss / (1024 * 1024)
                proc.kill()
                kill_count += 1
                freed_mb += mem
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
            
    print(f"✅ PURGE COMPLETE. Terminated {kill_count} stray Node processes.")
    print(f"📊 Estimated RAM Recovered: {freed_mb:.1f} MB")

if __name__ == "__main__":
    recover_ram()
