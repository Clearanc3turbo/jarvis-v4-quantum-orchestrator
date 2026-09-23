"""Runtime configuration for JARVIS."""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from typing import Dict, List


@dataclass
class Settings:
    app_name: str = "jarvis"
    domain: str = "quantum_architect"
    search_backend: str = "tavily"
    memory_backend: str = "in_memory"
    llm_provider: str = "local"
    memory_top_k: int = 3
    enabled_modules: List[str] = field(default_factory=lambda: ["vqc", "aletheia", "qnlp"])
    extra: Dict[str, str] = field(default_factory=dict)

    @classmethod
    def from_env(cls) -> "Settings":
        modules = os.getenv("JARVIS_MODULES", "vqc,aletheia,qnlp")
        return cls(
            domain=os.getenv("JARVIS_DOMAIN", "quantum_architect"),
            search_backend=os.getenv("JARVIS_SEARCH_BACKEND", "tavily"),
            memory_backend=os.getenv("JARVIS_MEMORY_BACKEND", "in_memory"),
            llm_provider=os.getenv("JARVIS_LLM_PROVIDER", "local"),
            enabled_modules=[item.strip() for item in modules.split(",") if item.strip()],
        )

    def as_dict(self) -> Dict[str, object]:
        return {
            "app_name": self.app_name,
            "domain": self.domain,
            "search_backend": self.search_backend,
            "memory_backend": self.memory_backend,
            "llm_provider": self.llm_provider,
            "memory_top_k": self.memory_top_k,
            "enabled_modules": list(self.enabled_modules),
            "extra": dict(self.extra),
        }
