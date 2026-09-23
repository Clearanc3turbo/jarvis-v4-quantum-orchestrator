"""Orchestrator runtime for JARVIS."""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from jarvis.config.settings import Settings
from jarvis.core.task import Task
from jarvis.core.workflow import Workflow, WorkflowNode
from jarvis.memory.vector_store import VectorMemoryStore
from jarvis.tools.registry import ToolRegistry


class JARVISOrchestrator:
    """Coordinates the agent runtime and module execution flow."""

    def __init__(self, settings: Optional[Settings] = None):
        self.settings = settings or Settings()
        self.memory = VectorMemoryStore()
        self.tools = ToolRegistry()
        self.workflow_history: List[Workflow] = []

    def build_workflow(self, task: Task) -> Workflow:
        workflow = Workflow(name=f"workflow-{task.id}")
        workflow.add_node(
            WorkflowNode(
                name="search",
                action="search",
                inputs={"query": task.query},
                dependencies=[],
            )
        )
        workflow.add_node(
            WorkflowNode(
                name="memory_lookup",
                action="memory_lookup",
                inputs={"query": task.query},
                dependencies=["search"],
            )
        )
        workflow.add_node(
            WorkflowNode(
                name="synthesize",
                action="synthesize",
                inputs={"query": task.query},
                dependencies=["memory_lookup"],
            )
        )
        self.workflow_history.append(workflow)
        return workflow

    def run(self, query: str) -> str:
        task = Task(query=query, domain=self.settings.domain)
        workflow = self.build_workflow(task)

        results: Dict[str, Any] = {}
        for node in workflow.nodes:
            if node.action == "search":
                results[node.name] = self.tools.execute("search", query=node.inputs["query"])
            elif node.action == "memory_lookup":
                results[node.name] = self.memory.search(node.inputs["query"])
            elif node.action == "synthesize":
                results[node.name] = f"Processed query: {query}"

        return str(results.get("synthesize", "No output generated."))
