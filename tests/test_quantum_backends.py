"""Adapter contract and validation tests; SDK-specific tests are opt-in."""
import pytest
from jarvis.integrations.quantum.backends import validate_circuit


def test_validate_circuit_accepts_supported_gates():
    gates = validate_circuit(2, [{"name": "h", "qubits": [0]}, {"name": "cx", "qubits": [0, 1]}])
    assert [g.name for g in gates] == ["h", "cx"]


@pytest.mark.parametrize("gates", [
    [{"name": "eval", "qubits": [0]}],
    [{"name": "cx", "qubits": [0, 2]}],
    [{"name": "rx", "qubits": [0], "params": []}],
])
def test_validate_circuit_rejects_unsafe_or_invalid_ir(gates):
    with pytest.raises(ValueError):
        validate_circuit(2, gates)


def test_backend_imports_are_lazy():
    # Importing the adapter must not require either SDK or contact a remote service.
    import jarvis.integrations.quantum.backends as backends
    assert callable(backends.compile_qiskit)
