from __future__ import annotations

from pathlib import Path
from typing import Any

from ..utils import write_json
from .specification_coverage_engine import SpecificationCoverageEngine


class HitoCompletionGate:
    """Blocks milestone progression until UC, RN, V, endpoints and screens are covered."""

    REQUIRED_KEYS = ("use_cases", "business_rules", "validations", "endpoints", "screens")

    def __init__(self, coverage_engine: SpecificationCoverageEngine | None = None) -> None:
        self.coverage_engine = coverage_engine or SpecificationCoverageEngine()

    def evaluate(self, hito: int, spec_index: dict[str, Any], evidence: dict[str, Any], output_path: Path) -> dict[str, Any]:
        coverage = self.coverage_engine.build_matrix(spec_index, evidence)
        relevant = [row for row in coverage["matrix"] if row["artifact"] in self.REQUIRED_KEYS]
        pending = sum(row["pending"] for row in relevant)
        report = {
            "hito": hito,
            "status": "complete" if pending == 0 else "blocked",
            "coverage": relevant,
            "pending": pending,
        }
        write_json(output_path, report)
        return report
