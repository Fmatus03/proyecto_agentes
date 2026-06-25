from __future__ import annotations

from factory.brewmaster.specification_coverage_engine import SpecificationCoverageEngine


def test_coverage_engine_blocks_any_pending_spec_item() -> None:
    spec_index = {
        "requirements": [{"id": "UC-001"}],
        "business_rules": [{"id": "RN-001"}],
        "validations": [],
        "screens": [],
        "endpoints": [],
        "entities": [],
        "states": [],
        "permissions": [],
        "use_cases": [{"id": "UC-001"}],
    }
    evidence = {"implemented_ids": ["UC-001"], "tested_ids": ["UC-001"]}

    matrix = SpecificationCoverageEngine().build_matrix(spec_index, evidence)

    assert matrix["status"] == "blocked"
    assert matrix["totals"]["pending"] == 1


def test_coverage_engine_requires_endpoint_documentation() -> None:
    spec_index = {
        "requirements": [],
        "business_rules": [],
        "validations": [],
        "screens": [],
        "endpoints": [{"id": "END-001"}],
        "entities": [],
        "states": [],
        "permissions": [],
        "use_cases": [],
    }

    blocked = SpecificationCoverageEngine().build_matrix(spec_index, {"implemented_ids": ["END-001"], "tested_ids": ["END-001"]})
    complete = SpecificationCoverageEngine().build_matrix(
        spec_index,
        {"implemented_ids": ["END-001"], "tested_ids": ["END-001"], "documented_endpoint_ids": ["END-001"]},
    )

    assert blocked["status"] == "blocked"
    assert complete["status"] == "complete"
