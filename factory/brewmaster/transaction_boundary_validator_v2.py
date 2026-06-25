from __future__ import annotations

import ast
from pathlib import Path
from typing import Any


class TransactionBoundaryValidatorV2:
    """Checks deterministic transaction boundaries for mutating service functions."""

    MUTATION_NAMES = ("create", "update", "delete", "register", "complete", "cancel", "receive")
    WRITE_CALLS = ("add", "delete", "execute", "commit")

    def validate(self, repo_root: Path) -> dict[str, Any]:
        violations = []
        for path in repo_root.glob("**/*service*.py"):
            tree = ast.parse(path.read_text(encoding="utf-8"))
            for fn in [node for node in ast.walk(tree) if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))]:
                if not any(name in fn.name.lower() for name in self.MUTATION_NAMES):
                    continue
                writes = self._write_lines(fn)
                commits = self._commit_lines(fn)
                rollback = self._has_rollback(fn)
                if writes and (not commits or not rollback or (commits and max(writes) > max(commits))):
                    violations.append({"file": str(path), "function": fn.name, "writes": writes, "commits": commits, "rollback": rollback})
        return {
            "validator": "TransactionBoundaryValidatorV2",
            "status": "complete" if not violations else "blocked",
            "violations": violations,
        }

    def _write_lines(self, fn: ast.AST) -> list[int]:
        lines = []
        for node in ast.walk(fn):
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute) and node.func.attr in self.WRITE_CALLS:
                lines.append(node.lineno)
        return lines

    def _commit_lines(self, fn: ast.AST) -> list[int]:
        return [node.lineno for node in ast.walk(fn) if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute) and node.func.attr == "commit"]

    def _has_rollback(self, fn: ast.AST) -> bool:
        return any(isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute) and node.func.attr == "rollback" for node in ast.walk(fn))
