# Deployment and backend support

The optional backend adapters live in `jarvis.integrations.quantum.backends`.
They accept a small validated gate IR and compile it to Qiskit or pytket without
requiring either SDK for core startup:

```python
from jarvis.integrations.quantum import compile_qiskit
circuit = compile_qiskit(2, [
    {"name": "h", "qubits": [0]},
    {"name": "cx", "qubits": [0, 1]},
], measure=True)
```

Install one backend with `pip install -e '.[qiskit]'` or
`pip install -e '.[pytket]'`. IBM Runtime access is opt-in via
`qiskit_ibm_backend("backend-name")`; configure credentials using the IBM SDK's
credential store or environment mechanism and never commit tokens.

## Local container

```bash
docker build -t jarvis .
docker run --rm --read-only --tmpfs /tmp jarvis --status
docker compose run --rm jarvis --query "hello"
```

The image runs as an unprivileged user, does not contain `.env` files, and the
compose service uses a read-only filesystem. Do not pass secrets in command-line
arguments or bake them into the image.

## Review findings addressed

* Optional SDK imports are lazy, so missing quantum packages do not prevent startup.
* Circuit inputs are allow-listed, range-checked, arity-checked, and parameter-checked;
  no dynamic Python evaluation is used.
* IBM backend creation is explicit and validates backend names; credentials are not
  accepted as ordinary arguments or logged.
* Backend compilation is separated from remote execution. Production deployments
  should add timeouts, quotas, audit logging, and an approval gate before submitting
  jobs to a provider.
