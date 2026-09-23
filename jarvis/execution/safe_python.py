"""Task and execution plan representations."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Mapping


@dataclass(frozen=True)
class PlannedAction:
    name: str
    tool: str
    arguments: Mapping[str, Any]
    risk: str = "low"
    requires_approval: bool = False

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "tool": self.tool,
            "arguments": dict(self.arguments),
            "risk": self.risk,
            "requires_approval": self.requires_approval,
        }


@dataclass(frozen=True)
class ExecutionPlan:
    goal: str
    domain: str
    actions: tuple[PlannedAction, ...] = field(default_factory=tuple)
    rationale: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "goal": self.goal,
            "domain": self.domain,
            "actions": [action.to_dict() for action in self.actions],
            "rationale": self.rationale,
        }
