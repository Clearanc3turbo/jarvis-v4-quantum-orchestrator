---
name: jarvis-v8
description: "Use when designing, implementing, reviewing, or testing JARVIS V8 changes in this quantum-classical orchestration repository, especially changes involving workflows, agentic safety, modules, memory, tools, quantum backends, or runtime compatibility."
---

# JARVIS V8

Evolve the JARVIS runtime deliberately from the existing V5/V7-compatible codebase. Keep behavior deterministic by default, preserve public APIs unless the task requires a change, and make safety and testability part of every feature.

## Inputs

- Desired V8 capability or bug report
- Affected runtime surface, if known
- Compatibility constraints and acceptable dependency changes
- Required execution mode: simulated, local, or provider-backed

If the request does not identify the affected surface, inspect the nearest implementation and test before exploring broadly.

## Workflow

1. **Locate the owning path.** Start with the closest file, symbol, failing test, or command. Follow forwarding code to the component that actually computes, mutates, authorizes, or executes the behavior.
2. **State a hypothesis.** Before editing, write down one falsifiable explanation of the current behavior and one cheap check that could disconfirm it.
3. **Choose the smallest compatible change.** Prefer existing abstractions:
   - `jarvis.core` for tasks, workflows, and orchestration
   - `jarvis.execution` for plans and safe execution
   - `jarvis.agentic` for planning, approvals, guardrails, and patch proposals
   - `jarvis.modules` for specialist module loading and execution
   - `jarvis.integrations.quantum` for backend adapters
   - `jarvis.memory`, `jarvis.tools`, and `jarvis.observability` for their named concerns
4. **Preserve safety boundaries.** Do not execute untrusted Python, bypass approval states, expose secrets, or imply that simulation demonstrates quantum hardware advantage. Provider submission must remain explicit and opt-in.
5. **Edit narrowly.** Preserve existing style and public APIs. Add an abstraction only when it removes real duplication or expresses a required V8 boundary.
6. **Validate immediately.** After the first substantive edit, run the narrowest relevant test or type/lint check. Repair the same slice and rerun it before broadening the change.
7. **Test the contract.** Add focused tests for success, invalid input, approval or guardrail behavior, compatibility, and backend fallback where applicable. Include deterministic tests for new orchestration paths.
8. **Run the appropriate suite.** Use the project’s configured Python tooling and run the focused tests first, then the full test suite when shared behavior or public contracts changed.
9. **Report residual risk.** Summarize changed behavior, validation performed, dependency or provider assumptions, and any test gaps.

## Decision Rules

### Runtime and workflow changes

- Put scheduling and dependency ordering in `jarvis.core.workflow` or the owning orchestrator, not in modules.
- Keep task normalization and domain selection at the runtime boundary.
- Preserve workflow history and status reporting unless the feature explicitly changes observability semantics.
- Prefer structured results over parsing display strings.

### Agentic changes

- Plans must remain inspectable and reviewable.
- Medium- and high-risk actions require the existing policy and approval flow.
- Guardrails run before planning or execution when the request can be unsafe.
- Audit entries should contain sanitized metadata and no credentials or raw sensitive prompts.

### Quantum changes

- Keep the backend interface provider-neutral.
- Make simulator behavior explicit in names, configuration, or result metadata.
- Treat unavailable optional quantum dependencies as a controlled capability state, not an import-time failure when the backend is unused.
- Never claim hardware execution, speedup, or advantage from a simulated result alone.

### Dependencies and compatibility

- Avoid adding a dependency when the standard library or an existing project dependency is sufficient.
- Keep optional integrations optional and update the relevant requirements file when a dependency is necessary.
- Maintain Python `>=3.10` compatibility unless the task explicitly changes the project requirement.
- Update documentation when a user-visible command, configuration value, or operational assumption changes.

## Completion Checklist

- The controlling code path and changed contract are named.
- The change is scoped to the owning module.
- Invalid input and safety-sensitive paths are covered.
- Focused validation passes after the edit.
- Relevant broader tests pass, or failures are clearly reported as pre-existing or environmental.
- No credentials, unsafe execution paths, or unsupported quantum claims were introduced.
- Public documentation and requirements are consistent with the implementation.