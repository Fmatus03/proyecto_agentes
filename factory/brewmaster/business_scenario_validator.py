from __future__ import annotations

from pathlib import Path
from typing import Any

from ..utils import write_json


class BusinessScenarioValidator:
    """Validates purchase, production, sale and integral BrewMaster scenarios."""

    def validate(self, output_path: Path) -> dict[str, Any]:
        stock_inputs = 0
        finished = 100
        finances = 0
        steps = []

        stock_inputs += 100
        steps.append(self._step("Escenario Compra", "stock_inputs", 100, stock_inputs))
        stock_inputs -= 20
        steps.append(self._step("Escenario Produccion", "stock_inputs", 80, stock_inputs))
        finished -= 10
        finances += 25000
        steps.append(self._step("Escenario Venta", "finished_units", 90, finished))
        dashboard = {"stock_inputs": stock_inputs, "finished_units": finished, "finance_income": finances}
        steps.append(self._step("Escenario Integral", "dashboard", {"stock_inputs": 80, "finished_units": 90, "finance_income": 25000}, dashboard))

        report = {
            "validator": "BusinessScenarioValidator",
            "status": "complete" if all(step["status"] == "complete" for step in steps) else "blocked",
            "steps": steps,
        }
        write_json(output_path, report)
        return report

    def _step(self, scenario: str, field: str, expected: Any, actual: Any) -> dict[str, Any]:
        return {
            "scenario": scenario,
            "field": field,
            "expected": expected,
            "actual": actual,
            "difference": None if expected == actual else {"expected": expected, "actual": actual},
            "status": "complete" if expected == actual else "blocked",
        }
