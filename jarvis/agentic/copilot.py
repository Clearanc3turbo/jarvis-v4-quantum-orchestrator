"""Agentic Wingman orchestration layer."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Mapping

from jarvis.agentic.policy import ActionPolicy
from jarvis.execution.plan import ExecutionPlan, PlannedAction
from jarvis.security.guardrails import PromptGuardrail


@dataclass
class WingmanAgent:
    """Coordinates planning, guardrails, policy enforcement, and execution audit."""

    guardrail: PromptGuardrail = field(default_factory=PromptGuardrail)
    policy: ActionPolicy = field(default_factory=ActionPolicy)

    def plan(self, goal: str, domain: str = "agentic") -> ExecutionPlan:
        normalized = goal.strip()
        if not normalized:
            raise ValueError("goal is required")

        actions: list[PlannedAction] = [
            PlannedAction(
                name="read_context",
                tool="memory_lookup",
                arguments={"query": normalized},
                risk="low",
                requires_approval=False,
            ),
            PlannedAction(
                name="verify_constraints",
                tool="guardrail_check",
                arguments={"prompt": normalized},
                risk="low",
                requires_approval=False,
            ),
            PlannedAction(
                name="produce_response",
                tool="synthesize",
                arguments={"goal": normalized, "domain": domain},
                risk="medium",
                requires_approval=False,
            ),
        ]
        return ExecutionPlan(goal=normalized, domain=domain, actions=tuple(actions), rationale="Safe agentic planning flow")

    def execute(self, goal: str, *, require_approval: bool = False, domain: str = "agentic") -> dict[str, Any]:
        allowed, issues = self.guardrail.screen(goal)
        if not allowed:
            return {
                "approved": False,
                "status": "blocked",
                "goal": goal,
                "issues": issues,
                "plan": None,
            }

        plan = self.plan(goal, domain=domain)
        audit = []
        for action in plan.actions:
            policy_result = self.policy.evaluate(action)
            if policy_result.requires_approval and (require_approval or policy_result.risk == "high"):
                audit.append({"action": action.name, "status": "awaiting_approval", "risk": policy_result.risk})
                continue
            audit.append({"action": action.name, "status": "allowed", "risk": policy_result.risk})

        approved = all(item["status"] != "awaiting_approval" for item in audit)
        return {
            "approved": approved,
            "status": "ok" if approved else "pending_approval",
            "goal": goal,
            "issues": [],
            "plan": [action.to_dict() for action in plan.actions],
            "audit": audit,
        }
