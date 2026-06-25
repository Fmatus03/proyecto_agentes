from __future__ import annotations

from pathlib import Path

from factory.brewmaster.hito_completion_gate import HitoCompletionGate


def test_hito_completion_gate_writes_blocking_report(tmp_path: Path) -> None:
    spec_index = {
        "requirements": [],
        "business_rules": [{"id": "RN-001"}],
        "validations": [],
        "screens": [],
        "endpoints": [],
        "entities": [],
        "states": [],
        "permissions": [],
        "use_cases": [],
    }

    report = HitoCompletionGate().evaluate(1, spec_index, {}, tmp_path / "coverage-report.json")

    assert report["status"] == "blocked"
    assert report["pending"] == 1
    assert (tmp_path / "coverage-report.json").exists()
