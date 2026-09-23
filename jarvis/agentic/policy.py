"""Policy decisions and explicit approval state transitions."""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any, Mapping


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


class ActionPolicy:
    def evaluate(self, action: Mapping[str, Any]) -> PolicyDecision:
        tool = str(action.get("tool", "")).casefold()
        name = str(action.get("name", "")).casefold()
        if tool in {"shell", "subprocess", "bash", "cmd", "powershell", "delete_file"} or name in {"read_secret", "write_secret"}:
            return PolicyDecision(RiskLevel.HIGH.value, ApprovalState.PENDING)
        if tool in {"network", "http", "api_call", "write_file", "rename_file", "synthesize"}:
            return PolicyDecision(RiskLevel.MEDIUM.value, ApprovalState.PENDING)
        return PolicyDecision(RiskLevel.LOW.value, ApprovalState.ALLOWED)

    def approve(self, action: Mapping[str, Any]) -> ApprovalState:
        decision = self.evaluate(action)
        if decision.state == ApprovalState.PENDING:
            return ApprovalState.APPROVED
        return decision.state

    def deny(self, action: Mapping[str, Any]) -> ApprovalState:
        return ApprovalState.DENIED
