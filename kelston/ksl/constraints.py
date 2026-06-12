"""Constraint evaluation: declarative comparisons plus the single Python
escape hatch (`rule: python:module.function`).

Declarative clauses support dotted paths that traverse references, so
`steward.species.locomotion` walks plot -> citizen -> species_profile.
"""

from __future__ import annotations

import importlib
from dataclasses import dataclass
from typing import Any

from kelston.ksl.loader import Catalog

MISSING = object()


@dataclass
class RuleContext:
    """What a python rule gets to work with."""

    catalog: Catalog
    store: "Store"  # noqa: F821 - defined in validator, imported lazily to avoid a cycle

    def resolve(self, instance: dict, path: str) -> Any:
        return resolve_path(instance, path, self.store)


def resolve_path(instance: dict, path: str, store) -> Any:
    """Walk a dotted path, dereferencing ids through the store as needed."""
    current: Any = instance
    segments = path.split(".")
    for index, segment in enumerate(segments):
        if isinstance(current, str) and current in store.by_id:
            current = store.by_id[current]
        if not isinstance(current, dict):
            return MISSING
        current = current.get(segment, MISSING)
        if current is MISSING:
            return MISSING
    # A trailing ref left as an id stays an id; callers compare ids directly.
    return current


def evaluate_clause(clause: dict, instance: dict, store, catalog: Catalog) -> bool:
    value = resolve_path(instance, clause["field"], store)
    op = clause["op"]
    if op == "present":
        return value is not MISSING and value is not None
    if op == "absent":
        return value is MISSING or value is None
    if value is MISSING:
        # A comparison against an absent optional field is vacuously true;
        # required-ness is the validator's job, not the constraint's.
        return True
    if "other_field" in clause:
        expected = resolve_path(instance, clause["other_field"], store)
        if expected is MISSING:
            return True
    else:
        expected = clause["value"]
    if op == "eq":
        return value == expected
    if op == "ne":
        return value != expected
    if op == "in":
        return value in expected
    if op == "contains":
        return isinstance(value, (list, str)) and expected in value
    if op in ("gte", "lte"):
        value, expected = _comparable(value, expected, clause, catalog)
        if value is None or expected is None:
            return False
        return value >= expected if op == "gte" else value <= expected
    raise ValueError(f"unknown op {op!r}")


def _comparable(value, expected, clause: dict, catalog: Catalog):
    """Numbers compare directly; ordered-vocabulary codes compare by rank."""
    if isinstance(value, (int, float)) and isinstance(expected, (int, float)):
        return value, expected
    if isinstance(value, str) and isinstance(expected, str):
        vocab_name = clause.get("vocabulary")
        candidates = (
            [catalog.vocabularies[vocab_name]]
            if vocab_name
            else [v for v in catalog.vocabularies.values() if v.ordered]
        )
        for vocab in candidates:
            if value in vocab.codes and expected in vocab.codes:
                return vocab.rank(value), vocab.rank(expected)
    return None, None


def check_constraint(constraint: dict, instance: dict, store, catalog: Catalog) -> str | None:
    """Return an error message if the constraint is violated."""
    when = constraint.get("when")
    if when is not None and not evaluate_clause(when, instance, store, catalog):
        return None
    if "check" in constraint:
        if not evaluate_clause(constraint["check"], instance, store, catalog):
            return _violation(constraint, instance)
    rule = constraint.get("rule")
    if rule:
        function = load_rule(rule)
        message = function(instance, RuleContext(catalog=catalog, store=store))
        if message:
            return f"{_violation(constraint, instance)} ({message})"
    return None


def load_rule(rule: str):
    """Resolve 'python:agriculture.semi_aquatic_steward_check' to a callable
    in kelston.rules.agriculture."""
    spec = rule.removeprefix("python:")
    module_name, _, function_name = spec.rpartition(".")
    module = importlib.import_module(f"kelston.rules.{module_name}")
    return getattr(module, function_name)


def _violation(constraint: dict, instance: dict) -> str:
    return f"{instance.get('id', '<no id>')}: violates {constraint['id']}"
