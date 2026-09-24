"""Type definitions and protocols for JARVIS.

Comprehensive type annotations for all public APIs including protocols,
type aliases, and generic types for better IDE support and type checking.
"""

from __future__ import annotations

from typing import Any, Callable, Dict, List, Optional, Protocol, Tuple, Union

# Numeric type aliases
Probability = float  # Value between 0.0 and 1.0
RiskScore = float  # Value between 0.0 and 1.0
Similarity = float  # Cosine similarity between 0.0 and 1.0

# Collection type aliases
QueryResults = Dict[str, Any]
WorkflowResults = Dict[str, Any]
ExecutionContext = Dict[str, Any]

# Action and tool types
ToolName = str
ToolArguments = Dict[str, Any]
ToolOutput = Union[str, Dict[str, Any], List[Any]]

# Memory and search types
DocumentId = str
DocumentContent = str
Embedding = List[float]
MetadataDict = Dict[str, Any]

# Configuration and settings
ConfigDict = Dict[str, Any]


class Tool(Protocol):
    """Protocol for a callable tool."""
    
    def __call__(self, **kwargs: Any) -> ToolOutput:
        """Execute the tool with given arguments."""
        ...


class MemoryStore(Protocol):
    """Protocol for memory storage backend."""
    
    def add_memory(self, doc_id: DocumentId, content: DocumentContent, 
                   metadata: Optional[MetadataDict] = None) -> None:
        """Add document to memory store."""
        ...
    
    def search(self, query: str, top_k: int = 3) -> List[Dict[str, Any]]:
        """Search memory store for relevant documents."""
        ...


class Module(Protocol):
    """Protocol for specialist modules."""
    
    def run(self, task: Any, context: ExecutionContext) -> Any:
        """Execute module logic with given task and context."""
        ...
    
    @property
    def name(self) -> str:
        """Module identifier."""
        ...


class LanguageModel(Protocol):
    """Protocol for language model backends."""
    
    def generate(self, prompt: str, **kwargs: Any) -> str:
        """Generate response from prompt."""
        ...
    
    def chat(self, messages: List[Dict[str, str]], **kwargs: Any) -> str:
        """Process multi-turn conversation."""
        ...


class SearchBackend(Protocol):
    """Protocol for search backends."""
    
    def search(self, query: str, top_k: int = 10) -> List[Dict[str, Any]]:
        """Execute search query."""
        ...
    
    def index(self, documents: List[Dict[str, str]]) -> None:
        """Index documents for searching."""
        ...
