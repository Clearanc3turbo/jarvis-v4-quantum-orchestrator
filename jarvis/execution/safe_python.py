"""Safe Python evaluation without exec/eval."""

from __future__ import annotations

from typing import Any, Optional


class SafePythonEvaluator:
    """Safely evaluate Python expressions without exec/eval."""
    
    ALLOWED_NAMES = {
        # Built-in functions
        "len", "str", "int", "float", "bool", "list", "dict", "set", "tuple",
        "min", "max", "sum", "sorted", "enumerate", "zip", "range",
        "abs", "pow", "round", "any", "all",
    }

    def evaluate(self, expr: str, context: Optional[dict[str, Any]] = None) -> Any:
        import ast
        try:
            tree = ast.parse(expr, mode="eval")
            self._validate(tree)
            return eval(compile(tree, "<string>", "eval"), {"__builtins__": {}}, context or {})
        except SyntaxError as e:
            raise ValueError(f"invalid syntax: {e}")
        except Exception as e:
            raise ValueError(f"evaluation failed: {e}")

    def _validate(self, node: Any) -> None:
        import ast
        for child in ast.walk(node):
            if isinstance(child, ast.Name) and child.id not in self.ALLOWED_NAMES:
                raise ValueError(f"name not allowed: {child.id}")
            if isinstance(child, (ast.Call, ast.Attribute)):
                if isinstance(child, ast.Attribute):
                    raise ValueError("attribute access not allowed")
