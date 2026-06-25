from __future__ import annotations

from pathlib import Path

from factory.brewmaster.release_readiness_gate_v2 import ReleaseReadinessGateV2


def test_release_readiness_gate_requires_all_validators_and_zero_pending(tmp_path: Path) -> None:
    validator_names = ReleaseReadinessGateV2.REQUIRED_VALIDATORS
    validation_reports = [{"validator": name, "status": "complete"} for name in validator_names]

    report = ReleaseReadinessGateV2().evaluate({"totals": {"pending": 0}}, validation_reports, tmp_path / "release.json")

    assert report["status"] == "complete"
    assert (tmp_path / "release.json").exists()


def test_release_readiness_gate_blocks_failed_validator(tmp_path: Path) -> None:
    validator_names = ReleaseReadinessGateV2.REQUIRED_VALIDATORS
    validation_reports = [{"validator": name, "status": "complete"} for name in validator_names]
    validation_reports[0]["status"] = "blocked"

    report = ReleaseReadinessGateV2().evaluate({"totals": {"pending": 0}}, validation_reports, tmp_path / "release.json")

    assert report["status"] == "blocked"
