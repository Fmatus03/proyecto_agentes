from __future__ import annotations

from pathlib import Path

from factory.brewmaster.architecture_drift_validator_v2 import ArchitectureDriftValidatorV2
from factory.brewmaster.transaction_boundary_validator_v2 import TransactionBoundaryValidatorV2


def test_architecture_drift_validator_blocks_router_repository_import(tmp_path: Path) -> None:
    routers = tmp_path / "routers"
    routers.mkdir()
    (routers / "item_router.py").write_text("from app.repositories.items import ItemRepository\n", encoding="utf-8")

    report = ArchitectureDriftValidatorV2().validate(tmp_path)

    assert report["status"] == "blocked"
    assert report["violations"][0]["forbidden_dependency"] in {"repository", "repositories"}


def test_transaction_boundary_validator_detects_writes_after_commit(tmp_path: Path) -> None:
    services = tmp_path / "services"
    services.mkdir()
    (services / "item_service.py").write_text(
        "\n".join(
            [
                "def create_item(session):",
                "    try:",
                "        session.add(object())",
                "        session.commit()",
                "        session.add(object())",
                "    except Exception:",
                "        session.rollback()",
            ]
        ),
        encoding="utf-8",
    )

    report = TransactionBoundaryValidatorV2().validate(tmp_path)

    assert report["status"] == "blocked"
