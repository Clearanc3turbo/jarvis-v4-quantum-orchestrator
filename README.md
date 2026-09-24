# Add v7 compatibility runtime, safe evaluator, tests, and benchmark

The v7-inspired runtime is available as `jarvis_system_v7.py`. It complements the
package runtime and the optional Qiskit/pytket adapters; it does not silently submit
jobs to quantum providers.

For production use, treat all heuristic PAT, memory, and fact-check scores as
signals requiring policy review. Do not execute untrusted Python, store provider
credentials in source control, or interpret simulated state-vector fidelity as a
claim of quantum hardware advantage.
