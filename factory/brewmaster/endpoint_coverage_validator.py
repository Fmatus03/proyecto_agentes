from __future__ import annotations

from typing import Any


class EndpointCoverageValidator:
    """Validates specified -> implemented -> documented -> tested endpoint coverage."""

    def validate(self, spec_index: dict[str, Any], evidence: dict[str, Any]) -> dict[str, Any]:
        endpoints = [item["id"] for item in spec_index.get("endpoints", [])]
        implemented = set(evidence.get("implemented_ids", []))
        documented = set(evidence.get("documented_endpoint_ids", []))
        tested = set(evidence.get("tested_ids", []))
        missing = [endpoint_id for endpoint_id in endpoints if endpoint_id not in implemented or endpoint_id not in documented or endpoint_id not in tested]
        return {"validator": "EndpointCoverageValidator", "status": "complete" if not missing else "blocked", "missing_endpoint_ids": missing}
