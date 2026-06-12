"""Meta-validation: are the schema files themselves well-formed KSL?

This is the layer that enforces the "extremely semantic" promise:
- every schema, field, vocabulary, and term carries a description
- field names are full snake_case words with type-revealing suffixes
- every vocab/ref/unit target actually exists

The canonical human-readable statement of these rules lives in
schemas/_meta/ksl.schema.yaml; this module is its executable twin.
"""

from __future__ import annotations

import re

from kelston.ksl.loader import Catalog
from kelston.ksl.types import ALL_TYPES, REQUIRED_TYPE_KEYS

SEMVER_RE = re.compile(r"^\d+\.\d+\.\d+$")
FIELD_NAME_RE = re.compile(r"^[a-z][a-z0-9]*(_[a-z0-9]+)*$")
SCHEMA_NAME_RE = re.compile(r"^kelston(\.[a-z][a-z0-9_]*)+$")
TERM_CODE_RE = re.compile(r"^[a-z][a-z0-9]*(_[a-z0-9]+)*$")
ID_PREFIX_RE = re.compile(r"^[A-Z][A-Z0-9]{1,7}$")
BOOLEAN_PREFIXES = ("is_", "has_", "can_", "requires_", "allows_", "includes_")
STATUSES = {"draft", "stable", "deprecated"}

UNITS_VOCAB = "kelston.vocab.unit"


def check_catalog(catalog: Catalog) -> list[str]:
    """Return every meta-level problem found across the catalog."""
    errors: list[str] = []
    for vocab in catalog.vocabularies.values():
        errors.extend(_check_vocabulary(vocab))
    prefixes: dict[str, str] = {}
    for schema in catalog.schemas.values():
        errors.extend(_check_schema(schema, catalog))
        if schema.identity_prefix:
            owner = prefixes.setdefault(schema.identity_prefix, schema.name)
            if owner != schema.name:
                errors.append(
                    f"{schema.path}: identity prefix {schema.identity_prefix!r} "
                    f"already belongs to {owner}"
                )
    return errors


def _check_vocabulary(vocab) -> list[str]:
    errors = []
    where = str(vocab.path)
    if not vocab.name.startswith("kelston.vocab."):
        errors.append(f"{where}: vocabulary name must start with 'kelston.vocab.'")
    if not SEMVER_RE.match(vocab.version):
        errors.append(f"{where}: version {vocab.version!r} is not semver")
    if not vocab.description.strip():
        errors.append(f"{where}: vocabulary needs a description")
    if not vocab.terms:
        errors.append(f"{where}: vocabulary has no terms")
    seen = set()
    for term in vocab.terms:
        code = term.get("code")
        if not code or not TERM_CODE_RE.match(str(code)):
            errors.append(f"{where}: bad term code {code!r}")
            continue
        if code in seen:
            errors.append(f"{where}: duplicate term code {code!r}")
        seen.add(code)
        if not str(term.get("description", "")).strip():
            errors.append(f"{where}: term {code!r} needs a description")
    return errors


def _check_schema(schema, catalog: Catalog) -> list[str]:
    errors = []
    where = str(schema.path)
    if not SCHEMA_NAME_RE.match(schema.name):
        errors.append(f"{where}: bad schema name {schema.name!r}")
    if not SEMVER_RE.match(schema.version):
        errors.append(f"{where}: version {schema.version!r} is not semver")
    if schema.status not in STATUSES:
        errors.append(f"{where}: status must be one of {sorted(STATUSES)}")
    if not schema.title.strip():
        errors.append(f"{where}: schema needs a title")
    if not schema.description.strip():
        errors.append(f"{where}: schema needs a description")
    if schema.extends and schema.extends not in catalog.schemas:
        errors.append(f"{where}: extends unknown schema {schema.extends!r}")
        return errors  # cannot resolve inheritance further
    if not schema.abstract and not _identity_prefix(schema, catalog):
        errors.append(f"{where}: concrete schema needs identity.prefix (or an ancestor's)")
    if schema.identity_prefix and not ID_PREFIX_RE.match(schema.identity_prefix):
        errors.append(f"{where}: identity prefix {schema.identity_prefix!r} must be 2-8 capitals")

    inherited = set()
    if schema.extends:
        inherited = set(catalog.resolved_fields(schema.extends))
    for name, spec in schema.fields.items():
        errors.extend(_check_field(name, spec, where, catalog, inherited))
    for constraint in schema.constraints:
        errors.extend(_check_constraint(constraint, where))
    return errors


def _identity_prefix(schema, catalog: Catalog) -> str | None:
    for ancestor in reversed(catalog.ancestors(schema.name)):
        if ancestor.identity_prefix:
            return ancestor.identity_prefix
    return None


def _check_field(name: str, spec, where: str, catalog: Catalog, inherited: set[str]) -> list[str]:
    errors = []
    label = f"{where}: field {name!r}"
    if not FIELD_NAME_RE.match(name):
        errors.append(f"{label}: not snake_case")
    if name in inherited:
        errors.append(f"{label}: redefines an inherited field")
    if not isinstance(spec, dict):
        return errors + [f"{label}: definition must be a mapping"]

    type_name = spec.get("type")
    if type_name not in ALL_TYPES:
        return errors + [f"{label}: unknown type {type_name!r}"]
    if not str(spec.get("description", "")).strip():
        errors.append(f"{label}: needs a description")

    for key in REQUIRED_TYPE_KEYS.get(type_name, []):
        if key not in spec:
            errors.append(f"{label}: type {type_name} requires {key!r}")

    # Type-revealing suffixes and prefixes: names should read like sentences.
    if type_name == "boolean" and not name.startswith(BOOLEAN_PREFIXES):
        errors.append(f"{label}: booleans read as predicates (is_/has_/can_/requires_...)")
    if type_name == "date" and not name.endswith("_on"):
        errors.append(f"{label}: date fields end in _on")
    if type_name == "datetime" and not name.endswith("_at"):
        errors.append(f"{label}: datetime fields end in _at")
    if type_name == "duration" and not name.endswith("_duration"):
        errors.append(f"{label}: duration fields end in _duration")

    if type_name == "vocab":
        target = spec.get("vocabulary")
        vocab = catalog.vocabularies.get(target)
        if vocab is None:
            errors.append(f"{label}: unknown vocabulary {target!r}")
        elif "default" in spec and spec["default"] not in vocab.codes:
            errors.append(f"{label}: default {spec['default']!r} not in {target}")
    if type_name == "quantity":
        units = catalog.vocabularies.get(UNITS_VOCAB)
        unit = spec.get("unit")
        if units is not None and unit not in units.codes:
            errors.append(f"{label}: unit {unit!r} not in {UNITS_VOCAB}")
    if type_name == "ref":
        target = spec.get("entity")
        if target not in catalog.schemas:
            errors.append(f"{label}: ref to unknown entity {target!r}")
    if type_name == "list":
        items = spec.get("items")
        if not isinstance(items, dict):
            errors.append(f"{label}: items must be a field definition")
        else:
            item_spec = dict(items)
            item_spec.setdefault("description", "items")
            errors.extend(_check_field(f"{name}_items", item_spec, where, catalog, set()))
    if type_name == "record":
        for sub_name, sub_spec in (spec.get("fields") or {}).items():
            errors.extend(_check_field(sub_name, sub_spec, where, catalog, set()))
    return errors


def _check_constraint(constraint, where: str) -> list[str]:
    errors = []
    if not isinstance(constraint, dict) or not constraint.get("id"):
        return [f"{where}: every constraint needs an id"]
    label = f"{where}: constraint {constraint['id']!r}"
    if not constraint.get("rule") and not constraint.get("check"):
        errors.append(f"{label}: needs a declarative 'check' or a python 'rule'")
    for clause_key in ("when", "check"):
        clause = constraint.get(clause_key)
        if clause is None:
            continue
        if not isinstance(clause, dict) or "field" not in clause or "op" not in clause:
            errors.append(f"{label}: {clause_key} needs 'field' and 'op'")
        elif clause["op"] not in {"eq", "ne", "gte", "lte", "in", "contains", "present", "absent"}:
            errors.append(f"{label}: unknown op {clause['op']!r}")
        elif clause["op"] not in {"present", "absent"} and (
            "value" not in clause and "other_field" not in clause
        ):
            errors.append(f"{label}: {clause_key} needs 'value' or 'other_field'")
    rule = constraint.get("rule")
    if rule is not None and not str(rule).startswith("python:"):
        errors.append(f"{label}: rule must look like 'python:module.function'")
    return errors
