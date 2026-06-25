from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class ComponentAuditEntry:
    component: str
    files_created: tuple[str, ...]
    responsibilities: tuple[str, ...]
    tests: tuple[str, ...]
    harness_registry: tuple[str, ...]


class ComponentAudit:
    def __init__(self, path: Path) -> None:
        self.path = path
        self.entries: list[ComponentAuditEntry] = []

    def add(self, entry: ComponentAuditEntry) -> None:
        self.entries.append(entry)

    def write(self) -> None:
        lines = [
            "# Component Audit",
            "",
            "| componente del plan | archivos creados | responsabilidades implementadas | pruebas asociadas | registro en harness |",
            "|---|---|---|---|---|",
        ]
        for entry in self.entries:
            lines.append(
                "| "
                + " | ".join(
                    [
                        entry.component,
                        "<br>".join(f"`{item}`" for item in entry.files_created),
                        "<br>".join(entry.responsibilities),
                        "<br>".join(f"`{item}`" for item in entry.tests),
                        "<br>".join(f"`{item}`" for item in entry.harness_registry),
                    ]
                )
                + " |"
            )
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text("\n".join(lines) + "\n", encoding="utf-8")
