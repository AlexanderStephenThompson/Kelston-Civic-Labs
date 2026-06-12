# The Kelston Schema Language (KSL)

KSL is how Kelston writes its data standards: YAML documents that are
pleasant to read, mechanically checkable, and impossible to drift out of
date silently. The canonical self-description lives at
[`schemas/_meta/ksl.schema.yaml`](../schemas/_meta/ksl.schema.yaml); its
executable twin is [`kelston/ksl/metaschema.py`](../kelston/ksl/metaschema.py).
CI runs the twin against every schema, so this document can stay friendly -
the rules are enforced elsewhere.

## Design intent

The whole experiment rests on one idea: **if everyone in an industry records
the same things the same way, data cleaning disappears.** KSL pushes that
idea into the language itself:

- **Names mean things.** Fields are full snake_case words. Dates end `_on`,
  datetimes `_at`, durations `_duration`; booleans read as predicates
  (`requires_basking_heat`). A reader needs no legend.
- **Descriptions are mandatory.** Every schema, field, vocabulary, and term
  carries one. The meta-validator fails CI otherwise.
- **Units live in the schema, not the data.** A `quantity` field declares its
  unit once (`unit: kilogram`); instances store bare numbers. No record can
  be ambiguous about what its "5" means.
- **Closed vocabularies, open growth.** Categorical fields draw from named,
  versioned vocabularies. Adding a term is a MINOR change everyone receives;
  redefining one is a MAJOR change with a migration.
- **References are typed.** `type: ref` declares the entity it points to,
  and the validator checks both that the target exists and that it is the
  right kind of thing (inheritance-aware).

## A schema file

```yaml
schema: kelston.agriculture.growing_plot   # dotted, always kelston.*
version: 2.0.0                             # semver, tracked by the registry
status: stable                             # draft | stable | deprecated
title: Growing Plot
description: >
  A bounded area of cultivated ground within a farm or commons garden - the
  unit at which plantings, soil care, and harvests are recorded.
extends: kelston.core.place                # single inheritance only
identity: { prefix: PLOT }                 # ids look like PLOT-000482
fields:
  area:
    type: quantity
    unit: square_meter
    required: true
    description: Cultivable surface area of the plot.
constraints:
  - id: submerged_plots_have_water_substrate
    description: A submerged plot's growing medium is water, by definition.
    when: { field: vertical_tier, op: eq, value: submerged }
    check: { field: soil_class, op: eq, value: substrate_water }
```

## The type system (closed set)

| type | instance value | notes |
|---|---|---|
| `id` | `PLOT-000482` | prefix + serial |
| `text` | string | |
| `integer`, `decimal`, `boolean` | as named | booleans are real booleans |
| `date`, `time_of_day`, `datetime` | ISO strings | `2026-06-12`, `08:30`, full ISO |
| `duration` | `P3D`, `PT2H`, `P1DT4H30M` | |
| `quantity` | bare number | unit declared in the schema |
| `vocab` | a term code | `vocabulary:` names the standard |
| `ref` | another instance's id | `entity:` names the target schema |
| `list` | array | `items:` is a field definition |
| `record` | nested object | `fields:` defines it inline |

## Vocabularies

One format for everything from species traits to produce grades:

```yaml
vocabulary: kelston.vocab.size_class
version: 1.0.0
description: Body-size bands that drive housing clearance, transit seating...
ordered: true        # term order is meaningful
terms:
  - code: tiny
    label: Tiny
    description: Under about 25 cm standing height...
```

`ordered: true` is the structural workhorse: it lets a constraint compare
terms with `gte`/`lte`, which is how "this dwelling fits this citizen"
becomes a mechanical check instead of a viewing appointment.

## Constraints

Declarative clauses cover most rules. Paths are dotted and traverse
references: `steward.species.locomotion` walks plot -> citizen -> species
profile. Ops: `eq ne gte lte in contains present absent`; compare against a
literal `value` or an `other_field` path.

Anything richer is a named python rule - `rule: python:module.function`,
resolved in [`kelston/rules/`](../kelston/rules/). One escape hatch, never
two; the rules are small, named, and tested.

## Inheritance

`extends` is single inheritance. Children inherit all parent fields and
constraints and may not redefine them. Two abstract bases organize the town:
`kelston.core.place` (anything located) and `kelston.core.civic_record`
(anything dated) - the latter gives every sector's records one queryable
event spine.
