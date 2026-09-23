"""Workflow graph with dependency validation and topological ordering."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class WorkflowNode:
    name: str
    action: str
    inputs: Dict[str, Any] = field(default_factory=dict)
    dependencies: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Workflow:
    name: str
    nodes: List[WorkflowNode] = field(default_factory=list)

    def add_node(self, node: WorkflowNode) -> None:
        if self.get_node(node.name) is not None:
            raise ValueError(f"Duplicate workflow node: {node.name}")
        self.nodes.append(node)

    def get_node(self, name: str) -> Optional[WorkflowNode]:
        return next((node for node in self.nodes if node.name == name), None)

    def topological_order(self) -> List[WorkflowNode]:
        names = {node.name for node in self.nodes}
        pending = {node.name: set(node.dependencies) for node in self.nodes}
        unknown = {dep for deps in pending.values() for dep in deps if dep not in names}
        if unknown:
            raise ValueError(f"Unknown workflow dependencies: {sorted(unknown)}")
        ordered: List[WorkflowNode] = []
        while pending:
            ready = [name for name, deps in pending.items() if not deps]
            if not ready:
                raise ValueError("Workflow contains a dependency cycle")
            for name in ready:
                ordered.append(self.get_node(name))  # type: ignore[arg-type]
                pending.pop(name)
            for deps in pending.values():
                deps.difference_update(ready)
        return ordered
