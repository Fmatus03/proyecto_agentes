from __future__ import annotations

from typing import Any


class CrossModuleConsistencyValidator:
    """Detects inconsistent global cross-module flows such as sales to finance."""

    REQUIRED_FLOWS = ("purchase_inventory", "production_inventory", "sales_finance", "dashboard_finance")

    def validate(self, evidence: dict[str, Any]) -> dict[str, Any]:
        flows = set(evidence.get("cross_module_flows", []))
        missing = [flow for flow in self.REQUIRED_FLOWS if flow not in flows]
        return {"validator": "CrossModuleConsistencyValidator", "status": "complete" if not missing else "blocked", "missing_flows": missing}
