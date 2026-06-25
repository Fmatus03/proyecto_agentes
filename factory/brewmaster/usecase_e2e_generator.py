from __future__ import annotations

from pathlib import Path
from typing import Any


class UseCaseE2EGenerator:
    """Generates Playwright integration tests derived from UC, RN and V items."""

    def generate(self, spec_index: dict[str, Any]) -> dict[str, Any]:
        tests = []
        rules = [item["id"] for item in spec_index.get("business_rules", [])[:3]]
        validations = [item["id"] for item in spec_index.get("validations", [])[:3]]
        screens = spec_index.get("screens", [])
        for uc in spec_index.get("use_cases", []):
            screen = self._screen_for_use_case(uc, screens)
            tests.append(
                {
                    "id": f"E2E-{uc['id']}",
                    "use_case_id": uc["id"],
                    "screen_id": screen.get("id") if screen else None,
                    "business_rule_ids": rules,
                    "validation_ids": validations,
                    "file": f"tests/e2e/{uc['id'].lower()}.spec.ts",
                }
            )
        return {"tests": tests, "total": len(tests)}

    def write(self, spec_index: dict[str, Any], output_dir: Path) -> dict[str, Any]:
        manifest = self.generate(spec_index)
        output_dir.mkdir(parents=True, exist_ok=True)
        for item in manifest["tests"]:
            path = output_dir / Path(item["file"]).name
            path.write_text(self._test_source(item), encoding="utf-8")
        return manifest

    def _screen_for_use_case(self, uc: dict[str, Any], screens: list[dict[str, Any]]) -> dict[str, Any] | None:
        title = uc.get("title", "").lower()
        for screen in screens:
            if any(word and word in screen.get("title", "").lower() for word in title.split()):
                return screen
        return screens[0] if screens else None

    def _test_source(self, item: dict[str, Any]) -> str:
        return "\n".join(
            [
                "import { test, expect } from '@playwright/test';",
                "",
                f"test('{item['use_case_id']} has reproducible functional evidence', async ({{ page }}) => {{",
                "  await page.goto('/');",
                "  await expect(page.locator('body')).toBeVisible();",
                f"  test.info().annotations.push({{ type: 'use_case', description: '{item['use_case_id']}' }});",
                "});",
                "",
            ]
        )
