"""Safe, AST-based evaluator for numeric expressions and simple scripts."""

from __future__ import annotations

import ast
from typing import Any, Mapping


class SafePythonEvaluator:
    """Executes only a narrow subset of arithmetic and safe builtins."""

    SAFE_FUNCS = {
        "abs": abs,
        "min": min,
        "max": max,
        "sum": sum,
        "len": len,
        "round": round,
        "pow": pow,
        "int": int,
        "float": float,
        "bool": bool,
    }
    SAFE_NAMES = {"__builtins__": False}

    def evaluate(self, expression: str, *, env: Mapping[str, Any] | None = None) -> Any:
        if not isinstance(expression, str):
            raise ValueError("expression must be a string")
        tree = ast.parse(expression, mode="eval")
        return self._eval_node(tree.body, env or {})

    def evaluate_statement(self, statement: str, *, env: Mapping[str, Any] | None = None) -> Any:
        if not isinstance(statement, str):
            raise ValueError("statement must be a string")
        tree = ast.parse(statement, mode="exec")
        local_env = dict(env or {})
        for node in tree.body:
            if isinstance(node, ast.Assign):
                if len(node.targets) != 1 or not isinstance(node.targets[0], ast.Name):
                    raise ValueError("only simple assignment is allowed")
                target_name = node.targets[0].id
                local_env[target_name] = self._eval_node(node.value, local_env)
                continue
            raise ValueError("only assignment statements are allowed")
        return local_env

    def _eval_node(self, node: ast.AST, env: Mapping[str, Any]) -> Any:
        if isinstance(node, ast.Constant):
            if type(node.value) not in (int, float, bool, str):
                raise ValueError("unsupported constant type")
            return node.value
        if isinstance(node, ast.Name):
            if node.id in env:
                return env[node.id]
            if node.id in self.SAFE_FUNCS:
                return self.SAFE_FUNCS[node.id]
            raise ValueError(f"name not allowed: {node.id}")
        if isinstance(node, ast.BinOp):
            left = self._eval_node(node.left, env)
            right = self._eval_node(node.right, env)
            if type(node.op) is ast.Add:
                return left + right
            if type(node.op) is ast.Sub:
                return left - right
            if type(node.op) is ast.Mult:
                return left * right
            if type(node.op) is ast.Div:
                return left / right
            if type(node.op) is ast.Pow:
                return left ** right
            raise ValueError("operator not allowed")
        if isinstance(node, ast.UnaryOp):
            value = self._eval_node(node.operand, env)
            if type(node.op) is ast.UAdd:
                return +value
            if type(node.op) is ast.USub:
                return -value
            raise ValueError("unary operator not allowed")
        if isinstance(node, ast.Call):
            if not isinstance(node.func, ast.Name):
                raise ValueError("only direct function calls are allowed")
            func_name = node.func.id
            if func_name not in self.SAFE_FUNCS:
                raise ValueError(f"function not allowed: {func_name}")
            args = [self._eval_node(arg, env) for arg in node.args]
            return self.SAFE_FUNCS[func_name](*args)
        if isinstance(node, ast.Tuple):
            return tuple(self._eval_node(x, env) for x in node.elts)
        if isinstance(node, ast.List):
            return [self._eval_node(x, env) for x in node.elts]
        raise ValueError(f"syntax not allowed: {type(node).__name__}")
