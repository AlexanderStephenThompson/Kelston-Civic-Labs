"""The migration engine: how an updated standard reaches every instance.

Migrations are declarative YAML. Four operations cover the routine cases,
and `derive_field` reaches into kelston/rules/ for the hard ones - the
same single escape hatch the constraint system uses.
"""

from __future__ import annotations

import importlib
from dataclasses import dataclass
from pathlib import Path

import yaml

from kelston import paths
from kelston.registry import semver


@dataclass
class Migration:
    schema: str
    from_range: str
    to_version: str
    summary: str
    operations: list[dict]
    path: Path

    def applies_to(self, version: str) -> bool:
        return semver.matches_range(version, self.from_range)


def load_migrations(schema_name: str) -> list[Migration]:
    directory = paths.MIGRATIONS_DIR / schema_name
    migrations = []
    if directory.is_dir():
        for path in sorted(directory.glob("*.yaml")):
            with open(path, encoding="utf-8") as handle:
                doc = yaml.safe_load(handle)
            head = doc["migration"]
            migrations.append(
                Migration(
                    schema=head["schema"],
                    from_range=str(head["from"]),
                    to_version=str(head["to"]),
                    summary=head.get("summary", ""),
                    operations=doc.get("operations") or [],
                    path=path,
                )
            )
    migrations.sort(key=lambda m: semver.parse(m.to_version))
    return migrations


def apply_migration(instance: dict, migration: Migration) -> dict:
    upgraded = dict(instance)
    for operation in migration.operations:
        (op_name, spec), = operation.items()
        if op_name == "rename_field":
            if spec["from"] in upgraded:
                upgraded[spec["to"]] = upgraded.pop(spec["from"])
        elif op_name == "add_field":
            upgraded.setdefault(spec["name"], spec.get("default"))
        elif op_name == "remove_field":
            upgraded.pop(spec["name"], None)
        elif op_name == "map_vocab":
            value = upgraded.get(spec["field"])
            if value in spec["mapping"]:
                upgraded[spec["field"]] = spec["mapping"][value]
        elif op_name == "derive_field":
            upgraded[spec["name"]] = _load_deriver(spec["using"])(upgraded)
        else:
            raise ValueError(f"{migration.path}: unknown operation {op_name!r}")
    upgraded["conforms_to"] = f"{migration.schema}@{migration.to_version}"
    return upgraded


def upgrade_instance(instance: dict, migrations: list[Migration]) -> tuple[dict, list[str]]:
    """Walk an instance through every migration that applies, in order."""
    applied = []
    current = instance
    for migration in migrations:
        stamped_version = current["conforms_to"].split("@", 1)[1]
        if migration.applies_to(stamped_version):
            current = apply_migration(current, migration)
            applied.append(migration.to_version)
    return current, applied


def _load_deriver(using: str):
    spec = using.removeprefix("python:")
    module_name, _, function_name = spec.rpartition(".")
    module = importlib.import_module(f"kelston.rules.{module_name}")
    return getattr(module, function_name)
