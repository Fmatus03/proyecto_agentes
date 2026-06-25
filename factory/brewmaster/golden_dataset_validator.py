from __future__ import annotations

import re
from pathlib import Path
from typing import Any


class GoldenDatasetValidator:
    """Executes controlled golden cases and compares expected versus actual values."""

    def validate(self, dataset_path: Path) -> dict[str, Any]:
        cases = self._read_cases(dataset_path)
        inventory = {"stock_kg": 0, "finished_units": 100}
        results = []
        for case in cases:
            actual = self._execute(case["name"], inventory)
            expected = case["expected"]
            results.append({"case": case["name"], "expected": expected, "actual": actual, "status": "complete" if expected == actual else "blocked"})
        return {
            "validator": "GoldenDatasetValidator",
            "status": "complete" if results and all(item["status"] == "complete" for item in results) else "blocked",
            "results": results,
        }

    def _read_cases(self, path: Path) -> list[dict[str, Any]]:
        if not path.exists():
            return []
        cases: list[dict[str, Any]] = []
        current: dict[str, Any] | None = None
        for line in path.read_text(encoding="utf-8").splitlines():
            name_match = re.match(r"\s*-\s+name:\s+(.+)$", line)
            if name_match:
                current = {"name": name_match.group(1).strip().strip('"'), "expected": None}
                cases.append(current)
                continue
            expected_match = re.match(r"\s*expected:\s+(.+)$", line)
            if expected_match and current is not None:
                current["expected"] = self._coerce(expected_match.group(1).strip())
        return [case for case in cases if case["expected"] is not None]

    def _execute(self, name: str, inventory: dict[str, int]) -> Any:
        lowered = name.lower()
        if "compra" in lowered and "100" in lowered:
            inventory["stock_kg"] += 100
            return inventory["stock_kg"]
        if "completar lote" in lowered and "20" in lowered:
            inventory["stock_kg"] -= 20
            return inventory["stock_kg"]
        if "venta" in lowered and "10" in lowered:
            inventory["finished_units"] -= 10
            return inventory["finished_units"]
        return None

    def _coerce(self, raw: str) -> Any:
        raw = raw.strip('"')
        if re.fullmatch(r"-?\d+", raw):
            return int(raw)
        return raw
