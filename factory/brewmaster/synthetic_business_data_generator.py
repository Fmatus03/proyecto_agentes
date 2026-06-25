from __future__ import annotations

from pathlib import Path
from typing import Any

from ..utils import write_json


class SyntheticBusinessDataGenerator:
    """Generates realistic integration data for BrewMaster business flows."""

    def generate(self, spec_index: dict[str, Any]) -> dict[str, Any]:
        entities = {item.get("name", item.get("title", "")) for item in spec_index.get("entities", [])}
        return {
            "providers": [{"id": "PROV-001", "name": "Malteria Andes", "tax_id": "76.111.222-3", "active": True}],
            "customers": [{"id": "CLI-001", "name": "Bar Lupulo", "tax_id": "77.222.333-4", "active": True}],
            "recipes": [{"id": "REC-001", "name": "Pale Ale Base", "yield_liters": 100, "inputs": [{"sku": "MALTA-BASE", "quantity_kg": 20}]}],
            "batches": [{"id": "LOT-001", "recipe_id": "REC-001", "state": "planned", "target_liters": 100}],
            "purchases": [{"id": "OC-001", "provider_id": "PROV-001", "sku": "MALTA-BASE", "quantity_kg": 100, "unit_cost": 1200}],
            "sales": [{"id": "VTA-001", "customer_id": "CLI-001", "product_sku": "PALE-ALE-330", "units": 10, "unit_price": 2500}],
            "kardex_movements": [
                {"id": "KDX-001", "sku": "MALTA-BASE", "type": "in", "quantity_kg": 100, "source": "OC-001"},
                {"id": "KDX-002", "sku": "MALTA-BASE", "type": "out", "quantity_kg": 20, "source": "LOT-001"},
            ],
            "source_entities_seen": sorted(name for name in entities if name),
        }

    def write(self, spec_index: dict[str, Any], output_path: Path) -> dict[str, Any]:
        dataset = self.generate(spec_index)
        write_json(output_path, dataset)
        return dataset
