"""Workflow graph for sequencing tasks and tool calls."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class WorkflowNode:
    """A node in the execution graph."""

    name: str
    action: str
    inputs: Dict[str, Any] = field(default_factory=dict)
    dependencies: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Workflow:
    """Simple DAG-style workflow container."""

    name: str
    nodes: List[WorkflowNode] = field(default_factory=list)

    def add_node(self, node: WorkflowNode) -> None:
        self.nodes.append(node)

    def get_node(self, name: str) -> Optional[WorkflowNode]:
        for node in self.nodes:
            if node.name == name:
                return node
        return None
