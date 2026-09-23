"""CLI interface for the JARVIS runtime."""

from __future__ import annotations

import argparse

from jarvis.app.launcher import JARVISLauncher


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="JARVIS orchestration CLI")
    parser.add_argument("--query", type=str, default="Explain the hybrid quantum orchestration flow.")
    parser.add_argument("--domain", type=str, default="quantum_architect")
    return parser


def main(argv: list[str] | None = None) -> None:
    parser = build_parser()
    args = parser.parse_args(argv)

    launcher = JARVISLauncher()
    launcher.settings.domain = args.domain
    print(launcher.run(args.query))


if __name__ == "__main__":
    main()
