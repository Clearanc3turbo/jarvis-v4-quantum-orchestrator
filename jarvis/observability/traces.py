"""Minimal logging helpers for the refactored JARVIS runtime."""

import logging


logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(name)s - %(message)s")
logger = logging.getLogger("jarvis")

__all__ = ["logger"]
