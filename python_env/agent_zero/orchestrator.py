# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import os
import re
import json
import importlib
import subprocess
from pathlib import Path
from .agent import Agent
from .tools.registry import registry, tool_link

class AgentOrchestrator:
    def __init__(self):
        self.inventory_dir = Path("/home/jake/Downloads/training/agents_inventory")
        self.tools_dir = Path("/home/jake/Downloads/training/python_env/tools")
        self.agents = {}
        self._load_inventory()
        self._link_tools()

    def _load_inventory(self):
        """Parses the agents_inventory directory and registers all meta-agents."""
        if not self.inventory_dir.exists():
            print(f"⚠️ Inventory directory {self.inventory_dir} not found.")
            return

        for md_file in self.inventory_dir.glob("*.md"):
            if md_file.name == "inventory.md":
                continue
                
            with open(md_file, "r") as f:
                content = f.read()
                
            # Extract Name, Role, Description via Regex
            name_match = re.search(r"# Agent: (.*)", content)
            role_match = re.search(r"- \*\*Role:\*\* (.*)", content)
            desc_match = re.search(r"- \*\*Description:\*\*\n(.*)---", content, re.DOTALL)
            
            if name_match and role_match:
                name = name_match.group(1).strip()
                role = role_match.group(1).strip()
                description = desc_match.group(1).strip() if desc_match else "No description provided."
                
                self.agents[name] = {
                    "role": role,
                    "prompt": description,
                    "file": md_file.name
                }
        print(f"🤖 [Orchestrator] Loaded {len(self.agents)} agents from inventory.")

    def _link_tools(self):
        """Scans the tools directory and creates dynamic tool wrappers for Python scripts."""
        if not self.tools_dir.exists():
            return

        python_tools = list(self.tools_dir.glob("*.py"))
        for tool_path in python_tools:
            tool_name = tool_path.stem
            
            # Create a closure to wrap the script execution
            def make_tool_func(path):
                def tool_func(args_string: str = ""):
                    """Dynamic wrapper for Omega Protocol tool."""
                    try:
                        cmd = [".venv/bin/python", str(path)]
                        if args_string:
                            cmd.extend(args_string.split())
                        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
                        return f"STDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}"
                    except Exception as e:
                        return f"Error running tool {path.name}: {str(e)}"
                
                tool_func.__name__ = f"tool_{tool_name}"
                tool_func.__doc__ = f"Executes the {tool_name} script from the Omega Tool Belt. Usage: tool_{tool_name}(args_string='--opt value')"
                return tool_func

            # Register with the global registry
            registry.register(make_tool_func(tool_path))
            
        print(f"🔧 [Orchestrator] Linked {len(python_tools)} scripts to the global Tool Registry.")

    def spawn(self, agent_name) -> Agent:
        """Instantiates an agent from the inventory."""
        if agent_name not in self.agents:
            raise ValueError(f"Agent '{agent_name}' not found in inventory.")
            
        data = self.agents[agent_name]
        return Agent(name=agent_name, role=data["role"], system_prompt=data["prompt"])

    def list_agents(self):
        return list(self.agents.keys())

# --- FRAMEWORK ENHANCEMENT: Tool-Aware Reasoning ---

@tool_link
def request_agent_assistance(agent_name: str, task: str):
    """Delegates a sub-task to another agent from the inventory."""
    orch = AgentOrchestrator()
    if agent_name not in orch.list_agents():
        return f"Error: Agent '{agent_name}' is not in the roster."
    
    sub_agent = orch.spawn(agent_name)
    print(f"🤝 [Delegation] {agent_name} is stepping in to help...")
    return sub_agent.reason(task)

if __name__ == "__main__":
    orch = AgentOrchestrator()
    print(f"Available Agents: {orch.list_agents()[:5]}...")
    print(f"Available Tools: {list(registry.tools.keys())[:5]}...")
