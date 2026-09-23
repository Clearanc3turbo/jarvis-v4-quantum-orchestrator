"""Bootstrap and CLI entrypoint for the JARVIS runtime."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from jarvis.config.settings import Settings
from jarvis.core.orchestrator import JARVISOrchestrator


@dataclass
class LaunchContext:
    settings: Settings
    orchestrator: Optional[JARVISOrchestrator] = None


class JARVISLauncher:
    """Minimal runtime bootstrapper for the refactored architecture."""

    def __init__(self, settings: Optional[Settings] = None):
        self.settings = settings or Settings()
        self.context = LaunchContext(settings=self.settings)

    def bootstrap(self) -> JARVISOrchestrator:
        orchestrator = JARVISOrchestrator(settings=self.settings)
        self.context.orchestrator = orchestrator
        return orchestrator

    def run(self, query: str) -> str:
        orchestrator = self.context.orchestrator or self.bootstrap()
        return orchestrator.run(query)


if __name__ == "__main__":
    launcher = JARVISLauncher()
    print(launcher.run("Explain the hybrid quantum orchestration flow."))
