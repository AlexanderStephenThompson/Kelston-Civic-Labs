"""Load every KSL schema and vocabulary into a Catalog.

The Catalog is the single in-memory picture of Kelston's standards: schema
definitions with their inheritance resolved, and vocabularies with their
term order preserved.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Iterator

import yaml

from kelston import paths


@dataclass
class Vocabulary:
    name: str
    version: str
    description: str
    ordered: bool
    terms: list[dict]
    path: Path

    @property
    def codes(self) -> list[str]:
        return [t["code"] for t in self.terms]

    def rank(self, code: str) -> int:
        return self.codes.index(code)


@dataclass
class SchemaDef:
    name: str
    version: str
    status: str
    title: str
    description: str
    extends: str | None
    abstract: bool
    identity_prefix: str | None
    fields: dict[str, dict]
    constraints: list[dict]
    path: Path
    raw: dict = field(repr=False, default_factory=dict)

    @property
    def short_name(self) -> str:
        return self.name.rsplit(".", 1)[-1]


@dataclass
class Catalog:
    schemas: dict[str, SchemaDef] = field(default_factory=dict)
    vocabularies: dict[str, Vocabulary] = field(default_factory=dict)

    def ancestors(self, name: str) -> list[SchemaDef]:
        """Inheritance chain from the root ancestor down to the schema itself."""
        chain: list[SchemaDef] = []
        current: str | None = name
        seen: set[str] = set()
        while current:
            if current in seen:
                raise ValueError(f"inheritance cycle at {current}")
            seen.add(current)
            schema = self.schemas[current]
            chain.append(schema)
            current = schema.extends
        chain.reverse()
        return chain

    def resolved_fields(self, name: str) -> dict[str, dict]:
        """All fields of a schema including inherited ones, ancestors first."""
        merged: dict[str, dict] = {}
        for ancestor in self.ancestors(name):
            merged.update(ancestor.fields)
        return merged

    def resolved_constraints(self, name: str) -> list[dict]:
        out: list[dict] = []
        for ancestor in self.ancestors(name):
            out.extend(ancestor.constraints)
        return out

    def is_kind_of(self, schema_name: str, entity_name: str) -> bool:
        """True if schema_name equals entity_name or descends from it."""
        return any(a.name == entity_name for a in self.ancestors(schema_name))

    def descendants(self, entity_name: str) -> list[str]:
        return [n for n in self.schemas if self.is_kind_of(n, entity_name)]


def schema_files(root: Path | None = None) -> Iterator[Path]:
    base = root or paths.SCHEMAS_DIR
    for directory in (base / "core", base / "sectors"):
        if directory.is_dir():
            yield from sorted(directory.rglob("*.yaml"))


def vocabulary_files(root: Path | None = None) -> Iterator[Path]:
    base = (root or paths.SCHEMAS_DIR) / "vocabularies"
    if base.is_dir():
        yield from sorted(base.glob("*.yaml"))


def load_yaml(path: Path) -> Any:
    with open(path, encoding="utf-8") as handle:
        return yaml.safe_load(handle)


def parse_schema(doc: dict, path: Path) -> SchemaDef:
    identity = doc.get("identity") or {}
    return SchemaDef(
        name=doc.get("schema", ""),
        version=str(doc.get("version", "")),
        status=doc.get("status", ""),
        title=doc.get("title", ""),
        description=doc.get("description", ""),
        extends=doc.get("extends"),
        abstract=bool(doc.get("abstract", False)),
        identity_prefix=identity.get("prefix"),
        fields=doc.get("fields") or {},
        constraints=doc.get("constraints") or [],
        path=path,
        raw=doc,
    )


def parse_vocabulary(doc: dict, path: Path) -> Vocabulary:
    return Vocabulary(
        name=doc.get("vocabulary", ""),
        version=str(doc.get("version", "")),
        description=doc.get("description", ""),
        ordered=bool(doc.get("ordered", False)),
        terms=doc.get("terms") or [],
        path=path,
    )


def load_catalog(root: Path | None = None) -> Catalog:
    """Load all schemas and vocabularies. Structural soundness is checked by
    the metaschema module; this only refuses files it cannot parse at all."""
    catalog = Catalog()
    for path in vocabulary_files(root):
        doc = load_yaml(path)
        if not isinstance(doc, dict):
            raise ValueError(f"{path}: not a mapping")
        vocab = parse_vocabulary(doc, path)
        if vocab.name in catalog.vocabularies:
            raise ValueError(f"{path}: duplicate vocabulary {vocab.name}")
        catalog.vocabularies[vocab.name] = vocab
    for path in schema_files(root):
        doc = load_yaml(path)
        if not isinstance(doc, dict):
            raise ValueError(f"{path}: not a mapping")
        # roles.yaml files are taxonomy data, not schemas; they have no `schema` key
        if "schema" not in doc:
            continue
        schema = parse_schema(doc, path)
        if schema.name in catalog.schemas:
            raise ValueError(f"{path}: duplicate schema {schema.name}")
        catalog.schemas[schema.name] = schema
    return catalog
