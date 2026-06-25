from __future__ import annotations

from typing import Any


class RequirementCompletenessValidator:
    """Requires functional evidence for each RN, V and UC requirement."""

    def validate(self, spec_index: dict[str, Any], evidence: dict[str, Any]) -> dict[str, Any]:
        required = [item["id"] for item in spec_index.get("requirements", [])]
        implemented = set(evidence.get("implemented_ids", []))
        tested = set(evidence.get("tested_ids", []))
        functional = set(evidence.get("functional_evidence_ids", []))
        missing = [item_id for item_id in required if item_id not in implemented or item_id not in tested or item_id not in functional]
        return {
            "validator": "RequirementCompletenessValidator",
            "status": "complete" if not missing else "blocked",
            "missing_requirement_ids": missing,
        }
