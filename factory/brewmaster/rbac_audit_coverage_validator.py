from __future__ import annotations

import ast
from pathlib import Path
from typing import Any


class RBACAuditCoverageValidator:
    """Validates permission rejection tests and async audit traces for mutations."""

    def validate(self, spec_index: dict[str, Any], evidence: dict[str, Any], repo_root: Path) -> dict[str, Any]:
        required_permissions = [item["id"] for item in spec_index.get("permissions", [])]
        tested_rejections = set(evidence.get("rbac_rejection_test_ids", []))
        missing_rbac = [perm for perm in required_permissions if perm not in tested_rejections]
        missing_audit = self._mutation_functions_without_audit(repo_root)
        return {
            "validator": "RBACAuditCoverageValidator",
            "status": "complete" if not missing_rbac and not missing_audit else "blocked",
            "missing_rbac_permission_ids": missing_rbac,
            "mutations_without_audit": missing_audit,
        }

    def _mutation_functions_without_audit(self, repo_root: Path) -> list[dict[str, str]]:
        results = []
        for path in repo_root.glob("**/*.py"):
            if any(part in {"factory", "tests", "__pycache__"} for part in path.parts):
                continue
            tree = ast.parse(path.read_text(encoding="utf-8"))
            for fn in [node for node in ast.walk(tree) if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))]:
                if any(word in fn.name.lower() for word in ("create", "update", "delete", "register", "complete")):
                    names = {node.attr for node in ast.walk(fn) if isinstance(node, ast.Attribute)}
                    if "audit" not in names and "record_audit" not in names:
                        results.append({"file": str(path), "function": fn.name})
        return results
