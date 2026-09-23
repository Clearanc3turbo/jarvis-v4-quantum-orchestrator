"""Comprehensive metrics collection and reporting for JARVIS.

Tracks performance metrics, execution statistics, and operational KPIs
across all components with structured storage and retrieval.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from collections import defaultdict


@dataclass
class PerformanceMetrics:
    """Performance statistics for an operation."""
    operation: str
    count: int = 0
    total_time_ms: float = 0.0
    min_time_ms: float = float('inf')
    max_time_ms: float = 0.0
    errors: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    @property
    def avg_time_ms(self) -> float:
        """Calculate average execution time."""
        return self.total_time_ms / self.count if self.count > 0 else 0.0
    
    @property
    def success_rate(self) -> float:
        """Calculate success rate as percentage."""
        total = self.count + self.errors
        return (self.count / total * 100) if total > 0 else 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert metrics to dictionary."""
        return {
            "operation": self.operation,
            "count": self.count,
            "errors": self.errors,
            "total_time_ms": round(self.total_time_ms, 2),
            "avg_time_ms": round(self.avg_time_ms, 2),
            "min_time_ms": round(self.min_time_ms, 2) if self.min_time_ms != float('inf') else 0.0,
            "max_time_ms": round(self.max_time_ms, 2),
            "success_rate_percent": round(self.success_rate, 1),
        }


class MetricsCollector:
    """Centralized metrics collection and reporting."""
    
    def __init__(self):
        self.metrics: Dict[str, PerformanceMetrics] = defaultdict(
            lambda: PerformanceMetrics(operation="")
        )
        self.start_times: Dict[str, float] = {}
        self.event_counters: Dict[str, int] = defaultdict(int)
    
    def record_operation(
        self,
        operation: str,
        duration_ms: float,
        success: bool = True,
        **metadata: Any
    ) -> None:
        """Record a single operation's metrics."""
        if operation not in self.metrics:
            self.metrics[operation] = PerformanceMetrics(operation=operation)
        
        metric = self.metrics[operation]
        metric.metadata.update(metadata)
        
        if success:
            metric.count += 1
            metric.total_time_ms += duration_ms
            metric.min_time_ms = min(metric.min_time_ms, duration_ms)
            metric.max_time_ms = max(metric.max_time_ms, duration_ms)
        else:
            metric.errors += 1
    
    def start_timer(self, operation_id: str) -> None:
        """Start a timer for an operation."""
        self.start_times[operation_id] = time.time()
    
    def end_timer(self, operation_id: str, operation: str, success: bool = True) -> float:
        """End a timer and record metrics."""
        if operation_id not in self.start_times:
            return 0.0
        
        start_time = self.start_times.pop(operation_id)
        duration_ms = (time.time() - start_time) * 1000
        self.record_operation(operation, duration_ms, success)
        return duration_ms
    
    def count_event(self, event_name: str, count: int = 1) -> None:
        """Increment event counter."""
        self.event_counters[event_name] += count
    
    def get_metrics(self, operation: Optional[str] = None) -> Dict[str, Any]:
        """Retrieve metrics summary."""
        if operation:
            if operation in self.metrics:
                return self.metrics[operation].to_dict()
            return {}
        
        return {
            op: metric.to_dict()
            for op, metric in sorted(self.metrics.items())
        }
    
    def get_summary(self) -> Dict[str, Any]:
        """Get comprehensive summary of all metrics."""
        total_operations = sum(m.count for m in self.metrics.values())
        total_errors = sum(m.errors for m in self.metrics.values())
        total_time = sum(m.total_time_ms for m in self.metrics.values())
        
        return {
            "total_operations": total_operations,
            "total_errors": total_errors,
            "total_time_ms": round(total_time, 2),
            "operations_tracked": len(self.metrics),
            "events_recorded": len(self.event_counters),
            "overall_success_rate": round(
                (total_operations / (total_operations + total_errors) * 100)
                if (total_operations + total_errors) > 0 else 100.0,
                1
            ),
        }
    
    def reset(self) -> None:
        """Reset all metrics."""
        self.metrics.clear()
        self.start_times.clear()
        self.event_counters.clear()


# Global metrics collector instance
_global_collector: Optional[MetricsCollector] = None


def get_collector() -> MetricsCollector:
    """Get or create global metrics collector."""
    global _global_collector
    if _global_collector is None:
        _global_collector = MetricsCollector()
    return _global_collector


__all__ = [
    "PerformanceMetrics",
    "MetricsCollector",
    "get_collector",
]
