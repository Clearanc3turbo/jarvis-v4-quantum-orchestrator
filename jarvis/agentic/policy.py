"""Copilot-style code assistance layer."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping


@dataclass
class PatchProposal:
    file_path: str
    before: str
    after: str
    summary: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "file_path": self.file_path,
            "before": self.before,
            "after": self.after,
            "summary": self.summary,
        }


class CopilotAgent:
    """Creates reviewable patch proposals without silently executing repo changes."""

    def suggest_patch(self, file_path: str, original: str, replacement: str, summary: str) -> PatchProposal:
        if not file_path or not isinstance(original, str) or not isinstance(replacement, str):
            raise ValueError("invalid patch input")
        return PatchProposal(
            file_path=file_path,
            before=original,
            after=replacement,
            summary=summary,
        )

    def apply_patch(self, proposal: PatchProposal, *, write: bool = False) -> str:
        if not isinstance(proposal, PatchProposal):
            raise ValueError("proposal must be a PatchProposal")
        if not write:
            return proposal.after

        target = Path(proposal.file_path)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(proposal.after, encoding="utf-8")
        return str(target)

    def summarize_edit(self, file_path: str, change: str) -> str:
        return f"Updated {file_path} with a focused change: {change[:80]}"
