"""Base module interface for JARVIS specialist capabilities."""

from __future__ import annotations

from typing import Any, Dict, Optional


class BaseModule:
    """Shared contract used by all specialist modules."""

    name: str = "base"

    def initialize(self) -> None:
        """Perform necessary setup."""

    def health_check(self) -> bool:
        return True

    def run(self, task: Any, context: Optional[Dict[str, Any]] = None) -> Any:
        raise NotImplementedError("Module run() must be implemented by subclass.")

    def register_tools(self, registry: Any) -> None:
        """Register this module's tools with a runtime registry."""
