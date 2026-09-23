"""Event tracking and observability for JARVIS runtime.

Implements event-based observability for monitoring execution flow,
state transitions, and operational events across the system.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional
from uuid import uuid4


class EventType(str, Enum):
    """Standard event types."""
    OPERATION_START = "operation_start"
    OPERATION_END = "operation_end"
    OPERATION_ERROR = "operation_error"
    STATE_CHANGE = "state_change"
    APPROVAL_REQUIRED = "approval_required"
    APPROVAL_GRANTED = "approval_granted"
    APPROVAL_DENIED = "approval_denied"
    MEMORY_UPDATED = "memory_updated"
    WORKFLOW_EXECUTED = "workflow_executed"
    MODULE_LOADED = "module_loaded"
    TOOL_EXECUTED = "tool_executed"


class EventSeverity(str, Enum):
    """Event severity levels."""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


@dataclass
class Event:
    """Represents a system event for observability."""
    event_id: str
    event_type: EventType
    timestamp: datetime
    severity: EventSeverity
    source: str
    message: str
    data: Dict[str, Any]
    corr_id: Optional[str] = None
    
    def __init__(
        self,
        event_type: EventType,
        source: str,
        message: str,
        severity: EventSeverity = EventSeverity.INFO,
        data: Optional[Dict[str, Any]] = None,
        corr_id: Optional[str] = None,
    ):
        self.event_id = str(uuid4())
        self.event_type = event_type
        self.timestamp = datetime.now(timezone.utc)
        self.severity = severity
        self.source = source
        self.message = message
        self.data = data or {}
        self.corr_id = corr_id or str(uuid4())
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert event to dictionary."""
        return {
            "event_id": self.event_id,
            "event_type": self.event_type.value,
            "timestamp": self.timestamp.isoformat(),
            "severity": self.severity.value,
            "source": self.source,
            "message": self.message,
            "data": self.data,
            "corr_id": self.corr_id,
        }


class EventCollector:
    """Collects and tracks system events."""
    
    def __init__(self, max_events: int = 1000):
        self.events: List[Event] = []
        self.max_events = max_events
        self.subscribers: List[callable] = []
    
    def record_event(self, event: Event) -> None:
        """Record a system event."""
        self.events.append(event)
        if len(self.events) > self.max_events:
            self.events.pop(0)
        
        for subscriber in self.subscribers:
            try:
                subscriber(event)
            except Exception:
                pass
    
    def subscribe(self, callback: callable) -> None:
        """Subscribe to events."""
        self.subscribers.append(callback)
    
    def get_events(
        self,
        event_type: Optional[EventType] = None,
        source: Optional[str] = None,
        severity: Optional[EventSeverity] = None,
        corr_id: Optional[str] = None,
    ) -> List[Event]:
        """Query events with optional filters."""
        results = self.events
        
        if event_type:
            results = [e for e in results if e.event_type == event_type]
        if source:
            results = [e for e in results if e.source == source]
        if severity:
            results = [e for e in results if e.severity == severity]
        if corr_id:
            results = [e for e in results if e.corr_id == corr_id]
        
        return results
    
    def clear(self) -> None:
        """Clear all events."""
        self.events.clear()


# Global event collector
_global_collector: Optional[EventCollector] = None


def get_event_collector() -> EventCollector:
    """Get or create global event collector."""
    global _global_collector
    if _global_collector is None:
        _global_collector = EventCollector()
    return _global_collector


__all__ = [
    "EventType",
    "EventSeverity",
    "Event",
    "EventCollector",
    "get_event_collector",
]
