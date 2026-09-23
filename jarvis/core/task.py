"""Task and request primitives for JARVIS execution."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class Task:
    """A single work item in the runtime."""

    query: str
    domain: str = "quantum_architect"
    metadata: Dict[str, Any] = field(default_factory=dict)
    dependencies: List[str] = field(default_factory=list)
    id: Optional[str] = None

    def __post_init__(self):
        if self.id is None:
            self.id = f"task-{abs(hash(self.query))}"
