"""Runtime orchestration for JARVIS."""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from jarvis.config.settings import Settings
from jarvis.config.loader import ModuleLoader
from jarvis.core.task import Task
from jarvis.core.workflow import Workflow, WorkflowNode
from jarvis.memory.vector_store import VectorMemoryStore
from jarvis.tools import ToolRegistry


class JARVISOrchestrator:
    """Coordinates planning, tools, specialist modules, memory, and synthesis."""

    def __init__(self, settings: Optional[Settings] = None):
        self.settings = settings or Settings()
        self.memory = VectorMemoryStore()
        self.tools = ToolRegistry()
        self.loader = ModuleLoader(self.settings)
        self.modules = self.loader.load_enabled()
        self.workflow_history: List[Workflow] = []
        self._register_default_tools()
        self.loader.register_tools(self.tools)

    def _register_default_tools(self) -> None:
        self.tools.register("search", self._search_tool, description="Search configured backend")
        self.tools.register("memory_lookup", self._memory_tool, description="Retrieve related memory")

    def _search_tool(self, query: str, **_: Any) -> Dict[str, Any]:
        return {"backend": self.settings.search_backend, "query": query, "results": []}

    def _memory_tool(self, query: str, **_: Any) -> List[Dict[str, Any]]:
        return self.memory.search(query, top_k=self.settings.memory_top_k)

    def build_workflow(self, task: Task) -> Workflow:
        workflow = Workflow(name=f"workflow-{task.id}")
        workflow.add_node(WorkflowNode("search", "search", {"query": task.query}))
        workflow.add_node(WorkflowNode("memory_lookup", "memory_lookup", {"query": task.query}, ["search"]))
        for module_name in self.settings.enabled_modules:
            if module_name in self.modules:
                workflow.add_node(
                    WorkflowNode(
                        name=module_name,
                        action=f"module:{module_name}",
                        inputs={"query": task.query},
                        dependencies=["memory_lookup"],
                    )
                )
        dependencies = [name for name in (self.settings.enabled_modules) if name in self.modules]
        workflow.add_node(WorkflowNode("synthesize", "synthesize", {"query": task.query}, dependencies or ["memory_lookup"]))
        self.workflow_history.append(workflow)
        return workflow

    def run(self, query: str, domain: Optional[str] = None) -> str:
        task = Task(query=query, domain=domain or self.settings.domain)
        workflow = self.build_workflow(task)
        results: Dict[str, Any] = {}
        for node in workflow.topological_order():
            if node.action == "search":
                results[node.name] = self.tools.execute("search", query=query)
            elif node.action == "memory_lookup":
                results[node.name] = self.tools.execute("memory_lookup", query=query)
            elif node.action.startswith("module:"):
                module_name = node.action.split(":", 1)[1]
                results[node.name] = self.modules[module_name].run(task, {"results": results})
            elif node.action == "synthesize":
                results[node.name] = self._synthesize(query, results)
        answer = str(results.get("synthesize", "No output generated."))
        self.memory.add_memory(task.id or query, answer, {"domain": task.domain})
        return answer

    def _synthesize(self, query: str, results: Dict[str, Any]) -> str:
        module_results = {name: results[name] for name in self.modules if name in results}
        return (
            f"Query: {query}\n"
            f"Search: {results.get('search', {})}\n"
            f"Memory matches: {len(results.get('memory_lookup', []))}\n"
            f"Modules: {module_results}"
        )

    def status(self) -> Dict[str, Any]:
        return {
            "settings": self.settings.as_dict(),
            "modules": self.loader.status(),
            "tools": self.tools.list_tools(),
            "workflows": len(self.workflow_history),
        }
