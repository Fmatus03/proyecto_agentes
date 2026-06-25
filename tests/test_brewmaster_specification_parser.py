from __future__ import annotations

from pathlib import Path

from factory.brewmaster.specification_parser import SpecificationParser


def test_specification_parser_builds_required_spec_index_keys() -> None:
    spec_path = Path("project/PROYECTO BrewMaster/brewmaster_especificacion_completa.md")
    index = SpecificationParser().parse_text(spec_path.read_text(encoding="utf-8"))

    for key in ("requirements", "business_rules", "validations", "screens", "endpoints", "entities", "states", "permissions", "use_cases"):
        assert key in index

    assert any(item["id"].startswith("UC-") for item in index["use_cases"])
    assert any(item["id"].startswith("RN-") for item in index["business_rules"])
    assert any(item["id"].startswith("V-") for item in index["validations"])
    assert any(item["id"].startswith("P-") for item in index["screens"])
    assert index["requirements"]


def test_specification_parser_writes_spec_index_json(tmp_path: Path) -> None:
    spec = tmp_path / "spec.md"
    out = tmp_path / "spec-index.json"
    spec.write_text(
        "\n".join(
            [
                "# C. Reglas de negocio",
                "1. Stock no puede ser negativo.",
                "# D. Validaciones y CHECK",
                "1. Nombre requerido.",
                "# F. Endpoints REST",
                "`POST /api/v1/items`",
                "# A. Casos de uso con flujos",
                "### UC-INS-01 Registrar insumo",
                "# B. Especificacion de pantallas",
                "### P-01 Login",
            ]
        ),
        encoding="utf-8",
    )

    index = SpecificationParser().parse_file(spec, out)

    assert out.exists()
    assert index["business_rules"][0]["id"] == "RN-001"
    assert index["validations"][0]["id"] == "V-001"
    assert index["endpoints"][0]["method"] == "POST"
