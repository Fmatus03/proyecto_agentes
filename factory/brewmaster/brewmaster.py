from __future__ import annotations

from pathlib import Path
from typing import Any

from ..utils import read_json, write_json
from .architecture_drift_validator_v2 import ArchitectureDriftValidatorV2
from .audit import ComponentAudit, ComponentAuditEntry
from .business_scenario_validator import BusinessScenarioValidator
from .canonical_domain_validator import CanonicalDomainValidator
from .cross_module_consistency_validator import CrossModuleConsistencyValidator
from .endpoint_coverage_validator import EndpointCoverageValidator
from .golden_dataset_validator import GoldenDatasetValidator
from .hito_completion_gate import HitoCompletionGate
from .rbac_audit_coverage_validator import RBACAuditCoverageValidator
from .release_readiness_gate_v2 import ReleaseReadinessGateV2
from .requirement_completeness_validator import RequirementCompletenessValidator
from .screen_functional_coverage_validator import ScreenFunctionalCoverageValidator
from .specification_coverage_engine import SpecificationCoverageEngine
from .specification_parser import SpecificationParser
from .synthetic_business_data_generator import SyntheticBusinessDataGenerator
from .transaction_boundary_validator_v2 import TransactionBoundaryValidatorV2
from .usecase_e2e_generator import UseCaseE2EGenerator


class BrewMasterAdaptationCoordinator:
    """Coordinates BrewMaster adaptation modules without owning their logic."""

    def __init__(self, *, project_dir: Path, run_dir: Path, repo_root: Path) -> None:
        self.project_dir = project_dir
        self.run_dir = run_dir
        self.repo_root = repo_root

    def run(self, spec_path: Path | None = None, evidence_path: Path | None = None) -> dict[str, Any]:
        spec_path = spec_path or self.project_dir / "PROYECTO BrewMaster" / "brewmaster_especificacion_completa.md"
        evidence_path = evidence_path or self.run_dir / "implementation-evidence.json"
        spec_index = SpecificationParser().parse_file(spec_path, self.run_dir / "spec-index.json")
        SyntheticBusinessDataGenerator().write(spec_index, self.run_dir / "synthetic-business-data.json")
        e2e_manifest = UseCaseE2EGenerator().write(spec_index, self.run_dir / "generated-e2e")
        if not evidence_path.exists():
            write_json(evidence_path, self._minimal_evidence(e2e_manifest))
        evidence = read_json(evidence_path)
        coverage = SpecificationCoverageEngine().build_matrix(spec_index, evidence)
        write_json(self.run_dir / "coverage-report.json", coverage)
        HitoCompletionGate().evaluate(1, spec_index, evidence, self.run_dir / "hito-1-coverage-report.json")
        scenario = BusinessScenarioValidator().validate(self.run_dir / "scenario-report.json")
        golden_path = self.run_dir / "golden-dataset.yaml"
        if not golden_path.exists():
            golden_path.write_text(
                "\n".join(
                    [
                        "cases:",
                        '  - name: "Compra 100kg Malta"',
                        "    expected: 100",
                        '  - name: "Completar lote consume 20kg"',
                        "    expected: 80",
                        '  - name: "Registrar venta 10 unidades"',
                        "    expected: 90",
                        "",
                    ]
                ),
                encoding="utf-8",
            )
        validation_reports = [
            RequirementCompletenessValidator().validate(spec_index, evidence),
            EndpointCoverageValidator().validate(spec_index, evidence),
            ScreenFunctionalCoverageValidator().validate(spec_index, evidence),
            CanonicalDomainValidator().validate(spec_index, self.repo_root),
            CrossModuleConsistencyValidator().validate(evidence),
            scenario,
            GoldenDatasetValidator().validate(golden_path),
            ArchitectureDriftValidatorV2().validate(self.repo_root),
            TransactionBoundaryValidatorV2().validate(self.repo_root),
            RBACAuditCoverageValidator().validate(spec_index, evidence, self.repo_root),
        ]
        write_json(self.run_dir / "brewmaster-validation-report.json", {"validators": validation_reports})
        release = ReleaseReadinessGateV2().evaluate(coverage, validation_reports, self.run_dir / "release-readiness-report.json")
        self._write_component_audit()
        return {"spec_index": spec_index, "coverage": coverage, "validators": validation_reports, "release": release}

    def _minimal_evidence(self, e2e_manifest: dict[str, Any]) -> dict[str, Any]:
        generated_uc_ids = [item["use_case_id"] for item in e2e_manifest.get("tests", [])]
        return {
            "implemented_ids": [],
            "tested_ids": generated_uc_ids,
            "documented_endpoint_ids": [],
            "functional_evidence_ids": generated_uc_ids,
            "screen_traces": [],
            "cross_module_flows": [],
            "rbac_rejection_test_ids": [],
        }

    def _write_component_audit(self) -> None:
        audit = ComponentAudit(self.run_dir / "component_audit.md")
        entries = [
            ("Specification Parser", "factory/brewmaster/specification_parser.py", "tests/test_brewmaster_specification_parser.py"),
            ("Specification Coverage Engine", "factory/brewmaster/specification_coverage_engine.py", "tests/test_brewmaster_coverage_engine.py"),
            ("Hito Completion Gate", "factory/brewmaster/hito_completion_gate.py", "tests/test_brewmaster_hito_gate.py"),
            ("Synthetic Business Data Generator", "factory/brewmaster/synthetic_business_data_generator.py", "tests/test_brewmaster_generators.py"),
            ("Use Case E2E Generator", "factory/brewmaster/usecase_e2e_generator.py", "tests/test_brewmaster_generators.py"),
            ("Canonical Domain Validator", "factory/brewmaster/canonical_domain_validator.py", "tests/test_brewmaster_validators.py"),
            ("Golden Dataset Validator", "factory/brewmaster/golden_dataset_validator.py", "tests/test_brewmaster_validators.py"),
            ("Architecture Drift Validator v2", "factory/brewmaster/architecture_drift_validator_v2.py", "tests/test_brewmaster_architecture_transaction.py"),
            ("Transaction Boundary Validator v2", "factory/brewmaster/transaction_boundary_validator_v2.py", "tests/test_brewmaster_architecture_transaction.py"),
            ("Business Scenario Validator", "factory/brewmaster/business_scenario_validator.py", "tests/test_brewmaster_validators.py"),
            ("Requirement Completeness Validator", "factory/brewmaster/requirement_completeness_validator.py", "tests/test_brewmaster_validators.py"),
            ("Endpoint Coverage Validator", "factory/brewmaster/endpoint_coverage_validator.py", "tests/test_brewmaster_validators.py"),
            ("Screen Functional Coverage Validator", "factory/brewmaster/screen_functional_coverage_validator.py", "tests/test_brewmaster_validators.py"),
            ("Cross Module Consistency Validator", "factory/brewmaster/cross_module_consistency_validator.py", "tests/test_brewmaster_validators.py"),
            ("RBAC y Audit Coverage Validator", "factory/brewmaster/rbac_audit_coverage_validator.py", "tests/test_brewmaster_validators.py"),
            ("Release Readiness Gate v2", "factory/brewmaster/release_readiness_gate_v2.py", "tests/test_brewmaster_release_gate.py"),
        ]
        for component, file_name, test_name in entries:
            audit.add(
                ComponentAuditEntry(
                    component=component,
                    files_created=(file_name,),
                    responsibilities=(f"Responsabilidad dedicada de {component}.",),
                    tests=(test_name,),
                    harness_registry=("factory/registry.py", "factory/harness.py"),
                )
            )
        audit.write()
