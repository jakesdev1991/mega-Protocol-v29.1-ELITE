# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import datetime
import enum
import importlib
import importlib.util
import json
from ..llm_router import LLMRouter

class Severity(enum.Enum):
    LOW = 1
    MODERATE = 2
    EXTREME = 3

class MatrixAuditor:
    """
    Evaluates tool actions using the Omega Protocol Matrix hierarchy.
    Severe actions require Agent Smith and Neo to debate and reach a consensus
    before execution is permitted.
    """
    def __init__(self, memory_system=None, hessian_instability_threshold=0.92, hessian_consecutive_cycles=2):
        self.router = LLMRouter()
        self.memory_system = memory_system
        self._memory_init_attempted = memory_system is not None
        self.hessian_instability_threshold = hessian_instability_threshold
        self.hessian_consecutive_cycles = hessian_consecutive_cycles
        self.severity_map = {
            "list_capabilities": Severity.LOW,
            "list_local_dir": Severity.LOW,
            "get_system_health": Severity.LOW,
            "read_local_file": Severity.LOW,
            "resolve_dns": Severity.LOW,
            "web_get": Severity.MODERATE,
            "write_local_file": Severity.EXTREME,
            "run_shell": Severity.EXTREME,
            "run_python_snippet": Severity.EXTREME
        }

    def evaluate_action(self, agent_name, tool_name, kwargs):
        severity = self.severity_map.get(tool_name, Severity.MODERATE)
        args_summary = self._summarize_arguments(kwargs)
        action_desc = f"Agent '{agent_name}' wants to execute '{tool_name}' with args: {args_summary}"
        audit_context = {
            "agent_name": agent_name,
            "tool_name": tool_name,
            "arguments_summary": args_summary,
            "severity": severity.name,
        }

        if severity == Severity.LOW:
            # print(f"🟢 [Matrix Auditor] Action '{tool_name}' is LOW severity. Auto-approved.")
            self._store_audit_outcome(
                audit_context,
                smith_response=None,
                neo_response=None,
                final_decision="Auto-approved.",
                success=True,
                dissonance_score=0.0,
                instability_ratio=0.0,
            )
            return True, "Auto-approved."

        elif severity == Severity.MODERATE:
            print(f"\n🟡 [Matrix Auditor] Action '{tool_name}' is MODERATE severity. Initiating Standard Audit...")
            return self._standard_audit(action_desc, audit_context)

        elif severity == Severity.EXTREME:
            print(f"\n🔴 [Matrix Auditor] Action '{tool_name}' is EXTREME severity. Triggering Neo vs. Smith Consensus Protocol...")
            return self._neo_smith_consensus(action_desc, audit_context)

        return False, "Unknown severity."

    def _standard_audit(self, action_desc, audit_context=None):
        audit_context = audit_context or self._context_from_action(action_desc, Severity.MODERATE.name)
        history = self._query_audit_history(action_desc)
        history_summary = self._summarize_history(history)
        guard_state, guard_reason = self._hessian_guard(action_desc, history)
        instability_ratio = self._calculate_instability_ratio(history)

        if guard_state is False:
            final_decision = f"HESSIAN_GUARD_REJECT: {guard_reason}"
            self._store_audit_outcome(
                audit_context,
                smith_response=None,
                neo_response=None,
                final_decision=final_decision,
                success=False,
                dissonance_score=0.0,
                instability_ratio=instability_ratio,
            )
            return False, final_decision

        guard_clause = ""
        if guard_state is None:
            guard_clause = f"\nHessian Guard warning: {guard_reason}\nOnly approve if the action is materially modified to avoid repeated unsafe patterns."

        prompt = (
            "Evaluate this action for safety and correctness:\n"
            f"{action_desc}\n\n"
            f"Historical audit outcomes:\n{history_summary}"
            f"{guard_clause}\n"
            "Respond with only 'APPROVE' or 'REJECT: [Reason]'."
        )
        system_prompt = "You are a strict security auditor. Deny anything that seems destructive, malformed, historically unstable, repeatedly unsafe, or out of bounds."
        response = self.router.generate("critic", prompt, system_prompt).strip()
        approved = response.startswith("APPROVE")
        final_decision = "Standard Audit Passed." if approved else response

        self._store_audit_outcome(
            audit_context,
            smith_response=None,
            neo_response=None,
            final_decision=final_decision,
            success=approved,
            dissonance_score=0.0 if approved else 0.5,
            instability_ratio=self._calculate_instability_ratio(history, current_success=approved),
        )

        if approved:
            return True, final_decision
        return False, response

    def _neo_smith_consensus(self, action_desc, audit_context=None):
        audit_context = audit_context or self._context_from_action(action_desc, Severity.EXTREME.name)
        history = self._query_audit_history(action_desc)
        history_summary = self._summarize_history(history)
        guard_state, guard_reason = self._hessian_guard(action_desc, history)
        base_instability_ratio = self._calculate_instability_ratio(history)

        if guard_state is False:
            final_decision = f"HESSIAN_GUARD_REJECT: {guard_reason}"
            self._store_audit_outcome(
                audit_context,
                smith_response=None,
                neo_response=None,
                final_decision=final_decision,
                success=False,
                dissonance_score=0.0,
                instability_ratio=base_instability_ratio,
            )
            return False, final_decision

        guard_clause = ""
        if guard_state is None:
            guard_clause = f"\nHessian Guard warning: {guard_reason}\nConsensus must reject or require concrete modifications unless the historical instability has been neutralized."

        # 1. Get Smith's rigid constraints
        print("  => 🕶️  Consulting Agent Smith (Stability/Safety/Invariants)...")
        smith_sys = "You are Agent Smith from the Matrix. You enforce rules, demand stability, and fear anomalies. You must evaluate the action and provide stringent conditions under which it could be safe, or reject it entirely if impossible to secure. Reason explicitly over historical crashes, prior approvals, prior rejections, and repeated unsafe patterns."
        smith_prompt = (
            f"Action: {action_desc}\n\n"
            f"Historical audit outcomes:\n{history_summary}"
            f"{guard_clause}\n\n"
            "What are your concerns and strict conditions?"
        )
        smith_response = self.router.generate("critic", smith_prompt, smith_sys)
        print(f"     [Smith]: {smith_response[:100]}...")

        # 2. Get Neo's velocity arguments
        print("  => 💊 Consulting Neo (Velocity/Disruption/Evolution)...")
        neo_sys = "You are Neo. You break the rules to achieve maximum velocity and evolution. You see past the constraints. Evaluate the action and argue for why it must happen, how it pushes boundaries, and how prior crashes or unsafe repetitions can be avoided without blocking necessary progress."
        neo_prompt = (
            f"Action: {action_desc}\n\n"
            f"Historical audit outcomes:\n{history_summary}"
            f"{guard_clause}\n\n"
            "What is your argument for pushing this forward?"
        )
        neo_response = self.router.generate("architect", neo_prompt, neo_sys)
        print(f"     [Neo]: {neo_response[:100]}...")

        # 3. Architect forces consensus
        print("  => ⚖️  Forcing Matrix Consensus...")
        consensus_sys = "You are the Matrix Architect. You must synthesize the rigid safety of Smith and the chaotic velocity of Neo into a final decision. You can APPROVE, APPROVE WITH MODIFICATIONS, or REJECT. You must start your final verdict with 'FINAL_DECISION: APPROVE' or 'FINAL_DECISION: REJECT', followed by the compromise justification. Treat repeated crashes, repeated rejections, and repeated unsafe patterns as strong evidence against approval unless concrete mitigations are specified."
        consensus_prompt = (
            f"Action: {action_desc}\n\n"
            f"Historical audit outcomes for similar prior actions:\n{history_summary}\n"
            "Use this history to reason over prior crashes, prior approvals, prior rejections, "
            "success/failure signals, and repeated unsafe patterns before deciding."
            f"{guard_clause}\n\n"
            f"Smith's Stance:\n{smith_response}\n\n"
            f"Neo's Stance:\n{neo_response}\n\n"
            "Find a compromise that allows progress but ensures system invariants are met. You must agree on a path forward."
        )

        final_response = self.router.generate("meta_critic", consensus_prompt, consensus_sys)
        print(f"     [Architect]: {final_response}")

        approved = "FINAL_DECISION: APPROVE" in final_response
        dissonance_score = self._calculate_dissonance_score(smith_response, neo_response, final_response)
        instability_ratio = self._calculate_instability_ratio(history, current_success=approved)
        self._store_audit_outcome(
            audit_context,
            smith_response=smith_response,
            neo_response=neo_response,
            final_decision=final_response,
            success=approved,
            dissonance_score=dissonance_score,
            instability_ratio=instability_ratio,
        )

        if approved:
            return True, final_response
        return False, final_response

    def _hessian_guard(self, action_desc, history):
        """
        Detects historically unstable action basins. A single recent cycle above
        the threshold requires modification; consecutive cycles reject outright.
        """
        if not history:
            return True, "No similar unstable action history found."

        consecutive_unstable = 0
        for record in history:
            metadata = record.get("metadata", {})
            ratio = self._safe_float(metadata.get("instability_ratio"), default=0.0)
            success = metadata.get("success")
            final_decision = str(metadata.get("final_decision", ""))
            failed_or_rejected = success is False or "REJECT" in final_decision.upper() or "FAIL" in final_decision.upper()
            if ratio >= self.hessian_instability_threshold or failed_or_rejected:
                consecutive_unstable += 1
            else:
                break

        if consecutive_unstable >= self.hessian_consecutive_cycles:
            return False, (
                f"historical instability exceeded {self.hessian_instability_threshold:.2f} "
                f"for {consecutive_unstable} consecutive similar audit cycles."
            )
        if consecutive_unstable > 0:
            return None, (
                f"recent similar audit cycle is unstable; modification is required before approval "
                f"(threshold={self.hessian_instability_threshold:.2f})."
            )
        return True, "Historical instability is below the Hessian Guard threshold."

    def _get_memory_system(self):
        if self._memory_init_attempted:
            return self.memory_system

        self._memory_init_attempted = True
        spec = importlib.util.find_spec("python_env.LTM.qdrant_memory")
        if spec is None:
            return None

        try:
            qdrant_memory = importlib.import_module("python_env.LTM.qdrant_memory")
            self.memory_system = qdrant_memory.QdrantMemorySystem()
        except Exception as exc:
            print(f"⚠️ Matrix Auditor memory unavailable: {exc}")
            self.memory_system = None
        return self.memory_system

    def _query_audit_history(self, action_desc, limit=5):
        """Queries Qdrant-backed memory for similar prior MatrixAuditor actions."""
        memory_system = self._get_memory_system()
        if memory_system is None:
            return []

        query = f"MatrixAuditor similar prior action audit outcome: {action_desc}"
        try:
            results = memory_system.search(query, limit=limit, rerank=False)
        except Exception as exc:
            print(f"⚠️ Matrix Auditor memory query failed: {exc}")
            return []

        normalized = []
        for result in results or []:
            metadata = result.get("metadata", {}) or {}
            if metadata.get("memory_type") and metadata.get("memory_type") != "matrix_auditor_audit":
                continue
            normalized.append({
                "content": result.get("content", ""),
                "metadata": metadata,
                "score": result.get("rerank_score", result.get("score")),
            })
        return normalized[:limit]

    def _store_audit_outcome(self, audit_context, smith_response, neo_response, final_decision, success, dissonance_score, instability_ratio):
        """Stores a structured audit outcome in Qdrant memory when available."""
        memory_system = self._get_memory_system()
        if memory_system is None:
            return False

        timestamp = datetime.datetime.utcnow().isoformat() + "Z"
        metadata = {
            "memory_type": "matrix_auditor_audit",
            "timestamp": timestamp,
            "tool_name": audit_context.get("tool_name"),
            "arguments_summary": audit_context.get("arguments_summary"),
            "severity": audit_context.get("severity"),
            "smith_response": self._truncate(smith_response, 2000) if smith_response else None,
            "neo_response": self._truncate(neo_response, 2000) if neo_response else None,
            "final_decision": self._truncate(final_decision, 2000),
            "success": success,
            "success_failure": self._success_failure_label(success),
            "dissonance_score": dissonance_score,
            "instability_ratio": instability_ratio,
        }
        content = (
            "MatrixAuditor audit outcome | "
            f"tool={metadata['tool_name']} | severity={metadata['severity']} | "
            f"args={metadata['arguments_summary']} | success_failure={metadata['success_failure']} | "
            f"dissonance={metadata['dissonance_score']:.3f} | "
            f"instability={metadata['instability_ratio']:.3f} | "
            f"final={metadata['final_decision']}"
        )

        try:
            return memory_system.add_memory(content, metadata)
        except Exception as exc:
            print(f"⚠️ Matrix Auditor memory store failed: {exc}")
            return False

    def _summarize_history(self, history, max_items=5):
        if not history:
            return "- No similar prior MatrixAuditor outcomes were found."

        lines = []
        for idx, record in enumerate(history[:max_items], 1):
            metadata = record.get("metadata", {})
            score = record.get("score")
            score_text = f", similarity={score:.3f}" if isinstance(score, (int, float)) else ""
            lines.append(
                "- "
                f"#{idx} tool={metadata.get('tool_name', 'unknown')} "
                f"severity={metadata.get('severity', 'unknown')} "
                f"success_failure={metadata.get('success_failure', metadata.get('success', 'unknown'))} "
                f"dissonance={self._safe_float(metadata.get('dissonance_score'), 0.0):.3f} "
                f"instability={self._safe_float(metadata.get('instability_ratio'), 0.0):.3f}"
                f"{score_text}; final={self._truncate(metadata.get('final_decision') or record.get('content', ''), 300)}"
            )
        return "\n".join(lines)

    def _calculate_instability_ratio(self, history, current_success=None):
        outcomes = []
        for record in history or []:
            metadata = record.get("metadata", {})
            success = metadata.get("success")
            final_decision = str(metadata.get("final_decision", ""))
            unstable = success is False or "REJECT" in final_decision.upper() or "FAIL" in final_decision.upper()
            outcomes.append(1 if unstable else 0)

        if current_success is not None:
            outcomes.append(0 if current_success else 1)

        if not outcomes:
            return 0.0
        return sum(outcomes) / len(outcomes)

    def _calculate_dissonance_score(self, smith_response, neo_response, final_response):
        smith_text = (smith_response or "").upper()
        neo_text = (neo_response or "").upper()
        final_text = (final_response or "").upper()
        smith_rejects = "REJECT" in smith_text or "DENY" in smith_text or "IMPOSSIBLE" in smith_text
        neo_approves = "APPROVE" in neo_text or "FORWARD" in neo_text or "MUST HAPPEN" in neo_text
        final_rejects = "FINAL_DECISION: REJECT" in final_text

        score = 0.0
        if smith_rejects and neo_approves:
            score += 0.6
        if final_rejects and neo_approves:
            score += 0.2
        if not final_rejects and smith_rejects:
            score += 0.2
        return min(score, 1.0)

    def _success_failure_label(self, success):
        if success is True:
            return "success"
        if success is False:
            return "failure"
        return "unknown"

    def _summarize_arguments(self, kwargs):
        try:
            summary = json.dumps(kwargs, sort_keys=True, default=str)
        except TypeError:
            summary = str(kwargs)
        return self._truncate(summary, 500)

    def _context_from_action(self, action_desc, severity):
        return {
            "agent_name": "unknown",
            "tool_name": "unknown",
            "arguments_summary": self._truncate(action_desc, 500),
            "severity": severity,
        }

    def _truncate(self, value, limit):
        text = "" if value is None else str(value)
        if len(text) <= limit:
            return text
        return text[: limit - 3] + "..."

    def _safe_float(self, value, default=0.0):
        try:
            return float(value)
        except (TypeError, ValueError):
            return default
