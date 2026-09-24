"""End-to-end agentic safety tests."""
from pathlib import Path
from jarvis.agentic.copilot import CopilotAgent
from jarvis.agentic.wingman import WingmanAgent


def test_wingman_requires_approval_for_medium_actions():
    result = WingmanAgent().execute("prepare a response")
    assert result["status"] == "pending_approval"
    assert result["approved"] is False


def test_wingman_approval_completes_plan():
    result = WingmanAgent().execute("prepare a response", approve=True)
    assert result["status"] == "ok"
    assert result["approved"] is True


def test_copilot_rejects_workspace_escape(tmp_path: Path):
    agent = CopilotAgent()
    proposal = agent.suggest_patch("../outside.txt", "", "x", "bad path")
    try:
        agent.apply_patch(proposal, workspace=tmp_path)
        assert False, "expected workspace escape rejection"
    except ValueError:
        pass
