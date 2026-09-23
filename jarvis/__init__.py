"""JARVIS package root."""

__all__ = [
    "JARVISOrchestrator",
    "JARVISLauncher",
]


def __getattr__(name):
    if name == "JARVISLauncher":
        from jarvis.app.launcher import JARVISLauncher
        return JARVISLauncher
    elif name == "JARVISOrchestrator":
        from jarvis.core.orchestrator import JARVISOrchestrator
        return JARVISOrchestrator
    raise AttributeError(f"module {__name__} has no attribute {name}")
