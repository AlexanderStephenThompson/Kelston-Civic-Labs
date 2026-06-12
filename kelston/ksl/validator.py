"""Instance validation: does every record conform to the exact standard it
is stamped with?

The Store holds every instance in town so references can be resolved and
cross-entity constraints checked.
"""

from __future__ import annotations

import json
from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path

from kelston.ksl import types
from kelston.ksl.constraints import check_constraint
from kelston.ksl.loader import Catalog, SchemaDef

INSTANCE_KEYS = {"id", "conforms_to"}


@dataclass
class Store:
    """Every instance in town, addressable by id and by schema."""

    by_id: dict[str, dict] = field(default_factory=dict)
    by_schema: dict[str, list[dict]] = field(default_factory=lambda: defaultdict(list))

    def add(self, instance: dict) -> None:
        instance_id = instance.get("id")
        if instance_id in self.by_id:
            raise ValueError(f"duplicate instance id {instance_id}")
        self.by_id[instance_id] = instance
        schema_name = str(instance.get("conforms_to", "")).split("@", 1)[0]
        self.by_schema[schema_name].append(instance)

    def schema_of(self, instance_id: str) -> str | None:
        instance = self.by_id.get(instance_id)
        if instance is None:
            return None
        return str(instance.get("conforms_to", "")).split("@", 1)[0]

    @classmethod
    def from_fixture_dir(cls, directory: Path) -> "Store":
        store = cls()
        for path in sorted(directory.glob("*.jsonl")):
            for instance in read_jsonl(path):
                store.add(instance)
        return store


def read_jsonl(path: Path) -> list[dict]:
    out = []
    with open(path, encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if line:
                out.append(json.loads(line))
    return out


def write_jsonl(path: Path, instances: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as handle:
        for instance in instances:
            handle.write(json.dumps(instance, sort_keys=True, default=str) + "\n")


def validate_store(store: Store, catalog: Catalog) -> list[str]:
    errors: list[str] = []
    for instance in store.by_id.values():
        errors.extend(validate_instance(instance, catalog, store))
    return errors


def validate_instance(
    instance: dict,
    catalog: Catalog,
    store: Store,
    schema_override: SchemaDef | None = None,
) -> list[str]:
    """Validate one instance against the schema version it is stamped with.

    schema_override lets the migration engine validate against an archived
    (non-current) version of a standard.
    """
    stamp = str(instance.get("conforms_to", ""))
    if "@" not in stamp:
        return [f"{instance.get('id')}: missing or malformed conforms_to stamp"]
    schema_name, stamped_version = stamp.split("@", 1)

    if schema_override is not None:
        schema = schema_override
    else:
        schema = catalog.schemas.get(schema_name)
        if schema is None:
            return [f"{instance.get('id')}: stamped with unknown schema {schema_name}"]
        if schema.abstract:
            return [f"{instance.get('id')}: {schema_name} is abstract, instances not allowed"]
        if stamped_version != schema.version:
            return [
                f"{instance.get('id')}: stamped {schema_name}@{stamped_version} but the "
                f"current standard is {schema.version} - run `kelston upgrade`"
            ]

    errors: list[str] = []
    label = instance.get("id", "<no id>")

    prefix = _identity_prefix(schema, catalog)
    if prefix and not str(instance.get("id", "")).startswith(prefix + "-"):
        errors.append(f"{label}: id does not carry the {prefix}- prefix of {schema_name}")

    fields = (
        catalog.resolved_fields(schema.name)
        if schema_override is None
        else _override_fields(schema, catalog)
    )
    for key in instance:
        if key not in fields and key not in INSTANCE_KEYS:
            errors.append(f"{label}: unknown field {key!r} for {schema_name}")
    for name, spec in fields.items():
        if name not in instance or instance[name] is None:
            if spec.get("required"):
                errors.append(f"{label}: missing required field {name!r}")
            continue
        errors.extend(
            f"{label}.{name}: {problem}"
            for problem in _check_value(spec, instance[name], catalog, store)
        )

    for constraint in catalog.resolved_constraints(schema.name) if schema_override is None else []:
        message = check_constraint(constraint, instance, store, catalog)
        if message:
            errors.append(message)
    return errors


def _override_fields(schema: SchemaDef, catalog: Catalog) -> dict[str, dict]:
    """Resolved fields for an archived schema: its own fields plus the
    *current* ancestors' fields (core ancestors rarely break compatibility)."""
    merged: dict[str, dict] = {}
    if schema.extends and schema.extends in catalog.schemas:
        merged.update(catalog.resolved_fields(schema.extends))
    merged.update(schema.fields)
    return merged


def _identity_prefix(schema: SchemaDef, catalog: Catalog) -> str | None:
    if schema.identity_prefix:
        return schema.identity_prefix
    if schema.name in catalog.schemas:
        for ancestor in reversed(catalog.ancestors(schema.name)):
            if ancestor.identity_prefix:
                return ancestor.identity_prefix
    return None


def _check_value(spec: dict, value, catalog: Catalog, store: Store) -> list[str]:
    type_name = spec["type"]
    if type_name in types.SCALAR_TYPES:
        problem = types.check_scalar(type_name, value)
        return [problem] if problem else []
    if type_name == "vocab":
        vocab = catalog.vocabularies.get(spec["vocabulary"])
        if vocab is None:
            return [f"unknown vocabulary {spec['vocabulary']!r}"]
        if value not in vocab.codes:
            return [f"{value!r} is not a term of {vocab.name}"]
        return []
    if type_name == "ref":
        if not isinstance(value, str):
            return [f"references are ids, got {value!r}"]
        target_schema = store.schema_of(value)
        if target_schema is None:
            return [f"reference to unknown instance {value!r}"]
        entity = spec["entity"]
        if entity in catalog.schemas and not catalog.is_kind_of(target_schema, entity):
            return [f"{value!r} is a {target_schema}, expected a kind of {entity}"]
        return []
    if type_name == "list":
        if not isinstance(value, list):
            return [f"expected a list, got {type(value).__name__}"]
        problems = []
        for index, item in enumerate(value):
            problems.extend(
                f"[{index}] {p}" for p in _check_value(spec["items"], item, catalog, store)
            )
        return problems
    if type_name == "record":
        if not isinstance(value, dict):
            return [f"expected a nested record, got {type(value).__name__}"]
        problems = []
        sub_fields = spec.get("fields") or {}
        for key in value:
            if key not in sub_fields:
                problems.append(f"unknown record field {key!r}")
        for sub_name, sub_spec in sub_fields.items():
            if sub_name not in value or value[sub_name] is None:
                if sub_spec.get("required"):
                    problems.append(f"missing required record field {sub_name!r}")
                continue
            problems.extend(
                f"{sub_name}: {p}"
                for p in _check_value(sub_spec, value[sub_name], catalog, store)
            )
        return problems
    return [f"unknown type {type_name!r}"]
