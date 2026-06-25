from __future__ import annotations

from typing import Any


class ScreenFunctionalCoverageValidator:
    """Validates Screen -> Use Case -> Endpoint -> Playwright test traces."""

    def validate(self, spec_index: dict[str, Any], evidence: dict[str, Any]) -> dict[str, Any]:
        traces = evidence.get("screen_traces", [])
        trace_by_screen = {trace.get("screen_id"): trace for trace in traces}
        missing = []
        for screen in spec_index.get("screens", []):
            trace = trace_by_screen.get(screen["id"])
            if not trace or not all(trace.get(key) for key in ("use_case_id", "endpoint_id", "playwright_test")):
                missing.append(screen["id"])
        return {"validator": "ScreenFunctionalCoverageValidator", "status": "complete" if not missing else "blocked", "missing_screen_ids": missing}
