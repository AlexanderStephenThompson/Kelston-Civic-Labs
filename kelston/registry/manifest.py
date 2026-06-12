"""Build and verify registry/manifest.yaml - the single source of truth
for which version of every standard is current.

Checksums make silent drift impossible: editing a schema without bumping
its registry entry fails `kelston registry status`, and therefore CI.
"""

from __future__ import annotations

import hashlib
from datetime import date
from pathlib import Path

import yaml

from kelston import paths
from kelston.ksl.loader import Catalog, SchemaDef
from kelston.registry import semver

UNITS_VOCAB = "kelston.vocab.unit"


def checksum(path: Path) -> str:
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


def depends_on(schema: SchemaDef, catalog: Catalog) -> list[str]:
    """Extract every standard this schema leans on, pinned to its major."""
    deps: set[str] = set()
    if schema.extends:
        deps.add(_pin(schema.extends, catalog.schemas[schema.extends].version))

    def walk(spec: dict) -> None:
        type_name = spec.get("type")
        if type_name == "ref" and spec.get("entity") in catalog.schemas:
            deps.add(_pin(spec["entity"], catalog.schemas[spec["entity"]].version))
        if type_name == "vocab" and spec.get("vocabulary") in catalog.vocabularies:
            deps.add(_pin(spec["vocabulary"], catalog.vocabularies[spec["vocabulary"]].version))
        if type_name == "quantity" and UNITS_VOCAB in catalog.vocabularies:
            deps.add(_pin(UNITS_VOCAB, catalog.vocabularies[UNITS_VOCAB].version))
        if type_name == "list" and isinstance(spec.get("items"), dict):
            walk(spec["items"])
        if type_name == "record":
            for sub in (spec.get("fields") or {}).values():
                walk(sub)

    for spec in schema.fields.values():
        if isinstance(spec, dict):
            walk(spec)
    return sorted(deps)


def _pin(name: str, version: str) -> str:
    return f"{name}@^{semver.parse(version)[0]}"


def load_manifest(path: Path | None = None) -> dict:
    with open(path or paths.MANIFEST, encoding="utf-8") as handle:
        return yaml.safe_load(handle)


def save_manifest(manifest: dict, path: Path | None = None) -> None:
    target = path or paths.MANIFEST
    target.parent.mkdir(parents=True, exist_ok=True)
    with open(target, "w", encoding="utf-8") as handle:
        yaml.safe_dump(manifest, handle, sort_keys=True, allow_unicode=True, width=100)


def build_manifest(catalog: Catalog, as_of: str | None = None) -> dict:
    """A fresh manifest where every standard starts its recorded history."""
    today = as_of or date.today().isoformat()
    manifest: dict = {"registry": "kelston", "schemas": {}, "vocabularies": {}}
    for name, schema in sorted(catalog.schemas.items()):
        manifest["schemas"][name] = {
            "current": schema.version,
            "status": schema.status,
            "checksum": checksum(schema.path),
            "depends_on": depends_on(schema, catalog),
            "history": [{"version": schema.version, "date": today, "change": "initial"}],
        }
    for name, vocab in sorted(catalog.vocabularies.items()):
        manifest["vocabularies"][name] = {
            "current": vocab.version,
            "checksum": checksum(vocab.path),
            "history": [{"version": vocab.version, "date": today, "change": "initial"}],
        }
    return manifest


def verify_manifest(manifest: dict, catalog: Catalog) -> list[str]:
    """Every problem that makes the manifest and the files disagree."""
    errors: list[str] = []
    recorded_schemas = manifest.get("schemas", {})
    recorded_vocabs = manifest.get("vocabularies", {})

    for name, schema in catalog.schemas.items():
        entry = recorded_schemas.get(name)
        if entry is None:
            errors.append(f"{name}: not in the registry manifest - run `kelston registry bump`")
            continue
        if entry["current"] != schema.version:
            errors.append(
                f"{name}: file says {schema.version}, manifest says {entry['current']}"
            )
        if entry["checksum"] != checksum(schema.path):
            errors.append(f"{name}: file changed without a registry bump")
        expected_deps = depends_on(schema, catalog)
        if entry.get("depends_on", []) != expected_deps:
            errors.append(f"{name}: depends_on is stale - re-run `kelston registry bump`")
        for requirement in entry.get("depends_on", []):
            dep_name, _, pin = requirement.partition("@")
            dep_entry = recorded_schemas.get(dep_name) or recorded_vocabs.get(dep_name)
            if dep_entry is None:
                errors.append(f"{name}: depends on unregistered {dep_name}")
            elif not semver.compatible(dep_entry["current"], pin):
                errors.append(
                    f"{name}: needs {requirement}, registry has {dep_entry['current']}"
                )
        for event in entry.get("history", []):
            if event.get("change") == "major":
                migration = (
                    paths.MIGRATIONS_DIR / name / f"{event['version']}.yaml"
                )
                if not migration.exists():
                    errors.append(
                        f"{name}: major version {event['version']} has no migration file"
                    )
    for name in recorded_schemas:
        if name not in catalog.schemas:
            errors.append(f"{name}: in the manifest but the schema file is gone")

    for name, vocab in catalog.vocabularies.items():
        entry = recorded_vocabs.get(name)
        if entry is None:
            errors.append(f"{name}: not in the registry manifest")
            continue
        if entry["current"] != vocab.version:
            errors.append(f"{name}: file says {vocab.version}, manifest says {entry['current']}")
        if entry["checksum"] != checksum(vocab.path):
            errors.append(f"{name}: vocabulary changed without a registry bump")
    for name in recorded_vocabs:
        if name not in catalog.vocabularies:
            errors.append(f"{name}: in the manifest but the vocabulary file is gone")
    return errors


def record_bump(
    manifest: dict,
    name: str,
    catalog: Catalog,
    change: str,
    as_of: str | None = None,
) -> None:
    """Update one standard's manifest entry after its file has been edited."""
    today = as_of or date.today().isoformat()
    if name in catalog.schemas:
        schema = catalog.schemas[name]
        entry = manifest["schemas"].setdefault(
            name, {"history": [], "status": schema.status}
        )
        entry.update(
            current=schema.version,
            status=schema.status,
            checksum=checksum(schema.path),
            depends_on=depends_on(schema, catalog),
        )
    elif name in catalog.vocabularies:
        vocab = catalog.vocabularies[name]
        entry = manifest["vocabularies"].setdefault(name, {"history": []})
        entry.update(current=vocab.version, checksum=checksum(vocab.path))
    else:
        raise KeyError(f"no schema or vocabulary named {name}")
    event = {"version": entry["current"], "date": today, "change": change}
    if change == "major":
        event["migration"] = f"{entry['current']}.yaml"
    entry["history"].append(event)
