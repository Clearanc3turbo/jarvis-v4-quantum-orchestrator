"""Simple metrics stubs for JARVIS runtime instrumentation."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class Metrics:
    calls: int = 0
    failures: int = 0
    metadata: dict[str, str] = field(default_factory=dict)

    def record_call(self) -> None:
        self.calls += 1

    def record_failure(self) -> None:
        self.failures += 1


__all__ = ["Metrics"]
