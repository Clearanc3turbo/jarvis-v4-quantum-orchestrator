[build-system]
requires = ["setuptools>=68"]
build-backend = "setuptools.build_meta"

[project]
name = "jarvis-v4-quantum-orchestrator"
version = "0.1.0"
description = "Quantum-classical AI orchestration runtime"
requires-python = ">=3.10"
dependencies = ["numpy>=1.24"]

[project.optional-dependencies]
embeddings = ["sentence-transformers>=2.2"]
quantum = ["pennylane>=0.35"]
qnlp = ["lambeq>=0.4", "pytket>=1.20"]
dev = ["pytest>=7", "ruff>=0.4"]

[project.scripts]
jarvis = "jarvis.app.cli:main"

[tool.setuptools.packages.find]
include = ["jarvis*"]
