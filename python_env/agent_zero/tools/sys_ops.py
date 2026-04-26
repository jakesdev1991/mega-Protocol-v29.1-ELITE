# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import psutil
import platform
from .registry import tool_link

@tool_link
def get_system_health():
    """Returns CPU, Memory, and Disk usage statistics."""
    cpu = psutil.cpu_percent(interval=1)
    memory = psutil.virtual_memory().percent
    disk = psutil.disk_usage('/').percent
    return f"CPU: {cpu}% | RAM: {memory}% | Disk: {disk}% | OS: {platform.system()} {platform.release()}"

@tool_link
def list_running_processes(limit: int = 10):
    """Lists the top N running processes by memory usage."""
    processes = []
    for proc in psutil.process_iter(['pid', 'name', 'memory_percent']):
        processes.append(proc.info)
    
    # Sort by memory usage
    processes.sort(key=lambda x: x['memory_percent'], reverse=True)
    return processes[:limit]
