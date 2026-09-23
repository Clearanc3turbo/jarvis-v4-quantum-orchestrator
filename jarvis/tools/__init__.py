"""In-memory vector retrieval store for JARVIS."""

from __future__ import annotations

from typing import Any, Dict, List, Optional


class VectorMemoryStore:
    """Minimal retrieval store that mimics a vector memory backend."""

    def __init__(self):
        self.documents: List[Dict[str, Any]] = []

    def add(self, doc_id: str, content: str, metadata: Optional[Dict[str, Any]] = None):
        self.documents.append({
            "id": doc_id,
            "content": content,
            "metadata": metadata or {},
        })

    def search(self, query: str, top_k: int = 3) -> List[Dict[str, Any]]:
        if not self.documents:
            return []

        matches: List[Dict[str, Any]] = []
        q = query.lower()
        for item in self.documents:
            content = str(item["content"]).lower()
            score = 0.0 if not q else sum(1 for token in q.split() if token in content)
            if score > 0:
                matches.append({"id": item["id"], "score": score, "content": item["content"]})

        matches.sort(key=lambda x: x["score"], reverse=True)
        return matches[:top_k]
