from __future__ import annotations

from pathlib import Path
from typing import Any

from ..utils import write_json


class ReleaseReadinessGateV2:
    """Final deterministic release gate requiring complete functional evidence."""

    REQUIRED_VALIDATORS = (
        "RequirementCompletenessValidator",
        "EndpointCoverageValidator",
        "ScreenFunctionalCoverageValidator",
        "CanonicalDomainValidator",
        "CrossModuleConsistencyValidator",
        "BusinessScenarioValidator",
        "GoldenDatasetValidator",
        "ArchitectureDriftValidatorV2",
        "TransactionBoundaryValidatorV2",
        "RBACAuditCoverageValidator",
    )

    def evaluate(self, coverage: dict[str, Any], validation_reports: list[dict[str, Any]], output_path: Path) -> dict[str, Any]:
        report_by_validator = {report.get("validator"): report for report in validation_reports}
        missing = [name for name in self.REQUIRED_VALIDATORS if name not in report_by_validator]
        failed = [name for name, report in report_by_validator.items() if report.get("status") != "complete"]
        coverage_pending = coverage.get("totals", {}).get("pending", 1)
        release = {
            "gate": "ReleaseReadinessGateV2",
            "status": "complete" if not missing and not failed and coverage_pending == 0 else "blocked",
            "coverage_pending": coverage_pending,
            "missing_validators": missing,
            "failed_validators": failed,
        }
        write_json(output_path, release)
        return release
