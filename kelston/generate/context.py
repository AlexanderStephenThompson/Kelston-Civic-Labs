"""Shared state for the generation pipeline.

Each stage draws randomness from its own named child RNG, so adding a new
stage never perturbs the output of earlier ones - the determinism guarantee
CI relies on.
"""

from __future__ import annotations

import random
from collections import defaultdict
from dataclasses import dataclass, field

from kelston.ksl.loader import Catalog


@dataclass
class GenContext:
    seed: int
    catalog: Catalog
    population: int = 5000
    instances: dict[str, list[dict]] = field(default_factory=lambda: defaultdict(list))
    by_id: dict[str, dict] = field(default_factory=dict)
    _counters: dict[str, int] = field(default_factory=lambda: defaultdict(int))

    def rng(self, stage: str) -> random.Random:
        return random.Random(f"{self.seed}:{stage}")

    def new_id(self, prefix: str) -> str:
        self._counters[prefix] += 1
        return f"{prefix}-{self._counters[prefix]:06d}"

    def add(self, schema_name: str, instance_id: str | None = None, **fields) -> dict:
        """Create an instance stamped with the schema's current version."""
        schema = self.catalog.schemas[schema_name]
        if instance_id is None:
            prefix = schema.identity_prefix
            if prefix is None:
                for ancestor in reversed(self.catalog.ancestors(schema_name)):
                    if ancestor.identity_prefix:
                        prefix = ancestor.identity_prefix
                        break
            instance_id = self.new_id(prefix)
        instance = {
            "id": instance_id,
            "conforms_to": f"{schema_name}@{schema.version}",
        }
        instance.update({k: v for k, v in fields.items() if v is not None})
        self.instances[schema_name].append(instance)
        self.by_id[instance_id] = instance
        return instance

    def adopt(self, instance: dict) -> dict:
        """Register an authored instance (world data) into the pipeline state."""
        schema_name = instance["conforms_to"].split("@", 1)[0]
        self.instances[schema_name].append(instance)
        self.by_id[instance["id"]] = instance
        return instance

    def all_of(self, schema_name: str) -> list[dict]:
        return self.instances[schema_name]
