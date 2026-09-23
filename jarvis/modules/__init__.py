"""Registry for tool execution in JARVIS."""

from __future__ import annotations

from typing import Any, Callable, Dict


class ToolRegistry:
    """Simple registry that resolves named tool callbacks."""

    def __init__(self):
        self._tools: Dict[str, Callable[..., Any]] = {}

    def register(self, name: str, fn: Callable[..., Any]):
        self._tools[name] = fn

    def execute(self, name: str, **kwargs: Any):
        if name not in self._tools:
            return f"[tool not found: {name}]"
        return self._tools[name](**kwargs)

    def list_tools(self) -> list[str]:
        return sorted(self._tools.keys())
