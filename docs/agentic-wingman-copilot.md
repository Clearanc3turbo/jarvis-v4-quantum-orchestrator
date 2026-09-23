# Agentic Wingman/Copilot usage

The branch exposes safe local modes:

```bash
python jarvis_launch.py --wingman --query "prepare a response"
python jarvis_launch.py --wingman --approve --audit /tmp/jarvis-audit.json --query "prepare a response"
python jarvis_launch.py --benchmark
```

Wingman creates plans and approval records. Copilot creates reviewable patches;
patches are workspace-bound and require an explicit `write=True` call. Audit output
is sanitized. These modes do not contact quantum providers or external services.
