from __future__ import annotations

from factory.brewmaster.synthetic_business_data_generator import SyntheticBusinessDataGenerator
from factory.brewmaster.usecase_e2e_generator import UseCaseE2EGenerator


def test_synthetic_business_data_generator_produces_required_business_data() -> None:
    dataset = SyntheticBusinessDataGenerator().generate({"entities": [{"name": "providers"}]})

    for key in ("providers", "customers", "recipes", "batches", "purchases", "sales", "kardex_movements"):
        assert dataset[key]


def test_usecase_e2e_generator_creates_one_test_per_use_case() -> None:
    spec_index = {
        "use_cases": [{"id": "UC-INS-01", "title": "Registrar insumo"}],
        "business_rules": [{"id": "RN-001"}],
        "validations": [{"id": "V-001"}],
        "screens": [{"id": "P-05", "title": "Formulario de insumo"}],
    }

    manifest = UseCaseE2EGenerator().generate(spec_index)

    assert manifest["total"] == 1
    assert manifest["tests"][0]["use_case_id"] == "UC-INS-01"
    assert manifest["tests"][0]["business_rule_ids"] == ["RN-001"]
