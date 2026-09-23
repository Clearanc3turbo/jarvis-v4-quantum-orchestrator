"""Module loading and registration for the JARVIS runtime."""

from __future__ import annotations

from typing import Dict, Any

from jarvis.config.settings import Settings


class ModuleLoader:
    """Loads optional specialist modules without making any dependency mandatory."""

    MODULES = {
        "vqc": ("jarvis.modules.vqc", "VQCModule"),
        "aletheia": ("jarvis.modules.aletheia", "AletheiaModule"),
        "qnlp": ("jarvis.modules.qnlp", "QNLPModule"),
    }

    def __init__(self, settings: Settings):
        self.settings = settings
        self.loaded: Dict[str, Any] = {}
        self.failed: Dict[str, str] = {}

    def load_enabled(self) -> Dict[str, Any]:
        import importlib
        for name in self.settings.enabled_modules:
            spec = self.MODULES.get(name)
            if spec is None:
                self.failed[name] = "unknown module"
                continue
            try:
                module = importlib.import_module(spec[0])
                instance = getattr(module, spec[1])()
                instance.initialize()
                self.loaded[name] = instance
            except Exception as exc:  # optional integrations must not block core startup
                self.failed[name] = f"{type(exc).__name__}: {exc}"
        return self.loaded

    def register_tools(self, registry: Any) -> None:
        for instance in self.loaded.values():
            instance.register_tools(registry)

    def status(self) -> Dict[str, Any]:
        return {
            "loaded": sorted(self.loaded),
            "failed": dict(self.failed),
            "health": {name: module.health_check() for name, module in self.loaded.items()},
        }
