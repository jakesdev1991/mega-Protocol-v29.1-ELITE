# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
from .llm_router import LLMRouter
from .tools.registry import registry
import os
import json
import sqlite3
import datetime
import re

from .framework import SharedConsensusMemory, MemoryRecord

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
DB_PATH = os.path.join(PROJECT_ROOT, 'LTM', 'memories.db')

class Agent:
    """Base Agent class representing a worker/brain in the hierarchy with Dual-Layer Memory."""
    
    def __init__(self, name, role, system_prompt):
        self.name = name
        self.role = role
        self.system_prompt = system_prompt
        self.router = LLMRouter()
        self.memory = []
        self.expert_context = []
        
        # Access to Global Tool Registry
        self.tools = registry
        
        # New v2 memory integration
        self.scm = SharedConsensusMemory(db_path=DB_PATH)
        
        # Ensure special logs directory exists
        self.special_logs_dir = os.path.join(PROJECT_ROOT, "agent_zero", "knowledge", "special_logs")
        os.makedirs(self.special_logs_dir, exist_ok=True)

    def use_tool(self, tool_name, **kwargs):
        """Allows the agent to execute a physical action via the registry."""
        print(f"🛠️ [{self.name}] Invoking Tool: {tool_name} with {kwargs}")
        kwargs["_agent_name"] = self.name
        return self.tools.invoke(tool_name, **kwargs)

    def _get_special_log_path(self, agent_name=None):
        target = agent_name if agent_name else self.name
        return os.path.join(self.special_logs_dir, f"{target.lower()}_special.jsonl")

    def _access_special_logs(self, query_text):
        """
        Special logic: If any special log is mentioned by name in the query, 
        aggregate them (e.g., 'special log Alpha' + 'special log Scraper').
        """
        aggregated_data = ""
        # Look for patterns like "special log [Name]"
        found_agents = re.findall(r"special log (\w+)", query_text, re.IGNORECASE)
        
        if found_agents:
            print(f"🔓 [Memory] Accessing Special Logs for: {found_agents}")
            for agent in found_agents:
                path = self._get_special_log_path(agent)
                if os.path.exists(path):
                    with open(path, "r", encoding="utf-8") as f:
                        # Grab last 10 entries for context
                        lines = f.readlines()[-10:]
                        aggregated_data += f"\n--- SPECIAL LOG: {agent} ---\n" + "".join(lines)
        
        return aggregated_data

    def reason(self, task, depth="standard", aggressive=False):
        """Execute reasoning with deep context, tool awareness, and memory reflection."""
        print(f"\n[{self.name} | {self.role.upper()}] Reasoning (Depth: {depth}, Aggressive: {aggressive})...")
        
        # 1. Fetch Shared Context from Vector DB
        shared_context = self._query_shared_memory(task)
        
        # 2. Fetch/Aggregate Special Logs
        special_context = self._access_special_logs(task)
        
        # 3. Inject Tool Manifest
        # Dynamically list all tools (including linked scripts) and other agents
        tool_manifest = json.dumps(self.tools.list_tools(), indent=2)
        
        # Build nuanced prompt
        past_memory = "\n".join([f"Previous Action: {m}" for m in self.memory[-5:]])
        expert_injection = "\n".join([f"EXPERT REMINDER: {k}" for k in self.expert_context])
        
        nuanced_prompt = f"""
        ### SOVEREIGN TOOL BELT (Capabilities)
        You have direct access to the following tools. 
        To use a tool, wrap your request in: [[TOOL_CALL: tool_name(arg1="val")]]
        
        AVAILABLE TOOLS:
        {tool_manifest}
        
        ### CONTEXTUAL AWARENESS
        {shared_context}
        {special_context}
        
        ### EXPERT KNOWLEDGE
        {expert_injection}
        
        ### RECENT HISTORY
        {past_memory}
        
        ### ACTIVE TASK
        {task}

        Perform deep technical reasoning. If a tool is required to solve the task, call it.
        Reflect on how this action affects the overall Omega Protocol Φ density.
        """
        
        if aggressive:
            response = self.router.nvidia.rotate_chat(nuanced_prompt, self.system_prompt)
        else:
            response = self.router.generate(self.role, nuanced_prompt, self.system_prompt)
        
        # 4. Handle tool calls if detected in the response
        if "[[TOOL_CALL:" in response:
            response = self._process_tool_calls(response)

        # 5. Meta-Cognitive Reflection
        reflection = self.reflect(task, response)
        
        # 6. ROBUST LOGGING
        self._log_robust_memory(task, response, reflection)
        
        self.memory.append(f"Task: {task} | Response: {response}")
        return response

    def _process_tool_calls(self, response):
        """Regex-based extraction and execution of tool calls from LLM output."""
        pattern = r"\[\[TOOL_CALL: (\w+)\((.*)\)\]\]"
        matches = re.findall(pattern, response)
        
        for tool_name, args_str in matches:
            try:
                # Basic parsing for string/numeric arguments
                # Note: For complex objects, a more robust JSON-based parser would be needed
                kwargs = {}
                if args_str.strip():
                    # Simple key="val" parser
                    arg_pairs = re.findall(r'(\w+)\s*=\s*["\'](.*?)["\']', args_str)
                    for k, v in arg_pairs:
                        kwargs[k] = v
                
                tool_result = self.use_tool(tool_name, **kwargs)
                response += f"\n\n--- TOOL OUTPUT ({tool_name}) ---\n{tool_result}"
            except Exception as e:
                response += f"\n\n--- TOOL ERROR ({tool_name}) ---\n{str(e)}"
        
        return response

    def reflect(self, task, response):
        """Internal Meta-Cognitive step to analyze methods and insights."""
        reflection_prompt = f"""
        Analyze your recent response:
        Task: {task}
        Response: {response}
        
        Provide a 3-part reflection:
        1. METHODS: What specific reasoning patterns did you use? (e.g. First Principles, Chain of Density)
        2. INSIGHTS: What was the most critical technical realization?
        3. EVOLUTION: How does this make you more skilled for future tasks?
        """
        reflection = self.router.generate("critic", reflection_prompt, "You are a Meta-Cognitive Analyst.")
        print(f"🧬 [{self.name}] Reflection Complete.")
        return reflection

    def _log_robust_memory(self, task, response, reflection):
        """Saves a rich, detailed record to both Private Special Log and Shared Consensus Memory."""
        timestamp = datetime.datetime.now().isoformat()
        
        memory_package = {
            "timestamp": timestamp,
            "agent": self.name,
            "role": self.role,
            "task": task,
            "thought_process": response,
            "reflection": reflection,
            "metadata": {
                "project": "Omega Protocol",
                "phi_n_relevance": "high"
            }
        }
        
        # A. Save to Private Special Log (JSONL)
        with open(self._get_special_log_path(), "a", encoding="utf-8") as f:
            f.write(json.dumps(memory_package) + "\n")
            
        # B. Save to Shared Consensus Memory (v2 unified pool)
        try:
            content = f"Agent {self.name} ({self.role}) performed task: {task}. Logic: {response}. Reflection: {reflection}"
            record = MemoryRecord(
                source=self.name,
                content=content,
                metadata=memory_package
            )
            self.scm.append(record)
        except Exception as e:
            print(f"⚠️ Shared Memory Update Failed: {e}")

    def _query_shared_memory(self, task):
        """Fetch relevant snippets from the shared consensus memory."""
        try:
            # Simple keyword search fallback for standard SQLite
            search_term = task.split()[0] if task.split() else None
            results = self.scm.read(query=search_term, limit=3, reader=self.name)
            if results:
                return "\n--- SHARED MEMORY RECALL ---\n" + "\n".join([r.content for r in results])
        except Exception as e:
            print(f"⚠️ Shared Memory Recall Failed: {e}")
        return ""

if __name__ == "__main__":
    # Test script logic
    from .llm_router import LLMRouter
    a = Agent("TestAgent", "writer", "You are a test.")
    print(a.reason("Say hello.", aggressive=True))
