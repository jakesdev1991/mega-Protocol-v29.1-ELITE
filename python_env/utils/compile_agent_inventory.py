# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import os
import sys
import json
import re
from datetime import datetime

# Ensure project root is in path
PROJECT_ROOT = "/home/jake/Downloads/training"
sys.path.append(os.path.join(PROJECT_ROOT, "python_env"))

AGENTS_DIR = os.path.join(PROJECT_ROOT, "agents_inventory")

def compile_agent_inventory():
    print("📋 [Inventory] Searching for generated agents across the framework history...")
    
    os.makedirs(AGENTS_DIR, exist_ok=True)
    
    # Pattern to find Agent definitions: Agent("Name", "Role", "Description")
    # Also handles subclass definitions like class FinanceAgent(Agent)
    
    search_dirs = [
        os.path.join(PROJECT_ROOT, "python_env/agent_zero"),
        os.path.join(PROJECT_ROOT, "python_env/matrix"),
        os.path.join(PROJECT_ROOT, "python_env/tokamak"),
        os.path.join(PROJECT_ROOT, "python_env/finance")
    ]
    
    found_agents = {}

    for d in search_dirs:
        if not os.path.exists(d): continue
        for root, _, files in os.walk(d):
            for file in files:
                if file.endswith(".py") or file.endswith(".log") or file.endswith(".md"):
                    path = os.path.join(root, file)
                    try:
                        with open(path, "r", encoding="utf-8", errors="ignore") as f:
                            content = f.read()
                            
                            # 1. Direct Agent Instantiations
                            # Agent("Name", "Role", "Description")
                            matches = re.finditer(r'Agent\(\s*["\']([^"\']+)["\']\s*,\s*["\']([^"\']+)["\']\s*,\s*(?:["\'](.*?)["\']|([^)]*))', content, re.DOTALL)
                            for m in matches:
                                name = m.group(1)
                                role = m.group(2)
                                desc = (m.group(3) or m.group(4) or "").strip()
                                
                                # Clean desc if it's a variable or multi-line
                                if desc.startswith("self."): desc = "Variable-defined description."
                                
                                found_agents[name] = {"role": role, "description": desc, "source": path}
                                
                            # 2. Agent Subclasses
                            # class Name(Agent)
                            subclasses = re.finditer(r'class\s+(\w+)\((Agent|FinanceAgent|DiscoveryAgent)\)', content)
                            for s in subclasses:
                                name = s.group(1)
                                parent = s.group(2)
                                found_agents[name] = {"role": "specialist_subclass", "description": f"Subclass of {parent}", "source": path}
                                
                    except Exception as e:
                        print(f"Error reading {path}: {e}")

    # Write to inventory
    inventory_md = "# OMEGA PROTOCOL AGENT INVENTORY\n\n"
    inventory_md += f"Compiled on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
    
    # Organize agents into individual files
    for name, data in found_agents.items():
        # Sanitize filename
        safe_name = "".join([c if c.isalnum() else "_" for c in name.lower()]).strip("_")
        agent_file = os.path.join(AGENTS_DIR, f"{safe_name}.md")
        
        content = f"# Agent: {name}\n\n"
        content += f"- **Role:** {data['role']}\n"
        content += f"- **Source:** `{data['source']}`\n"
        content += f"- **Description:**\n{data['description']}\n\n"
        content += "---\n*Status: Verified & Filed.*\n"
        
        with open(agent_file, "w") as af:
            af.write(content)
            
        inventory_md += f"## [{name}]({safe_name}.md)\n"
        inventory_md += f"- **Role:** {data['role']}\n"
        inventory_md += f"- **Source:** `{data['source']}`\n\n"

    with open(os.path.join(AGENTS_DIR, "inventory.md"), "w") as f:
        f.write(inventory_md)
        
    print(f"✅ Inventory complete. {len(found_agents)} agents registered in {AGENTS_DIR}.")

if __name__ == "__main__":
    compile_agent_inventory()
