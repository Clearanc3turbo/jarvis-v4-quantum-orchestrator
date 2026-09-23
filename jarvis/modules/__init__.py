"""Shared base class for JARVIS modules."""

from __future__ import annotations

from typing import Any, Dict, Optional


class BaseModule:
    """Common interface for specialist modules."""

    name: str = "base"

    def initialize(self) -> None:
        """Perform one-time setup."""

    def health_check(self) -> bool:
        return True

    def run(self, task: Any, context: Optional[Dict[str, Any]] = None) -> Any:
        raise NotImplementedError("Subclasses must implement run().")

    def register_tools(self, registry: Any) -> None:
        """Register module-specific tools."""
