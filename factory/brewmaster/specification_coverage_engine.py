from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from ..utils import read_json, write_json
from .specification_parser import SPEC_INDEX_KEYS


@dataclass(frozen=True)
class CoverageRow:
    artifact: str
    total: int
    implemented: int
    pending: int
    pending_ids: tuple[str, ...]

    def to_dict(self) -> dict[str, Any]:
        return {
            "artifact": self.artifact,
            "total": self.total,
            "implemented": self.implemented,
            "pending": self.pending,
            "pending_ids": list(self.pending_ids),
        }


class SpecificationCoverageEngine:
    """Builds the immutable global coverage matrix from spec-index.json."""

    COVERAGE_KEYS = SPEC_INDEX_KEYS

    def build_matrix(self, spec_index: dict[str, Any], evidence: dict[str, Any]) -> dict[str, Any]:
        implemented_ids = set(evidence.get("implemented_ids", []))
        tested_ids = set(evidence.get("tested_ids", []))
        documented_endpoints = set(evidence.get("documented_endpoint_ids", []))
        rows: list[CoverageRow] = []
        for key in self.COVERAGE_KEYS:
            ids = [item["id"] for item in spec_index.get(key, []) if "id" in item]
            covered = implemented_ids & set(ids)
            if key in {"requirements", "use_cases", "business_rules", "validations", "screens"}:
                covered &= tested_ids
            if key == "endpoints":
                covered &= documented_endpoints
            pending_ids = tuple(item_id for item_id in ids if item_id not in covered)
            rows.append(CoverageRow(key, len(ids), len(covered), len(pending_ids), pending_ids))
        return {
            "status": "complete" if all(row.pending == 0 for row in rows) else "blocked",
            "matrix": [row.to_dict() for row in rows],
            "totals": {
                "total": sum(row.total for row in rows),
                "implemented": sum(row.implemented for row in rows),
                "pending": sum(row.pending for row in rows),
            },
        }

    def build_from_files(self, spec_index_path: Path, evidence_path: Path, output_path: Path) -> dict[str, Any]:
        spec_index = read_json(spec_index_path)
        evidence = read_json(evidence_path) if evidence_path.exists() else {}
        matrix = self.build_matrix(spec_index, evidence)
        write_json(output_path, matrix)
        return matrix
