"""Policy decisions and explicit approval state transitions."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any, Mapping, Union


class RiskLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class ApprovalState(str, Enum):
    ALLOWED = "allowed"
    PENDING = "pending_approval"
    APPROVED = "approved"
    DENIED = "denied"


@dataclass(frozen=True)
class PolicyDecision:
    risk: str
    state: ApprovalState
    requires_approval: bool = False  # For compatibility


class ActionPolicy:
    def evaluate(self, action: Union[Mapping[str, Any], Any]) -> PolicyDecision:
        # Handle both dict and PlannedAction objects
        if isinstance(action, dict):
            tool = str(action.get("tool", "")).casefold()
            name = str(action.get("name", "")).casefold()
        else:
            tool = str(getattr(action, "tool", "")).casefold()
            name = str(getattr(action, "name", "")).casefold()

        if tool in {"shell", "subprocess", "bash", "cmd", "powershell", "delete_file"} or name in {"read_secret", "write_secret"}:
            return PolicyDecision(RiskLevel.HIGH.value, ApprovalState.PENDING, requires_approval=True)
        if tool in {"network", "http", "api_call", "write_file", "rename_file", "synthesize"}:
            return PolicyDecision(RiskLevel.MEDIUM.value, ApprovalState.PENDING, requires_approval=True)
        return PolicyDecision(RiskLevel.LOW.value, ApprovalState.ALLOWED, requires_approval=False)

    def approve(self, action: Union[Mapping[str, Any], Any]) -> ApprovalState:
        decision = self.evaluate(action)
        if decision.state == ApprovalState.PENDING:
            return ApprovalState.APPROVED
        return decision.state

    def deny(self, action: Union[Mapping[str, Any], Any]) -> ApprovalState:
        return ApprovalState.DENIED
