"""Tool registry for JARVIS."""

from __future__ import annotations

from typing import Any, Callable, Dict, Optional


class ToolRegistry:
    """Registry for managing tools and their metadata."""

    def __init__(self):
        self._tools: Dict[str, Dict[str, Any]] = {}

    def register(self, name: str, func: Callable, description: str = "") -> None:
        """Register a tool."""
        self._tools[name] = {"func": func, "description": description}

    def execute(self, name: str, **kwargs: Any) -> Any:
        """Execute a registered tool."""
        if name not in self._tools:
            raise ValueError(f"tool not found: {name}")
        return self._tools[name]["func"](**kwargs)

    def list(self) -> Dict[str, str]:
        """List all registered tools."""
        return {name: info.get("description", "") for name, info in self._tools.items()}
