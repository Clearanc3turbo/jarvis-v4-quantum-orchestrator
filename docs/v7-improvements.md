# JARVIS v7 compatibility improvements

The supplied v6/v7 prototypes are now represented by `jarvis_system_v7.py`, with
several correctness and security fixes:

- quantum-inspired state vectors are explicitly local classical simulations;
- arbitrary `exec` and `eval` were replaced by an AST allow-list evaluator;
- prompt length and qubit counts are bounded;
- entropy is telemetry, not a standalone jailbreak detector;
- fact-check results expose heuristic evidence scores and must not be treated as
  proof of truth;
- dashboard output creates its parent directory and uses the latest execution trace;
- the deterministic benchmark avoids network calls and provider credentials.

Run `pytest -q`, then `python benchmarks/benchmark_v7.py`.
