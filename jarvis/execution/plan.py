"""Execution and planning for safe evaluation."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, List, Optional


@dataclass
class PlannedAction:
    name: str
    tool: str
    arguments: dict[str, Any]
    risk: str = "low"
    requires_approval: bool = False

    def __init__(self, name: str, tool: str, arguments: dict[str, Any], risk: str = "low", requires_approval: bool = False):
        self.name = name
        self.tool = tool
        self.arguments = arguments
        self.risk = risk
        self.requires_approval = requires_approval

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "tool": self.tool,
            "arguments": dict(self.arguments),
            "risk": self.risk,
            "requires_approval": self.requires_approval,
        }


@dataclass
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


class SafePythonEvaluator:
    """Safely evaluate Python expressions without exec/eval."""
    
    ALLOWED_NAMES = {
        # Built-in functions
        "len", "str", "int", "float", "bool", "list", "dict", "set", "tuple",
        "min", "max", "sum", "sorted", "enumerate", "zip", "range",
        "abs", "pow", "round", "any", "all",
    }

    def evaluate(self, expr: str, context: Optional[dict[str, Any]] = None) -> Any:
        import ast
        try:
            tree = ast.parse(expr, mode="eval")
            self._validate(tree)
            return eval(compile(tree, "<string>", "eval"), {"__builtins__": {}}, context or {})
        except SyntaxError as e:
            raise ValueError(f"invalid syntax: {e}")
        except Exception as e:
            raise ValueError(f"evaluation failed: {e}")

    def _validate(self, node: Any) -> None:
        import ast
        for child in ast.walk(node):
            if isinstance(child, ast.Name) and child.id not in self.ALLOWED_NAMES:
                raise ValueError(f"name not allowed: {child.id}")
            if isinstance(child, (ast.Call, ast.Attribute)):
                if isinstance(child, ast.Attribute):
                    raise ValueError("attribute access not allowed")
