# Versioning & Update Propagation

This is the heart of the experiment. In the real world, a standards change
means months of cleanup. In Kelston, a standard changes, one command runs,
and every record in town is current and provably valid.

## The registry

[`registry/manifest.yaml`](../registry/manifest.yaml) records, for every
schema and vocabulary: the current version, a sha256 checksum of the file,
its dependencies (pinned to majors), and its full history. Checksums make
silent drift impossible - editing a file without recording the bump fails
`kelston registry status`, and therefore CI.

Every instance is stamped with exactly what it conforms to:

```json
{"id": "PLOT-000482", "conforms_to": "kelston.agriculture.growing_plot@2.0.0", ...}
```

The stamp is a column in SQLite and a key in every fixture. "What version
is this record?" is never a guess.

## Change classes

`kelston registry diff <name>` compares the newest archived version against
the current file and classifies the change mechanically:

- **PATCH** - descriptions, titles, lore. No instance impact.
- **MINOR** - new optional field, new vocabulary term, loosened constraint.
  Instances auto-adopt: re-validate, restamp, done.
- **MAJOR** - removed/renamed field, type change, new required field,
  removed term, tightened constraint. **CI fails unless a migration file
  exists.**

## Migrations are data

A MAJOR change ships with a declarative migration in
[`registry/migrations/`](../registry/migrations/):

```yaml
migration:
  schema: kelston.agriculture.growing_plot
  from: ">=1.0.0 <2.0.0"
  to: 2.0.0
  summary: Renamed keeper to steward; split soil_class into texture + drainage.
operations:
  - rename_field: { from: keeper, to: steward }
  - derive_field:
      name: drainage_class
      using: python:agriculture.derive_drainage_from_legacy_soil
  - map_vocab:
      field: soil_class
      mapping: { loam_wet: loam, loam_dry: loam, clay_heavy: clay }
```

Four operations (`rename_field`, `add_field`, `remove_field`, `map_vocab`)
cover the routine cases; `derive_field` reaches into `kelston/rules/` for
the hard ones - the same single escape hatch the constraint system uses.
Operations run in order, so a deriver can read legacy codes before
`map_vocab` rewrites them.

## The demo

The repo ships a legacy corpus - every growing plot as it was recorded
under the 1.x standard, in
`data/fixtures/legacy/growing_plot@1.2.0.jsonl`. Then:

```
$ kelston upgrade
Scanned 1,118 legacy instances: 1,118 upgraded, 0 already current, 0 failures.
```

Each instance walks through the migration chain, gets restamped, and is
re-validated against the current standard - types, vocabularies,
references, and cross-entity constraints included. A report lands in
`data/reports/`. The round-trip is also a test
([`tests/test_migration.py`](../tests/test_migration.py)): migrated legacy
records must equal the current records exactly.

## The contributor loop

1. Edit a schema or vocabulary.
2. `kelston registry diff <name>` tells you what class of change you made.
3. Update the file's `version`, then `kelston registry bump <name> <level>`.
4. MAJOR? Write the migration. `kelston upgrade` must run clean.
5. `kelston generate && kelston validate --all` - PR.

The standards office of Kelston (a real industry in the governance sector -
see `schemas/sectors/governance/`) would tell you this is the whole point:
change is welcome, drift is impossible.
