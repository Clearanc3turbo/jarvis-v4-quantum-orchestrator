"""Reviewable Copilot patch proposals with workspace-bound writes."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class PatchProposal:
    file_path: str
    before: str
    after: str
    summary: str

    def to_dict(self) -> dict[str, Any]:
        return {"file_path": self.file_path, "before": self.before, "after": self.after, "summary": self.summary}


class CopilotAgent:
    def suggest_patch(self, file_path: str, original: str, replacement: str, summary: str) -> PatchProposal:
        if not file_path or not isinstance(original, str) or not isinstance(replacement, str):
            raise ValueError("invalid patch input")
        return PatchProposal(file_path, original, replacement, summary)

    def validate_patch(self, proposal: PatchProposal, workspace: str | Path) -> Path:
        root = Path(workspace).resolve()
        target = (root / proposal.file_path).resolve()
        if target != root and root not in target.parents:
            raise ValueError("patch path escapes workspace")
        if target.exists() and target.read_text(encoding="utf-8") != proposal.before:
            raise ValueError("patch base does not match current file")
        return target

    def apply_patch(self, proposal: PatchProposal, *, workspace: str | Path = ".", write: bool = False) -> str:
        target = self.validate_patch(proposal, workspace)
        if not write:
            return proposal.after
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(proposal.after, encoding="utf-8")
        return str(target)

    def summarize_edit(self, file_path: str, change: str) -> str:
        return f"Updated {file_path} with a focused change: {change[:80]}"
