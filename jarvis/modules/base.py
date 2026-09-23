"""Runtime orchestration for JARVIS."""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from jarvis.config.settings import Settings
from jarvis.core.task import Task
from jarvis.core.workflow import Workflow, WorkflowNode
from jarvis.memory.vector_store import VectorMemoryStore
from jarvis.tools.registry import ToolRegistry


class JARVISOrchestrator:
    """Coordinates the execution flow for a JARVIS query."""

    def __init__(self, settings: Optional[Settings] = None):
        self.settings = settings or Settings()
        self.memory = VectorMemoryStore()
        self.tools = ToolRegistry()
        self.workflow_history: List[Workflow] = []
        self._register_default_tools()

    def _register_default_tools(self) -> None:
        self.tools.register("search", self._search_tool)
        self.tools.register("memory_lookup", self._memory_tool)

    def _search_tool(self, query: str, **_: Any) -> str:
        return f"Search backend result for: {query}"

    def _memory_tool(self, query: str, **_: Any) -> list[dict[str, Any]]:
        return self.memory.search(query, top_k=3)

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
                results[node.name] = self.tools.execute("memory_lookup", query=node.inputs["query"])
            elif node.action == "synthesize":
                context = {
                    "query": query,
                    "search": results.get("search"),
                    "memory": results.get("memory_lookup"),
                }
                results[node.name] = self._synthesize(context)

        return str(results.get("synthesize", "No output generated."))

    def _synthesize(self, context: Dict[str, Any]) -> str:
        query = context.get("query", "")
        search_result = context.get("search", "")
        memory_result = context.get("memory", [])
        return (
            f"Query: {query}\n"
            f"Search: {search_result}\n"
            f"Memory matches: {len(memory_result)}"
        )
