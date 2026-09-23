"""Runtime settings for JARVIS."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List


@dataclass
class Settings:
    """Simple configuration object for the runtime."""

    app_name: str = "jarvis"
    domain: str = "quantum_architect"
    search_backend: str = "tavily"
    memory_backend: str = "in_memory"
    llm_provider: str = "local"
    enabled_modules: List[str] = field(
        default_factory=lambda: ["vqc", "aletheia", "qnlp"]
    )
    extra: Dict[str, str] = field(default_factory=dict)

    def as_dict(self) -> Dict[str, object]:
        return {
            "app_name": self.app_name,
            "domain": self.domain,
            "search_backend": self.search_backend,
            "memory_backend": self.memory_backend,
            "llm_provider": self.llm_provider,
            "enabled_modules": self.enabled_modules,
            "extra": self.extra,
        }
