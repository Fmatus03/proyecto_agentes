from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from ..utils import sha256_text, write_json


SPEC_INDEX_KEYS = (
    "requirements",
    "business_rules",
    "validations",
    "screens",
    "endpoints",
    "entities",
    "states",
    "permissions",
    "use_cases",
)


@dataclass(frozen=True)
class ParsedItem:
    id: str
    title: str
    source_section: str
    source_line: int
    text: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "title": self.title,
            "source_section": self.source_section,
            "source_line": self.source_line,
            "text": self.text,
        }


class SpecificationParser:
    """Transforms BrewMaster natural language markdown into spec-index.json."""

    def parse_text(self, text: str) -> dict[str, Any]:
        lines = text.splitlines()
        index: dict[str, Any] = {key: [] for key in SPEC_INDEX_KEYS}
        index["metadata"] = {"source_hash": sha256_text(text), "parser": "SpecificationParser"}

        section = ""
        subsection = ""
        for line_no, line in enumerate(lines, start=1):
            heading = re.match(r"^(#+)\s+(.+?)\s*$", line)
            if heading:
                title = heading.group(2).strip()
                level = len(heading.group(1))
                if level <= 2:
                    section = title
                else:
                    subsection = title
                self._parse_heading(index, line_no, section, subsection or title, title)
                continue

            stripped = line.strip()
            if not stripped:
                continue
            self._parse_numbered_rule(index, line_no, section, subsection, stripped)
            self._parse_endpoint(index, line_no, section, stripped)
            self._parse_domain_row(index, line_no, section, stripped)
            self._parse_permission_row(index, line_no, section, stripped)
            self._parse_state_line(index, line_no, section, subsection, stripped)

        index["requirements"] = self._requirements(index)
        return index

    def parse_file(self, spec_path: Path, output_path: Path) -> dict[str, Any]:
        index = self.parse_text(spec_path.read_text(encoding="utf-8"))
        index["metadata"]["source_path"] = str(spec_path)
        write_json(output_path, index)
        return index

    def _parse_heading(self, index: dict[str, Any], line_no: int, section: str, subsection: str, title: str) -> None:
        uc = re.match(r"^(UC-[A-Z]+-\d+)\s+(.+)$", title)
        if uc:
            index["use_cases"].append(ParsedItem(uc.group(1), uc.group(2), section, line_no, title).to_dict())
            return
        screen = re.match(r"^(P-\d+)\s+(.+)$", title)
        if screen:
            index["screens"].append(ParsedItem(screen.group(1), screen.group(2), section, line_no, title).to_dict())

    def _parse_numbered_rule(self, index: dict[str, Any], line_no: int, section: str, subsection: str, stripped: str) -> None:
        numbered = re.match(r"^(\d+)\.\s+(.+)$", stripped)
        if not numbered:
            return
        number, text = numbered.groups()
        normalized_section = section.lower()
        if "reglas de negocio" in normalized_section:
            index["business_rules"].append(ParsedItem(f"RN-{int(number):03d}", text, section, line_no, text).to_dict())
        elif "validaciones" in normalized_section:
            index["validations"].append(ParsedItem(f"V-{int(number):03d}", text, section, line_no, text).to_dict())
        elif "permisos" in normalized_section:
            index["permissions"].append(ParsedItem(f"PERM-{int(number):03d}", text, section, line_no, text).to_dict())
        elif "estados" in normalized_section:
            index["states"].append(ParsedItem(f"STATE-{int(number):03d}", subsection, section, line_no, text).to_dict())

    def _parse_endpoint(self, index: dict[str, Any], line_no: int, section: str, stripped: str) -> None:
        if "endpoints" not in section.lower() and "endpoint" not in section.lower():
            return
        match = re.search(r"`?(GET|POST|PUT|PATCH|DELETE)\s+([^`\s]+)`?", stripped, flags=re.IGNORECASE)
        if match:
            method = match.group(1).upper()
            path = match.group(2)
            index["endpoints"].append(
                {
                    "id": f"END-{len(index['endpoints']) + 1:03d}",
                    "method": method,
                    "path": path,
                    "title": f"{method} {path}",
                    "source_section": section,
                    "source_line": line_no,
                    "text": stripped,
                }
            )

    def _parse_domain_row(self, index: dict[str, Any], line_no: int, section: str, stripped: str) -> None:
        if "modelo de dominio" not in section.lower() or not stripped.startswith("|"):
            return
        cells = [cell.strip().strip("`") for cell in stripped.strip("|").split("|")]
        if len(cells) < 3 or cells[0].lower() in {"entidad", "---"} or set(cells[0]) == {"-"}:
            return
        attrs = [attr.strip().strip("`") for attr in cells[2].split(",") if attr.strip()]
        index["entities"].append(
            {
                "id": f"ENT-{len(index['entities']) + 1:03d}",
                "name": cells[0],
                "title": cells[0],
                "description": cells[1],
                "attributes": attrs,
                "source_section": section,
                "source_line": line_no,
                "text": stripped,
            }
        )

    def _parse_permission_row(self, index: dict[str, Any], line_no: int, section: str, stripped: str) -> None:
        if "permisos" not in section.lower() or not stripped.startswith("|"):
            return
        cells = [cell.strip().strip("`") for cell in stripped.strip("|").split("|")]
        if len(cells) < 2 or cells[0].lower() in {"rol", "permiso", "---"} or set(cells[0]) == {"-"}:
            return
        index["permissions"].append(
            {
                "id": f"PERM-{len(index['permissions']) + 1:03d}",
                "role": cells[0],
                "title": cells[0],
                "permissions": cells[1:],
                "source_section": section,
                "source_line": line_no,
                "text": stripped,
            }
        )

    def _parse_state_line(self, index: dict[str, Any], line_no: int, section: str, subsection: str, stripped: str) -> None:
        if "estados recomendados" not in section.lower() or "->" not in stripped:
            return
        index["states"].append(
            {
                "id": f"STATE-{len(index['states']) + 1:03d}",
                "module": subsection,
                "title": subsection,
                "flow": [part.strip() for part in stripped.split("->")],
                "source_section": section,
                "source_line": line_no,
                "text": stripped,
            }
        )

    def _requirements(self, index: dict[str, Any]) -> list[dict[str, Any]]:
        requirements: list[dict[str, Any]] = []
        for key, req_type in (("use_cases", "UC"), ("business_rules", "RN"), ("validations", "V")):
            for item in index[key]:
                requirements.append(
                    {
                        "id": item["id"],
                        "type": req_type,
                        "title": item["title"],
                        "source_section": item["source_section"],
                        "source_line": item["source_line"],
                    }
                )
        return requirements
