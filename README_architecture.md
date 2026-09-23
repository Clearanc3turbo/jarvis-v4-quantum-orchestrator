"""Event stubs for runtime lifecycle notices."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class RuntimeEvent:
    kind: str
    message: str


__all__ = ["RuntimeEvent"]
