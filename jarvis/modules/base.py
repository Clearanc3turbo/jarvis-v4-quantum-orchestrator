"""Base class for specialist modules."""

from __future__ import annotations

from typing import Any, Optional


class BaseModule:
    """Base class for specialist modules."""

    name: str = "base"

    def initialize(self) -> None:
        """Initialize the module."""
        pass

    def run(self, task: Any, context: Optional[Any] = None) -> Any:
        """Run the module."""
        raise NotImplementedError

    def register_tools(self, registry: Any) -> None:
        """Register tools with the registry."""
        pass

    def health_check(self) -> dict[str, Any]:
        """Return health status."""
        return {"status": "ok", "module": self.name}
