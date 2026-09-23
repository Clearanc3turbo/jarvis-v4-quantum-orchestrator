"""Observability, logging, metrics, and events for JARVIS runtime.

Comprehensive observability stack including structured logging with audit
trails, performance metrics collection, system event tracking, and trace context.
"""

from __future__ import annotations

from jarvis.observability.logging import (
    LogLevel,
    AuditEvent,
    StructuredLogger,
    trace_calls,
    get_logger,
)
from jarvis.observability.metrics import (
    PerformanceMetrics,
    MetricsCollector,
    get_collector,
)
from jarvis.observability.events import (
    EventType,
    EventSeverity,
    Event,
    EventCollector,
    get_event_collector,
)
from jarvis.observability.traces import TraceContext


__all__ = [
    # Logging
    "LogLevel",
    "AuditEvent",
    "StructuredLogger",
    "trace_calls",
    "get_logger",
    # Metrics
    "PerformanceMetrics",
    "MetricsCollector",
    "get_collector",
    # Events
    "EventType",
    "EventSeverity",
    "Event",
    "EventCollector",
    "get_event_collector",
    # Traces
    "TraceContext",
]
