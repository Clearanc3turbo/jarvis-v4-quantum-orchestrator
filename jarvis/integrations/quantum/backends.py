"""Optional Qiskit and pytket compilation adapters.

The adapters are deliberately import-lazy: the core runtime remains usable without
quantum SDKs. They compile a small, validated gate IR and never submit jobs unless
the caller explicitly invokes a backend-specific runtime.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Iterable, Mapping


_ALLOWED_GATES = {"h", "x", "y", "z", "s", "t", "rx", "ry", "rz", "cx", "cz"}


@dataclass(frozen=True)
class Gate:
    name: str
    qubits: tuple[int, ...]
    params: tuple[float, ...] = ()


def validate_circuit(num_qubits: int, gates: Iterable[Mapping[str, Any]]) -> list[Gate]:
    """Validate untrusted circuit data before passing it to an SDK."""
    if not isinstance(num_qubits, int) or not 1 <= num_qubits <= 128:
        raise ValueError("num_qubits must be an integer between 1 and 128")
    validated: list[Gate] = []
    arity = {"cx": 2, "cz": 2}
    for raw in gates:
        name = str(raw.get("name", "")).lower()
        if name not in _ALLOWED_GATES:
            raise ValueError(f"unsupported gate: {name!r}")
        qubits = tuple(raw.get("qubits", ()))
        if len(qubits) != arity.get(name, 1) or any(
            not isinstance(q, int) or not 0 <= q < num_qubits for q in qubits
        ):
            raise ValueError(f"invalid qubits for {name}")
        params = tuple(float(p) for p in raw.get("params", ()))
        if name in {"rx", "ry", "rz"} and len(params) != 1:
            raise ValueError(f"{name} requires one parameter")
        if name not in {"rx", "ry", "rz"} and params:
            raise ValueError(f"{name} does not accept parameters")
        validated.append(Gate(name, qubits, params))
    return validated


def compile_qiskit(num_qubits: int, gates: Iterable[Mapping[str, Any]], *, measure: bool = False):
    """Return a Qiskit QuantumCircuit; raises a useful error if not installed."""
    try:
        from qiskit import QuantumCircuit
    except ImportError as exc:
        raise RuntimeError("Install the 'qiskit' optional dependency") from exc
    circuit = QuantumCircuit(num_qubits, num_qubits if measure else 0)
    for gate in validate_circuit(num_qubits, gates):
        q = gate.qubits
        if gate.name == "h": circuit.h(q[0])
        elif gate.name == "x": circuit.x(q[0])
        elif gate.name == "y": circuit.y(q[0])
        elif gate.name == "z": circuit.z(q[0])
        elif gate.name == "s": circuit.s(q[0])
        elif gate.name == "t": circuit.t(q[0])
        elif gate.name == "rx": circuit.rx(gate.params[0], q[0])
        elif gate.name == "ry": circuit.ry(gate.params[0], q[0])
        elif gate.name == "rz": circuit.rz(gate.params[0], q[0])
        elif gate.name == "cx": circuit.cx(q[0], q[1])
        elif gate.name == "cz": circuit.cz(q[0], q[1])
    if measure:
        circuit.measure(range(num_qubits), range(num_qubits))
    return circuit


def compile_pytket(num_qubits: int, gates: Iterable[Mapping[str, Any]]):
    """Return a pytket Circuit without importing pytket at module import time."""
    try:
        from pytket import Circuit
        from pytket.circuit import OpType
    except ImportError as exc:
        raise RuntimeError("Install the 'pytket' optional dependency") from exc
    mapping = {"h": OpType.H, "x": OpType.X, "y": OpType.Y, "z": OpType.Z,
               "s": OpType.S, "t": OpType.T, "cx": OpType.CX, "cz": OpType.CZ,
               "rx": OpType.Rx, "ry": OpType.Ry, "rz": OpType.Rz}
    circuit = Circuit(num_qubits)
    for gate in validate_circuit(num_qubits, gates):
        args = list(gate.qubits)
        if gate.name in {"rx", "ry", "rz"}:
            circuit.add_gate(mapping[gate.name], [gate.params[0]], args)
        else:
            circuit.add_gate(mapping[gate.name], args)
    return circuit


def qiskit_ibm_backend(name: str = "ibm_fez"):
    """Create an IBM Runtime backend only when explicitly requested by the caller.

    IBM credentials are read by qiskit-ibm-runtime's normal credential mechanism;
    this function does not log, persist, or accept tokens as arguments.
    """
    if not name or len(name) > 128 or any(c not in "abcdefghijklmnopqrstuvwxyz0123456789_-" for c in name.lower()):
        raise ValueError("invalid IBM backend name")
    try:
        from qiskit_ibm_runtime import QiskitRuntimeService
    except ImportError as exc:
        raise RuntimeError("Install the 'ibm' optional dependency") from exc
    return QiskitRuntimeService().backend(name)
