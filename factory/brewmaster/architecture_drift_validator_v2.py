from __future__ import annotations

import ast
from pathlib import Path
from typing import Any


class ArchitectureDriftValidatorV2:
    """Audits Python imports for Router -> Service -> Repository -> ORM boundaries."""

    FORBIDDEN = (
        ("router", "repository"),
        ("router", "repositories"),
        ("router", "models"),
        ("service", "fastapi"),
    )

    def validate(self, repo_root: Path) -> dict[str, Any]:
        violations = []
        for path in repo_root.glob("**/*.py"):
            if any(part in {"__pycache__", ".venv"} for part in path.parts):
                continue
            role = self._role(path)
            if not role:
                continue
            imports = self._imports(path)
            for source_role, forbidden in self.FORBIDDEN:
                if role == source_role and any(forbidden in imported.lower() for imported in imports):
                    violations.append({"file": str(path), "role": role, "forbidden_dependency": forbidden})
        return {
            "validator": "ArchitectureDriftValidatorV2",
            "status": "complete" if not violations else "blocked",
            "violations": violations,
        }

    def _role(self, path: Path) -> str | None:
        lowered = path.as_posix().lower()
        for role in ("router", "service", "repository"):
            if role in lowered:
                return role
        return None

    def _imports(self, path: Path) -> set[str]:
        tree = ast.parse(path.read_text(encoding="utf-8"))
        imports: set[str] = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imports.update(alias.name for alias in node.names)
            elif isinstance(node, ast.ImportFrom) and node.module:
                imports.add(node.module)
        return imports
