"""Risk policy and approval checks for agentic actions."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any, Mapping


class RiskLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


@dataclass(frozen=True)
class PolicyDecision:
    risk: str
    requires_approval: bool


class ActionPolicy:
    """Deny-by-default policy for risky shell, network, and credential-sensitive work."""

    def evaluate(self, action: Mapping[str, Any]) -> PolicyDecision:
        name = str(action.get("name", "")).lower()
        tool = str(action.get("tool", "")).lower()
        risk = "low"

        if tool in {"shell", "subprocess", "bash", "cmd", "powershell", "curl", "wget"}:
            risk = "high"
        elif tool in {"network", "http", "web_request", "api_call"}:
            risk = "medium"
        elif tool in {"write_file", "delete_file", "rename_file"}:
            risk = "medium"
        elif name in {"export_env", "write_secret", "read_secret"}:
            risk = "high"

        requires_approval = risk in {"medium", "high"}
        return PolicyDecision(risk=risk, requires_approval=requires_approval)
