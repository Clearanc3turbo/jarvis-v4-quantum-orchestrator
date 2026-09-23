"""Simple trace helpers for runtime tracking."""

from __future__ import annotations

from uuid import uuid4


class TraceContext:
    """Context object for correlation IDs."""

    def __init__(self, trace_id: str | None = None):
        self.trace_id = trace_id or str(uuid4())


__all__ = ["TraceContext"]
