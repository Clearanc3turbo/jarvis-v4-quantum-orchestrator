"""Trace context and correlation for observability.

Provides correlation IDs and trace context for tracking operations
across distributed components and async execution boundaries.
"""

from __future__ import annotations

from typing import Optional, Dict, Any
from uuid import uuid4
from contextvars import ContextVar


# Context variable for trace context (thread-safe and async-safe)
_trace_context: ContextVar[Optional[TraceContext]] = ContextVar('trace_context', default=None)


class TraceContext:
    """Context object for request/operation correlation and tracing."""
    
    def __init__(self, trace_id: Optional[str] = None, parent_id: Optional[str] = None):
        self.trace_id = trace_id or str(uuid4())
        self.parent_id = parent_id
        self.span_id = str(uuid4())
        self.metadata: Dict[str, Any] = {}
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert context to dictionary."""
        return {
            "trace_id": self.trace_id,
            "parent_id": self.parent_id,
            "span_id": self.span_id,
            "metadata": dict(self.metadata),
        }
    
    def create_child(self) -> TraceContext:
        """Create a child context for nested operations."""
        return TraceContext(trace_id=self.trace_id, parent_id=self.span_id)
    
    @staticmethod
    def get_current() -> Optional[TraceContext]:
        """Get current trace context if set."""
        return _trace_context.get()
    
    @staticmethod
    def set_current(context: Optional[TraceContext]) -> None:
        """Set current trace context."""
        _trace_context.set(context)


__all__ = ["TraceContext"]
