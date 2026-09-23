"""Unified runtime bootstrap and compatibility-friendly launcher."""

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
    def __init__(self, settings: Optional[Settings] = None):
        self.settings = settings or Settings.from_env()
        self.context = LaunchContext(self.settings)

    def bootstrap(self) -> JARVISOrchestrator:
        self.context.orchestrator = JARVISOrchestrator(self.settings)
        return self.context.orchestrator

    @property
    def orchestrator(self) -> JARVISOrchestrator:
        return self.context.orchestrator or self.bootstrap()

    def run(self, query: str, domain: Optional[str] = None) -> str:
        return self.orchestrator.run(query, domain=domain)

    def status(self) -> dict:
        return self.orchestrator.status()
