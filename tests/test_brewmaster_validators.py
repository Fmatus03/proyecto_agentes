from __future__ import annotations

from pathlib import Path

from factory.brewmaster.business_scenario_validator import BusinessScenarioValidator
from factory.brewmaster.canonical_domain_validator import CanonicalDomainValidator
from factory.brewmaster.cross_module_consistency_validator import CrossModuleConsistencyValidator
from factory.brewmaster.endpoint_coverage_validator import EndpointCoverageValidator
from factory.brewmaster.golden_dataset_validator import GoldenDatasetValidator
from factory.brewmaster.rbac_audit_coverage_validator import RBACAuditCoverageValidator
from factory.brewmaster.requirement_completeness_validator import RequirementCompletenessValidator
from factory.brewmaster.screen_functional_coverage_validator import ScreenFunctionalCoverageValidator


def test_requirement_completeness_requires_implemented_tested_and_functional_evidence() -> None:
    spec_index = {"requirements": [{"id": "UC-001"}]}

    blocked = RequirementCompletenessValidator().validate(spec_index, {"implemented_ids": ["UC-001"], "tested_ids": ["UC-001"]})
    complete = RequirementCompletenessValidator().validate(
        spec_index,
        {"implemented_ids": ["UC-001"], "tested_ids": ["UC-001"], "functional_evidence_ids": ["UC-001"]},
    )

    assert blocked["status"] == "blocked"
    assert complete["status"] == "complete"


def test_endpoint_coverage_requires_documented_and_tested_endpoint() -> None:
    spec_index = {"endpoints": [{"id": "END-001"}]}

    report = EndpointCoverageValidator().validate(
        spec_index,
        {"implemented_ids": ["END-001"], "tested_ids": ["END-001"], "documented_endpoint_ids": ["END-001"]},
    )

    assert report["status"] == "complete"


def test_screen_functional_coverage_requires_full_trace() -> None:
    spec_index = {"screens": [{"id": "P-01"}]}

    report = ScreenFunctionalCoverageValidator().validate(
        spec_index,
        {"screen_traces": [{"screen_id": "P-01", "use_case_id": "UC-001", "endpoint_id": "END-001", "playwright_test": "tests/e2e/x.spec.ts"}]},
    )

    assert report["status"] == "complete"


def test_cross_module_consistency_requires_all_core_flows() -> None:
    report = CrossModuleConsistencyValidator().validate(
        {"cross_module_flows": ["purchase_inventory", "production_inventory", "sales_finance", "dashboard_finance"]}
    )

    assert report["status"] == "complete"


def test_business_scenario_validator_writes_scenario_report(tmp_path: Path) -> None:
    report = BusinessScenarioValidator().validate(tmp_path / "scenario-report.json")

    assert report["status"] == "complete"
    assert (tmp_path / "scenario-report.json").exists()


def test_golden_dataset_validator_compares_expected_and_actual(tmp_path: Path) -> None:
    dataset = tmp_path / "golden-dataset.yaml"
    dataset.write_text(
        "\n".join(
            [
                "cases:",
                '  - name: "Compra 100kg Malta"',
                "    expected: 100",
                '  - name: "Completar lote consume 20kg"',
                "    expected: 80",
                '  - name: "Registrar venta 10 unidades"',
                "    expected: 90",
            ]
        ),
        encoding="utf-8",
    )

    report = GoldenDatasetValidator().validate(dataset)

    assert report["status"] == "complete"


def test_canonical_domain_validator_checks_entities_and_attributes(tmp_path: Path) -> None:
    models = tmp_path / "models"
    models.mkdir()
    (models / "provider.py").write_text("class Providers:\n    id: int\n    name: str\n", encoding="utf-8")
    spec_index = {"entities": [{"name": "providers", "attributes": ["id", "name"]}]}

    report = CanonicalDomainValidator().validate(spec_index, tmp_path)

    assert report["status"] == "complete"


def test_rbac_audit_validator_requires_rejection_tests(tmp_path: Path) -> None:
    spec_index = {"permissions": [{"id": "PERM-001"}]}
    evidence = {"rbac_rejection_test_ids": ["PERM-001"]}

    report = RBACAuditCoverageValidator().validate(spec_index, evidence, tmp_path)

    assert report["status"] == "complete"
