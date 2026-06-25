from __future__ import annotations

import ast
from pathlib import Path
from typing import Any


class CanonicalDomainValidator:
    """Validates models and schemas against J.5 entities in spec-index.json."""

    def validate(self, spec_index: dict[str, Any], repo_root: Path) -> dict[str, Any]:
        defined = self._python_classes(repo_root)
        expected = [entity for entity in spec_index.get("entities", []) if entity.get("name")]
        missing = [entity["name"] for entity in expected if self._class_name(entity["name"]) not in defined]
        attribute_mismatches = []
        for entity in expected:
            class_name = self._class_name(entity["name"])
            attrs = defined.get(class_name, set())
            missing_attrs = [attr for attr in entity.get("attributes", []) if attr and attr not in attrs]
            if class_name in defined and missing_attrs:
                attribute_mismatches.append({"entity": entity["name"], "missing_attributes": missing_attrs})
        return {
            "validator": "CanonicalDomainValidator",
            "status": "complete" if not missing and not attribute_mismatches else "blocked",
            "missing_entities": missing,
            "attribute_mismatches": attribute_mismatches,
        }

    def _python_classes(self, repo_root: Path) -> dict[str, set[str]]:
        classes: dict[str, set[str]] = {}
        paths = list((repo_root / "models").glob("**/*.py")) if (repo_root / "models").exists() else []
        paths += list((repo_root / "schemas").glob("**/*.py")) if (repo_root / "schemas").exists() else []
        for path in paths:
            tree = ast.parse(path.read_text(encoding="utf-8"))
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    attrs = {target.id for stmt in node.body if isinstance(stmt, ast.AnnAssign) and isinstance((target := stmt.target), ast.Name)}
                    classes[node.name] = attrs
        return classes

    def _class_name(self, table_name: str) -> str:
        return "".join(part.capitalize() for part in table_name.strip("`").split("_"))
