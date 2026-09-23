#!/usr/bin/env python3
"""
JARVIS v4 — Unified Launcher
=============================

Boots the full JARVIS stack (Core + VQC + Aletheia + QNLP) in one command.

Features:
    1. Dependency check with colour-coded status table.
    2. Graceful module loading with try/except isolation.
    3. Stack bootstrap: instantiates modules and registers tools.
    4. CLI: --query, --domain, --status, --interactive.

Usage:
    python jarvis_launch.py
    python jarvis_launch.py --query "Explain VQC attention"
    python jarvis_launch.py --status
    python jarvis_launch.py --interactive
"""

from __future__ import annotations

import argparse
import importlib
import os
import sys
import traceback
from typing import Any, Callable, Dict, List, Optional, Tuple

# ---------------------------------------------------------------------------
# 0. ASCII Banner
# ---------------------------------------------------------------------------

BANNER = r"""
╔══════════════════════════════════════╗
║         JARVIS v4 — FULL STACK       ║
║  Quantum-Classical AI Orchestrator   ║
╚══════════════════════════════════════╝
"""

# ---------------------------------------------------------------------------
# 1. Dependency Check
# ---------------------------------------------------------------------------

REQUIRED_PACKAGES: List[Tuple[str, str]] = [
    ("pennylane", "pennylane"),
    ("torch", "torch"),
    ("numpy", "numpy"),
    ("sentence_transformers", "sentence-transformers"),
    ("nltk", "nltk"),
    ("lambeq", "lambeq"),
    ("pytket", "pytket"),
]


def check_dependencies(
    requirements_path: Optional[str] = None,
) -> Dict[str, bool]:
    packages = list(REQUIRED_PACKAGES)

    if requirements_path and os.path.isfile(requirements_path):
        packages = []
        with open(requirements_path, "r") as fh:
            for line in fh:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                pkg_name = line.split(">=")[0].split("<=")[0].split("==")[0].split("[")[0].strip()
                import_name = pkg_name.replace("-", "_")
                packages.append((import_name, pkg_name))

    results: Dict[str, bool] = {}
    for import_name, display_name in packages:
        try:
            importlib.import_module(import_name)
            results[display_name] = True
        except ImportError:
            results[display_name] = False

    print("┌─────────────────────────────┐")
    print("│  Package                    │  Status  │")
    print("├─────────────────────────────┤")
    for name, installed in results.items():
        icon = "\033[92m✅ installed\033[0m" if installed else "\033[93m⚠️  missing \033[0m"
        print(f"│  {name:<27s}│  {icon} │")
    print("└─────────────────────────────┘")

    missing = [n for n, ok in results.items() if not ok]
    if missing:
        print(f"\n  ⚠️  {len(missing)} optional package(s) missing — some modules may not load.")
    else:
        print("\n  ✅ All packages available.")

    return results


# ---------------------------------------------------------------------------
# 2. Module Loader
# ---------------------------------------------------------------------------

class ModuleLoader:
    MODULE_MAP: List[Tuple[str, str, str]] = [
        ("jarvis_v4_integrated", "JARVISCore", "JARVIS Core (Integrated)"),
        ("jarvis_vqc_layer", "JARVISVQCModule", "VQC Layer"),
        ("jarvis_aletheia", "AletheiaModule", "Aletheia Fact-Checker"),
        ("jarvis_qnlp", "QNLPModule", "QNLP Compiler"),
    ]

    def __init__(self) -> None:
        self.loaded: Dict[str, Any] = {}
        self.failed: Dict[str, str] = {}
        self._labels: Dict[str, str] = {}

    def load_all(self) -> None:
        workspace = os.path.dirname(os.path.abspath(__file__))
        if workspace not in sys.path:
            sys.path.insert(0, workspace)

        for file_stem, class_name, label in self.MODULE_MAP:
            self._labels[class_name] = label
            try:
                mod = importlib.import_module(file_stem)
                cls = getattr(mod, class_name)
                self.loaded[class_name] = cls
            except SystemExit:
                self.failed[class_name] = "Module called sys.exit (missing dependencies)"
            except ImportError as exc:
                self.failed[class_name] = f"ImportError: {exc}"
            except AttributeError as exc:
                self.failed[class_name] = f"AttributeError: {exc}"
            except Exception as exc:
                self.failed[class_name] = f"{type(exc).__name__}: {exc}"

    def print_summary(self) -> None:
        print("\n── Module Load Status ──────────────────────────────")
        for _stem, class_name, _label in self.MODULE_MAP:
            label = self._labels.get(class_name, class_name)
            if class_name in self.loaded:
                print(f"  \033[92m✅  {label:<30s}\033[0m  loaded")
            else:
                reason = self.failed.get(class_name, "unknown")
                print(f"  \033[91m❌  {label:<30s}\033[0m  {reason}")
        ok = len(self.loaded)
        total = len(self.MODULE_MAP)
        print(f"\n  {ok}/{total} modules loaded successfully.\n")


# ---------------------------------------------------------------------------
# 3. Stack Bootstrap
# ---------------------------------------------------------------------------

class JARVISStack:
    def __init__(self, loader: ModuleLoader) -> None:
        self.loader = loader
        self.core: Any = None
        self.vqc: Any = None
        self.aletheia: Any = None
        self.qnlp: Any = None
        self.tools: Dict[str, Callable] = {}
        self._boot()

    def _safe_instantiate(self, class_name: str, **kwargs: Any) -> Any:
        cls = self.loader.loaded.get(class_name)
        if cls is None:
            return None
        try:
            return cls(**kwargs)
        except Exception as exc:
            print(f"  ⚠️  Failed to instantiate {class_name}: {exc}")
            return None

    def _boot(self) -> None:
        self.core = self._safe_instantiate("JARVISCore")
        self.vqc = self._safe_instantiate("JARVISVQCModule")
        self.aletheia = self._safe_instantiate("AletheiaModule")
        self.qnlp = self._safe_instantiate("QNLPModule", use_lambeq=False)

        if self.vqc is not None and hasattr(self.vqc, "run_projection"):
            self.tools["vqc_query_project"] = self.vqc.run_projection
            if self.core is not None:
                self.core.tools.register("vqc_query_project", self.vqc.run_projection)

        if self.aletheia is not None and hasattr(self.aletheia, "run_verification"):
            self.tools["aletheia_verify"] = self.aletheia.run_verification
            if self.core is not None:
                self.core.tools.register("aletheia_verify", self.aletheia.run_verification)

        if self.qnlp is not None and hasattr(self.qnlp, "compile"):
            self.tools["qnlp_compile"] = self.qnlp.compile
            if self.core is not None:
                self.core.tools.register("qnlp_compile", self.qnlp.compile)

    def run(self, query: str, domain: str = "quantum_architect") -> str:
        if self.core is None:
            return "[ERROR] JARVISCore is not loaded — cannot execute queries."
        try:
            return self.core.run(query, domain_module=domain)
        except Exception as exc:
            return f"[ERROR] Execution failed: {exc}"

    def status(self) -> None:
        print("\n══════════════════════════════════════")
        print("       JARVIS Stack — Status")
        print("══════════════════════════════════════")
        modules = [
            ("JARVISCore", self.core),
            ("JARVISVQCModule", self.vqc),
            ("AletheiaModule", self.aletheia),
            ("QNLPModule", self.qnlp),
        ]
        print("\n  Modules:")
        for name, instance in modules:
            label = self.loader._labels.get(name, name)
            if instance is not None:
                print(f"    \033[92m✅  {label}\033[0m")
            else:
                print(f"    \033[91m❌  {label}\033[0m")

        print("\n  Registered Tools:")
        if self.tools:
            for tool_name, func in self.tools.items():
                target = getattr(func, "__qualname__", str(func))
                print(f"    🔧  {tool_name} → {target}")
        else:
            print("    (none)")

        if self.core is not None:
            all_tools = self.core.tools.list_tools()
            extra = [t for t in all_tools if t not in self.tools]
            if extra:
                print("\n  Core Built-in Tools:")
                for t in extra:
                    print(f"    🔧  {t}")

        print("\n══════════════════════════════════════\n")


# ---------------------------------------------------------------------------
# 4. CLI Interface
# ---------------------------------------------------------------------------

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="jarvis_launch",
        description="JARVIS v4 — Unified Full-Stack Launcher",
    )
    parser.add_argument(
        "--query",
        type=str,
        default="Explain quantum-classical hybrid transformer architecture",
        help="Query to run through the JARVIS stack.",
    )
    parser.add_argument(
        "--domain",
        type=str,
        default="quantum_architect",
        help="Domain module for query routing.",
    )
    parser.add_argument(
        "--status",
        action="store_true",
        help="Print stack status and exit.",
    )
    parser.add_argument(
        "--interactive",
        action="store_true",
        help="Drop into an interactive REPL loop.",
    )
    return parser


# ---------------------------------------------------------------------------
# 5. Main Entry
# ---------------------------------------------------------------------------

def main(argv: Optional[List[str]] = None) -> None:
    parser = build_parser()
    args = parser.parse_args(argv)

    print(BANNER)

    requirements_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "requirements_unified.txt",
    )
    check_dependencies(requirements_path)

    loader = ModuleLoader()
    loader.load_all()
    loader.print_summary()

    print("  Bootstrapping JARVIS stack …")
    stack = JARVISStack(loader)

    if args.status:
        stack.status()
        return

    if args.interactive:
        stack.status()
        print("  Entering interactive mode. Type 'exit' or 'quit' to leave.\n")
        while True:
            try:
                query = input("\033[96mJARVIS> \033[0m")
            except (EOFError, KeyboardInterrupt):
                print("\n  Goodbye.")
                break
            query = query.strip()
            if query.lower() in ("exit", "quit", "q"):
                print("  Goodbye.")
                break
            if not query:
                continue
            result = stack.run(query, domain=args.domain)
            print(f"\n{result}\n")
        return

    print(f"  Query  : {args.query}")
    print(f"  Domain : {args.domain}\n")
    result = stack.run(args.query, domain=args.domain)
    print(result)


if __name__ == "__main__":
    main()
