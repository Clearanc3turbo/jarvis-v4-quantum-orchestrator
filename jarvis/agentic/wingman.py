"""Approval-aware Wingman orchestration with sanitized audit records."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from jarvis.agentic.policy import ActionPolicy, ApprovalState
from jarvis.execution.plan import ExecutionPlan, PlannedAction
from jarvis.security.audit import AuditLog
from jarvis.security.guardrails import PromptGuardrail


@dataclass
class WingmanAgent:
    guardrail: PromptGuardrail = field(default_factory=PromptGuardrail)
    policy: ActionPolicy = field(default_factory=ActionPolicy)
    audit: AuditLog = field(default_factory=AuditLog)

    def plan(self, goal: str, domain: str = "agentic") -> ExecutionPlan:
        normalized = goal.strip() if isinstance(goal, str) else ""
        if not normalized:
            raise ValueError("goal is required")
        return ExecutionPlan(
            goal=normalized,
            domain=domain,
            actions=(
                PlannedAction("read_context", "memory_lookup", {"query": normalized}, "low"),
                PlannedAction("verify_constraints", "guardrail_check", {"prompt": normalized}, "low"),
                PlannedAction("produce_response", "synthesize", {"goal": normalized, "domain": domain}, "medium"),
            ),
            rationale="Safe, reviewable agentic planning flow",
        )

    def execute(self, goal: str, *, domain: str = "agentic", approve: bool = False) -> dict[str, Any]:
        allowed, issues = self.guardrail.screen(goal)
        if not allowed:
            self.audit.record("plan", "blocked", {"reason_count": len(issues)})
            return {"status": "blocked", "approved": False, "goal": goal, "issues": list(issues), "audit": self.audit.entries}
        plan = self.plan(goal, domain)
        decisions = []
        for action in plan.actions:
            decision = self.policy.evaluate(action)
            state = decision.state
            if state == ApprovalState.PENDING and approve:
                state = self.policy.approve(action)
            decisions.append({"action": action.name, "state": state.value, "risk": decision.risk})
            self.audit.record(action.name, state.value, {"risk": decision.risk})
        pending = any(item["state"] == ApprovalState.PENDING.value for item in decisions)
        return {"status": "pending_approval" if pending else "ok", "approved": not pending, "goal": plan.goal, "plan": plan.to_dict(), "audit": self.audit.entries}
